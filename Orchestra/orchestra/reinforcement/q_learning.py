import random
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class QState:
    task_type: str
    complexity: str
    agent_count: int
    
    def to_key(self) -> str:
        return f"{self.task_type}_{self.complexity}_{self.agent_count}"


@dataclass
class QAction:
    routing_decision: str
    consensus_strategy: Optional[str] = None
    
    def to_key(self) -> str:
        if self.consensus_strategy:
            return f"{self.routing_decision}_{self.consensus_strategy}"
        return self.routing_decision


class QLearningRouter:
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.2,
        epsilon_decay: float = 0.995,
        min_epsilon: float = 0.05
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        self.q_table: Dict[Tuple[str, str], float] = defaultdict(float)
        
        self.state_action_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        
        self.available_actions = [
            QAction("chain_of_thought"),
            QAction("parallel_swarm", "voting"),
            QAction("parallel_swarm", "best_performer"),
            QAction("parallel_swarm", "weighted_average"),
            QAction("tree_route"),
        ]
        
        self.statistics = {
            "total_updates": 0,
            "exploration_count": 0,
            "exploitation_count": 0,
            "current_epsilon": epsilon
        }
    
    def select_action(self, state: QState) -> QAction:
        if random.random() < self.epsilon:
            self.statistics["exploration_count"] += 1
            return random.choice(self.available_actions)
        
        self.statistics["exploitation_count"] += 1
        
        state_key = state.to_key()
        
        best_action = None
        best_q_value = float('-inf')
        
        for action in self.available_actions:
            action_key = action.to_key()
            q_value = self.q_table[(state_key, action_key)]
            
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = action
        
        if best_action is None:
            best_action = random.choice(self.available_actions)
        
        return best_action
    
    def update(
        self,
        state: QState,
        action: QAction,
        reward: float,
        next_state: Optional[QState] = None
    ) -> None:
        state_key = state.to_key()
        action_key = action.to_key()
        
        current_q = self.q_table[(state_key, action_key)]
        
        if next_state:
            next_state_key = next_state.to_key()
            max_next_q = max(
                self.q_table[(next_state_key, a.to_key())]
                for a in self.available_actions
            )
        else:
            max_next_q = 0.0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[(state_key, action_key)] = new_q
        
        self.state_action_counts[(state_key, action_key)] += 1
        
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        self.statistics["current_epsilon"] = self.epsilon
        self.statistics["total_updates"] += 1
    
    def compute_reward(
        self,
        success: bool,
        execution_time: float,
        cost: float,
        performance_score: float
    ) -> float:
        success_reward = 10.0 if success else -10.0
        
        time_penalty = -min(execution_time / 10.0, 5.0)
        
        cost_penalty = -min(cost / 1.0, 3.0)
        
        performance_reward = performance_score * 5.0
        
        total_reward = success_reward + time_penalty + cost_penalty + performance_reward
        
        return total_reward
    
    def get_best_action_for_state(self, state: QState) -> Tuple[QAction, float]:
        state_key = state.to_key()
        
        best_action = None
        best_q_value = float('-inf')
        
        for action in self.available_actions:
            action_key = action.to_key()
            q_value = self.q_table[(state_key, action_key)]
            
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = action
        
        if best_action is None:
            best_action = self.available_actions[0]
            best_q_value = 0.0
        
        return best_action, best_q_value
    
    def get_q_values_for_state(self, state: QState) -> Dict[str, float]:
        state_key = state.to_key()
        
        return {
            action.to_key(): self.q_table[(state_key, action.to_key())]
            for action in self.available_actions
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "q_table_size": len(self.q_table),
            "unique_states": len(set(k[0] for k in self.q_table.keys())),
            "exploration_rate": (
                self.statistics["exploration_count"] /
                (self.statistics["exploration_count"] + self.statistics["exploitation_count"])
                if (self.statistics["exploration_count"] + self.statistics["exploitation_count"]) > 0
                else 0.0
            )
        }
    
    def save_q_table(self) -> Dict[str, float]:
        return dict(self.q_table)
    
    def load_q_table(self, q_table_data: Dict[str, float]) -> None:
        self.q_table.clear()
        for key_str, value in q_table_data.items():
            self.q_table[eval(key_str)] = value
