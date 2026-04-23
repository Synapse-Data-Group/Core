"""
Neuron Network - The living neural organism

Self-organizing brain that dynamically creates/removes neurons based on task needs.
Replaces traditional agent workflows with emergent collective intelligence.
"""

import time
import random
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
from dataclasses import dataclass

from neuron_core import (
    MicroNeuron, ReasoningNeuron, MetaNeuron, SpecialistNeuron,
    MemoryNeuron, OutputNeuron, NeuronType, LLMProvider
)
from vector_base import VirtualVectorBase


@dataclass
class CollectiveState:
    """Current state of the entire neural network"""
    active_neurons: Set[str]
    activation_pattern: Dict[str, float]
    firing_neurons: List[str]
    convergence_score: float
    cycle_count: int
    timestamp: float
    
    def has_converged(self, threshold: float = 0.95) -> bool:
        """Check if network has reached stable state"""
        return self.convergence_score >= threshold


class NeuronNetwork:
    """
    The complete neural organism
    
    Self-organizing brain that:
    - Starts with baseline neurons (1K)
    - Dynamically spawns specialists as needed
    - Prunes unnecessary neurons
    - Reasons collectively
    - Replaces LangChain/agent workflows
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        baseline_neurons: int = 1000,
        vector_dimension: int = 128
    ):
        self.llm_provider = llm_provider
        self.baseline_neurons = baseline_neurons
        
        self.neurons: Dict[str, MicroNeuron] = {}
        self.vector_base = VirtualVectorBase(vector_dimension=vector_dimension)
        
        self.meta_neurons: Dict[str, MetaNeuron] = {}
        self.output_neurons: Dict[str, OutputNeuron] = {}
        
        self.collective_state = None
        self.reasoning_history: List[Dict[str, Any]] = []
        
        self.neuron_id_counter = 0
        
        self._initialize_baseline_network()
    
    def _initialize_baseline_network(self):
        """Create baseline neural network"""
        print(f"Initializing baseline network with {self.baseline_neurons} neurons...")
        
        reasoning_count = int(self.baseline_neurons * 0.7)
        memory_count = int(self.baseline_neurons * 0.2)
        meta_count = int(self.baseline_neurons * 0.05)
        output_count = 5
        
        for i in range(reasoning_count):
            neuron = ReasoningNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_random_function(),
                specialization="general",
                llm_provider=self.llm_provider,
                threshold=random.uniform(0.4, 0.6)
            )
            self._add_neuron(neuron)
        
        for i in range(memory_count):
            neuron = MemoryNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description="Store and recall patterns",
                threshold=random.uniform(0.3, 0.5)
            )
            self._add_neuron(neuron)
        
        for i in range(meta_count):
            neuron = MetaNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_meta_function(),
                llm_provider=self.llm_provider,
                threshold=0.6
            )
            self.meta_neurons[neuron.id] = neuron
            self._add_neuron(neuron)
        
        output_types = ['response', 'confidence', 'reasoning', 'uncertainty', 'action']
        for output_type in output_types:
            neuron = OutputNeuron(
                neuron_id=self._generate_neuron_id(),
                output_type=output_type,
                threshold=0.3
            )
            self.output_neurons[neuron.id] = neuron
            self._add_neuron(neuron)
        
        self._initialize_connections()
        
        print(f"✓ Network initialized: {len(self.neurons)} neurons")
    
    def _generate_neuron_id(self) -> str:
        """Generate unique neuron ID"""
        self.neuron_id_counter += 1
        return f"neuron_{self.neuron_id_counter:06d}"
    
    def _generate_random_function(self) -> str:
        """Generate random reasoning function for baseline neurons"""
        functions = [
            "Detect logical contradictions",
            "Find analogies and patterns",
            "Evaluate argument strength",
            "Generate hypotheses",
            "Assess evidence quality",
            "Identify assumptions",
            "Synthesize information",
            "Challenge conclusions",
            "Validate reasoning steps",
            "Propose alternatives"
        ]
        return random.choice(functions)
    
    def _generate_meta_function(self) -> str:
        """Generate meta-neuron function"""
        functions = [
            "Assess network capacity",
            "Detect capability gaps",
            "Monitor neuron health",
            "Manage resource allocation",
            "Coordinate neuron spawning"
        ]
        return random.choice(functions)
    
    def _add_neuron(self, neuron: MicroNeuron):
        """Add neuron to network"""
        self.neurons[neuron.id] = neuron
        
        vector = self.vector_base.create_specialized_vector(neuron.function)
        self.vector_base.add_neuron(neuron.id, vector)
    
    def _remove_neuron(self, neuron_id: str):
        """Remove neuron from network"""
        if neuron_id in self.neurons:
            del self.neurons[neuron_id]
        
        self.vector_base.remove_neuron(neuron_id)
        
        if neuron_id in self.meta_neurons:
            del self.meta_neurons[neuron_id]
        if neuron_id in self.output_neurons:
            del self.output_neurons[neuron_id]
    
    def _initialize_connections(self):
        """Initialize connections based on semantic similarity"""
        print("Establishing neural connections...")
        
        for neuron_id in self.neurons:
            neighbors = self.vector_base.find_nearest_neighbors(neuron_id, k=10)
            
            for neighbor_id, similarity in neighbors:
                if similarity > self.vector_base.similarity_threshold:
                    self.neurons[neuron_id].add_connection(neighbor_id, weight=similarity)
        
        print(f"✓ Connections established")
    
    def process(self, user_input: str, max_cycles: int = 100) -> str:
        """
        Main interface - like chat.completions.create()
        But powered by living neural organism
        """
        print(f"\n{'='*60}")
        print(f"Processing: {user_input[:50]}...")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        task_complexity = self._assess_task_complexity(user_input)
        print(f"Task complexity: {task_complexity:.2f}")
        
        target_neurons = self._calculate_target_neurons(task_complexity)
        current_neurons = len(self.neurons)
        
        if target_neurons > current_neurons:
            print(f"Scaling up: {current_neurons} → {target_neurons} neurons")
            self._scale_up(user_input, target_neurons - current_neurons)
        
        print(f"\nRunning neural dynamics with {len(self.neurons)} neurons...")
        self._activate_input_layer(user_input)
        
        self._run_neural_dynamics(max_cycles)
        
        response = self._extract_response()
        
        if target_neurons > self.baseline_neurons:
            print(f"\nScaling down: {len(self.neurons)} → {self.baseline_neurons} neurons")
            self._scale_down_to_baseline()
        
        elapsed = time.time() - start_time
        print(f"\n✓ Processing complete in {elapsed:.2f}s")
        print(f"{'='*60}\n")
        
        return response
    
    def _assess_task_complexity(self, task: str) -> float:
        """Assess task complexity (0.0 - 1.0)"""
        complexity_indicators = {
            'simple': 0.2,
            'explain': 0.3,
            'analyze': 0.5,
            'design': 0.6,
            'build': 0.7,
            'create': 0.7,
            'prove': 0.9,
            'research': 0.8,
            'code': 0.6,
            'react': 0.6,
            'landing page': 0.6
        }
        
        task_lower = task.lower()
        max_complexity = 0.3
        
        for keyword, complexity in complexity_indicators.items():
            if keyword in task_lower:
                max_complexity = max(max_complexity, complexity)
        
        word_count = len(task.split())
        if word_count > 50:
            max_complexity += 0.1
        
        return min(1.0, max_complexity)
    
    def _calculate_target_neurons(self, complexity: float) -> int:
        """Calculate how many neurons needed for task"""
        if complexity < 0.3:
            return self.baseline_neurons
        elif complexity < 0.5:
            return int(self.baseline_neurons * 2)
        elif complexity < 0.7:
            return int(self.baseline_neurons * 5)
        else:
            return int(self.baseline_neurons * 10)
    
    def _scale_up(self, task_description: str, additional_neurons: int):
        """Spawn additional specialized neurons"""
        for meta_neuron in list(self.meta_neurons.values())[:3]:
            assessment = meta_neuron.assess_capability_gap(
                network_state=self._get_network_state(),
                task_description=task_description
            )
            
            if assessment and assessment.get('gap_detected'):
                print(f"\n  Meta-neuron detected gap: {assessment.get('missing_capability')}")
                
                suggested_types = assessment.get('suggested_neurons', [])
                neurons_per_type = additional_neurons // max(len(suggested_types), 1)
                
                for specialization in suggested_types[:3]:
                    self._spawn_specialist_neurons(
                        specialization=specialization,
                        count=neurons_per_type,
                        task_context=task_description
                    )
                
                break
        else:
            self._spawn_general_neurons(additional_neurons)
    
    def _spawn_specialist_neurons(self, specialization: str, count: int, task_context: str):
        """Spawn specialized neurons for specific capability"""
        print(f"  Spawning {count} {specialization} specialist neurons...")
        
        meta_neuron = list(self.meta_neurons.values())[0]
        design = meta_neuron.design_specialist_neuron(specialization, task_context)
        
        if not design:
            return
        
        for i in range(count):
            neuron = SpecialistNeuron(
                neuron_id=self._generate_neuron_id(),
                specialization=specialization,
                function_description=design.get('function_description', f'{specialization} specialist'),
                required_knowledge=design.get('required_knowledge', []),
                llm_provider=self.llm_provider,
                threshold=random.uniform(0.4, 0.6)
            )
            
            if i == 0 and design.get('required_knowledge'):
                for knowledge in design['required_knowledge'][:2]:
                    neuron.acquire_knowledge(knowledge)
            
            self._add_neuron(neuron)
            
            neighbors = self.vector_base.find_nearest_neighbors(neuron.id, k=15)
            for neighbor_id, similarity in neighbors:
                if similarity > 0.5:
                    neuron.add_connection(neighbor_id, weight=similarity)
        
        print(f"  ✓ {count} {specialization} neurons created and connected")
    
    def _spawn_general_neurons(self, count: int):
        """Spawn general reasoning neurons"""
        print(f"  Spawning {count} general reasoning neurons...")
        
        for i in range(count):
            neuron = ReasoningNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_random_function(),
                specialization="general",
                llm_provider=self.llm_provider,
                threshold=random.uniform(0.4, 0.6)
            )
            self._add_neuron(neuron)
            
            neighbors = self.vector_base.find_nearest_neighbors(neuron.id, k=10)
            for neighbor_id, similarity in neighbors:
                if similarity > 0.5:
                    neuron.add_connection(neighbor_id, weight=similarity)
    
    def _scale_down_to_baseline(self):
        """Prune neurons back to baseline"""
        current_count = len(self.neurons)
        target_count = self.baseline_neurons
        
        if current_count <= target_count:
            return
        
        to_remove = current_count - target_count
        
        specialist_neurons = [
            n for n in self.neurons.values()
            if n.type == NeuronType.SPECIALIST
        ]
        
        specialist_neurons.sort(key=lambda n: n.state.fire_count)
        
        for neuron in specialist_neurons[:to_remove]:
            self._remove_neuron(neuron.id)
        
        remaining = to_remove - len(specialist_neurons[:to_remove])
        if remaining > 0:
            general_neurons = [
                n for n in self.neurons.values()
                if n.type == NeuronType.REASONING and n.id not in self.meta_neurons
            ]
            general_neurons.sort(key=lambda n: n.state.fire_count)
            
            for neuron in general_neurons[:remaining]:
                self._remove_neuron(neuron.id)
    
    def _activate_input_layer(self, user_input: str):
        """Activate input layer neurons with user query"""
        # Store query in network for neurons to access
        self.current_query = user_input
        
        for neuron in list(self.neurons.values())[:10]:
            neuron.state.activation = 0.8
            neuron.state.is_active = True
            # Store query in neuron metadata
            neuron.metadata['current_query'] = user_input
    
    def _run_neural_dynamics(self, max_cycles: int):
        """Run neural network until convergence"""
        for cycle in range(max_cycles):
            active_count = 0
            firing_neurons = []
            
            for neuron in self.neurons.values():
                for conn in neuron.connections.values():
                    if conn.target_id in self.neurons:
                        target = self.neurons[conn.target_id]
                        signal = neuron.state.activation * conn.weight
                        target.receive_signal(neuron.id, signal)
                
                neuron.compute_activation()
                
                if neuron.should_fire():
                    active_count += 1
                    firing_neurons.append(neuron.id)
            
            if cycle % 10 == 0:
                print(f"  Cycle {cycle}: {active_count} neurons active")
            
            if active_count < len(self.neurons) * 0.05:
                print(f"  ✓ Converged at cycle {cycle}")
                break
    
    def _extract_response(self) -> str:
        """Extract response from collective neural state"""
        print("\nExtracting collective response...")
        
        active_reasoning_neurons = [
            n for n in self.neurons.values()
            if isinstance(n, (ReasoningNeuron, SpecialistNeuron))
            and n.state.activation > n.threshold
        ]
        
        active_reasoning_neurons.sort(key=lambda n: n.state.activation, reverse=True)
        
        top_neurons = active_reasoning_neurons[:5]
        
        neuron_outputs = []
        for neuron in top_neurons:
            output = neuron.fire()
            neuron_outputs.append(output)
        
        if not neuron_outputs:
            return "No collective response generated"
        
        output_neuron = list(self.output_neurons.values())[0]
        integrated_response = output_neuron.integrate_collective_state(neuron_outputs)
        
        return integrated_response
    
    def _get_network_state(self) -> Dict[str, Any]:
        """Get current network state"""
        neuron_types = defaultdict(int)
        for neuron in self.neurons.values():
            neuron_types[neuron.type.value] += 1
        
        active_neurons = sum(1 for n in self.neurons.values() if n.state.is_active)
        
        return {
            'total_neurons': len(self.neurons),
            'active_neurons': active_neurons,
            'neuron_types': dict(neuron_types),
            'meta_neurons': len(self.meta_neurons),
            'output_neurons': len(self.output_neurons)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        stats = self._get_network_state()
        stats.update(self.vector_base.get_network_statistics())
        
        specialist_count = sum(
            1 for n in self.neurons.values()
            if n.type == NeuronType.SPECIALIST
        )
        
        stats['specialist_neurons'] = specialist_count
        stats['baseline_neurons'] = self.baseline_neurons
        
        return stats
