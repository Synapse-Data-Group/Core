import asyncio
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class AgentState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Goal:
    goal_id: str
    description: str
    success_criteria: Dict[str, Any]
    priority: int = 1
    deadline: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_achieved(self, current_state: Dict[str, Any]) -> bool:
        for criterion, expected_value in self.success_criteria.items():
            if criterion not in current_state:
                return False
            if current_state[criterion] != expected_value:
                return False
        return True


@dataclass
class Action:
    action_id: str
    action_type: str
    executor: Callable
    parameters: Dict[str, Any]
    preconditions: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: Optional[Dict[str, Any]] = None
    executed: bool = False
    result: Optional[Any] = None
    execution_time: float = 0.0
    
    def can_execute(self, current_state: Dict[str, Any]) -> bool:
        for condition, expected_value in self.preconditions.items():
            if condition not in current_state:
                return False
            if current_state[condition] != expected_value:
                return False
        return True


@dataclass
class Plan:
    plan_id: str
    goal: Goal
    actions: List[Action]
    created_at: float = field(default_factory=time.time)
    estimated_duration: float = 0.0
    confidence: float = 1.0
    
    def get_next_action(self, current_state: Dict[str, Any]) -> Optional[Action]:
        for action in self.actions:
            if not action.executed and action.can_execute(current_state):
                return action
        return None
    
    def is_complete(self) -> bool:
        return all(action.executed for action in self.actions)
    
    def get_progress(self) -> float:
        if not self.actions:
            return 0.0
        executed = sum(1 for action in self.actions if action.executed)
        return executed / len(self.actions)


class AutonomousAgent:
    def __init__(
        self,
        agent_id: str,
        planner: Optional[Callable] = None,
        executor: Optional[Callable] = None,
        reflector: Optional[Callable] = None,
        max_iterations: int = 10,
        reflection_interval: int = 3
    ):
        self.agent_id = agent_id
        self.planner = planner or self._default_planner
        self.executor = executor
        self.reflector = reflector or self._default_reflector
        self.max_iterations = max_iterations
        self.reflection_interval = reflection_interval
        
        self.state = AgentState.IDLE
        self.current_goal: Optional[Goal] = None
        self.current_plan: Optional[Plan] = None
        self.world_state: Dict[str, Any] = {}
        self.memory: List[Dict[str, Any]] = []
        
        self.iteration_count = 0
        self.total_actions_executed = 0
        self.successful_goals = 0
        self.failed_goals = 0
    
    async def pursue_goal(
        self,
        goal: Goal,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.current_goal = goal
        self.world_state = initial_state or {}
        self.iteration_count = 0
        
        self.state = AgentState.PLANNING
        
        plan = await self._create_plan(goal)
        if not plan:
            self.state = AgentState.FAILED
            self.failed_goals += 1
            return {
                "success": False,
                "error": "Failed to create plan",
                "agent_id": self.agent_id
            }
        
        self.current_plan = plan
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            if goal.is_achieved(self.world_state):
                self.state = AgentState.COMPLETED
                self.successful_goals += 1
                return {
                    "success": True,
                    "goal_achieved": True,
                    "iterations": self.iteration_count,
                    "actions_executed": self.total_actions_executed,
                    "final_state": self.world_state,
                    "agent_id": self.agent_id
                }
            
            self.state = AgentState.EXECUTING
            
            next_action = plan.get_next_action(self.world_state)
            if not next_action:
                if plan.is_complete():
                    if goal.is_achieved(self.world_state):
                        self.state = AgentState.COMPLETED
                        self.successful_goals += 1
                        return {
                            "success": True,
                            "goal_achieved": True,
                            "iterations": self.iteration_count,
                            "actions_executed": self.total_actions_executed,
                            "final_state": self.world_state,
                            "agent_id": self.agent_id
                        }
                    else:
                        self.state = AgentState.PLANNING
                        plan = await self._create_plan(goal)
                        if not plan:
                            break
                        self.current_plan = plan
                        continue
                else:
                    break
            
            action_result = await self._execute_action(next_action)
            
            if self.iteration_count % self.reflection_interval == 0:
                self.state = AgentState.REFLECTING
                await self._reflect()
        
        self.state = AgentState.FAILED
        self.failed_goals += 1
        return {
            "success": False,
            "goal_achieved": False,
            "reason": "Max iterations reached",
            "iterations": self.iteration_count,
            "actions_executed": self.total_actions_executed,
            "final_state": self.world_state,
            "agent_id": self.agent_id
        }
    
    async def _create_plan(self, goal: Goal) -> Optional[Plan]:
        try:
            plan_data = self.planner({
                "goal": goal,
                "world_state": self.world_state,
                "memory": self.memory[-5:] if self.memory else []
            })
            
            if asyncio.iscoroutine(plan_data):
                plan_data = await plan_data
            
            if isinstance(plan_data, Plan):
                return plan_data
            
            return None
        
        except Exception as e:
            return None
    
    async def _execute_action(self, action: Action) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            if self.executor:
                result = self.executor({
                    "action": action,
                    "world_state": self.world_state,
                    "goal": self.current_goal
                })
                
                if asyncio.iscoroutine(result):
                    result = await result
            else:
                result = action.executor(action.parameters)
                if asyncio.iscoroutine(result):
                    result = await result
            
            action.executed = True
            action.result = result
            action.execution_time = time.time() - start_time
            
            self.total_actions_executed += 1
            
            if isinstance(result, dict):
                self.world_state.update(result)
            
            self.memory.append({
                "type": "action",
                "action_id": action.action_id,
                "result": result,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "result": result,
                "execution_time": action.execution_time
            }
        
        except Exception as e:
            action.executed = True
            action.result = None
            action.execution_time = time.time() - start_time
            
            self.memory.append({
                "type": "action_failed",
                "action_id": action.action_id,
                "error": str(e),
                "timestamp": time.time()
            })
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": action.execution_time
            }
    
    async def _reflect(self) -> None:
        reflection = self.reflector({
            "goal": self.current_goal,
            "plan": self.current_plan,
            "world_state": self.world_state,
            "memory": self.memory[-10:] if self.memory else [],
            "iteration": self.iteration_count
        })
        
        if asyncio.iscoroutine(reflection):
            reflection = await reflection
        
        self.memory.append({
            "type": "reflection",
            "content": reflection,
            "timestamp": time.time()
        })
    
    def _default_planner(self, context: Dict[str, Any]) -> Plan:
        goal = context["goal"]
        
        actions = [
            Action(
                action_id=f"action_{i}",
                action_type="default",
                executor=lambda params: {"status": "executed"},
                parameters={}
            )
            for i in range(3)
        ]
        
        return Plan(
            plan_id=f"plan_{goal.goal_id}",
            goal=goal,
            actions=actions,
            confidence=0.5
        )
    
    def _default_reflector(self, context: Dict[str, Any]) -> str:
        plan = context.get("plan")
        if plan:
            progress = plan.get_progress()
            return f"Progress: {progress:.1%}, continuing execution"
        return "Reflecting on current state"
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "total_actions_executed": self.total_actions_executed,
            "successful_goals": self.successful_goals,
            "failed_goals": self.failed_goals,
            "current_goal": self.current_goal.description if self.current_goal else None,
            "current_plan_progress": self.current_plan.get_progress() if self.current_plan else 0.0,
            "memory_size": len(self.memory)
        }
