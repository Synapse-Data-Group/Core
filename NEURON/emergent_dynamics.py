"""
Emergent Dynamics - Oscillations, synchronization, attractors, and self-organizing criticality

Implements mechanisms for true emergent behavior in the neural network.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np


@dataclass
class OscillatorState:
    """State of a neural oscillator"""
    phase: float = 0.0
    frequency: float = 1.0
    amplitude: float = 1.0
    last_update: float = field(default_factory=time.time)


@dataclass
class AttractorState:
    """Represents an attractor in state space"""
    center: List[float]
    basin_size: float
    stability: float
    visit_count: int = 0
    last_visited: float = 0.0


class NeuralOscillator:
    """
    Implements oscillatory dynamics in neurons
    
    Neurons can fire rhythmically, creating waves of activity
    """
    
    def __init__(self, base_frequency: float = 1.0):
        self.base_frequency = base_frequency
        self.oscillators: Dict[str, OscillatorState] = {}
        self.phase_coupling: Dict[Tuple[str, str], float] = {}
    
    def add_oscillator(self, neuron_id: str, frequency: Optional[float] = None):
        """Add oscillator for a neuron"""
        if frequency is None:
            frequency = self.base_frequency + random.gauss(0, 0.1)
        
        self.oscillators[neuron_id] = OscillatorState(
            phase=random.uniform(0, 2 * math.pi),
            frequency=frequency,
            amplitude=1.0
        )
    
    def update_oscillator(self, neuron_id: str, dt: float = 0.01) -> float:
        """Update oscillator phase and return current activation"""
        if neuron_id not in self.oscillators:
            return 0.0
        
        osc = self.oscillators[neuron_id]
        
        coupling_term = 0.0
        for (pre, post), strength in self.phase_coupling.items():
            if post == neuron_id and pre in self.oscillators:
                pre_osc = self.oscillators[pre]
                phase_diff = pre_osc.phase - osc.phase
                coupling_term += strength * math.sin(phase_diff)
        
        osc.phase += 2 * math.pi * osc.frequency * dt + coupling_term * dt
        osc.phase = osc.phase % (2 * math.pi)
        osc.last_update = time.time()
        
        activation = osc.amplitude * (1 + math.sin(osc.phase)) / 2
        
        return activation
    
    def couple_oscillators(self, neuron_a: str, neuron_b: str, strength: float = 0.1):
        """Create phase coupling between oscillators"""
        self.phase_coupling[(neuron_a, neuron_b)] = strength
        self.phase_coupling[(neuron_b, neuron_a)] = strength
    
    def get_synchronization_index(self, neuron_ids: List[str]) -> float:
        """Measure synchronization among oscillators"""
        if len(neuron_ids) < 2:
            return 0.0
        
        phases = [
            self.oscillators[nid].phase
            for nid in neuron_ids
            if nid in self.oscillators
        ]
        
        if len(phases) < 2:
            return 0.0
        
        mean_cos = sum(math.cos(p) for p in phases) / len(phases)
        mean_sin = sum(math.sin(p) for p in phases) / len(phases)
        
        r = math.sqrt(mean_cos**2 + mean_sin**2)
        
        return r


class SynchronizationDetector:
    """
    Detects and tracks synchronized neuron groups
    
    Synchronized groups represent coherent patterns of activity
    """
    
    def __init__(self, sync_threshold: float = 0.7):
        self.sync_threshold = sync_threshold
        self.synchronized_groups: List[Set[str]] = []
        self.group_history: deque = deque(maxlen=100)
    
    def detect_synchronized_groups(
        self,
        neuron_activations: Dict[str, float],
        time_window: int = 10
    ) -> List[Set[str]]:
        """Detect groups of neurons firing synchronously"""
        active_neurons = [
            nid for nid, activation in neuron_activations.items()
            if activation > 0.5
        ]
        
        if len(active_neurons) < 2:
            return []
        
        groups = []
        visited = set()
        
        for neuron_id in active_neurons:
            if neuron_id in visited:
                continue
            
            group = self._find_synchronized_group(
                neuron_id,
                active_neurons,
                neuron_activations
            )
            
            if len(group) >= 2:
                groups.append(group)
                visited.update(group)
        
        self.synchronized_groups = groups
        self.group_history.append({
            'timestamp': time.time(),
            'groups': [list(g) for g in groups]
        })
        
        return groups
    
    def _find_synchronized_group(
        self,
        seed_neuron: str,
        candidates: List[str],
        activations: Dict[str, float]
    ) -> Set[str]:
        """Find group of neurons synchronized with seed"""
        group = {seed_neuron}
        seed_activation = activations[seed_neuron]
        
        for candidate in candidates:
            if candidate == seed_neuron:
                continue
            
            activation_diff = abs(activations[candidate] - seed_activation)
            
            if activation_diff < (1.0 - self.sync_threshold):
                group.add(candidate)
        
        return group
    
    def get_dominant_pattern(self) -> Optional[Set[str]]:
        """Get most frequently occurring synchronized pattern"""
        if not self.group_history:
            return None
        
        pattern_counts = defaultdict(int)
        
        for entry in self.group_history:
            for group in entry['groups']:
                pattern_key = tuple(sorted(group))
                pattern_counts[pattern_key] += 1
        
        if not pattern_counts:
            return None
        
        dominant = max(pattern_counts.items(), key=lambda x: x[1])
        return set(dominant[0])


class AttractorDynamics:
    """
    Implements attractor dynamics
    
    Network settles into stable patterns (attractors) that represent learned states
    """
    
    def __init__(self, state_dimension: int = 128):
        self.state_dimension = state_dimension
        self.attractors: List[AttractorState] = []
        self.current_state: List[float] = [0.0] * state_dimension
        self.state_history: deque = deque(maxlen=100)
    
    def update_state(self, neuron_activations: Dict[str, float]):
        """Update network state from neuron activations"""
        neuron_ids = sorted(neuron_activations.keys())
        
        state_vector = []
        for i in range(self.state_dimension):
            if i < len(neuron_ids):
                state_vector.append(neuron_activations[neuron_ids[i]])
            else:
                state_vector.append(0.0)
        
        self.current_state = state_vector
        self.state_history.append({
            'timestamp': time.time(),
            'state': state_vector.copy()
        })
    
    def find_nearest_attractor(self) -> Optional[AttractorState]:
        """Find attractor closest to current state"""
        if not self.attractors:
            return None
        
        min_distance = float('inf')
        nearest = None
        
        for attractor in self.attractors:
            distance = self._euclidean_distance(self.current_state, attractor.center)
            
            if distance < min_distance:
                min_distance = distance
                nearest = attractor
        
        return nearest
    
    def is_in_attractor_basin(self, attractor: AttractorState, threshold: float = 0.5) -> bool:
        """Check if current state is in attractor's basin"""
        distance = self._euclidean_distance(self.current_state, attractor.center)
        return distance < attractor.basin_size * threshold
    
    def create_attractor(self, state: List[float], basin_size: float = 1.0):
        """Create new attractor at given state"""
        attractor = AttractorState(
            center=state.copy(),
            basin_size=basin_size,
            stability=1.0,
            visit_count=1,
            last_visited=time.time()
        )
        self.attractors.append(attractor)
    
    def strengthen_attractor(self, attractor: AttractorState):
        """Strengthen attractor (make basin deeper)"""
        attractor.visit_count += 1
        attractor.stability = min(2.0, attractor.stability * 1.05)
        attractor.basin_size = min(2.0, attractor.basin_size * 1.02)
        attractor.last_visited = time.time()
    
    def weaken_attractor(self, attractor: AttractorState):
        """Weaken attractor (make basin shallower)"""
        attractor.stability *= 0.95
        attractor.basin_size *= 0.98
        
        if attractor.stability < 0.1:
            self.attractors.remove(attractor)
    
    def _euclidean_distance(self, state1: List[float], state2: List[float]) -> float:
        """Calculate Euclidean distance between states"""
        return math.sqrt(sum((a - b)**2 for a, b in zip(state1, state2)))
    
    def detect_convergence(self, window: int = 10, threshold: float = 0.01) -> bool:
        """Detect if network has converged to stable state"""
        if len(self.state_history) < window:
            return False
        
        recent_states = [entry['state'] for entry in list(self.state_history)[-window:]]
        
        variances = []
        for dim in range(self.state_dimension):
            values = [state[dim] for state in recent_states]
            mean = sum(values) / len(values)
            variance = sum((v - mean)**2 for v in values) / len(values)
            variances.append(variance)
        
        avg_variance = sum(variances) / len(variances)
        
        return avg_variance < threshold


class SelfOrganizedCriticality:
    """
    Implements self-organized criticality
    
    Network operates at edge of chaos - critical point between order and disorder
    """
    
    def __init__(self):
        self.avalanche_sizes: List[int] = []
        self.current_avalanche_size = 0
        self.is_avalanche_active = False
        self.criticality_parameter = 1.0
    
    def trigger_avalanche(self, initial_neurons: List[str]):
        """Start an avalanche of neural activity"""
        self.is_avalanche_active = True
        self.current_avalanche_size = len(initial_neurons)
    
    def propagate_avalanche(
        self,
        active_neurons: Set[str],
        connections: Dict[str, List[str]]
    ) -> Set[str]:
        """Propagate avalanche to connected neurons"""
        if not self.is_avalanche_active:
            return set()
        
        newly_active = set()
        
        for neuron_id in active_neurons:
            if neuron_id in connections:
                for target_id in connections[neuron_id]:
                    if random.random() < self.criticality_parameter:
                        newly_active.add(target_id)
        
        self.current_avalanche_size += len(newly_active)
        
        if not newly_active:
            self.end_avalanche()
        
        return newly_active
    
    def end_avalanche(self):
        """End current avalanche and record size"""
        if self.is_avalanche_active:
            self.avalanche_sizes.append(self.current_avalanche_size)
            self.is_avalanche_active = False
            self.current_avalanche_size = 0
    
    def calculate_criticality_index(self) -> float:
        """
        Calculate criticality index
        
        At critical point, avalanche sizes follow power law distribution
        """
        if len(self.avalanche_sizes) < 10:
            return 0.5
        
        recent_sizes = self.avalanche_sizes[-100:]
        
        if not recent_sizes:
            return 0.5
        
        avg_size = sum(recent_sizes) / len(recent_sizes)
        max_size = max(recent_sizes)
        
        if max_size == 0:
            return 0.0
        
        criticality = avg_size / max_size
        
        return criticality
    
    def adjust_criticality(self, target: float = 0.5):
        """Adjust network to maintain criticality"""
        current = self.calculate_criticality_index()
        
        if current < target:
            self.criticality_parameter *= 1.01
        elif current > target:
            self.criticality_parameter *= 0.99
        
        self.criticality_parameter = max(0.1, min(1.0, self.criticality_parameter))


class EmergentPatternRecognizer:
    """
    Recognizes emergent patterns in network activity
    
    Patterns that weren't programmed but emerge from dynamics
    """
    
    def __init__(self):
        self.discovered_patterns: List[Dict[str, Any]] = []
        self.pattern_occurrences: Dict[str, int] = defaultdict(int)
    
    def detect_emergent_pattern(
        self,
        neuron_activations: Dict[str, float],
        synchronized_groups: List[Set[str]]
    ) -> Optional[Dict[str, Any]]:
        """Detect novel emergent patterns"""
        active_neurons = {
            nid for nid, act in neuron_activations.items()
            if act > 0.5
        }
        
        if len(active_neurons) < 3:
            return None
        
        pattern_signature = self._compute_pattern_signature(
            active_neurons,
            synchronized_groups
        )
        
        if pattern_signature not in self.pattern_occurrences:
            pattern = {
                'signature': pattern_signature,
                'neurons': list(active_neurons),
                'groups': [list(g) for g in synchronized_groups],
                'discovered_at': time.time(),
                'occurrence_count': 1
            }
            
            self.discovered_patterns.append(pattern)
            self.pattern_occurrences[pattern_signature] = 1
            
            return pattern
        else:
            self.pattern_occurrences[pattern_signature] += 1
            return None
    
    def _compute_pattern_signature(
        self,
        active_neurons: Set[str],
        synchronized_groups: List[Set[str]]
    ) -> str:
        """Compute unique signature for pattern"""
        neuron_sig = '_'.join(sorted(active_neurons)[:10])
        
        group_sig = '_'.join(
            str(len(g)) for g in sorted(synchronized_groups, key=len, reverse=True)[:3]
        )
        
        return f"{neuron_sig}_{group_sig}"
    
    def get_recurring_patterns(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """Get patterns that occur frequently"""
        recurring = []
        
        for pattern in self.discovered_patterns:
            sig = pattern['signature']
            if self.pattern_occurrences[sig] >= min_occurrences:
                pattern_copy = pattern.copy()
                pattern_copy['occurrence_count'] = self.pattern_occurrences[sig]
                recurring.append(pattern_copy)
        
        return sorted(recurring, key=lambda x: x['occurrence_count'], reverse=True)


class EmergentDynamicsEngine:
    """
    Integrates all emergent dynamics mechanisms
    """
    
    def __init__(self):
        self.oscillator = NeuralOscillator()
        self.synchronization = SynchronizationDetector()
        self.attractors = AttractorDynamics()
        self.criticality = SelfOrganizedCriticality()
        self.pattern_recognizer = EmergentPatternRecognizer()
        
        self.dynamics_enabled = True
    
    def update_dynamics(
        self,
        neuron_activations: Dict[str, float],
        connections: Dict[str, List[str]],
        dt: float = 0.01
    ) -> Dict[str, Any]:
        """Update all emergent dynamics"""
        if not self.dynamics_enabled:
            return {}
        
        for neuron_id in neuron_activations.keys():
            if neuron_id not in self.oscillator.oscillators:
                self.oscillator.add_oscillator(neuron_id)
        
        oscillatory_activations = {}
        for neuron_id in neuron_activations.keys():
            osc_activation = self.oscillator.update_oscillator(neuron_id, dt)
            combined = (neuron_activations[neuron_id] + osc_activation) / 2
            oscillatory_activations[neuron_id] = combined
        
        sync_groups = self.synchronization.detect_synchronized_groups(
            oscillatory_activations
        )
        
        self.attractors.update_state(oscillatory_activations)
        nearest_attractor = self.attractors.find_nearest_attractor()
        
        if nearest_attractor and self.attractors.is_in_attractor_basin(nearest_attractor):
            self.attractors.strengthen_attractor(nearest_attractor)
        elif self.attractors.detect_convergence():
            self.attractors.create_attractor(self.attractors.current_state)
        
        active_neurons = {
            nid for nid, act in oscillatory_activations.items()
            if act > 0.6
        }
        
        if active_neurons and not self.criticality.is_avalanche_active:
            self.criticality.trigger_avalanche(list(active_neurons))
        
        if self.criticality.is_avalanche_active:
            newly_active = self.criticality.propagate_avalanche(
                active_neurons,
                connections
            )
        
        self.criticality.adjust_criticality()
        
        emergent_pattern = self.pattern_recognizer.detect_emergent_pattern(
            oscillatory_activations,
            sync_groups
        )
        
        return {
            'oscillatory_activations': oscillatory_activations,
            'synchronized_groups': sync_groups,
            'nearest_attractor': nearest_attractor,
            'criticality_index': self.criticality.calculate_criticality_index(),
            'emergent_pattern': emergent_pattern,
            'converged': self.attractors.detect_convergence()
        }
    
    def get_emergent_statistics(self) -> Dict[str, Any]:
        """Get statistics about emergent behavior"""
        sync_index = 0.0
        if self.synchronization.synchronized_groups:
            all_neurons = set()
            for group in self.synchronization.synchronized_groups:
                all_neurons.update(group)
            sync_index = len(all_neurons) / max(1, len(self.oscillator.oscillators))
        
        return {
            'oscillator_count': len(self.oscillator.oscillators),
            'synchronized_groups': len(self.synchronization.synchronized_groups),
            'synchronization_index': sync_index,
            'attractor_count': len(self.attractors.attractors),
            'criticality_index': self.criticality.calculate_criticality_index(),
            'discovered_patterns': len(self.pattern_recognizer.discovered_patterns),
            'recurring_patterns': len(self.pattern_recognizer.get_recurring_patterns())
        }
