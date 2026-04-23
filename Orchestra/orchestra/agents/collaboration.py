import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class CollaborationPattern(Enum):
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    BROADCAST = "broadcast"
    PIPELINE = "pipeline"
    CONSENSUS = "consensus"


@dataclass
class AgentMessage:
    sender_id: str
    recipient_id: Optional[str]
    message_type: str
    content: Any
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageBus:
    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.message_handlers: Dict[str, Callable] = {}
    
    def subscribe(self, agent_id: str, message_type: str) -> None:
        self.subscriptions[message_type].add(agent_id)
    
    def unsubscribe(self, agent_id: str, message_type: str) -> None:
        if message_type in self.subscriptions:
            self.subscriptions[message_type].discard(agent_id)
    
    def register_handler(self, agent_id: str, handler: Callable) -> None:
        self.message_handlers[agent_id] = handler
    
    async def send(self, message: AgentMessage) -> None:
        self.messages.append(message)
        
        if message.recipient_id:
            if message.recipient_id in self.message_handlers:
                handler = self.message_handlers[message.recipient_id]
                result = handler(message)
                if asyncio.iscoroutine(result):
                    await result
        else:
            subscribers = self.subscriptions.get(message.message_type, set())
            for agent_id in subscribers:
                if agent_id in self.message_handlers:
                    handler = self.message_handlers[agent_id]
                    result = handler(message)
                    if asyncio.iscoroutine(result):
                        await result
    
    def get_messages_for(
        self,
        agent_id: str,
        message_type: Optional[str] = None,
        since: Optional[float] = None
    ) -> List[AgentMessage]:
        messages = [
            msg for msg in self.messages
            if msg.recipient_id == agent_id or msg.recipient_id is None
        ]
        
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]
        
        if since:
            messages = [msg for msg in messages if msg.timestamp >= since]
        
        return messages
    
    def clear(self) -> None:
        self.messages.clear()


class AgentTeam:
    def __init__(
        self,
        team_id: str,
        pattern: CollaborationPattern = CollaborationPattern.PEER_TO_PEER
    ):
        self.team_id = team_id
        self.pattern = pattern
        self.agents: Dict[str, Any] = {}
        self.message_bus = MessageBus()
        self.leader_id: Optional[str] = None
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_agent(
        self,
        agent_id: str,
        agent: Any,
        role: Optional[str] = None,
        is_leader: bool = False
    ) -> None:
        self.agents[agent_id] = {
            "agent": agent,
            "role": role,
            "is_leader": is_leader
        }
        
        if is_leader:
            self.leader_id = agent_id
    
    def remove_agent(self, agent_id: str) -> None:
        if agent_id in self.agents:
            del self.agents[agent_id]
            if self.leader_id == agent_id:
                self.leader_id = None
    
    async def execute_collaborative_task(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        
        if self.pattern == CollaborationPattern.HIERARCHICAL:
            return await self._execute_hierarchical(task, context)
        elif self.pattern == CollaborationPattern.PEER_TO_PEER:
            return await self._execute_peer_to_peer(task, context)
        elif self.pattern == CollaborationPattern.BROADCAST:
            return await self._execute_broadcast(task, context)
        elif self.pattern == CollaborationPattern.PIPELINE:
            return await self._execute_pipeline(task, context)
        elif self.pattern == CollaborationPattern.CONSENSUS:
            return await self._execute_consensus(task, context)
        else:
            return {"error": "Unknown collaboration pattern"}
    
    async def _execute_hierarchical(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.leader_id or self.leader_id not in self.agents:
            return {"error": "No leader assigned for hierarchical pattern"}
        
        leader_agent = self.agents[self.leader_id]["agent"]
        
        subtasks = task.get("subtasks", [])
        if not subtasks:
            subtasks = [{"id": f"subtask_{i}", "data": task} for i in range(len(self.agents) - 1)]
        
        results = []
        
        for i, (agent_id, agent_data) in enumerate(self.agents.items()):
            if agent_id == self.leader_id:
                continue
            
            if i - 1 < len(subtasks):
                agent = agent_data["agent"]
                
                subtask = subtasks[i - 1]
                
                if hasattr(agent, 'execute'):
                    result = await agent.execute(subtask, context)
                else:
                    result = agent(subtask)
                    if asyncio.iscoroutine(result):
                        result = await result
                
                results.append({
                    "agent_id": agent_id,
                    "result": result
                })
                
                await self.message_bus.send(AgentMessage(
                    sender_id=agent_id,
                    recipient_id=self.leader_id,
                    message_type="subtask_complete",
                    content=result
                ))
        
        if hasattr(leader_agent, 'execute'):
            final_result = await leader_agent.execute({
                "task": task,
                "subtask_results": results
            }, context)
        else:
            final_result = leader_agent({
                "task": task,
                "subtask_results": results
            })
            if asyncio.iscoroutine(final_result):
                final_result = await final_result
        
        return {
            "pattern": "hierarchical",
            "leader": self.leader_id,
            "subtask_results": results,
            "final_result": final_result,
            "team_id": self.team_id
        }
    
    async def _execute_peer_to_peer(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        results = []
        
        for agent_id, agent_data in self.agents.items():
            agent = agent_data["agent"]
            
            if hasattr(agent, 'execute'):
                result = await agent.execute(task, context)
            else:
                result = agent(task)
                if asyncio.iscoroutine(result):
                    result = await result
            
            results.append({
                "agent_id": agent_id,
                "result": result
            })
            
            await self.message_bus.send(AgentMessage(
                sender_id=agent_id,
                recipient_id=None,
                message_type="task_complete",
                content=result
            ))
        
        return {
            "pattern": "peer_to_peer",
            "results": results,
            "team_id": self.team_id
        }
    
    async def _execute_broadcast(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        await self.message_bus.send(AgentMessage(
            sender_id="system",
            recipient_id=None,
            message_type="broadcast_task",
            content=task
        ))
        
        tasks = []
        for agent_id, agent_data in self.agents.items():
            agent = agent_data["agent"]
            
            if hasattr(agent, 'execute'):
                tasks.append(agent.execute(task, context))
            else:
                result = agent(task)
                if asyncio.iscoroutine(result):
                    tasks.append(result)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "pattern": "broadcast",
            "results": [
                {"agent_id": agent_id, "result": result}
                for agent_id, result in zip(self.agents.keys(), results)
                if not isinstance(result, Exception)
            ],
            "team_id": self.team_id
        }
    
    async def _execute_pipeline(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        current_data = task
        results = []
        
        for agent_id, agent_data in self.agents.items():
            agent = agent_data["agent"]
            
            if hasattr(agent, 'execute'):
                result = await agent.execute(current_data, context)
            else:
                result = agent(current_data)
                if asyncio.iscoroutine(result):
                    result = await result
            
            results.append({
                "agent_id": agent_id,
                "input": current_data,
                "output": result
            })
            
            current_data = result if isinstance(result, dict) else {"data": result}
            
            await self.message_bus.send(AgentMessage(
                sender_id=agent_id,
                recipient_id=None,
                message_type="pipeline_stage_complete",
                content=result
            ))
        
        return {
            "pattern": "pipeline",
            "stages": results,
            "final_output": current_data,
            "team_id": self.team_id
        }
    
    async def _execute_consensus(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        proposals = []
        
        for agent_id, agent_data in self.agents.items():
            agent = agent_data["agent"]
            
            if hasattr(agent, 'execute'):
                result = await agent.execute(task, context)
            else:
                result = agent(task)
                if asyncio.iscoroutine(result):
                    result = await result
            
            proposals.append({
                "agent_id": agent_id,
                "proposal": result
            })
        
        votes = defaultdict(int)
        for proposal in proposals:
            proposal_key = str(proposal["proposal"])
            votes[proposal_key] += 1
        
        consensus = max(votes.items(), key=lambda x: x[1])
        
        return {
            "pattern": "consensus",
            "proposals": proposals,
            "consensus": consensus[0],
            "votes": dict(votes),
            "team_id": self.team_id
        }
    
    def get_team_statistics(self) -> Dict[str, Any]:
        return {
            "team_id": self.team_id,
            "pattern": self.pattern.value,
            "total_agents": len(self.agents),
            "leader": self.leader_id,
            "agents": {
                agent_id: {
                    "role": data["role"],
                    "is_leader": data["is_leader"]
                }
                for agent_id, data in self.agents.items()
            },
            "total_messages": len(self.message_bus.messages),
            "executions": len(self.execution_history)
        }
