import uuid
import time
import random
from typing import List, Dict, Any, Optional
from learning_engine import ExperienceMemory, QLearningEngine, GeneticEvolution, ArgumentGenerator


class SentientAgent:
    def __init__(self, agent_id: str, name: str, personality: Optional[Dict[str, float]] = None,
                 memory_path: Optional[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality or self._initialize_random_personality()
        self.is_active = True
        self.created_at = time.time()
        
        self.memory = ExperienceMemory(capacity=10000)
        if memory_path:
            try:
                self.memory.load(memory_path)
            except:
                pass
        
        self.q_learning = QLearningEngine(
            learning_rate=0.1,
            discount_factor=0.95,
            exploration_rate=0.3,
            exploration_decay=0.995
        )
        
        self.genetic_evolution = GeneticEvolution(
            mutation_rate=0.1,
            mutation_strength=0.2
        )
        
        self.argument_generator = ArgumentGenerator(self.memory)
        
        self.tools: Dict[str, Any] = {}
        self.message_history: List[Any] = []
        self.proposals_made: List[str] = []
        self.challenges_made: List[str] = []
        self.rebuttals_made: List[str] = []
        self.score = 0.0
        self.lifetime_score = 0.0
        self.debates_participated = 0
        self.wins = 0
        self.losses = 0
        
        self.current_state = None
        self.last_action = None
        self.performance_history: List[float] = []
    
    def _initialize_random_personality(self) -> Dict[str, float]:
        return {
            "creativity": random.uniform(0.3, 0.9),
            "boldness": random.uniform(0.2, 0.8),
            "aggressiveness": random.uniform(0.2, 0.8),
            "defensiveness": random.uniform(0.3, 0.7),
            "supportiveness": random.uniform(0.2, 0.7),
            "analytical_depth": random.uniform(0.3, 0.9),
            "evidence_reliance": random.uniform(0.3, 0.8),
            "confidence": random.uniform(0.4, 0.9),
            "optimism": random.uniform(0.3, 0.8),
            "verbosity": random.uniform(0.3, 0.7),
            "formality": random.uniform(0.3, 0.8)
        }
    
    def add_tool(self, tool: Any):
        self.tools[tool.tool_id] = tool
    
    def remove_tool(self, tool_id: str):
        if tool_id in self.tools:
            self.tools[tool_id].deactivate()
            del self.tools[tool_id]
    
    def use_tool(self, tool_id: str, *args, **kwargs) -> Any:
        if tool_id in self.tools and self.tools[tool_id].is_active:
            return self.tools[tool_id].execute(*args, **kwargs)
        return None
    
    def propose_solution(self, problem: str, context: Dict[str, Any]) -> str:
        state = self.q_learning.get_state_hash(context)
        self.current_state = state
        
        available_actions = ["propose_innovative", "propose_conservative", "propose_analytical", "propose_balanced"]
        
        action = self.q_learning.choose_action(state, available_actions)
        self.last_action = action
        
        context_with_problem = context.copy()
        context_with_problem["problem"] = problem
        context_with_problem["phase"] = "proposal"
        
        proposal = self.argument_generator.generate_argument(
            "proposal",
            context_with_problem,
            self.personality
        )
        
        similar_experiences = self.memory.recall_similar(problem, k=3)
        if similar_experiences and random.random() < 0.4:
            best_exp = max(similar_experiences, key=lambda x: x["outcome"])
            if best_exp["outcome"] > 0.6:
                proposal += f" Building on past successes, {best_exp['action'].lower()}."
        
        return proposal
    
    def challenge_proposal(self, proposal: Any, all_proposals: List[Any], context: Dict[str, Any]) -> Optional[str]:
        if proposal.agent_id == self.agent_id:
            return None
        
        state = self.q_learning.get_state_hash(context)
        
        aggressiveness = self.personality.get("aggressiveness", 0.5)
        analytical_depth = self.personality.get("analytical_depth", 0.5)
        
        should_challenge_prob = aggressiveness * 0.7 + analytical_depth * 0.3
        
        if random.random() > should_challenge_prob:
            return None
        
        available_actions = ["challenge_weakness", "challenge_evidence", "challenge_logic", "no_challenge"]
        action = self.q_learning.choose_action(state, available_actions)
        
        if action == "no_challenge":
            return None
        
        challenge_context = context.copy()
        challenge_context["target_proposal"] = proposal.content
        challenge_context["phase"] = "challenge"
        
        challenge = self.argument_generator.generate_argument(
            "challenge",
            challenge_context,
            self.personality
        )
        
        return challenge
    
    def rebut_challenge(self, challenge: Any, original_proposal: Any, context: Dict[str, Any]) -> Optional[str]:
        if original_proposal.agent_id != self.agent_id:
            return None
        
        state = self.q_learning.get_state_hash(context)
        
        defensiveness = self.personality.get("defensiveness", 0.5)
        confidence = self.personality.get("confidence", 0.5)
        
        should_rebut_prob = defensiveness * 0.6 + confidence * 0.4
        
        if random.random() > should_rebut_prob:
            return None
        
        available_actions = ["rebut_directly", "rebut_reframe", "rebut_evidence", "no_rebuttal"]
        action = self.q_learning.choose_action(state, available_actions)
        
        if action == "no_rebuttal":
            return None
        
        rebuttal_context = context.copy()
        rebuttal_context["challenge_content"] = challenge.content
        rebuttal_context["original_proposal"] = original_proposal.content
        rebuttal_context["phase"] = "rebuttal"
        
        rebuttal = self.argument_generator.generate_argument(
            "rebuttal",
            rebuttal_context,
            self.personality
        )
        
        return rebuttal
    
    def learn_from_outcome(self, outcome: float, context: Dict[str, Any]):
        if self.current_state and self.last_action:
            next_state = self.q_learning.get_state_hash(context)
            
            reward = (outcome - 50) / 50
            
            available_next_actions = ["propose_innovative", "propose_conservative", "challenge_weakness", "rebut_directly"]
            
            self.q_learning.update(
                self.current_state,
                self.last_action,
                reward,
                next_state,
                available_next_actions
            )
        
        self.memory.add_experience(
            state=context.get("problem", "unknown"),
            action=self.last_action or "unknown",
            outcome=outcome / 100,
            context=context
        )
        
        self.performance_history.append(outcome / 100)
        if len(self.performance_history) > 50:
            self.performance_history.pop(0)
        
        avg_performance = sum(self.performance_history) / len(self.performance_history) if self.performance_history else 0.5
        
        if len(self.performance_history) >= 5:
            self.personality = self.genetic_evolution.mutate_personality(
                self.personality,
                avg_performance
            )
    
    def evolve_with(self, other_agent: 'SentientAgent', my_fitness: float, other_fitness: float) -> Dict[str, float]:
        new_personality = self.genetic_evolution.crossover(
            self.personality,
            other_agent.personality,
            my_fitness,
            other_fitness
        )
        
        return self.genetic_evolution.mutate_personality(new_personality, (my_fitness + other_fitness) / 2)
    
    def update_score(self, score: float, is_winner: bool):
        self.score = score
        self.lifetime_score += score
        self.debates_participated += 1
        
        if is_winner:
            self.wins += 1
        else:
            self.losses += 1
        
        context = {
            "score": score,
            "is_winner": is_winner,
            "debates": self.debates_participated,
            "timestamp": time.time()
        }
        
        self.learn_from_outcome(score, context)
    
    def deactivate(self):
        self.is_active = False
        for tool in self.tools.values():
            if hasattr(tool, 'deactivate'):
                tool.deactivate()
    
    def save_memory(self, filepath: str):
        self.memory.save(filepath)
    
    def get_stats(self) -> Dict[str, Any]:
        win_rate = self.wins / self.debates_participated if self.debates_participated > 0 else 0
        avg_lifetime_score = self.lifetime_score / self.debates_participated if self.debates_participated > 0 else 0
        
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_active": self.is_active,
            "proposals_made": len(self.proposals_made),
            "challenges_made": len(self.challenges_made),
            "rebuttals_made": len(self.rebuttals_made),
            "current_score": self.score,
            "lifetime_score": self.lifetime_score,
            "debates_participated": self.debates_participated,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": win_rate,
            "avg_score": avg_lifetime_score,
            "tools_count": len(self.tools),
            "message_count": len(self.message_history),
            "personality": self.personality.copy(),
            "exploration_rate": self.q_learning.exploration_rate,
            "memory_size": len(self.memory.experiences)
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        top_q_values = sorted(
            [(state_action, q_val) for state_action, q_val in self.q_learning.q_table.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "top_strategies": [
                {"state": sa[0], "action": sa[1], "q_value": q_val}
                for (sa, q_val) in top_q_values
            ],
            "total_learned_strategies": len(self.q_learning.q_table),
            "exploration_rate": self.q_learning.exploration_rate,
            "recent_performance": self.performance_history[-10:] if self.performance_history else [],
            "avg_recent_performance": sum(self.performance_history[-10:]) / min(10, len(self.performance_history)) if self.performance_history else 0
        }
