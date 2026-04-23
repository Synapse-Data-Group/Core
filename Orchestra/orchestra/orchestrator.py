import asyncio
from typing import Any, Callable, Dict, List, Optional
from .tree_orchestrator import TreeOrchestrator, TaskType, ExecutionMode
from .chain_of_thought import ChainOfThought, ReasoningStep
from .parallel_swarm import ParallelSwarm, SwarmAgent, ConsensusStrategy
from .integration import IntegrationLayer


class Orchestra:
    def __init__(
        self,
        clm_config: Optional[Dict[str, Any]] = None,
        meo_config: Optional[Dict[str, Any]] = None,
        default_consensus: ConsensusStrategy = ConsensusStrategy.VOTING
    ):
        self.integration = IntegrationLayer(clm_config, meo_config)
        self.tree = TreeOrchestrator()
        self.chains: Dict[str, ChainOfThought] = {}
        self.swarms: Dict[str, ParallelSwarm] = {}
        self.default_consensus = default_consensus
        self.execution_history: List[Dict[str, Any]] = []
        
        self._setup_default_routing()
    
    def _setup_default_routing(self) -> None:
        self.tree.add_decision_node(
            node_id="route_simple",
            condition=lambda ctx: ctx.get("routing_result", {}).get("task_type") == "simple",
            action=self._route_to_chain,
            metadata={"description": "Route simple tasks to Chain-of-Thought"}
        )
        
        self.tree.add_decision_node(
            node_id="route_complex",
            condition=lambda ctx: ctx.get("routing_result", {}).get("task_type") == "complex",
            action=self._route_to_swarm,
            metadata={"description": "Route complex tasks to Parallel Swarm"}
        )
        
        self.tree.add_decision_node(
            node_id="route_moderate",
            condition=lambda ctx: ctx.get("routing_result", {}).get("task_type") == "moderate",
            action=self._route_based_on_history,
            metadata={"description": "Route moderate tasks based on history"}
        )
    
    def create_chain(self, chain_id: str) -> ChainOfThought:
        if chain_id in self.chains:
            return self.chains[chain_id]
        
        chain = ChainOfThought(
            chain_id=chain_id,
            clm_integration=self.integration.get_clm()
        )
        self.chains[chain_id] = chain
        return chain
    
    def create_swarm(
        self,
        swarm_id: str,
        consensus_strategy: Optional[ConsensusStrategy] = None
    ) -> ParallelSwarm:
        if swarm_id in self.swarms:
            return self.swarms[swarm_id]
        
        swarm = ParallelSwarm(
            swarm_id=swarm_id,
            clm_integration=self.integration.get_clm(),
            meo_integration=self.integration.get_meo(),
            consensus_strategy=consensus_strategy or self.default_consensus
        )
        self.swarms[swarm_id] = swarm
        return swarm
    
    def get_chain(self, chain_id: str) -> Optional[ChainOfThought]:
        return self.chains.get(chain_id)
    
    def get_swarm(self, swarm_id: str) -> Optional[ParallelSwarm]:
        return self.swarms.get(swarm_id)
    
    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        
        routing_guidance = await self.integration.guide_routing(task)
        context["routing_guidance"] = routing_guidance
        
        routing_result = await self.tree.route_task(task, context)
        
        final_output = routing_result.get("final_result")
        
        clm_report = self.integration.get_clm().get_load_report()
        meo_stats = self.integration.get_meo().get_memory_stats()
        
        await self.integration.store_task_history(
            task=task,
            routing_result=routing_result,
            final_output=final_output
        )
        
        execution_summary = {
            "task": task,
            "routing": routing_result,
            "output": final_output,
            "clm_report": clm_report,
            "meo_stats": meo_stats,
            "integration_report": self.integration.get_integration_report()
        }
        
        self.execution_history.append(execution_summary)
        
        return execution_summary
    
    async def _route_to_chain(self, context: Dict[str, Any]) -> Any:
        task = context.get("task", {})
        chain_id = task.get("chain_id", "default_chain")
        
        if chain_id not in self.chains:
            chain = self.create_chain(chain_id)
            
            if "steps" in task:
                for step_config in task["steps"]:
                    chain.add_step(**step_config)
        else:
            chain = self.chains[chain_id]
        
        result = await chain.execute(initial_context=context)
        return result
    
    async def _route_to_swarm(self, context: Dict[str, Any]) -> Any:
        task = context.get("task", {})
        swarm_id = task.get("swarm_id", "default_swarm")
        
        if swarm_id not in self.swarms:
            swarm = self.create_swarm(swarm_id)
            
            if "agents" in task:
                for agent_config in task["agents"]:
                    swarm.add_agent(**agent_config)
        else:
            swarm = self.swarms[swarm_id]
        
        result = await swarm.execute(
            task=task,
            context=context,
            max_agents=task.get("max_agents"),
            timeout=task.get("timeout")
        )
        return result
    
    async def _route_based_on_history(self, context: Dict[str, Any]) -> Any:
        routing_guidance = context.get("routing_guidance", {})
        recommendation = routing_guidance.get("recommendation", "default")
        
        if recommendation == "parallel" or recommendation == "parallel_swarm":
            return await self._route_to_swarm(context)
        else:
            return await self._route_to_chain(context)
    
    def add_routing_rule(
        self,
        node_id: str,
        condition: Callable[[Dict[str, Any]], bool],
        action: Callable,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        self.tree.add_decision_node(
            node_id=node_id,
            condition=condition,
            action=action,
            parent_id=parent_id,
            metadata=metadata
        )
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        return {
            "total_executions": len(self.execution_history),
            "active_chains": len(self.chains),
            "active_swarms": len(self.swarms),
            "tree_statistics": self.tree.get_node_statistics(),
            "chain_statistics": {
                chain_id: chain.get_cognitive_load_report()
                for chain_id, chain in self.chains.items()
            },
            "swarm_statistics": {
                swarm_id: swarm.get_swarm_statistics()
                for swarm_id, swarm in self.swarms.items()
            },
            "integration_report": self.integration.get_integration_report()
        }
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history
    
    def introspect_tree_paths(self) -> Dict[str, Any]:
        return {
            "nodes": self.tree.get_node_statistics(),
            "execution_history": self.tree.get_execution_history(limit=10)
        }
    
    def introspect_agent_outputs(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        swarm = self.get_swarm(swarm_id)
        if not swarm:
            return None
        
        return {
            "swarm_id": swarm_id,
            "agents": {
                agent_id: {
                    "status": agent.status.value,
                    "current_result": agent.current_result,
                    "performance_score": agent.performance_score,
                    "cognitive_load": agent.cognitive_load
                }
                for agent_id, agent in swarm.agents.items()
            },
            "statistics": swarm.get_swarm_statistics()
        }
    
    def reset(self) -> None:
        for chain in self.chains.values():
            chain.reset()
        
        for swarm in self.swarms.values():
            swarm.reset_agents()
        
        self.tree.clear_history()
        self.execution_history.clear()
