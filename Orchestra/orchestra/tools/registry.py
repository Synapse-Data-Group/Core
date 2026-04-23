from typing import Any, Callable, Dict, List, Optional
from .base import Tool, ToolType, ToolSchema


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.tool_categories: Dict[str, List[str]] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        required: Optional[List[str]] = None,
        tool_type: ToolType = ToolType.FUNCTION,
        returns: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tool:
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")
        
        tool = Tool(
            name=name,
            func=func,
            description=description,
            parameters=parameters,
            required=required,
            tool_type=tool_type,
            returns=returns,
            examples=examples,
            metadata=metadata
        )
        
        self.tools[name] = tool
        
        if category:
            if category not in self.tool_categories:
                self.tool_categories[category] = []
            self.tool_categories[category].append(name)
        
        return tool
    
    def register_tool(self, tool: Tool, category: Optional[str] = None) -> None:
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        
        self.tools[tool.name] = tool
        
        if category:
            if category not in self.tool_categories:
                self.tool_categories[category] = []
            self.tool_categories[category].append(tool.name)
    
    def unregister(self, name: str) -> None:
        if name in self.tools:
            del self.tools[name]
            
            for category, tool_names in self.tool_categories.items():
                if name in tool_names:
                    tool_names.remove(name)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        tool_names = self.tool_categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_all_tools(self) -> Dict[str, Tool]:
        return self.tools.copy()
    
    def get_tool_names(self) -> List[str]:
        return list(self.tools.keys())
    
    def get_schemas(self) -> List[ToolSchema]:
        return [tool.get_schema() for tool in self.tools.values()]
    
    def get_openai_functions(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_function() for tool in self.tools.values()]
    
    def get_anthropic_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_anthropic_tool() for tool in self.tools.values()]
    
    def search_tools(self, query: str) -> List[Tool]:
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_tools": len(self.tools),
            "categories": len(self.tool_categories),
            "tool_stats": {
                name: tool.get_statistics()
                for name, tool in self.tools.items()
            }
        }
    
    def clear(self) -> None:
        self.tools.clear()
        self.tool_categories.clear()
