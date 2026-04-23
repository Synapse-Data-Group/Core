"""
Evolutionary System - Genetic algorithms, mutation, selection, and reproduction

Implements mechanisms for neurons to evolve, mutate, and naturally select based on fitness.
"""

import random
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class NeuronGenome:
    """Genetic code for a neuron - can mutate and evolve"""
    threshold: float = 0.5
    learning_rate: float = 0.01
    decay_rate: float = 0.001
    mutation_rate: float = 0.001
    activation_bias: float = 0.0
    refractory_period: float = 0.0
    energy_efficiency: float = 1.0
    specialization_strength: float = 0.5
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'threshold': self.threshold,
            'learning_rate': self.learning_rate,
            'decay_rate': self.decay_rate,
            'mutation_rate': self.mutation_rate,
            'activation_bias': self.activation_bias,
            'refractory_period': self.refractory_period,
            'energy_efficiency': self.energy_efficiency,
            'specialization_strength': self.specialization_strength
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'NeuronGenome':
        return cls(**data)
    
    def get_hash(self) -> str:
        """Get unique hash for this genome"""
        genome_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.md5(genome_str.encode()).hexdigest()[:8]


@dataclass
class FitnessMetrics:
    """Tracks neuron fitness over time"""
    fire_count: int = 0
    successful_contributions: int = 0
    failed_contributions: int = 0
    energy_consumed: float = 0.0
    reward_accumulated: float = 0.0
    age: float = 0.0
    generation: int = 0
    
    def calculate_fitness(self) -> float:
        """Calculate overall fitness score"""
        if self.fire_count == 0:
            return 0.0
        
        success_rate = self.successful_contributions / max(1, self.fire_count)
        
        efficiency = 1.0 / (1.0 + self.energy_consumed / max(1, self.fire_count))
        
        contribution_score = self.successful_contributions - self.failed_contributions * 0.5
        
        age_penalty = 1.0 / (1.0 + self.age / 1000.0)
        
        fitness = (
            success_rate * 0.4 +
            efficiency * 0.2 +
            contribution_score * 0.3 +
            self.reward_accumulated * 0.1
        ) * age_penalty
        
        return max(0.0, fitness)


class GeneticOperators:
    """Implements genetic operations: mutation, crossover, selection"""
    
    def __init__(self, mutation_rate: float = 0.01, mutation_strength: float = 0.1):
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
    
    def mutate_genome(self, genome: NeuronGenome) -> NeuronGenome:
        """Apply random mutations to genome"""
        mutated = NeuronGenome()
        
        for gene_name, gene_value in genome.to_dict().items():
            if random.random() < genome.mutation_rate:
                mutation = random.gauss(0, self.mutation_strength)
                new_value = gene_value + mutation
                
                if gene_name == 'threshold':
                    new_value = max(0.1, min(0.9, new_value))
                elif gene_name in ['learning_rate', 'decay_rate', 'mutation_rate']:
                    new_value = max(0.0001, min(0.1, new_value))
                elif gene_name == 'refractory_period':
                    new_value = max(0.0, min(10.0, new_value))
                elif gene_name in ['energy_efficiency', 'specialization_strength']:
                    new_value = max(0.1, min(2.0, new_value))
                else:
                    new_value = max(-1.0, min(1.0, new_value))
                
                setattr(mutated, gene_name, new_value)
            else:
                setattr(mutated, gene_name, gene_value)
        
        return mutated
    
    def crossover(self, parent1: NeuronGenome, parent2: NeuronGenome) -> NeuronGenome:
        """Combine genes from two parents"""
        child = NeuronGenome()
        
        for gene_name in parent1.to_dict().keys():
            if random.random() < 0.5:
                setattr(child, gene_name, getattr(parent1, gene_name))
            else:
                setattr(child, gene_name, getattr(parent2, gene_name))
        
        return child
    
    def tournament_selection(
        self,
        population: List[Tuple[str, FitnessMetrics]],
        tournament_size: int = 3
    ) -> str:
        """Select winner from random tournament"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        
        winner = max(tournament, key=lambda x: x[1].calculate_fitness())
        return winner[0]
    
    def roulette_selection(
        self,
        population: List[Tuple[str, FitnessMetrics]]
    ) -> str:
        """Select based on fitness-proportional probability"""
        total_fitness = sum(metrics.calculate_fitness() for _, metrics in population)
        
        if total_fitness == 0:
            return random.choice(population)[0]
        
        pick = random.uniform(0, total_fitness)
        current = 0
        
        for neuron_id, metrics in population:
            current += metrics.calculate_fitness()
            if current >= pick:
                return neuron_id
        
        return population[-1][0]


class EvolutionaryEngine:
    """
    Manages evolutionary processes for the neural network
    
    - Natural selection (weak neurons die)
    - Reproduction (strong neurons replicate)
    - Mutation (offspring have variations)
    - Speciation (new neuron types emerge)
    """
    
    def __init__(
        self,
        selection_pressure: float = 0.3,
        reproduction_rate: float = 0.1,
        mutation_rate: float = 0.01
    ):
        self.selection_pressure = selection_pressure
        self.reproduction_rate = reproduction_rate
        self.mutation_rate = mutation_rate
        
        self.genetic_operators = GeneticOperators(mutation_rate=mutation_rate)
        
        self.neuron_genomes: Dict[str, NeuronGenome] = {}
        self.neuron_fitness: Dict[str, FitnessMetrics] = {}
        self.neuron_lineage: Dict[str, List[str]] = {}
        
        self.generation_count = 0
        self.species: Dict[str, List[str]] = defaultdict(list)
        
        self.evolution_history: List[Dict[str, Any]] = []
    
    def register_neuron(
        self,
        neuron_id: str,
        genome: Optional[NeuronGenome] = None,
        parent_id: Optional[str] = None
    ):
        """Register a new neuron in the evolutionary system"""
        if genome is None:
            genome = NeuronGenome()
        
        self.neuron_genomes[neuron_id] = genome
        self.neuron_fitness[neuron_id] = FitnessMetrics(
            generation=self.generation_count
        )
        
        if parent_id:
            self.neuron_lineage[neuron_id] = [parent_id] + self.neuron_lineage.get(parent_id, [])
        else:
            self.neuron_lineage[neuron_id] = []
        
        genome_hash = genome.get_hash()
        self.species[genome_hash].append(neuron_id)
    
    def update_fitness(
        self,
        neuron_id: str,
        fired: bool = False,
        success: bool = False,
        energy_used: float = 0.0,
        reward: float = 0.0
    ):
        """Update fitness metrics for a neuron"""
        if neuron_id not in self.neuron_fitness:
            return
        
        metrics = self.neuron_fitness[neuron_id]
        
        if fired:
            metrics.fire_count += 1
            
            if success:
                metrics.successful_contributions += 1
            else:
                metrics.failed_contributions += 1
        
        metrics.energy_consumed += energy_used
        metrics.reward_accumulated += reward
        metrics.age = time.time() - metrics.age if metrics.age > 0 else time.time()
    
    def select_for_death(self, population_size: int, target_size: int) -> List[str]:
        """Select neurons to remove based on low fitness"""
        if population_size <= target_size:
            return []
        
        to_remove = population_size - target_size
        
        population = [
            (nid, self.neuron_fitness[nid])
            for nid in self.neuron_fitness.keys()
        ]
        
        population.sort(key=lambda x: x[1].calculate_fitness())
        
        threshold_idx = int(len(population) * self.selection_pressure)
        weak_neurons = population[:threshold_idx]
        
        if len(weak_neurons) < to_remove:
            weak_neurons = population[:to_remove]
        
        selected_for_death = random.sample(
            weak_neurons,
            min(to_remove, len(weak_neurons))
        )
        
        return [nid for nid, _ in selected_for_death]
    
    def select_for_reproduction(self, count: int) -> List[Tuple[str, str]]:
        """Select pairs of neurons for reproduction"""
        population = [
            (nid, self.neuron_fitness[nid])
            for nid in self.neuron_fitness.keys()
        ]
        
        if len(population) < 2:
            return []
        
        population.sort(key=lambda x: x[1].calculate_fitness(), reverse=True)
        
        elite_size = max(2, int(len(population) * 0.2))
        elite = population[:elite_size]
        
        pairs = []
        for _ in range(count):
            parent1_id = self.genetic_operators.tournament_selection(elite)
            parent2_id = self.genetic_operators.tournament_selection(elite)
            
            if parent1_id != parent2_id:
                pairs.append((parent1_id, parent2_id))
        
        return pairs
    
    def reproduce(self, parent1_id: str, parent2_id: str) -> Tuple[NeuronGenome, str]:
        """Create offspring from two parents"""
        parent1_genome = self.neuron_genomes[parent1_id]
        parent2_genome = self.neuron_genomes[parent2_id]
        
        if random.random() < 0.7:
            child_genome = self.genetic_operators.crossover(parent1_genome, parent2_genome)
        else:
            child_genome = parent1_genome if random.random() < 0.5 else parent2_genome
        
        child_genome = self.genetic_operators.mutate_genome(child_genome)
        
        parent_id = parent1_id if random.random() < 0.5 else parent2_id
        
        return child_genome, parent_id
    
    def evolve_generation(
        self,
        current_population_size: int,
        target_population_size: int
    ) -> Tuple[List[str], List[Tuple[NeuronGenome, str]]]:
        """
        Execute one generation of evolution
        
        Returns:
            (neurons_to_remove, offspring_to_create)
        """
        self.generation_count += 1
        
        neurons_to_remove = []
        if current_population_size > target_population_size:
            neurons_to_remove = self.select_for_death(
                current_population_size,
                target_population_size
            )
        
        offspring_to_create = []
        if current_population_size < target_population_size:
            offspring_count = target_population_size - current_population_size
            reproduction_pairs = self.select_for_reproduction(offspring_count)
            
            for parent1_id, parent2_id in reproduction_pairs:
                child_genome, parent_id = self.reproduce(parent1_id, parent2_id)
                offspring_to_create.append((child_genome, parent_id))
        
        self.evolution_history.append({
            'generation': self.generation_count,
            'population_size': current_population_size,
            'removed': len(neurons_to_remove),
            'created': len(offspring_to_create),
            'species_count': len(self.species),
            'timestamp': time.time()
        })
        
        return neurons_to_remove, offspring_to_create
    
    def get_species_diversity(self) -> Dict[str, int]:
        """Get count of neurons in each species"""
        return {
            species_id: len(neurons)
            for species_id, neurons in self.species.items()
            if neurons
        }
    
    def get_elite_neurons(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get top performing neurons"""
        population = [
            (nid, self.neuron_fitness[nid].calculate_fitness())
            for nid in self.neuron_fitness.keys()
        ]
        
        population.sort(key=lambda x: x[1], reverse=True)
        return population[:top_n]
    
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive evolution statistics"""
        if not self.neuron_fitness:
            return {'generation': self.generation_count, 'population': 0}
        
        fitness_values = [
            metrics.calculate_fitness()
            for metrics in self.neuron_fitness.values()
        ]
        
        return {
            'generation': self.generation_count,
            'population': len(self.neuron_fitness),
            'species_count': len(self.species),
            'average_fitness': sum(fitness_values) / len(fitness_values),
            'max_fitness': max(fitness_values),
            'min_fitness': min(fitness_values),
            'elite_neurons': len([f for f in fitness_values if f > 0.7]),
            'weak_neurons': len([f for f in fitness_values if f < 0.3])
        }
    
    def remove_neuron(self, neuron_id: str):
        """Remove neuron from evolutionary tracking"""
        if neuron_id in self.neuron_genomes:
            genome_hash = self.neuron_genomes[neuron_id].get_hash()
            if genome_hash in self.species:
                self.species[genome_hash] = [
                    nid for nid in self.species[genome_hash]
                    if nid != neuron_id
                ]
            
            del self.neuron_genomes[neuron_id]
        
        if neuron_id in self.neuron_fitness:
            del self.neuron_fitness[neuron_id]
        
        if neuron_id in self.neuron_lineage:
            del self.neuron_lineage[neuron_id]


class SpeciationSystem:
    """
    Manages emergence of new neuron species
    
    Species = groups of neurons with similar genomes
    New species emerge through mutation and selection
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.species_representatives: Dict[str, NeuronGenome] = {}
        self.species_metadata: Dict[str, Dict[str, Any]] = {}
    
    def calculate_genome_similarity(
        self,
        genome1: NeuronGenome,
        genome2: NeuronGenome
    ) -> float:
        """Calculate similarity between two genomes"""
        genes1 = genome1.to_dict()
        genes2 = genome2.to_dict()
        
        differences = []
        for gene_name in genes1.keys():
            diff = abs(genes1[gene_name] - genes2[gene_name])
            
            if gene_name == 'threshold':
                max_diff = 0.8
            elif gene_name in ['learning_rate', 'decay_rate', 'mutation_rate']:
                max_diff = 0.1
            else:
                max_diff = 2.0
            
            normalized_diff = diff / max_diff
            differences.append(normalized_diff)
        
        avg_difference = sum(differences) / len(differences)
        similarity = 1.0 - min(1.0, avg_difference)
        
        return similarity
    
    def assign_species(self, genome: NeuronGenome) -> str:
        """Assign genome to existing species or create new one"""
        for species_id, representative in self.species_representatives.items():
            similarity = self.calculate_genome_similarity(genome, representative)
            
            if similarity >= self.similarity_threshold:
                return species_id
        
        new_species_id = f"species_{len(self.species_representatives) + 1}"
        self.species_representatives[new_species_id] = genome
        self.species_metadata[new_species_id] = {
            'created': time.time(),
            'member_count': 0,
            'avg_fitness': 0.0
        }
        
        return new_species_id
    
    def update_species_metadata(
        self,
        species_id: str,
        member_count: int,
        avg_fitness: float
    ):
        """Update species metadata"""
        if species_id in self.species_metadata:
            self.species_metadata[species_id]['member_count'] = member_count
            self.species_metadata[species_id]['avg_fitness'] = avg_fitness
    
    def get_species_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all species"""
        return self.species_metadata.copy()
