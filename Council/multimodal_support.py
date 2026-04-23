import json
import base64
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field


@dataclass
class MultiModalContent:
    """Container for multi-modal content"""
    content_id: str
    content_type: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "data_summary": self._summarize_data()
        }
    
    def _summarize_data(self) -> str:
        if self.content_type == "text":
            return f"Text: {len(str(self.data))} characters"
        elif self.content_type == "code":
            return f"Code: {len(str(self.data))} characters"
        elif self.content_type == "data":
            return f"Data: {type(self.data).__name__}"
        elif self.content_type == "chart":
            return f"Chart: {self.metadata.get('chart_type', 'unknown')}"
        elif self.content_type == "image":
            return "Image data"
        else:
            return f"Content type: {self.content_type}"


class MultiModalProcessor:
    """Process and integrate multi-modal inputs"""
    
    def __init__(self):
        self.content_store: Dict[str, MultiModalContent] = {}
        self.content_counter = 0
        self.processing_history: List[Dict[str, Any]] = []
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add text content"""
        
        self.content_counter += 1
        content_id = f"text_{self.content_counter}"
        
        content = MultiModalContent(
            content_id=content_id,
            content_type="text",
            data=text,
            metadata=metadata or {}
        )
        
        self.content_store[content_id] = content
        
        self.processing_history.append({
            "action": "add_text",
            "content_id": content_id,
            "length": len(text),
            "timestamp": time.time()
        })
        
        return content_id
    
    def add_code(self, code: str, language: str = "python", 
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add code content"""
        
        self.content_counter += 1
        content_id = f"code_{self.content_counter}"
        
        meta = metadata or {}
        meta["language"] = language
        
        content = MultiModalContent(
            content_id=content_id,
            content_type="code",
            data=code,
            metadata=meta
        )
        
        self.content_store[content_id] = content
        
        self.processing_history.append({
            "action": "add_code",
            "content_id": content_id,
            "language": language,
            "timestamp": time.time()
        })
        
        return content_id
    
    def add_data(self, data: Union[Dict, List], data_format: str = "json",
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add structured data"""
        
        self.content_counter += 1
        content_id = f"data_{self.content_counter}"
        
        meta = metadata or {}
        meta["format"] = data_format
        
        content = MultiModalContent(
            content_id=content_id,
            content_type="data",
            data=data,
            metadata=meta
        )
        
        self.content_store[content_id] = content
        
        self.processing_history.append({
            "action": "add_data",
            "content_id": content_id,
            "format": data_format,
            "timestamp": time.time()
        })
        
        return content_id
    
    def add_chart(self, chart_data: Dict[str, Any], chart_type: str = "bar",
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add chart/visualization data"""
        
        self.content_counter += 1
        content_id = f"chart_{self.content_counter}"
        
        meta = metadata or {}
        meta["chart_type"] = chart_type
        
        content = MultiModalContent(
            content_id=content_id,
            content_type="chart",
            data=chart_data,
            metadata=meta
        )
        
        self.content_store[content_id] = content
        
        self.processing_history.append({
            "action": "add_chart",
            "content_id": content_id,
            "chart_type": chart_type,
            "timestamp": time.time()
        })
        
        return content_id
    
    def add_tool_output(self, tool_name: str, output: Any,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add tool execution output"""
        
        self.content_counter += 1
        content_id = f"tool_{self.content_counter}"
        
        meta = metadata or {}
        meta["tool_name"] = tool_name
        
        content = MultiModalContent(
            content_id=content_id,
            content_type="tool_output",
            data=output,
            metadata=meta
        )
        
        self.content_store[content_id] = content
        
        self.processing_history.append({
            "action": "add_tool_output",
            "content_id": content_id,
            "tool_name": tool_name,
            "timestamp": time.time()
        })
        
        return content_id
    
    def get_content(self, content_id: str) -> Optional[MultiModalContent]:
        """Retrieve content by ID"""
        return self.content_store.get(content_id)
    
    def integrate_into_argument(self, content_ids: List[str], base_argument: str) -> str:
        """Integrate multi-modal content into an argument"""
        
        integrated = base_argument + "\n\n"
        
        for content_id in content_ids:
            content = self.get_content(content_id)
            if not content:
                continue
            
            if content.content_type == "text":
                integrated += f"\nSupporting text: {content.data}\n"
            
            elif content.content_type == "code":
                language = content.metadata.get("language", "")
                integrated += f"\nCode example ({language}):\n{content.data}\n"
            
            elif content.content_type == "data":
                data_format = content.metadata.get("format", "json")
                if data_format == "json":
                    integrated += f"\nData: {json.dumps(content.data, indent=2)}\n"
                else:
                    integrated += f"\nData: {content.data}\n"
            
            elif content.content_type == "chart":
                chart_type = content.metadata.get("chart_type", "unknown")
                integrated += f"\nVisualization ({chart_type}): [Chart data available]\n"
            
            elif content.content_type == "tool_output":
                tool_name = content.metadata.get("tool_name", "unknown")
                integrated += f"\nTool output from {tool_name}: {content.data}\n"
        
        return integrated
    
    def extract_references(self, argument: str) -> List[str]:
        """Extract content references from argument text"""
        
        import re
        
        pattern = r'\[ref:(\w+_\d+)\]'
        matches = re.findall(pattern, argument)
        
        return matches
    
    def resolve_references(self, argument: str) -> str:
        """Resolve content references in argument"""
        
        references = self.extract_references(argument)
        
        resolved = argument
        for ref_id in references:
            content = self.get_content(ref_id)
            if content:
                placeholder = f"[ref:{ref_id}]"
                
                if content.content_type == "text":
                    replacement = content.data
                elif content.content_type == "code":
                    replacement = f"```{content.metadata.get('language', '')}\n{content.data}\n```"
                elif content.content_type == "data":
                    replacement = json.dumps(content.data)
                else:
                    replacement = f"[{content.content_type} content]"
                
                resolved = resolved.replace(placeholder, replacement)
        
        return resolved
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get summary of all content"""
        
        type_counts = {}
        for content in self.content_store.values():
            type_counts[content.content_type] = type_counts.get(content.content_type, 0) + 1
        
        return {
            "total_content": len(self.content_store),
            "content_by_type": type_counts,
            "recent_additions": self.processing_history[-10:]
        }
    
    def export_content(self, filepath: str):
        """Export all content to file"""
        
        export_data = {
            "content": [c.to_dict() for c in self.content_store.values()],
            "summary": self.get_content_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)


class RichArgumentBuilder:
    """Build arguments with multi-modal content"""
    
    def __init__(self):
        self.processor = MultiModalProcessor()
        self.arguments: List[Dict[str, Any]] = []
    
    def create_argument(self, base_text: str, agent_id: str) -> Dict[str, Any]:
        """Create a new argument"""
        
        argument = {
            "argument_id": f"arg_{len(self.arguments) + 1}",
            "agent_id": agent_id,
            "base_text": base_text,
            "content_ids": [],
            "timestamp": time.time()
        }
        
        self.arguments.append(argument)
        
        return argument
    
    def add_supporting_code(self, argument_id: str, code: str, language: str = "python"):
        """Add code to support an argument"""
        
        content_id = self.processor.add_code(code, language)
        
        argument = next((a for a in self.arguments if a["argument_id"] == argument_id), None)
        if argument:
            argument["content_ids"].append(content_id)
    
    def add_supporting_data(self, argument_id: str, data: Union[Dict, List]):
        """Add data to support an argument"""
        
        content_id = self.processor.add_data(data)
        
        argument = next((a for a in self.arguments if a["argument_id"] == argument_id), None)
        if argument:
            argument["content_ids"].append(content_id)
    
    def add_tool_result(self, argument_id: str, tool_name: str, result: Any):
        """Add tool execution result to argument"""
        
        content_id = self.processor.add_tool_output(tool_name, result)
        
        argument = next((a for a in self.arguments if a["argument_id"] == argument_id), None)
        if argument:
            argument["content_ids"].append(content_id)
    
    def build_final_argument(self, argument_id: str) -> str:
        """Build final argument with all content integrated"""
        
        argument = next((a for a in self.arguments if a["argument_id"] == argument_id), None)
        if not argument:
            return ""
        
        return self.processor.integrate_into_argument(
            argument["content_ids"],
            argument["base_text"]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get builder statistics"""
        
        return {
            "total_arguments": len(self.arguments),
            "content_summary": self.processor.get_content_summary()
        }
