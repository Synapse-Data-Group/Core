import asyncio
from typing import Any, Dict, List, Optional
import importlib.util


class CLMIntegration:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.clm_module = None
        self.monitor = None
        self._initialize_clm()
    
    def _initialize_clm(self) -> None:
        try:
            if importlib.util.find_spec("cognitive_load_monitor") is not None:
                import cognitive_load_monitor as clm
                self.clm_module = clm
                self.monitor = clm.CognitiveLoadMonitor(**self.config)
        except ImportError:
            pass
    
    async def measure_step_load(
        self,
        step_id: str,
        description: str,
        dependencies: int
    ) -> float:
        if not self.monitor:
            return self._estimate_load(description, dependencies)
        
        try:
            load = await self._async_wrapper(
                self.monitor.measure_load,
                step_id=step_id,
                description=description,
                dependencies=dependencies
            )
            return load
        except Exception:
            return self._estimate_load(description, dependencies)
    
    async def measure_agent_load(
        self,
        agent_id: str,
        task: Dict[str, Any],
        execution_count: int
    ) -> float:
        if not self.monitor:
            return self._estimate_agent_load(task, execution_count)
        
        try:
            load = await self._async_wrapper(
                self.monitor.measure_agent_load,
                agent_id=agent_id,
                task=task,
                execution_count=execution_count
            )
            return load
        except Exception:
            return self._estimate_agent_load(task, execution_count)
    
    def _estimate_load(self, description: str, dependencies: int) -> float:
        base_load = len(description.split()) / 100.0
        dependency_load = dependencies * 0.1
        return min(1.0, base_load + dependency_load)
    
    def _estimate_agent_load(self, task: Dict[str, Any], execution_count: int) -> float:
        task_complexity = len(str(task)) / 500.0
        execution_factor = min(execution_count / 10.0, 0.3)
        return min(1.0, task_complexity + execution_factor)
    
    async def _async_wrapper(self, func: Any, **kwargs) -> Any:
        if asyncio.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return await asyncio.get_event_loop().run_in_executor(None, lambda: func(**kwargs))
    
    def get_load_report(self) -> Dict[str, Any]:
        if not self.monitor:
            return {"status": "not_initialized", "total_measurements": 0}
        
        try:
            return self.monitor.get_report()
        except Exception:
            return {"status": "error", "total_measurements": 0}


class MEOIntegration:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.meo_module = None
        self.memory_store = None
        self._initialize_meo()
    
    def _initialize_meo(self) -> None:
        try:
            if importlib.util.find_spec("synapse_meo") is not None:
                import synapse_meo as meo
                self.meo_module = meo
                self.memory_store = meo.MemoryStore(**self.config)
        except ImportError:
            pass
    
    async def store_execution(self, memory_entry: Dict[str, Any]) -> bool:
        if not self.memory_store:
            return False
        
        try:
            await self._async_wrapper(
                self.memory_store.store,
                entry=memory_entry
            )
            return True
        except Exception:
            return False
    
    async def recall_similar_tasks(
        self,
        task: Dict[str, Any],
        swarm_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        if not self.memory_store:
            return []
        
        try:
            results = await self._async_wrapper(
                self.memory_store.recall,
                query=task,
                swarm_id=swarm_id,
                limit=limit
            )
            return results if results else []
        except Exception:
            return []
    
    async def store_orchestration_outcome(
        self,
        task: Dict[str, Any],
        routing_result: Dict[str, Any],
        final_output: Any
    ) -> bool:
        if not self.memory_store:
            return False
        
        try:
            memory_entry = {
                "type": "orchestration",
                "task": task,
                "routing": routing_result,
                "output": final_output,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self._async_wrapper(
                self.memory_store.store,
                entry=memory_entry
            )
            return True
        except Exception:
            return False
    
    async def get_agent_performance_history(
        self,
        agent_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        if not self.memory_store:
            return []
        
        try:
            results = await self._async_wrapper(
                self.memory_store.query,
                filters={"agent_id": agent_id},
                limit=limit
            )
            return results if results else []
        except Exception:
            return []
    
    async def _async_wrapper(self, func: Any, **kwargs) -> Any:
        if asyncio.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return await asyncio.get_event_loop().run_in_executor(None, lambda: func(**kwargs))
    
    def get_memory_stats(self) -> Dict[str, Any]:
        if not self.memory_store:
            return {"status": "not_initialized", "total_entries": 0}
        
        try:
            return self.memory_store.get_stats()
        except Exception:
            return {"status": "error", "total_entries": 0}


class IntegrationLayer:
    def __init__(
        self,
        clm_config: Optional[Dict[str, Any]] = None,
        meo_config: Optional[Dict[str, Any]] = None
    ):
        self.clm = CLMIntegration(clm_config)
        self.meo = MEOIntegration(meo_config)
        self.integration_log: List[Dict[str, Any]] = []
    
    def get_clm(self) -> CLMIntegration:
        return self.clm
    
    def get_meo(self) -> MEOIntegration:
        return self.meo
    
    async def prevent_overload(
        self,
        agents: List[Any],
        load_threshold: float = 0.8
    ) -> List[str]:
        overloaded_agents = []
        
        for agent in agents:
            if hasattr(agent, 'cognitive_load') and agent.cognitive_load >= load_threshold:
                overloaded_agents.append(agent.agent_id)
                
                self.integration_log.append({
                    "event": "overload_detected",
                    "agent_id": agent.agent_id,
                    "cognitive_load": agent.cognitive_load,
                    "threshold": load_threshold,
                    "timestamp": asyncio.get_event_loop().time()
                })
        
        return overloaded_agents
    
    async def guide_routing(
        self,
        task: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        past_executions = await self.meo.recall_similar_tasks(
            task=task,
            swarm_id="routing_history",
            limit=5
        )
        
        if not past_executions:
            return {
                "recommendation": "default",
                "confidence": 0.5,
                "reasoning": "No historical data available"
            }
        
        successful_routes = [
            exec_data for exec_data in past_executions
            if exec_data.get("success", False)
        ]
        
        if successful_routes:
            most_common_route = self._find_most_common_route(successful_routes)
            return {
                "recommendation": most_common_route,
                "confidence": len(successful_routes) / len(past_executions),
                "reasoning": f"Based on {len(successful_routes)} successful past executions"
            }
        
        return {
            "recommendation": "parallel_swarm",
            "confidence": 0.6,
            "reasoning": "No successful routes found, defaulting to parallel exploration"
        }
    
    def _find_most_common_route(self, executions: List[Dict[str, Any]]) -> str:
        route_counts: Dict[str, int] = {}
        
        for execution in executions:
            route = execution.get("routing", {}).get("execution_mode", "unknown")
            route_counts[route] = route_counts.get(route, 0) + 1
        
        if route_counts:
            return max(route_counts.items(), key=lambda x: x[1])[0]
        
        return "default"
    
    async def store_task_history(
        self,
        task: Dict[str, Any],
        routing_result: Dict[str, Any],
        final_output: Any
    ) -> bool:
        success = await self.meo.store_orchestration_outcome(
            task=task,
            routing_result=routing_result,
            final_output=final_output
        )
        
        if success:
            self.integration_log.append({
                "event": "task_history_stored",
                "task_id": task.get("id", "unknown"),
                "timestamp": asyncio.get_event_loop().time()
            })
        
        return success
    
    def get_integration_report(self) -> Dict[str, Any]:
        return {
            "clm_status": self.clm.get_load_report(),
            "meo_status": self.meo.get_memory_stats(),
            "integration_events": len(self.integration_log),
            "recent_events": self.integration_log[-10:] if self.integration_log else []
        }
