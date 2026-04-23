import asyncio
from typing import Any, Dict, List, Optional
from .base import Tool, ToolResult
from .registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        result = await tool.execute(**parameters)
        
        self.execution_history.append({
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result.to_dict(),
            "context": context
        })
        
        return result
    
    async def execute_batch(
        self,
        tool_calls: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[ToolResult]:
        if parallel:
            tasks = [
                self.execute(call["tool_name"], call.get("parameters", {}))
                for call in tool_calls
            ]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for call in tool_calls:
                result = await self.execute(call["tool_name"], call.get("parameters", {}))
                results.append(result)
            return results
    
    async def execute_chain(
        self,
        tool_chain: List[Dict[str, Any]],
        initial_input: Optional[Any] = None
    ) -> ToolResult:
        current_output = initial_input
        
        for i, tool_call in enumerate(tool_chain):
            tool_name = tool_call["tool_name"]
            parameters = tool_call.get("parameters", {})
            
            if i > 0 and "use_previous_output" in tool_call and tool_call["use_previous_output"]:
                if isinstance(parameters, dict):
                    parameters["input"] = current_output
            
            result = await self.execute(tool_name, parameters)
            
            if not result.success:
                return result
            
            current_output = result.output
        
        return ToolResult(
            success=True,
            output=current_output,
            metadata={"chain_length": len(tool_chain)}
        )
    
    async def execute_with_fallback(
        self,
        primary_tool: str,
        fallback_tools: List[str],
        parameters: Dict[str, Any]
    ) -> ToolResult:
        result = await self.execute(primary_tool, parameters)
        
        if result.success:
            return result
        
        for fallback_tool in fallback_tools:
            result = await self.execute(fallback_tool, parameters)
            if result.success:
                result.metadata["used_fallback"] = fallback_tool
                return result
        
        return ToolResult(
            success=False,
            output=None,
            error="All tools failed including fallbacks"
        )
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history
    
    def clear_history(self) -> None:
        self.execution_history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_executions": len(self.execution_history),
            "tool_usage": self._count_tool_usage(),
            "success_rate": self._calculate_success_rate()
        }
    
    def _count_tool_usage(self) -> Dict[str, int]:
        usage = {}
        for entry in self.execution_history:
            tool_name = entry["tool_name"]
            usage[tool_name] = usage.get(tool_name, 0) + 1
        return usage
    
    def _calculate_success_rate(self) -> float:
        if not self.execution_history:
            return 0.0
        
        successful = sum(
            1 for entry in self.execution_history
            if entry["result"]["success"]
        )
        return successful / len(self.execution_history)
