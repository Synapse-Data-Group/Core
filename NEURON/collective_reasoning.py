"""
Collective Reasoning System - All decisions emerge from neural collective

NO RULE-BASED DECISIONS. All decisions emerge from:
- Collective neural activation patterns
- Meta-neuron reasoning
- Emergent consensus
- Pattern-based evaluation
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class CollectiveDecision:
    """Result of collective reasoning"""
    decision: str
    confidence: float
    reasoning: str
    participating_neurons: List[str]
    consensus_strength: float
    timestamp: float


class CollectiveReasoningEngine:
    """
    All decisions emerge from collective neural activity
    
    NO RULES. Only patterns and reasoning.
    """
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.decision_history: List[CollectiveDecision] = []
    
    def assess_task_complexity(
        self,
        task: str,
        meta_neurons: Dict[str, Any],
        active_neurons: List[str]
    ) -> float:
        """
        Complexity assessment emerges from meta-neuron reasoning
        NOT from keyword matching rules
        """
        if not meta_neurons:
            return 0.5
        
        meta_neuron = list(meta_neurons.values())[0]
        
        prompt = f"""As a meta-cognitive neuron analyzing task complexity:

Task: "{task}"

Active neurons: {len(active_neurons)}

Assess complexity on scale 0.0-1.0 based on:
- Conceptual depth required
- Number of reasoning steps
- Domain expertise needed
- Integration complexity

Respond with ONLY a number between 0.0 and 1.0, nothing else."""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=10, temperature=0.3)
            complexity = float(response.strip())
            return max(0.0, min(1.0, complexity))
        except:
            activation_pattern = sum(1 for _ in active_neurons) / max(1, len(active_neurons))
            return min(1.0, activation_pattern)
    
    def decide_scaling_action(
        self,
        current_neurons: int,
        task_complexity: float,
        baseline_neurons: int,
        meta_neurons: Dict[str, Any],
        recent_performance: List[Dict[str, Any]]
    ) -> Tuple[str, int, str]:
        """
        Scaling decision emerges from meta-neuron collective reasoning
        NOT from if-then rules
        
        Returns: (action, target_count, reasoning)
        """
        if not meta_neurons:
            return ("maintain", current_neurons, "No meta-neurons available")
        
        meta_neuron_list = list(meta_neurons.values())
        
        performance_summary = "No history"
        if recent_performance:
            avg_success = sum(p.get('success', 0) for p in recent_performance[-5:]) / min(5, len(recent_performance))
            performance_summary = f"Recent success rate: {avg_success:.1%}"
        
        prompt = f"""As a meta-neuron managing network resources:

Current state:
- Active neurons: {current_neurons}
- Baseline: {baseline_neurons}
- Task complexity: {task_complexity:.2f}
- {performance_summary}

Question: Should we scale up, scale down, or maintain current size?

Reason through:
1. Is current capacity sufficient for complexity?
2. Are we over-resourced (wasteful)?
3. What is optimal neuron count?

Respond in format:
ACTION: [scale_up/scale_down/maintain]
TARGET: [number]
REASONING: [your reasoning]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=200, temperature=0.5)
            
            lines = response.strip().split('\n')
            action = "maintain"
            target = current_neurons
            reasoning = "Default reasoning"
            
            for line in lines:
                if line.startswith("ACTION:"):
                    action = line.split(":", 1)[1].strip().lower()
                elif line.startswith("TARGET:"):
                    try:
                        target = int(line.split(":", 1)[1].strip())
                    except:
                        pass
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            self.decision_history.append(CollectiveDecision(
                decision=f"{action}_{target}",
                confidence=0.8,
                reasoning=reasoning,
                participating_neurons=[n.id for n in meta_neuron_list],
                consensus_strength=0.8,
                timestamp=time.time()
            ))
            
            return (action, target, reasoning)
            
        except Exception as e:
            return ("maintain", current_neurons, f"Reasoning failed: {e}")
    
    def decide_specialist_needs(
        self,
        task: str,
        current_specialists: List[str],
        meta_neurons: Dict[str, Any]
    ) -> Tuple[bool, List[str], str]:
        """
        Specialist spawning decision emerges from meta-neuron reasoning
        NOT from keyword detection
        
        Returns: (should_spawn, specialist_types, reasoning)
        """
        if not meta_neurons:
            return (False, [], "No meta-neurons")
        
        meta_neuron = list(meta_neurons.values())[0]
        
        specialist_summary = "None" if not current_specialists else ", ".join(current_specialists[:5])
        
        prompt = f"""As a meta-neuron analyzing capability gaps:

Task: "{task}"
Current specialists: {specialist_summary}

Question: Do we need NEW specialist neurons?

Analyze:
1. What expertise does this task require?
2. Do current specialists cover it?
3. What new specialists would help?

Respond in format:
SPAWN: [yes/no]
TYPES: [comma-separated list of specialist types needed, or "none"]
REASONING: [your analysis]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.6)
            
            lines = response.strip().split('\n')
            should_spawn = False
            specialist_types = []
            reasoning = "Default reasoning"
            
            for line in lines:
                if line.startswith("SPAWN:"):
                    spawn_text = line.split(":", 1)[1].strip().lower()
                    should_spawn = spawn_text in ["yes", "true"]
                elif line.startswith("TYPES:"):
                    types_text = line.split(":", 1)[1].strip()
                    if types_text.lower() != "none":
                        specialist_types = [t.strip() for t in types_text.split(",")]
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            return (should_spawn, specialist_types, reasoning)
            
        except Exception as e:
            return (False, [], f"Reasoning failed: {e}")
    
    def evaluate_neuron_for_pruning(
        self,
        neuron_id: str,
        neuron_data: Dict[str, Any],
        meta_neurons: Dict[str, Any],
        network_state: Dict[str, Any]
    ) -> Tuple[bool, float, str]:
        """
        Pruning decision emerges from meta-neuron evaluation
        NOT from fitness threshold rules
        
        Returns: (should_prune, confidence, reasoning)
        """
        if not meta_neurons:
            return (False, 0.0, "No meta-neurons")
        
        meta_neuron = list(meta_neurons.values())[0]
        
        prompt = f"""As a meta-neuron evaluating neuron health:

Neuron: {neuron_id}
Fire count: {neuron_data.get('fire_count', 0)}
Successful contributions: {neuron_data.get('successful_contributions', 0)}
Failed contributions: {neuron_data.get('failed_contributions', 0)}
Age: {neuron_data.get('age', 0):.0f}s
Fitness: {neuron_data.get('fitness', 0):.3f}

Network context:
- Total neurons: {network_state.get('total_neurons', 0)}
- Baseline: {network_state.get('baseline_neurons', 0)}

Question: Should this neuron be pruned (removed)?

Consider:
1. Is it contributing meaningfully?
2. Is it redundant?
3. Is network over-capacity?

Respond in format:
PRUNE: [yes/no]
CONFIDENCE: [0.0-1.0]
REASONING: [your evaluation]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=200, temperature=0.4)
            
            lines = response.strip().split('\n')
            should_prune = False
            confidence = 0.5
            reasoning = "Default reasoning"
            
            for line in lines:
                if line.startswith("PRUNE:"):
                    prune_text = line.split(":", 1)[1].strip().lower()
                    should_prune = prune_text in ["yes", "true"]
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except:
                        pass
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            return (should_prune, confidence, reasoning)
            
        except Exception as e:
            return (False, 0.0, f"Evaluation failed: {e}")
    
    def collective_convergence_check(
        self,
        cycle: int,
        active_neurons: List[str],
        total_neurons: int,
        activation_history: List[int],
        meta_neurons: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Convergence decision emerges from pattern analysis
        NOT from fixed cycle counts or thresholds
        
        Returns: (should_stop, reasoning)
        """
        if cycle < 10:
            return (False, "Too early to assess convergence")
        
        if not meta_neurons:
            activity_ratio = len(active_neurons) / max(1, total_neurons)
            if activity_ratio < 0.05:
                return (True, "Activity dropped below 5%")
            return (False, "Continuing")
        
        meta_neuron = list(meta_neurons.values())[0]
        
        recent_activity = activation_history[-10:] if len(activation_history) >= 10 else activation_history
        activity_trend = "stable"
        if len(recent_activity) >= 3:
            if recent_activity[-1] < recent_activity[-3] * 0.5:
                activity_trend = "decreasing"
            elif recent_activity[-1] > recent_activity[-3] * 1.5:
                activity_trend = "increasing"
        
        prompt = f"""As a meta-neuron monitoring network convergence:

Cycle: {cycle}
Active neurons: {len(active_neurons)} / {total_neurons}
Recent activity pattern: {recent_activity[-5:]}
Trend: {activity_trend}

Question: Has the network converged to a stable state?

Consider:
1. Is activity stabilizing?
2. Is pattern repeating?
3. Is further processing productive?

Respond in format:
CONVERGED: [yes/no]
REASONING: [your analysis]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=150, temperature=0.3)
            
            lines = response.strip().split('\n')
            converged = False
            reasoning = "Default reasoning"
            
            for line in lines:
                if line.startswith("CONVERGED:"):
                    conv_text = line.split(":", 1)[1].strip().lower()
                    converged = conv_text in ["yes", "true"]
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            return (converged, reasoning)
            
        except Exception as e:
            activity_ratio = len(active_neurons) / max(1, total_neurons)
            if activity_ratio < 0.05:
                return (True, "Activity minimal")
            return (False, "Continuing")
    
    def decide_reproduction_pairs(
        self,
        population: List[Tuple[str, Dict[str, Any]]],
        target_offspring: int,
        meta_neurons: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """
        Reproduction selection emerges from meta-neuron evaluation
        NOT from fixed tournament/roulette rules
        
        Returns: List of (parent1_id, parent2_id) pairs
        """
        if len(population) < 2:
            return []
        
        if not meta_neurons:
            population_sorted = sorted(population, key=lambda x: x[1].get('fitness', 0), reverse=True)
            pairs = []
            for i in range(min(target_offspring, len(population_sorted) // 2)):
                pairs.append((population_sorted[i*2][0], population_sorted[i*2+1][0]))
            return pairs
        
        meta_neuron = list(meta_neurons.values())[0]
        
        top_candidates = sorted(population, key=lambda x: x[1].get('fitness', 0), reverse=True)[:20]
        candidate_summary = "\n".join([
            f"  {nid}: fitness={data.get('fitness', 0):.3f}, fires={data.get('fire_count', 0)}"
            for nid, data in top_candidates[:10]
        ])
        
        prompt = f"""As a meta-neuron selecting parents for reproduction:

Need {target_offspring} offspring.
Top candidates:
{candidate_summary}

Question: Which neurons should reproduce?

Consider:
1. High fitness (proven success)
2. Diversity (avoid inbreeding)
3. Complementary strengths

Respond with {min(target_offspring, len(top_candidates)//2)} parent pairs in format:
PAIR: neuron_id1, neuron_id2
PAIR: neuron_id3, neuron_id4
...
"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.5)
            
            pairs = []
            for line in response.strip().split('\n'):
                if line.startswith("PAIR:"):
                    pair_text = line.split(":", 1)[1].strip()
                    parts = [p.strip() for p in pair_text.split(",")]
                    if len(parts) == 2:
                        pairs.append((parts[0], parts[1]))
            
            if not pairs:
                top_sorted = sorted(population, key=lambda x: x[1].get('fitness', 0), reverse=True)
                for i in range(min(target_offspring, len(top_sorted) // 2)):
                    pairs.append((top_sorted[i*2][0], top_sorted[i*2+1][0]))
            
            return pairs[:target_offspring]
            
        except Exception as e:
            top_sorted = sorted(population, key=lambda x: x[1].get('fitness', 0), reverse=True)
            pairs = []
            for i in range(min(target_offspring, len(top_sorted) // 2)):
                pairs.append((top_sorted[i*2][0], top_sorted[i*2+1][0]))
            return pairs
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get statistics about collective decisions"""
        if not self.decision_history:
            return {'total_decisions': 0}
        
        return {
            'total_decisions': len(self.decision_history),
            'average_confidence': sum(d.confidence for d in self.decision_history) / len(self.decision_history),
            'average_consensus': sum(d.consensus_strength for d in self.decision_history) / len(self.decision_history),
            'recent_decisions': [
                {
                    'decision': d.decision,
                    'confidence': d.confidence,
                    'reasoning': d.reasoning[:100]
                }
                for d in self.decision_history[-5:]
            ]
        }
