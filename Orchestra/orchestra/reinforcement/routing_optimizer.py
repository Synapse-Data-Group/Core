import time
from typing import Any, Dict, List, Optional
from .q_learning import QLearningRouter, QState, QAction


class RoutingOptimizer:
    def __init__(
        self,
        q_learning_router: Optional[QLearningRouter] = None,
        optimization_window: int = 100
    ):
        self.router = q_learning_router or QLearningRouter()
        self.optimization_window = optimization_window
        
        self.execution_history: List[Dict[str, Any]] = []
        
        self.statistics = {
            "total_optimizations": 0,
            "avg_reward": 0.0,
            "best_reward": float('-inf'),
            "worst_reward": float('inf')
        }
    
    def get_optimal_routing(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        state = self._task_to_state(task, context)
        
        action = self.router.select_action(state)
        
        return {
            "routing_decision": action.routing_decision,
            "consensus_strategy": action.consensus_strategy,
            "state": state,
            "action": action,
            "q_values": self.router.get_q_values_for_state(state)
        }
    
    def record_execution_result(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any],
        routing_decision: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        state = routing_decision.get("state")
        action = routing_decision.get("action")
        
        if not state or not action:
            return
        
        success = result.get("success", False)
        execution_time = result.get("execution_time", 0.0)
        cost = result.get("cost", 0.0)
        performance_score = result.get("performance_score", 0.0)
        
        reward = self.router.compute_reward(
            success,
            execution_time,
            cost,
            performance_score
        )
        
        self.router.update(state, action, reward)
        
        self.execution_history.append({
            "state": state,
            "action": action,
            "reward": reward,
            "result": result,
            "timestamp": time.time()
        })
        
        self._update_statistics(reward)
        
        if len(self.execution_history) % self.optimization_window == 0:
            self._analyze_performance()
    
    def _task_to_state(self, task: Dict[str, Any], context: Dict[str, Any]) -> QState:
        task_type = task.get("type", "unknown")
        complexity = task.get("complexity", "moderate")
        agent_count = context.get("available_agents", 3)
        
        return QState(
            task_type=task_type,
            complexity=complexity,
            agent_count=agent_count
        )
    
    def _update_statistics(self, reward: float) -> None:
        self.statistics["total_optimizations"] += 1
        
        n = self.statistics["total_optimizations"]
        self.statistics["avg_reward"] = (
            (self.statistics["avg_reward"] * (n - 1) + reward) / n
        )
        
        if reward > self.statistics["best_reward"]:
            self.statistics["best_reward"] = reward
        
        if reward < self.statistics["worst_reward"]:
            self.statistics["worst_reward"] = reward
    
    def _analyze_performance(self) -> None:
        recent = self.execution_history[-self.optimization_window:]
        
        successful = [e for e in recent if e["result"].get("success", False)]
        
        if successful:
            avg_reward_successful = sum(e["reward"] for e in successful) / len(successful)
            
            print(f"Routing Optimizer: {len(successful)}/{len(recent)} successful, "
                  f"avg reward: {avg_reward_successful:.2f}")
    
    def get_routing_recommendations(self) -> Dict[str, Any]:
        state_performance = {}
        
        for execution in self.execution_history:
            state_key = execution["state"].to_key()
            
            if state_key not in state_performance:
                state_performance[state_key] = {
                    "rewards": [],
                    "best_action": None,
                    "best_reward": float('-inf')
                }
            
            state_performance[state_key]["rewards"].append(execution["reward"])
            
            if execution["reward"] > state_performance[state_key]["best_reward"]:
                state_performance[state_key]["best_reward"] = execution["reward"]
                state_performance[state_key]["best_action"] = execution["action"]
        
        recommendations = {}
        for state_key, perf in state_performance.items():
            if perf["best_action"]:
                recommendations[state_key] = {
                    "recommended_action": perf["best_action"].to_key(),
                    "avg_reward": sum(perf["rewards"]) / len(perf["rewards"]),
                    "best_reward": perf["best_reward"],
                    "sample_count": len(perf["rewards"])
                }
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "router_stats": self.router.get_statistics(),
            "execution_history_size": len(self.execution_history)
        }
    
    def export_learned_policy(self) -> Dict[str, Any]:
        return {
            "q_table": self.router.save_q_table(),
            "statistics": self.get_statistics(),
            "recommendations": self.get_routing_recommendations()
        }
