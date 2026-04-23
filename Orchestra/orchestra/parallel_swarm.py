import asyncio
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time


class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    OVERLOADED = "overloaded"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"


class ConsensusStrategy(Enum):
    VOTING = "voting"
    WEIGHTED_AVERAGE = "weighted_average"
    BEST_PERFORMER = "best_performer"
    MERGE_ALL = "merge_all"
    FIRST_VALID = "first_valid"


@dataclass
class SwarmAgent:
    agent_id: str
    executor: Callable[[Dict[str, Any]], Any]
    status: AgentStatus = AgentStatus.IDLE
    cognitive_load: float = 0.0
    performance_score: float = 1.0
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time: float = 0.0
    current_result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    load_threshold: float = 0.8
    
    def update_performance(self, success: bool, execution_time: float) -> None:
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.total_execution_time += execution_time
        
        success_rate = self.success_count / self.execution_count if self.execution_count > 0 else 0.0
        avg_time = self.total_execution_time / self.execution_count if self.execution_count > 0 else 1.0
        time_factor = max(0.1, 1.0 / avg_time) if avg_time > 0 else 1.0
        
        self.performance_score = (success_rate * 0.7) + (min(time_factor, 1.0) * 0.3)
    
    def is_overloaded(self) -> bool:
        return self.cognitive_load >= self.load_threshold
    
    def can_execute(self) -> bool:
        return self.status in [AgentStatus.IDLE, AgentStatus.ACTIVE] and not self.is_overloaded()


class ParallelSwarm:
    def __init__(
        self,
        swarm_id: str,
        clm_integration: Optional[Any] = None,
        meo_integration: Optional[Any] = None,
        consensus_strategy: ConsensusStrategy = ConsensusStrategy.VOTING
    ):
        self.swarm_id = swarm_id
        self.agents: Dict[str, SwarmAgent] = {}
        self.clm_integration = clm_integration
        self.meo_integration = meo_integration
        self.consensus_strategy = consensus_strategy
        self.execution_history: List[Dict[str, Any]] = []
        self.swarm_memory: Dict[str, Any] = {}
        self.coordination_log: List[Dict[str, Any]] = []

    def add_agent(
        self,
        agent_id: str,
        executor: Callable[[Dict[str, Any]], Any],
        load_threshold: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SwarmAgent:
        if agent_id in self.agents:
            raise ValueError(f"Agent with id '{agent_id}' already exists")
        
        agent = SwarmAgent(
            agent_id=agent_id,
            executor=executor,
            load_threshold=load_threshold,
            metadata=metadata or {}
        )
        
        self.agents[agent_id] = agent
        return agent

    def remove_agent(self, agent_id: str) -> None:
        if agent_id in self.agents:
            del self.agents[agent_id]

    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        max_agents: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        # Create base context that will be copied for each agent
        base_context = context.copy() if context else {}
        base_context["task"] = task
        base_context["swarm_id"] = self.swarm_id
        
        if self.meo_integration:
            past_experiences = await self._recall_past_experiences(task)
            base_context["past_experiences"] = past_experiences
        
        available_agents = self._select_agents(max_agents)
        
        if not available_agents:
            raise RuntimeError("No available agents to execute task")
        
        agent_tasks = []
        for agent in available_agents:
            agent.status = AgentStatus.ACTIVE
            # Give each agent its own isolated copy of the context
            agent_context = self._create_agent_context(base_context, agent)
            agent_tasks.append(self._execute_agent(agent, agent_context))
        
        try:
            if timeout:
                results = await asyncio.wait_for(
                    asyncio.gather(*agent_tasks, return_exceptions=True),
                    timeout=timeout
                )
            else:
                results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        except asyncio.TimeoutError:
            results = [None] * len(available_agents)
            for agent in available_agents:
                if agent.status == AgentStatus.ACTIVE:
                    agent.status = AgentStatus.FAILED
                    agent.error = "Execution timeout"
        
        await self._monitor_and_adapt(available_agents, base_context)
        
        merged_result = await self._merge_results(available_agents, base_context)
        
        if self.meo_integration:
            await self._update_memory(task, merged_result, available_agents)
        
        execution_summary = self._create_execution_summary(
            task, available_agents, merged_result, base_context
        )
        
        self.execution_history.append(execution_summary)
        
        return execution_summary

    def _create_agent_context(
        self,
        base_context: Dict[str, Any],
        agent: SwarmAgent
    ) -> Dict[str, Any]:
        """Create an isolated context copy for each agent to prevent race conditions."""
        import copy
        
        # Deep copy the context to ensure complete isolation
        agent_context = copy.deepcopy(base_context)
        
        # Add agent-specific metadata
        agent_context["agent_id"] = agent.agent_id
        agent_context["agent_metadata"] = agent.metadata.copy()
        agent_context["agent_performance_score"] = agent.performance_score
        
        return agent_context
    
    def _select_agents(self, max_agents: Optional[int] = None) -> List[SwarmAgent]:
        available = [
            agent for agent in self.agents.values()
            if agent.can_execute()
        ]
        
        available.sort(key=lambda a: a.performance_score, reverse=True)
        
        if max_agents:
            available = available[:max_agents]
        
        return available

    async def _execute_agent(
        self,
        agent: SwarmAgent,
        context: Dict[str, Any]
    ) -> None:
        start_time = time.time()
        
        try:
            if self.clm_integration:
                agent.cognitive_load = await self._measure_agent_load(agent, context)
                
                if agent.is_overloaded():
                    agent.status = AgentStatus.OVERLOADED
                    agent.error = "Cognitive load threshold exceeded"
                    return
            
            result = agent.executor(context)
            if asyncio.iscoroutine(result):
                result = await result
            
            agent.current_result = result
            agent.status = AgentStatus.COMPLETED
            agent.error = None
            
            execution_time = time.time() - start_time
            agent.update_performance(success=True, execution_time=execution_time)
            
        except Exception as e:
            agent.status = AgentStatus.FAILED
            agent.error = str(e)
            agent.current_result = None
            
            execution_time = time.time() - start_time
            agent.update_performance(success=False, execution_time=execution_time)

    async def _monitor_and_adapt(
        self,
        agents: List[SwarmAgent],
        context: Dict[str, Any]
    ) -> None:
        overloaded_agents = [a for a in agents if a.status == AgentStatus.OVERLOADED]
        failed_agents = [a for a in agents if a.status == AgentStatus.FAILED]
        
        coordination_event = {
            "timestamp": time.time(),
            "total_agents": len(agents),
            "overloaded_count": len(overloaded_agents),
            "failed_count": len(failed_agents),
            "actions_taken": []
        }
        
        for agent in overloaded_agents:
            agent.status = AgentStatus.PAUSED
            coordination_event["actions_taken"].append({
                "agent_id": agent.agent_id,
                "action": "paused",
                "reason": "cognitive_overload"
            })
        
        if len(failed_agents) > len(agents) * 0.5:
            backup_agents = [
                a for a in self.agents.values()
                if a not in agents and a.can_execute()
            ]
            
            for backup_agent in backup_agents[:len(failed_agents)]:
                backup_agent.status = AgentStatus.ACTIVE
                await self._execute_agent(backup_agent, context)
                agents.append(backup_agent)
                
                coordination_event["actions_taken"].append({
                    "agent_id": backup_agent.agent_id,
                    "action": "activated",
                    "reason": "replace_failed_agent"
                })
        
        self.coordination_log.append(coordination_event)

    async def _merge_results(
        self,
        agents: List[SwarmAgent],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        successful_agents = [
            a for a in agents
            if a.status == AgentStatus.COMPLETED and a.current_result is not None
        ]
        
        if not successful_agents:
            return {
                "success": False,
                "merged_output": None,
                "consensus_strategy": self.consensus_strategy.value,
                "participating_agents": 0,
                "error": "No successful agent results to merge"
            }
        
        if self.consensus_strategy == ConsensusStrategy.VOTING:
            merged_output = self._voting_consensus(successful_agents)
        elif self.consensus_strategy == ConsensusStrategy.WEIGHTED_AVERAGE:
            merged_output = self._weighted_average_consensus(successful_agents)
        elif self.consensus_strategy == ConsensusStrategy.BEST_PERFORMER:
            merged_output = self._best_performer_consensus(successful_agents)
        elif self.consensus_strategy == ConsensusStrategy.MERGE_ALL:
            merged_output = self._merge_all_consensus(successful_agents)
        else:
            merged_output = self._first_valid_consensus(successful_agents)
        
        return {
            "success": True,
            "merged_output": merged_output,
            "consensus_strategy": self.consensus_strategy.value,
            "participating_agents": len(successful_agents),
            "agent_results": {
                agent.agent_id: agent.current_result
                for agent in successful_agents
            }
        }

    def _voting_consensus(self, agents: List[SwarmAgent]) -> Any:
        vote_counts: Dict[str, int] = {}
        result_map: Dict[str, Any] = {}
        
        for agent in agents:
            result_key = str(agent.current_result)
            vote_counts[result_key] = vote_counts.get(result_key, 0) + 1
            result_map[result_key] = agent.current_result
        
        winning_key = max(vote_counts.items(), key=lambda x: x[1])[0]
        return result_map[winning_key]

    def _weighted_average_consensus(self, agents: List[SwarmAgent]) -> Any:
        total_weight = sum(agent.performance_score for agent in agents)
        
        if total_weight == 0:
            return agents[0].current_result
        
        try:
            weighted_sum = sum(
                agent.current_result * agent.performance_score
                for agent in agents
                if isinstance(agent.current_result, (int, float))
            )
            return weighted_sum / total_weight
        except (TypeError, ValueError):
            return self._best_performer_consensus(agents)

    def _best_performer_consensus(self, agents: List[SwarmAgent]) -> Any:
        best_agent = max(agents, key=lambda a: a.performance_score)
        return best_agent.current_result

    def _merge_all_consensus(self, agents: List[SwarmAgent]) -> Any:
        results = [agent.current_result for agent in agents]
        
        if all(isinstance(r, dict) for r in results):
            merged = {}
            for result in results:
                merged.update(result)
            return merged
        elif all(isinstance(r, list) for r in results):
            merged = []
            for result in results:
                merged.extend(result)
            return merged
        else:
            return results

    def _first_valid_consensus(self, agents: List[SwarmAgent]) -> Any:
        return agents[0].current_result if agents else None

    async def _measure_agent_load(
        self,
        agent: SwarmAgent,
        context: Dict[str, Any]
    ) -> float:
        if not self.clm_integration:
            return 0.0
        
        try:
            load = await self.clm_integration.measure_agent_load(
                agent_id=agent.agent_id,
                task=context.get("task", {}),
                execution_count=agent.execution_count
            )
            return load
        except Exception:
            return 0.0

    async def _recall_past_experiences(
        self,
        task: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if not self.meo_integration:
            return []
        
        try:
            experiences = await self.meo_integration.recall_similar_tasks(
                task=task,
                swarm_id=self.swarm_id,
                limit=5
            )
            return experiences
        except Exception:
            return []

    async def _update_memory(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        agents: List[SwarmAgent]
    ) -> None:
        if not self.meo_integration:
            return
        
        try:
            memory_entry = {
                "swarm_id": self.swarm_id,
                "task": task,
                "result": result,
                "agents": [
                    {
                        "agent_id": agent.agent_id,
                        "status": agent.status.value,
                        "performance_score": agent.performance_score,
                        "cognitive_load": agent.cognitive_load
                    }
                    for agent in agents
                ],
                "timestamp": time.time()
            }
            
            await self.meo_integration.store_execution(memory_entry)
        except Exception:
            pass

    def _create_execution_summary(
        self,
        task: Dict[str, Any],
        agents: List[SwarmAgent],
        merged_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "swarm_id": self.swarm_id,
            "task": task,
            "merged_result": merged_result,
            "agent_summary": {
                agent.agent_id: {
                    "status": agent.status.value,
                    "cognitive_load": agent.cognitive_load,
                    "performance_score": agent.performance_score,
                    "execution_count": agent.execution_count,
                    "success_rate": agent.success_count / agent.execution_count if agent.execution_count > 0 else 0.0,
                    "error": agent.error
                }
                for agent in agents
            },
            "coordination_events": len(self.coordination_log),
            "timestamp": time.time()
        }

    def get_swarm_statistics(self) -> Dict[str, Any]:
        total_agents = len(self.agents)
        active_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.ACTIVE)
        overloaded_agents = sum(1 for a in self.agents.values() if a.is_overloaded())
        
        avg_performance = sum(a.performance_score for a in self.agents.values()) / total_agents if total_agents > 0 else 0.0
        avg_load = sum(a.cognitive_load for a in self.agents.values()) / total_agents if total_agents > 0 else 0.0
        
        return {
            "swarm_id": self.swarm_id,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "overloaded_agents": overloaded_agents,
            "average_performance": avg_performance,
            "average_cognitive_load": avg_load,
            "total_executions": len(self.execution_history),
            "coordination_events": len(self.coordination_log)
        }

    def reset_agents(self) -> None:
        for agent in self.agents.values():
            agent.status = AgentStatus.IDLE
            agent.current_result = None
            agent.error = None
