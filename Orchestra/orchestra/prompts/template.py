import re
from typing import Any, Dict, List, Optional, Union


class PromptTemplate:
    def __init__(
        self,
        template: str,
        input_variables: Optional[List[str]] = None,
        partial_variables: Optional[Dict[str, Any]] = None,
        template_format: str = "f-string"
    ):
        self.template = template
        self.template_format = template_format
        self.partial_variables = partial_variables or {}
        
        if input_variables is None:
            self.input_variables = self._extract_variables()
        else:
            self.input_variables = input_variables
    
    def _extract_variables(self) -> List[str]:
        if self.template_format == "f-string":
            pattern = r'\{([^{}]+)\}'
        elif self.template_format == "jinja2":
            pattern = r'\{\{([^{}]+)\}\}'
        else:
            pattern = r'\{([^{}]+)\}'
        
        matches = re.findall(pattern, self.template)
        return list(set(matches))
    
    def format(self, **kwargs) -> str:
        all_vars = {**self.partial_variables, **kwargs}
        
        missing_vars = set(self.input_variables) - set(all_vars.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        if self.template_format == "f-string":
            return self.template.format(**all_vars)
        elif self.template_format == "jinja2":
            template_str = self.template
            for key, value in all_vars.items():
                template_str = template_str.replace(f"{{{{{key}}}}}", str(value))
            return template_str
        else:
            return self.template.format(**all_vars)
    
    def partial(self, **kwargs) -> 'PromptTemplate':
        new_partial = {**self.partial_variables, **kwargs}
        return PromptTemplate(
            template=self.template,
            input_variables=self.input_variables,
            partial_variables=new_partial,
            template_format=self.template_format
        )
    
    @classmethod
    def from_template(cls, template: str, **kwargs) -> 'PromptTemplate':
        return cls(template=template, **kwargs)
    
    @classmethod
    def from_file(cls, file_path: str, **kwargs) -> 'PromptTemplate':
        with open(file_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return cls(template=template, **kwargs)


class ChatPromptTemplate:
    def __init__(
        self,
        messages: List[Dict[str, Union[str, PromptTemplate]]],
        input_variables: Optional[List[str]] = None
    ):
        self.messages = messages
        self.input_variables = input_variables or self._extract_all_variables()
    
    def _extract_all_variables(self) -> List[str]:
        all_vars = set()
        for message in self.messages:
            content = message.get("content", "")
            if isinstance(content, PromptTemplate):
                all_vars.update(content.input_variables)
            elif isinstance(content, str):
                pattern = r'\{([^{}]+)\}'
                matches = re.findall(pattern, content)
                all_vars.update(matches)
        return list(all_vars)
    
    def format_messages(self, **kwargs) -> List[Dict[str, str]]:
        formatted_messages = []
        
        for message in self.messages:
            role = message["role"]
            content = message["content"]
            
            if isinstance(content, PromptTemplate):
                formatted_content = content.format(**kwargs)
            elif isinstance(content, str):
                formatted_content = content.format(**kwargs)
            else:
                formatted_content = str(content)
            
            formatted_messages.append({
                "role": role,
                "content": formatted_content
            })
        
        return formatted_messages
    
    @classmethod
    def from_messages(
        cls,
        messages: List[tuple]
    ) -> 'ChatPromptTemplate':
        formatted_messages = []
        for role, content in messages:
            if isinstance(content, str):
                formatted_messages.append({"role": role, "content": content})
            else:
                formatted_messages.append({"role": role, "content": content})
        
        return cls(messages=formatted_messages)
    
    @classmethod
    def from_template(cls, system: str, human: str) -> 'ChatPromptTemplate':
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": human}
        ]
        return cls(messages=messages)


class FewShotPromptTemplate:
    def __init__(
        self,
        examples: List[Dict[str, str]],
        example_template: PromptTemplate,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        input_variables: Optional[List[str]] = None,
        example_separator: str = "\n\n"
    ):
        self.examples = examples
        self.example_template = example_template
        self.prefix = prefix or ""
        self.suffix = suffix or ""
        self.example_separator = example_separator
        self.input_variables = input_variables or []
    
    def format(self, **kwargs) -> str:
        example_strings = []
        for example in self.examples:
            example_strings.append(self.example_template.format(**example))
        
        examples_text = self.example_separator.join(example_strings)
        
        parts = []
        if self.prefix:
            parts.append(self.prefix.format(**kwargs))
        parts.append(examples_text)
        if self.suffix:
            parts.append(self.suffix.format(**kwargs))
        
        return "\n\n".join(parts)
    
    def add_example(self, example: Dict[str, str]) -> None:
        self.examples.append(example)
    
    @classmethod
    def from_examples(
        cls,
        examples: List[Dict[str, str]],
        example_prompt: str,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        **kwargs
    ) -> 'FewShotPromptTemplate':
        example_template = PromptTemplate.from_template(example_prompt)
        return cls(
            examples=examples,
            example_template=example_template,
            prefix=prefix,
            suffix=suffix,
            **kwargs
        )
