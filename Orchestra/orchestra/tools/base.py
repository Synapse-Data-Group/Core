import asyncio
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ToolType(Enum):
    FUNCTION = "function"
    API = "api"
    SEARCH = "search"
    COMPUTATION = "computation"
    CUSTOM = "custom"


@dataclass
class ToolSchema:
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = field(default_factory=list)
    returns: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "required": self.required,
            "returns": self.returns,
            "examples": self.examples
        }
    
    def to_openai_function(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required
            }
        }
    
    def to_anthropic_tool(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required
            }
        }


@dataclass
class ToolResult:
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


class Tool:
    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        required: Optional[List[str]] = None,
        tool_type: ToolType = ToolType.FUNCTION,
        returns: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters
        self.required = required or []
        self.tool_type = tool_type
        self.returns = returns
        self.examples = examples or []
        self.metadata = metadata or {}
        self.execution_count = 0
        self.success_count = 0
        self.total_execution_time = 0.0
        
        self.schema = ToolSchema(
            name=name,
            description=description,
            parameters=parameters,
            required=required or [],
            returns=returns,
            examples=examples or []
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        start_time = time.time()
        self.execution_count += 1
        
        missing_params = set(self.required) - set(kwargs.keys())
        if missing_params:
            return ToolResult(
                success=False,
                output=None,
                error=f"Missing required parameters: {missing_params}",
                execution_time=time.time() - start_time
            )
        
        try:
            result = self.func(**kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            
            execution_time = time.time() - start_time
            self.success_count += 1
            self.total_execution_time += execution_time
            
            return ToolResult(
                success=True,
                output=result,
                execution_time=execution_time,
                metadata={"tool_name": self.name, "tool_type": self.tool_type.value}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                metadata={"tool_name": self.name, "tool_type": self.tool_type.value}
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.tool_type.value,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / self.execution_count if self.execution_count > 0 else 0.0,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": self.total_execution_time / self.execution_count if self.execution_count > 0 else 0.0
        }
    
    def get_schema(self) -> ToolSchema:
        return self.schema
    
    def to_openai_function(self) -> Dict[str, Any]:
        return self.schema.to_openai_function()
    
    def to_anthropic_tool(self) -> Dict[str, Any]:
        return self.schema.to_anthropic_tool()
