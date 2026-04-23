import random
import math
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import pickle
import os


class ExperienceMemory:
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.experiences: List[Dict[str, Any]] = []
        self.concept_graph: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.success_patterns: Dict[str, List[float]] = defaultdict(list)
        
    def add_experience(self, state: str, action: str, outcome: float, context: Dict[str, Any]):
        experience = {
            "state": state,
            "action": action,
            "outcome": outcome,
            "context": context,
            "timestamp": context.get("timestamp", 0)
        }
        
        self.experiences.append(experience)
        
        if len(self.experiences) > self.capacity:
            self.experiences.pop(0)
        
        self._update_concept_graph(state, action, outcome)
        self._update_success_patterns(action, outcome)
    
    def _update_concept_graph(self, state: str, action: str, outcome: float):
        state_words = set(state.lower().split())
        action_words = set(action.lower().split())
        
        for s_word in state_words:
            for a_word in action_words:
                self.concept_graph[s_word][a_word] += outcome * 0.1
    
    def _update_success_patterns(self, action: str, outcome: float):
        self.success_patterns[action].append(outcome)
        if len(self.success_patterns[action]) > 100:
            self.success_patterns[action].pop(0)
    
    def recall_similar(self, state: str, k: int = 5) -> List[Dict[str, Any]]:
        state_words = set(state.lower().split())
        
        scored_experiences = []
        for exp in self.experiences:
            exp_words = set(exp["state"].lower().split())
            similarity = len(state_words & exp_words) / max(len(state_words | exp_words), 1)
            scored_experiences.append((similarity, exp))
        
        scored_experiences.sort(reverse=True, key=lambda x: x[0])
        return [exp for _, exp in scored_experiences[:k]]
    
    def get_concept_strength(self, word1: str, word2: str) -> float:
        return self.concept_graph.get(word1.lower(), {}).get(word2.lower(), 0.0)
    
    def get_action_success_rate(self, action: str) -> float:
        patterns = self.success_patterns.get(action, [])
        if not patterns:
            return 0.5
        return sum(patterns) / len(patterns)
    
    def save(self, filepath: str):
        data = {
            "experiences": self.experiences,
            "concept_graph": dict(self.concept_graph),
            "success_patterns": dict(self.success_patterns)
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.experiences = data["experiences"]
                self.concept_graph = defaultdict(lambda: defaultdict(float), data["concept_graph"])
                self.success_patterns = defaultdict(list, data["success_patterns"])


class QLearningEngine:
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95, 
                 exploration_rate: float = 0.3, exploration_decay: float = 0.995):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = 0.05
        
        self.q_table: Dict[Tuple[str, str], float] = defaultdict(float)
        self.state_visits: Dict[str, int] = defaultdict(int)
        self.action_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    
    def get_state_hash(self, context: Dict[str, Any]) -> str:
        phase = context.get("phase", "unknown")
        proposal_count = context.get("proposal_count", 0)
        challenge_count = context.get("challenge_count", 0)
        my_score = context.get("my_score", 0)
        
        score_bucket = "low" if my_score < 40 else "medium" if my_score < 70 else "high"
        
        return f"{phase}_{proposal_count}_{challenge_count}_{score_bucket}"
    
    def choose_action(self, state: str, available_actions: List[str]) -> str:
        if not available_actions:
            return "default"
        
        if random.random() < self.exploration_rate:
            return random.choice(available_actions)
        
        q_values = [(action, self.q_table[(state, action)]) for action in available_actions]
        
        max_q = max(q_values, key=lambda x: x[1])[1]
        best_actions = [action for action, q in q_values if q == max_q]
        
        return random.choice(best_actions)
    
    def update(self, state: str, action: str, reward: float, next_state: str, 
               next_available_actions: List[str]):
        current_q = self.q_table[(state, action)]
        
        if next_available_actions:
            max_next_q = max(self.q_table[(next_state, a)] for a in next_available_actions)
        else:
            max_next_q = 0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[(state, action)] = new_q
        self.state_visits[state] += 1
        self.action_counts[(state, action)] += 1
        
        self.exploration_rate = max(
            self.min_exploration,
            self.exploration_rate * self.exploration_decay
        )
    
    def get_q_value(self, state: str, action: str) -> float:
        return self.q_table.get((state, action), 0.0)
    
    def get_best_action(self, state: str, available_actions: List[str]) -> str:
        if not available_actions:
            return "default"
        
        return max(available_actions, key=lambda a: self.q_table[(state, a)])


class GeneticEvolution:
    def __init__(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2):
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.generation = 0
        self.fitness_history: List[float] = []
    
    def mutate_personality(self, personality: Dict[str, float], performance: float) -> Dict[str, float]:
        new_personality = personality.copy()
        
        if performance < 0.3:
            effective_mutation_rate = self.mutation_rate * 2
        elif performance > 0.7:
            effective_mutation_rate = self.mutation_rate * 0.5
        else:
            effective_mutation_rate = self.mutation_rate
        
        for trait, value in new_personality.items():
            if isinstance(value, (int, float)) and random.random() < effective_mutation_rate:
                mutation = random.gauss(0, self.mutation_strength)
                new_value = value + mutation
                new_personality[trait] = max(0.0, min(1.0, new_value))
        
        return new_personality
    
    def crossover(self, parent1: Dict[str, float], parent2: Dict[str, float], 
                  fitness1: float, fitness2: float) -> Dict[str, float]:
        child = {}
        
        total_fitness = fitness1 + fitness2
        if total_fitness > 0:
            p1_weight = fitness1 / total_fitness
        else:
            p1_weight = 0.5
        
        for trait in parent1.keys():
            if trait in parent2:
                if random.random() < p1_weight:
                    child[trait] = parent1[trait]
                else:
                    child[trait] = parent2[trait]
            else:
                child[trait] = parent1[trait]
        
        for trait in parent2.keys():
            if trait not in child:
                child[trait] = parent2[trait]
        
        return child
    
    def evolve_population(self, agents_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.generation += 1
        
        agents_data.sort(key=lambda x: x.get("fitness", 0), reverse=True)
        
        elite_count = max(1, len(agents_data) // 4)
        new_population = agents_data[:elite_count]
        
        while len(new_population) < len(agents_data):
            parent1 = random.choice(agents_data[:len(agents_data)//2])
            parent2 = random.choice(agents_data[:len(agents_data)//2])
            
            child_personality = self.crossover(
                parent1["personality"],
                parent2["personality"],
                parent1.get("fitness", 0),
                parent2.get("fitness", 0)
            )
            
            child_personality = self.mutate_personality(
                child_personality,
                (parent1.get("fitness", 0) + parent2.get("fitness", 0)) / 2
            )
            
            child = {
                "personality": child_personality,
                "fitness": 0,
                "generation": self.generation
            }
            
            new_population.append(child)
        
        return new_population


class ArgumentGenerator:
    def __init__(self, memory: ExperienceMemory):
        self.memory = memory
        self.argument_templates = self._build_template_library()
        self.concept_combinations: Dict[str, List[str]] = defaultdict(list)
    
    def _build_template_library(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "proposal": [
                {
                    "structure": "problem_analysis_solution",
                    "components": ["analyze", "propose", "justify"]
                },
                {
                    "structure": "comparative_advantage",
                    "components": ["compare", "contrast", "recommend"]
                },
                {
                    "structure": "evidence_based",
                    "components": ["evidence", "reasoning", "conclusion"]
                },
                {
                    "structure": "innovative_approach",
                    "components": ["challenge_assumption", "novel_method", "benefits"]
                }
            ],
            "challenge": [
                {
                    "structure": "identify_weakness",
                    "components": ["weakness", "consequence", "alternative"]
                },
                {
                    "structure": "request_evidence",
                    "components": ["claim", "question", "requirement"]
                },
                {
                    "structure": "counter_example",
                    "components": ["scenario", "contradiction", "implication"]
                }
            ],
            "rebuttal": [
                {
                    "structure": "address_directly",
                    "components": ["acknowledge", "counter", "strengthen"]
                },
                {
                    "structure": "reframe",
                    "components": ["reinterpret", "context", "resolution"]
                },
                {
                    "structure": "provide_evidence",
                    "components": ["data", "analysis", "conclusion"]
                }
            ]
        }
    
    def generate_argument(self, argument_type: str, context: Dict[str, Any], 
                         personality: Dict[str, float]) -> str:
        similar_experiences = self.memory.recall_similar(
            context.get("problem", "") + " " + context.get("phase", ""),
            k=3
        )
        
        templates = self.argument_templates.get(argument_type, [])
        if not templates:
            return self._generate_fallback(argument_type, context, personality)
        
        creativity = personality.get("creativity", 0.5)
        if random.random() < creativity:
            template = random.choice(templates)
        else:
            template = templates[0]
        
        argument_parts = []
        
        for component in template["components"]:
            part = self._generate_component(
                component, context, personality, similar_experiences
            )
            argument_parts.append(part)
        
        argument = " ".join(argument_parts)
        
        argument = self._apply_personality_style(argument, personality)
        
        return argument
    
    def _generate_component(self, component: str, context: Dict[str, Any],
                           personality: Dict[str, float], 
                           experiences: List[Dict[str, Any]]) -> str:
        problem = context.get("problem", "the issue")
        phase = context.get("phase", "")
        
        component_generators = {
            "analyze": lambda: self._analyze_problem(problem, experiences, personality),
            "propose": lambda: self._propose_solution(problem, experiences, personality),
            "justify": lambda: self._justify_approach(problem, experiences, personality),
            "compare": lambda: self._compare_options(problem, experiences, personality),
            "contrast": lambda: self._contrast_approaches(problem, experiences, personality),
            "recommend": lambda: self._make_recommendation(problem, experiences, personality),
            "evidence": lambda: self._cite_evidence(problem, experiences, personality),
            "reasoning": lambda: self._provide_reasoning(problem, experiences, personality),
            "conclusion": lambda: self._draw_conclusion(problem, experiences, personality),
            "challenge_assumption": lambda: self._challenge_assumption(problem, experiences, personality),
            "novel_method": lambda: self._suggest_novel_method(problem, experiences, personality),
            "benefits": lambda: self._describe_benefits(problem, experiences, personality),
            "weakness": lambda: self._identify_weakness(context, experiences, personality),
            "consequence": lambda: self._describe_consequence(context, experiences, personality),
            "alternative": lambda: self._suggest_alternative(context, experiences, personality),
            "claim": lambda: self._state_claim(context, experiences, personality),
            "question": lambda: self._pose_question(context, experiences, personality),
            "requirement": lambda: self._state_requirement(context, experiences, personality),
            "scenario": lambda: self._describe_scenario(context, experiences, personality),
            "contradiction": lambda: self._show_contradiction(context, experiences, personality),
            "implication": lambda: self._explain_implication(context, experiences, personality),
            "acknowledge": lambda: self._acknowledge_point(context, experiences, personality),
            "counter": lambda: self._counter_argument(context, experiences, personality),
            "strengthen": lambda: self._strengthen_position(context, experiences, personality),
            "reinterpret": lambda: self._reinterpret_challenge(context, experiences, personality),
            "context": lambda: self._provide_context(context, experiences, personality),
            "resolution": lambda: self._offer_resolution(context, experiences, personality),
            "data": lambda: self._present_data(context, experiences, personality),
            "analysis": lambda: self._analyze_data(context, experiences, personality)
        }
        
        generator = component_generators.get(component)
        if generator:
            return generator()
        
        return f"Regarding {component},"
    
    def _analyze_problem(self, problem: str, experiences: List[Dict[str, Any]], 
                        personality: Dict[str, float]) -> str:
        analytical_depth = personality.get("analytical_depth", 0.5)
        
        if analytical_depth > 0.7:
            return f"Through systematic analysis of {problem}, we can identify multiple interdependent factors."
        elif analytical_depth > 0.4:
            return f"Examining {problem} reveals several key considerations."
        else:
            return f"Looking at {problem},"
    
    def _propose_solution(self, problem: str, experiences: List[Dict[str, Any]],
                         personality: Dict[str, float]) -> str:
        boldness = personality.get("boldness", 0.5)
        
        successful_actions = [exp["action"] for exp in experiences if exp["outcome"] > 0.6]
        
        if successful_actions and random.random() < 0.6:
            learned_approach = random.choice(successful_actions)
            return f"I propose we {learned_approach.lower()}, adapting proven strategies to {problem}."
        
        if boldness > 0.7:
            return f"I propose a transformative approach that fundamentally reimagines how we address {problem}."
        elif boldness > 0.4:
            return f"I propose a balanced strategy that addresses {problem} through measured innovation."
        else:
            return f"I propose a conservative approach to {problem} with minimal risk."
    
    def _justify_approach(self, problem: str, experiences: List[Dict[str, Any]],
                         personality: Dict[str, float]) -> str:
        evidence_based = personality.get("evidence_reliance", 0.5)
        
        if evidence_based > 0.6 and experiences:
            success_rate = sum(1 for exp in experiences if exp["outcome"] > 0.5) / len(experiences)
            return f"This approach is justified by a {success_rate:.0%} success rate in similar contexts."
        
        return "This approach balances effectiveness with feasibility."
    
    def _compare_options(self, problem: str, experiences: List[Dict[str, Any]],
                        personality: Dict[str, float]) -> str:
        return f"Comparing available options for {problem},"
    
    def _contrast_approaches(self, problem: str, experiences: List[Dict[str, Any]],
                            personality: Dict[str, float]) -> str:
        return "while alternative approaches exist, they face significant limitations."
    
    def _make_recommendation(self, problem: str, experiences: List[Dict[str, Any]],
                            personality: Dict[str, float]) -> str:
        confidence = personality.get("confidence", 0.5)
        
        if confidence > 0.7:
            return "I strongly recommend this course of action."
        elif confidence > 0.4:
            return "I recommend we proceed with this approach."
        else:
            return "This may be worth considering."
    
    def _cite_evidence(self, problem: str, experiences: List[Dict[str, Any]],
                      personality: Dict[str, float]) -> str:
        if experiences:
            return f"Evidence from {len(experiences)} similar situations supports this direction."
        return "Multiple factors support this approach."
    
    def _provide_reasoning(self, problem: str, experiences: List[Dict[str, Any]],
                          personality: Dict[str, float]) -> str:
        return "The reasoning follows from first principles and empirical observation."
    
    def _draw_conclusion(self, problem: str, experiences: List[Dict[str, Any]],
                        personality: Dict[str, float]) -> str:
        return f"Therefore, this represents the optimal path forward for {problem}."
    
    def _challenge_assumption(self, problem: str, experiences: List[Dict[str, Any]],
                             personality: Dict[str, float]) -> str:
        return f"The conventional wisdom about {problem} may be fundamentally flawed."
    
    def _suggest_novel_method(self, problem: str, experiences: List[Dict[str, Any]],
                             personality: Dict[str, float]) -> str:
        creativity = personality.get("creativity", 0.5)
        
        if creativity > 0.7:
            return "I propose an unconventional methodology that synthesizes insights from disparate domains."
        return "A novel approach could yield breakthrough results."
    
    def _describe_benefits(self, problem: str, experiences: List[Dict[str, Any]],
                          personality: Dict[str, float]) -> str:
        optimism = personality.get("optimism", 0.5)
        
        if optimism > 0.7:
            return "The benefits are substantial and far-reaching."
        return "This offers clear advantages."
    
    def _identify_weakness(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                          personality: Dict[str, float]) -> str:
        target_proposal = context.get("target_proposal", "this proposal")
        return f"A critical weakness in {target_proposal} is its failure to account for edge cases."
    
    def _describe_consequence(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                             personality: Dict[str, float]) -> str:
        return "This oversight could lead to cascading failures under stress conditions."
    
    def _suggest_alternative(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                            personality: Dict[str, float]) -> str:
        return "A more robust alternative would incorporate fail-safes and contingency planning."
    
    def _state_claim(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                    personality: Dict[str, float]) -> str:
        return "The proposal claims to solve the problem comprehensively."
    
    def _pose_question(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                      personality: Dict[str, float]) -> str:
        return "However, what evidence supports this claim?"
    
    def _state_requirement(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                          personality: Dict[str, float]) -> str:
        return "Concrete metrics and validation criteria are required."
    
    def _describe_scenario(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                          personality: Dict[str, float]) -> str:
        return "Consider a scenario where initial assumptions prove incorrect."
    
    def _show_contradiction(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                           personality: Dict[str, float]) -> str:
        return "This directly contradicts the proposal's core premise."
    
    def _explain_implication(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                            personality: Dict[str, float]) -> str:
        return "The implications undermine the entire approach."
    
    def _acknowledge_point(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                          personality: Dict[str, float]) -> str:
        defensiveness = personality.get("defensiveness", 0.5)
        
        if defensiveness < 0.3:
            return "That's a valid concern that deserves attention."
        elif defensiveness < 0.7:
            return "While I understand the concern,"
        else:
            return "The challenge mischaracterizes my position."
    
    def _counter_argument(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                         personality: Dict[str, float]) -> str:
        return "the underlying analysis actually supports my proposal when examined more carefully."
    
    def _strengthen_position(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                            personality: Dict[str, float]) -> str:
        return "In fact, this reinforces the need for my proposed approach."
    
    def _reinterpret_challenge(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                              personality: Dict[str, float]) -> str:
        return "Reframing the challenge reveals it as an opportunity rather than an obstacle."
    
    def _provide_context(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                        personality: Dict[str, float]) -> str:
        return "Within the broader context,"
    
    def _offer_resolution(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                         personality: Dict[str, float]) -> str:
        return "this apparent conflict resolves naturally through proper implementation."
    
    def _present_data(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                     personality: Dict[str, float]) -> str:
        if experiences:
            avg_outcome = sum(exp["outcome"] for exp in experiences) / len(experiences)
            return f"Data from {len(experiences)} cases shows {avg_outcome:.1%} positive outcomes."
        return "Available data supports this position."
    
    def _analyze_data(self, context: Dict[str, Any], experiences: List[Dict[str, Any]],
                     personality: Dict[str, float]) -> str:
        return "Analysis reveals strong correlations with successful outcomes."
    
    def _apply_personality_style(self, argument: str, personality: Dict[str, float]) -> str:
        verbosity = personality.get("verbosity", 0.5)
        formality = personality.get("formality", 0.5)
        
        if formality > 0.7:
            argument = argument.replace(" I ", " I respectfully ")
            argument = argument.replace("This ", "This particular ")
        elif formality < 0.3:
            argument = argument.replace(" is ", "'s ")
            argument = argument.replace(" we ", " we'd ")
        
        if verbosity < 0.3:
            words = argument.split()
            if len(words) > 20:
                argument = " ".join(words[:20]) + "."
        
        return argument
    
    def _generate_fallback(self, argument_type: str, context: Dict[str, Any],
                          personality: Dict[str, float]) -> str:
        problem = context.get("problem", "this issue")
        return f"Regarding {problem}, I have a {argument_type} to present based on careful consideration."
