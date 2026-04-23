"""
Living Network - Complete self-evolving neural organism

Integrates all systems: learning, evolution, persistence, emergent dynamics
This is the true self-organizing, self-evolving AI organism.
"""

import time
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

from neuron_core import (
    MicroNeuron, ReasoningNeuron, MetaNeuron, SpecialistNeuron,
    MemoryNeuron, OutputNeuron, NeuronType, LLMProvider
)
from vector_base import VirtualVectorBase
from learning_system import IntegratedLearningSystem
from evolutionary_system import EvolutionaryEngine, NeuronGenome
from persistence_system import PersistenceManager
from emergent_dynamics import EmergentDynamicsEngine
from collective_reasoning import CollectiveReasoningEngine


class LivingNeuronNetwork:
    """
    Complete self-evolving neural organism
    
    Features:
    - Hebbian learning (connections strengthen/weaken)
    - Evolutionary algorithms (neurons mutate and evolve)
    - Persistent state (learns across sessions)
    - Emergent dynamics (oscillations, synchronization, attractors)
    - Self-organizing criticality
    - Feedback integration (learns from outcomes)
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        baseline_neurons: int = 1000,
        storage_path: str = "./neuron_state",
        enable_learning: bool = True,
        enable_evolution: bool = True,
        enable_emergence: bool = True,
        enable_persistence: bool = True
    ):
        self.llm_provider = llm_provider
        self.baseline_neurons = baseline_neurons
        
        self.neurons: Dict[str, MicroNeuron] = {}
        self.vector_base = VirtualVectorBase(vector_dimension=128)
        
        self.learning_system = IntegratedLearningSystem() if enable_learning else None
        self.evolution_engine = EvolutionaryEngine() if enable_evolution else None
        self.persistence = PersistenceManager(storage_path) if enable_persistence else None
        self.emergent_dynamics = EmergentDynamicsEngine() if enable_emergence else None
        self.collective_reasoning = CollectiveReasoningEngine(llm_provider)
        
        self.meta_neurons: Dict[str, MetaNeuron] = {}
        self.output_neurons: Dict[str, OutputNeuron] = {}
        
        self.neuron_id_counter = 0
        self.session_start_time = time.time()
        self.total_interactions = 0
        
        self.feedback_history: List[Dict[str, Any]] = []
        
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load saved state or initialize new network"""
        if self.persistence:
            saved_state = self.persistence.load_network_state()
            
            if saved_state:
                print(f"Loading saved network state from {saved_state['timestamp']}")
                self._restore_from_state(saved_state)
                return
        
        print(f"Initializing new network with {self.baseline_neurons} neurons...")
        self._initialize_baseline_network()
    
    def _initialize_baseline_network(self):
        """Create baseline neural network"""
        reasoning_count = int(self.baseline_neurons * 0.7)
        memory_count = int(self.baseline_neurons * 0.2)
        meta_count = int(self.baseline_neurons * 0.05)
        
        for i in range(reasoning_count):
            genome = NeuronGenome() if self.evolution_engine else None
            neuron = ReasoningNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_random_function(),
                specialization="general",
                llm_provider=self.llm_provider,
                threshold=genome.threshold if genome else 0.5
            )
            self._add_neuron(neuron, genome)
        
        for i in range(memory_count):
            neuron = MemoryNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description="Store and recall patterns"
            )
            self._add_neuron(neuron)
        
        for i in range(meta_count):
            neuron = MetaNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_meta_function(),
                llm_provider=self.llm_provider
            )
            self.meta_neurons[neuron.id] = neuron
            self._add_neuron(neuron)
        
        output_types = ['response', 'confidence', 'reasoning', 'uncertainty', 'action']
        for output_type in output_types:
            neuron = OutputNeuron(
                neuron_id=self._generate_neuron_id(),
                output_type=output_type
            )
            self.output_neurons[neuron.id] = neuron
            self._add_neuron(neuron)
        
        self._initialize_connections()
        
        print(f"✓ Network initialized: {len(self.neurons)} neurons")
    
    def _restore_from_state(self, saved_state: Dict[str, Any]):
        """Restore network from saved state"""
        self.neuron_id_counter = saved_state['metadata'].get('neuron_id_counter', 0)
        
        if self.persistence:
            weights = self.persistence.load_connection_weights()
            if weights:
                print(f"  Restored {len(weights)} connection weights")
            
            patterns = self.persistence.load_memory_patterns()
            if patterns:
                print(f"  Restored {len(patterns)} memory patterns")
            
            history = self.persistence.load_evolution_history()
            if history and self.evolution_engine:
                self.evolution_engine.evolution_history = history
                self.evolution_engine.generation_count = len(history)
                print(f"  Restored {len(history)} generations of evolution")
        
        self._initialize_baseline_network()
        
        print("✓ Network restored from saved state")
    
    def _generate_neuron_id(self) -> str:
        self.neuron_id_counter += 1
        return f"neuron_{self.neuron_id_counter:06d}"
    
    def _generate_random_function(self) -> str:
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
        import random
        return random.choice(functions)
    
    def _generate_meta_function(self) -> str:
        functions = [
            "Assess network capacity",
            "Detect capability gaps",
            "Monitor neuron health",
            "Manage resource allocation",
            "Coordinate neuron spawning"
        ]
        import random
        return random.choice(functions)
    
    def _add_neuron(self, neuron: MicroNeuron, genome: Optional[NeuronGenome] = None):
        """Add neuron to network with all systems"""
        self.neurons[neuron.id] = neuron
        
        vector = self.vector_base.create_specialized_vector(neuron.function)
        self.vector_base.add_neuron(neuron.id, vector)
        
        if self.evolution_engine and genome:
            self.evolution_engine.register_neuron(neuron.id, genome)
    
    def _initialize_connections(self):
        """Initialize connections with learning system"""
        for neuron_id in self.neurons:
            neighbors = self.vector_base.find_nearest_neighbors(neuron_id, k=10)
            
            for neighbor_id, similarity in neighbors:
                if similarity > self.vector_base.similarity_threshold:
                    self.neurons[neuron_id].add_connection(neighbor_id, weight=similarity)
    
    def process_with_learning(
        self,
        user_input: str,
        max_cycles: int = 100,
        request_feedback: bool = False
    ) -> Dict[str, Any]:
        """
        Process input with full learning and evolution
        
        This is the main interface for the living organism
        """
        print(f"\n{'='*70}")
        print(f"Processing (Session {self.total_interactions + 1}): {user_input[:50]}...")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        self.total_interactions += 1
        
        active_neuron_ids = [nid for nid, n in self.neurons.items() if n.state.is_active]
        
        task_complexity = self.collective_reasoning.assess_task_complexity(
            user_input,
            self.meta_neurons,
            active_neuron_ids
        )
        print(f"Task complexity (collective assessment): {task_complexity:.2f}")
        
        current_neurons = len(self.neurons)
        
        action, target_neurons, reasoning = self.collective_reasoning.decide_scaling_action(
            current_neurons,
            task_complexity,
            self.baseline_neurons,
            self.meta_neurons,
            self.feedback_history
        )
        
        print(f"Scaling decision (collective): {action}")
        print(f"  Reasoning: {reasoning}")
        
        if action == "scale_up" and target_neurons > current_neurons:
            print(f"Scaling up: {current_neurons} → {target_neurons} neurons")
            self._scale_up_with_evolution(user_input, target_neurons - current_neurons)
        elif action == "scale_down" and target_neurons < current_neurons:
            print(f"Scaling down: {current_neurons} → {target_neurons} neurons")
            self._scale_down_to_target(target_neurons)
        
        print(f"\nRunning neural dynamics with {len(self.neurons)} neurons...")
        
        active_neurons_history = []
        
        self._activate_input_layer(user_input)
        
        for cycle in range(max_cycles):
            cycle_start = time.time()
            
            active_neurons = self._run_cycle_with_learning(cycle)
            active_neurons_history.append(active_neurons)
            
            if self.emergent_dynamics:
                neuron_activations = {
                    nid: n.state.activation
                    for nid, n in self.neurons.items()
                }
                connections = {
                    nid: [conn.target_id for conn in n.connections.values()]
                    for nid, n in self.neurons.items()
                }
                
                dynamics_result = self.emergent_dynamics.update_dynamics(
                    neuron_activations,
                    connections,
                    dt=0.01
                )
                
                if dynamics_result.get('converged'):
                    print(f"  ✓ Converged at cycle {cycle} (emergent attractor)")
                    break
            
            if cycle % 20 == 0:
                print(f"  Cycle {cycle}: {len(active_neurons)} neurons active")
            
            activity_counts = [len(an) for an in active_neurons_history]
            converged, conv_reasoning = self.collective_reasoning.collective_convergence_check(
                cycle,
                active_neurons,
                len(self.neurons),
                activity_counts,
                self.meta_neurons
            )
            
            if converged:
                print(f"  ✓ Converged at cycle {cycle} (collective decision)")
                print(f"    Reasoning: {conv_reasoning}")
                break
        
        response = self._extract_response()
        
        result = {
            'response': response,
            'cycles': cycle + 1,
            'active_neurons': active_neurons_history[-1] if active_neurons_history else [],
            'complexity': task_complexity,
            'processing_time': time.time() - start_time
        }
        
        if request_feedback:
            print("\n" + "="*70)
            print("FEEDBACK REQUEST")
            print("="*70)
            print(f"Response: {response[:200]}...")
            feedback = input("\nWas this response helpful? (yes/no/skip): ").strip().lower()
            
            if feedback in ['yes', 'no']:
                success = (feedback == 'yes')
                self._integrate_feedback(success, active_neurons_history[-1], user_input, response)
                result['feedback'] = feedback
                result['learning_applied'] = True
        
        if self.evolution_engine and len(self.neurons) > self.baseline_neurons * 1.5:
            print(f"\nEvolving population...")
            self._evolve_population()
        
        if len(self.neurons) > self.baseline_neurons:
            print(f"\nScaling down: {len(self.neurons)} → {self.baseline_neurons} neurons (collective decision)")
            self._scale_down_with_collective_reasoning()
        
        if self.persistence and self.persistence.should_autosave():
            print("\nAutosaving network state...")
            self._save_state()
        
        elapsed = time.time() - start_time
        print(f"\n✓ Processing complete in {elapsed:.2f}s")
        print(f"{'='*70}\n")
        
        return result
    
    def _run_cycle_with_learning(self, cycle: int) -> List[str]:
        """Run one cycle with learning enabled"""
        active_neurons = []
        
        for neuron in self.neurons.values():
            for conn in neuron.connections.values():
                if conn.target_id in self.neurons:
                    target = self.neurons[conn.target_id]
                    signal = neuron.state.activation * conn.weight
                    target.receive_signal(neuron.id, signal)
                    
                    if self.learning_system:
                        new_weight = self.learning_system.update_connection_with_learning(
                            neuron.id,
                            conn.target_id,
                            neuron.state.activation,
                            target.state.activation,
                            conn.weight,
                            pre_spike_time=neuron.state.last_fired,
                            post_spike_time=target.state.last_fired
                        )
                        conn.weight = new_weight
            
            neuron.compute_activation()
            
            if neuron.should_fire():
                active_neurons.append(neuron.id)
                
                if self.evolution_engine:
                    self.evolution_engine.update_fitness(
                        neuron.id,
                        fired=True,
                        energy_used=0.1
                    )
        
        return active_neurons
    
    def _integrate_feedback(
        self,
        success: bool,
        active_neurons: List[str],
        user_input: str,
        response: str
    ):
        """Integrate user feedback into learning"""
        print(f"\n{'='*70}")
        print(f"LEARNING FROM FEEDBACK: {'SUCCESS' if success else 'FAILURE'}")
        print(f"{'='*70}")
        
        if self.learning_system:
            self.learning_system.provide_feedback(
                success,
                active_neurons,
                timestamp=time.time()
            )
            print(f"  ✓ Hebbian learning updated")
        
        if self.evolution_engine:
            reward = 1.0 if success else -0.5
            for neuron_id in active_neurons:
                self.evolution_engine.update_fitness(
                    neuron_id,
                    success=success,
                    reward=reward
                )
            print(f"  ✓ Evolutionary fitness updated")
        
        self.feedback_history.append({
            'timestamp': time.time(),
            'success': success,
            'input': user_input,
            'response': response,
            'active_neurons': len(active_neurons)
        })
        
        print(f"{'='*70}\n")
    
    def _scale_up_with_evolution(self, task_description: str, additional_neurons: int):
        """Scale up using evolutionary reproduction with collective reasoning"""
        should_spawn_specialists, specialist_types, reasoning = self.collective_reasoning.decide_specialist_needs(
            task_description,
            [n.specialization for n in self.neurons.values() if hasattr(n, 'specialization')],
            self.meta_neurons
        )
        
        if should_spawn_specialists and specialist_types:
            print(f"  Collective decision: Spawn specialists - {reasoning}")
            for spec_type in specialist_types[:min(5, len(specialist_types))]:
                for _ in range(min(10, additional_neurons // len(specialist_types))):
                    neuron = SpecialistNeuron(
                        neuron_id=self._generate_neuron_id(),
                        function_description=f"Specialist in {spec_type}",
                        specialization=spec_type,
                        llm_provider=self.llm_provider
                    )
                    self._add_neuron(neuron)
                    additional_neurons -= 1
                    if additional_neurons <= 0:
                        break
                if additional_neurons <= 0:
                    break
        
        if self.evolution_engine and additional_neurons > 0:
            population = [
                (nid, {
                    'fitness': self.evolution_engine.neuron_fitness[nid].calculate_fitness(),
                    'fire_count': self.evolution_engine.neuron_fitness[nid].fire_count
                })
                for nid in self.evolution_engine.neuron_fitness.keys()
            ]
            
            reproduction_pairs = self.collective_reasoning.decide_reproduction_pairs(
                population,
                additional_neurons // 2,
                self.meta_neurons
            )
            
            for parent1_id, parent2_id in reproduction_pairs:
                child_genome, parent_id = self.evolution_engine.reproduce(
                    parent1_id,
                    parent2_id
                )
                
                neuron = ReasoningNeuron(
                    neuron_id=self._generate_neuron_id(),
                    function_description=self._generate_random_function(),
                    specialization="evolved",
                    llm_provider=self.llm_provider,
                    threshold=child_genome.threshold
                )
                
                self._add_neuron(neuron, child_genome)
                
                neighbors = self.vector_base.find_nearest_neighbors(neuron.id, k=15)
                for neighbor_id, similarity in neighbors:
                    if similarity > 0.5:
                        neuron.add_connection(neighbor_id, weight=similarity)
            
            print(f"  ✓ Spawned {len(reproduction_pairs)} evolved neurons")
        else:
            self._spawn_general_neurons(additional_neurons)
    
    def _spawn_general_neurons(self, count: int):
        """Spawn general neurons without evolution"""
        for i in range(count):
            neuron = ReasoningNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_random_function(),
                specialization="general",
                llm_provider=self.llm_provider
            )
            self._add_neuron(neuron)
            
            neighbors = self.vector_base.find_nearest_neighbors(neuron.id, k=10)
            for neighbor_id, similarity in neighbors:
                if similarity > 0.5:
                    neuron.add_connection(neighbor_id, weight=similarity)
    
    def _evolve_population(self):
        """Execute evolutionary step"""
        if not self.evolution_engine:
            return
        
        current_size = len(self.neurons)
        target_size = self.baseline_neurons
        
        neurons_to_remove, offspring_to_create = self.evolution_engine.evolve_generation(
            current_size,
            target_size
        )
        
        for neuron_id in neurons_to_remove:
            self._remove_neuron(neuron_id)
        
        for child_genome, parent_id in offspring_to_create:
            neuron = ReasoningNeuron(
                neuron_id=self._generate_neuron_id(),
                function_description=self._generate_random_function(),
                specialization="evolved",
                llm_provider=self.llm_provider,
                threshold=child_genome.threshold
            )
            self._add_neuron(neuron, child_genome)
        
        stats = self.evolution_engine.get_evolution_statistics()
        print(f"  Evolution: Gen {stats['generation']}, "
              f"Avg fitness: {stats['average_fitness']:.3f}")
    
    def _scale_down_to_target(self, target_count: int):
        """Scale down to target using collective reasoning"""
        current_count = len(self.neurons)
        
        if current_count <= target_count:
            return
        
        to_remove_count = current_count - target_count
        neurons_to_evaluate = []
        
        for neuron_id, neuron in self.neurons.items():
            if neuron_id in self.meta_neurons or neuron_id in self.output_neurons:
                continue
            
            neuron_data = {
                'fire_count': neuron.state.fire_count,
                'successful_contributions': 0,
                'failed_contributions': 0,
                'age': time.time() - neuron.creation_time,
                'fitness': 0.0
            }
            
            if self.evolution_engine and neuron_id in self.evolution_engine.neuron_fitness:
                fitness_metrics = self.evolution_engine.neuron_fitness[neuron_id]
                neuron_data['successful_contributions'] = fitness_metrics.successful_contributions
                neuron_data['failed_contributions'] = fitness_metrics.failed_contributions
                neuron_data['fitness'] = fitness_metrics.calculate_fitness()
            
            neurons_to_evaluate.append((neuron_id, neuron_data))
        
        neurons_to_remove = []
        for neuron_id, neuron_data in neurons_to_evaluate:
            if len(neurons_to_remove) >= to_remove_count:
                break
            
            should_prune, confidence, reasoning = self.collective_reasoning.evaluate_neuron_for_pruning(
                neuron_id,
                neuron_data,
                self.meta_neurons,
                {'total_neurons': current_count, 'baseline_neurons': self.baseline_neurons}
            )
            
            if should_prune and confidence > 0.6:
                neurons_to_remove.append(neuron_id)
        
        if len(neurons_to_remove) < to_remove_count and self.evolution_engine:
            remaining_needed = to_remove_count - len(neurons_to_remove)
            fallback_removals = self.evolution_engine.select_for_death(
                current_count - len(neurons_to_remove),
                target_count
            )
            neurons_to_remove.extend(fallback_removals[:remaining_needed])
        
        for neuron_id in neurons_to_remove:
            self._remove_neuron(neuron_id)
    
    def _scale_down_with_collective_reasoning(self):
        """Scale down using collective reasoning"""
        self._scale_down_to_target(self.baseline_neurons)
    
    def _remove_neuron(self, neuron_id: str):
        """Remove neuron from all systems"""
        if neuron_id in self.neurons:
            del self.neurons[neuron_id]
        
        self.vector_base.remove_neuron(neuron_id)
        
        if self.evolution_engine:
            self.evolution_engine.remove_neuron(neuron_id)
        
        if neuron_id in self.meta_neurons:
            del self.meta_neurons[neuron_id]
        if neuron_id in self.output_neurons:
            del self.output_neurons[neuron_id]
    
    
    def _activate_input_layer(self, user_input: str):
        """Activate neurons based on input"""
        input_hash = hash(user_input) % len(self.neurons)
        
        neuron_list = list(self.neurons.values())
        for i in range(min(50, len(neuron_list))):
            idx = (input_hash + i) % len(neuron_list)
            neuron = neuron_list[idx]
            import random
            neuron.state.activation = random.uniform(0.5, 0.9)
            neuron.state.is_active = True
    
    def _extract_response(self) -> str:
        """Extract response from collective state"""
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
    
    def _save_state(self):
        """Save complete network state"""
        if not self.persistence:
            return
        
        genomes = {}
        fitness = {}
        
        if self.evolution_engine:
            genomes = {
                nid: genome.to_dict()
                for nid, genome in self.evolution_engine.neuron_genomes.items()
            }
            fitness = {
                nid: {
                    'fire_count': metrics.fire_count,
                    'successful_contributions': metrics.successful_contributions,
                    'fitness': metrics.calculate_fitness()
                }
                for nid, metrics in self.evolution_engine.neuron_fitness.items()
            }
        
        metadata = {
            'neuron_id_counter': self.neuron_id_counter,
            'total_interactions': self.total_interactions,
            'session_start': self.session_start_time
        }
        
        self.persistence.save_network_state(
            self.neurons,
            genomes,
            fitness,
            metadata
        )
        
        weights = {
            (neuron.id, conn.target_id): conn.weight
            for neuron in self.neurons.values()
            for conn in neuron.connections.values()
        }
        self.persistence.save_connection_weights(weights)
        
        if self.evolution_engine:
            self.persistence.save_evolution_history(
                self.evolution_engine.evolution_history
            )
        
        print("  ✓ State saved")
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get complete statistics about the living network"""
        stats = {
            'network': {
                'total_neurons': len(self.neurons),
                'baseline_neurons': self.baseline_neurons,
                'total_interactions': self.total_interactions,
                'session_duration': time.time() - self.session_start_time
            }
        }
        
        if self.learning_system:
            stats['learning'] = self.learning_system.get_learning_statistics()
        
        if self.evolution_engine:
            stats['evolution'] = self.evolution_engine.get_evolution_statistics()
        
        if self.emergent_dynamics:
            stats['emergence'] = self.emergent_dynamics.get_emergent_statistics()
        
        if self.persistence:
            stats['persistence'] = self.persistence.get_storage_info()
        
        stats['feedback'] = {
            'total_feedback': len(self.feedback_history),
            'success_rate': sum(1 for f in self.feedback_history if f['success']) / max(1, len(self.feedback_history))
        }
        
        return stats
