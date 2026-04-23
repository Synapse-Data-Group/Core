import json
import re
from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod


class OutputParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> Any:
        pass
    
    @abstractmethod
    def get_format_instructions(self) -> str:
        pass


class JSONParser(OutputParser):
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        self.schema = schema
    
    def parse(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
        
        try:
            parsed = json.loads(text)
            
            if self.schema:
                self._validate_schema(parsed, self.schema)
            
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}")
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
    
    def get_format_instructions(self) -> str:
        if self.schema:
            return f"Return a valid JSON object matching this schema:\n{json.dumps(self.schema, indent=2)}"
        return "Return a valid JSON object."


class StructuredParser(OutputParser):
    def __init__(self, fields: Dict[str, Type]):
        self.fields = fields
    
    def parse(self, text: str) -> Dict[str, Any]:
        result = {}
        
        for field_name, field_type in self.fields.items():
            pattern = rf'{field_name}:\s*(.+?)(?:\n|$)'
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                value = match.group(1).strip()
                
                try:
                    if field_type == int:
                        result[field_name] = int(value)
                    elif field_type == float:
                        result[field_name] = float(value)
                    elif field_type == bool:
                        result[field_name] = value.lower() in ['true', 'yes', '1']
                    elif field_type == list:
                        result[field_name] = [item.strip() for item in value.split(',')]
                    else:
                        result[field_name] = value
                except (ValueError, TypeError):
                    result[field_name] = value
        
        return result
    
    def get_format_instructions(self) -> str:
        instructions = ["Return your response in the following format:"]
        for field_name, field_type in self.fields.items():
            type_name = field_type.__name__ if hasattr(field_type, '__name__') else str(field_type)
            instructions.append(f"{field_name}: <{type_name}>")
        return "\n".join(instructions)


class ListParser(OutputParser):
    def __init__(self, item_separator: str = "\n", strip_items: bool = True):
        self.item_separator = item_separator
        self.strip_items = strip_items
    
    def parse(self, text: str) -> List[str]:
        items = text.split(self.item_separator)
        
        if self.strip_items:
            items = [item.strip() for item in items]
        
        items = [item for item in items if item]
        
        cleaned_items = []
        for item in items:
            item = re.sub(r'^\d+[\.\)]\s*', '', item)
            item = re.sub(r'^[-*•]\s*', '', item)
            if item:
                cleaned_items.append(item)
        
        return cleaned_items
    
    def get_format_instructions(self) -> str:
        return f"Return a list of items separated by '{self.item_separator}'."


class RegexParser(OutputParser):
    def __init__(self, pattern: str, group: int = 0):
        self.pattern = pattern
        self.group = group
    
    def parse(self, text: str) -> str:
        match = re.search(self.pattern, text, re.DOTALL)
        if match:
            return match.group(self.group)
        raise ValueError(f"Pattern '{self.pattern}' not found in text")
    
    def get_format_instructions(self) -> str:
        return f"Ensure your response matches the pattern: {self.pattern}"


class ChainParser(OutputParser):
    def __init__(self, parsers: List[OutputParser]):
        self.parsers = parsers
    
    def parse(self, text: str) -> Any:
        result = text
        for parser in self.parsers:
            result = parser.parse(str(result))
        return result
    
    def get_format_instructions(self) -> str:
        instructions = []
        for i, parser in enumerate(self.parsers, 1):
            instructions.append(f"Step {i}: {parser.get_format_instructions()}")
        return "\n".join(instructions)
