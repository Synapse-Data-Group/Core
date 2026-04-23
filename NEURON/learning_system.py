"""
Learning System - Hebbian learning, synaptic plasticity, and reward-based adaptation

Implements the mechanisms that allow neurons to learn from experience and improve over time.
"""

import time
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class SynapticTrace:
    """Tracks synaptic activity for learning"""
    pre_synaptic_activity: deque = field(default_factory=lambda: deque(maxlen=100))
    post_synaptic_activity: deque = field(default_factory=lambda: deque(maxlen=100))
    correlation_history: List[float] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)


@dataclass
class LearningMetrics:
    """Metrics for tracking learning progress"""
    total_updates: int = 0
    successful_updates: int = 0
    failed_updates: int = 0
    average_weight_change: float = 0.0
    learning_rate_history: List[float] = field(default_factory=list)


class HebbianLearning:
    """
    Implements Hebbian learning: "Neurons that fire together, wire together"
    
    Core principle: When neuron A repeatedly activates neuron B,
    the connection between them strengthens.
    """
    
    def __init__(
        self,
        base_learning_rate: float = 0.01,
        decay_rate: float = 0.001,
        min_weight: float = -1.0,
        max_weight: float = 1.0
    ):
        self.base_learning_rate = base_learning_rate
        self.decay_rate = decay_rate
        self.min_weight = min_weight
        self.max_weight = max_weight
        
        self.synaptic_traces: Dict[Tuple[str, str], SynapticTrace] = {}
        self.metrics = LearningMetrics()
    
    def update_connection(
        self,
        pre_neuron_id: str,
        post_neuron_id: str,
        pre_activation: float,
        post_activation: float,
        current_weight: float,
        reward_signal: Optional[float] = None
    ) -> float:
        """
        Update connection weight based on correlated activity
        
        Args:
            pre_neuron_id: Source neuron
            post_neuron_id: Target neuron
            pre_activation: Activation of source neuron
            post_activation: Activation of target neuron
            current_weight: Current connection weight
            reward_signal: Optional reward/punishment signal
        
        Returns:
            Updated weight
        """
        connection_key = (pre_neuron_id, post_neuron_id)
        
        if connection_key not in self.synaptic_traces:
            self.synaptic_traces[connection_key] = SynapticTrace()
        
        trace = self.synaptic_traces[connection_key]
        trace.pre_synaptic_activity.append(pre_activation)
        trace.post_synaptic_activity.append(post_activation)
        
        correlation = pre_activation * post_activation
        trace.correlation_history.append(correlation)
        
        learning_rate = self.base_learning_rate
        if reward_signal is not None:
            learning_rate *= (1.0 + reward_signal)
        
        weight_change = learning_rate * correlation
        
        weight_change -= self.decay_rate * current_weight
        
        new_weight = current_weight + weight_change
        new_weight = max(self.min_weight, min(self.max_weight, new_weight))
        
        self.metrics.total_updates += 1
        self.metrics.average_weight_change = (
            (self.metrics.average_weight_change * (self.metrics.total_updates - 1) + 
             abs(weight_change)) / self.metrics.total_updates
        )
        
        trace.last_update = time.time()
        
        return new_weight
    
    def apply_stdp(
        self,
        pre_neuron_id: str,
        post_neuron_id: str,
        pre_spike_time: float,
        post_spike_time: float,
        current_weight: float
    ) -> float:
        """
        Spike-Timing-Dependent Plasticity (STDP)
        
        If pre-neuron fires before post-neuron: strengthen (causation)
        If post-neuron fires before pre-neuron: weaken (no causation)
        """
        time_diff = post_spike_time - pre_spike_time
        
        tau_plus = 20.0
        tau_minus = 20.0
        A_plus = 0.01
        A_minus = 0.01
        
        if time_diff > 0:
            weight_change = A_plus * math.exp(-time_diff / tau_plus)
        else:
            weight_change = -A_minus * math.exp(time_diff / tau_minus)
        
        new_weight = current_weight + weight_change
        new_weight = max(self.min_weight, min(self.max_weight, new_weight))
        
        return new_weight
    
    def get_connection_strength(self, pre_neuron_id: str, post_neuron_id: str) -> float:
        """Get average correlation for a connection"""
        connection_key = (pre_neuron_id, post_neuron_id)
        
        if connection_key not in self.synaptic_traces:
            return 0.0
        
        trace = self.synaptic_traces[connection_key]
        if not trace.correlation_history:
            return 0.0
        
        recent_correlations = trace.correlation_history[-20:]
        return sum(recent_correlations) / len(recent_correlations)


class RewardSystem:
    """
    Implements reward-based learning
    
    Tracks outcomes and provides reward signals to strengthen/weaken connections
    """
    
    def __init__(self, discount_factor: float = 0.95):
        self.discount_factor = discount_factor
        self.reward_history: List[Tuple[float, float]] = []
        self.active_neurons_at_reward: Dict[float, List[str]] = {}
        self.neuron_rewards: Dict[str, List[float]] = {}
    
    def record_active_neurons(self, timestamp: float, active_neuron_ids: List[str]):
        """Record which neurons were active at this time"""
        self.active_neurons_at_reward[timestamp] = active_neuron_ids
    
    def provide_reward(self, reward_value: float, timestamp: Optional[float] = None):
        """
        Provide reward signal
        
        Positive reward: Strengthen connections that led to success
        Negative reward: Weaken connections that led to failure
        """
        if timestamp is None:
            timestamp = time.time()
        
        self.reward_history.append((timestamp, reward_value))
        
        recent_timestamps = [t for t, _ in self.reward_history[-10:]]
        
        for past_time in recent_timestamps:
            if past_time in self.active_neurons_at_reward:
                time_diff = timestamp - past_time
                discounted_reward = reward_value * (self.discount_factor ** time_diff)
                
                for neuron_id in self.active_neurons_at_reward[past_time]:
                    if neuron_id not in self.neuron_rewards:
                        self.neuron_rewards[neuron_id] = []
                    self.neuron_rewards[neuron_id].append(discounted_reward)
    
    def get_neuron_reward(self, neuron_id: str) -> float:
        """Get accumulated reward for a neuron"""
        if neuron_id not in self.neuron_rewards:
            return 0.0
        
        recent_rewards = self.neuron_rewards[neuron_id][-10:]
        if not recent_rewards:
            return 0.0
        
        return sum(recent_rewards) / len(recent_rewards)
    
    def clear_old_history(self, max_age: float = 300.0):
        """Clear old reward history"""
        current_time = time.time()
        
        self.reward_history = [
            (t, r) for t, r in self.reward_history
            if current_time - t < max_age
        ]
        
        self.active_neurons_at_reward = {
            t: neurons for t, neurons in self.active_neurons_at_reward.items()
            if current_time - t < max_age
        }


class SynapticPlasticity:
    """
    Manages long-term potentiation (LTP) and long-term depression (LTD)
    
    LTP: Persistent strengthening of connections
    LTD: Persistent weakening of connections
    """
    
    def __init__(
        self,
        ltp_threshold: float = 0.7,
        ltd_threshold: float = 0.3,
        consolidation_rate: float = 0.001
    ):
        self.ltp_threshold = ltp_threshold
        self.ltd_threshold = ltd_threshold
        self.consolidation_rate = consolidation_rate
        
        self.potentiated_connections: Dict[Tuple[str, str], float] = {}
        self.depressed_connections: Dict[Tuple[str, str], float] = {}
    
    def evaluate_plasticity(
        self,
        pre_neuron_id: str,
        post_neuron_id: str,
        correlation_strength: float,
        current_weight: float
    ) -> Tuple[float, str]:
        """
        Evaluate if connection should undergo LTP or LTD
        
        Returns:
            (new_weight, plasticity_type)
        """
        connection_key = (pre_neuron_id, post_neuron_id)
        
        if correlation_strength > self.ltp_threshold:
            if connection_key not in self.potentiated_connections:
                self.potentiated_connections[connection_key] = 0.0
            
            self.potentiated_connections[connection_key] += self.consolidation_rate
            
            potentiation = self.potentiated_connections[connection_key]
            new_weight = current_weight + potentiation
            new_weight = min(1.0, new_weight)
            
            return new_weight, "LTP"
        
        elif correlation_strength < self.ltd_threshold:
            if connection_key not in self.depressed_connections:
                self.depressed_connections[connection_key] = 0.0
            
            self.depressed_connections[connection_key] += self.consolidation_rate
            
            depression = self.depressed_connections[connection_key]
            new_weight = current_weight - depression
            new_weight = max(-1.0, new_weight)
            
            return new_weight, "LTD"
        
        return current_weight, "stable"
    
    def consolidate_memory(self, connection_key: Tuple[str, str]):
        """Make plasticity changes permanent"""
        if connection_key in self.potentiated_connections:
            self.potentiated_connections[connection_key] *= 1.1
        
        if connection_key in self.depressed_connections:
            self.depressed_connections[connection_key] *= 0.9


class MetaplasticitySystem:
    """
    Metaplasticity: Plasticity of plasticity
    
    Learning rates themselves adapt based on history
    """
    
    def __init__(self, base_learning_rate: float = 0.01):
        self.base_learning_rate = base_learning_rate
        self.neuron_learning_rates: Dict[str, float] = {}
        self.learning_success_history: Dict[str, deque] = {}
    
    def get_adaptive_learning_rate(self, neuron_id: str) -> float:
        """Get learning rate adapted to neuron's history"""
        if neuron_id not in self.neuron_learning_rates:
            self.neuron_learning_rates[neuron_id] = self.base_learning_rate
        
        return self.neuron_learning_rates[neuron_id]
    
    def update_learning_rate(self, neuron_id: str, learning_success: bool):
        """Adapt learning rate based on success"""
        if neuron_id not in self.learning_success_history:
            self.learning_success_history[neuron_id] = deque(maxlen=50)
        
        self.learning_success_history[neuron_id].append(1.0 if learning_success else 0.0)
        
        if len(self.learning_success_history[neuron_id]) >= 10:
            success_rate = sum(self.learning_success_history[neuron_id]) / len(
                self.learning_success_history[neuron_id]
            )
            
            if success_rate > 0.7:
                self.neuron_learning_rates[neuron_id] *= 1.05
            elif success_rate < 0.3:
                self.neuron_learning_rates[neuron_id] *= 0.95
            
            self.neuron_learning_rates[neuron_id] = max(
                0.001,
                min(0.1, self.neuron_learning_rates[neuron_id])
            )


class IntegratedLearningSystem:
    """
    Combines all learning mechanisms into unified system
    """
    
    def __init__(self):
        self.hebbian = HebbianLearning()
        self.reward = RewardSystem()
        self.plasticity = SynapticPlasticity()
        self.metaplasticity = MetaplasticitySystem()
        
        self.learning_enabled = True
        self.global_learning_rate = 1.0
    
    def update_connection_with_learning(
        self,
        pre_neuron_id: str,
        post_neuron_id: str,
        pre_activation: float,
        post_activation: float,
        current_weight: float,
        pre_spike_time: Optional[float] = None,
        post_spike_time: Optional[float] = None
    ) -> float:
        """Apply all learning mechanisms to update connection"""
        if not self.learning_enabled:
            return current_weight
        
        reward_signal = self.reward.get_neuron_reward(pre_neuron_id)
        
        new_weight = self.hebbian.update_connection(
            pre_neuron_id,
            post_neuron_id,
            pre_activation,
            post_activation,
            current_weight,
            reward_signal
        )
        
        if pre_spike_time is not None and post_spike_time is not None:
            new_weight = self.hebbian.apply_stdp(
                pre_neuron_id,
                post_neuron_id,
                pre_spike_time,
                post_spike_time,
                new_weight
            )
        
        correlation = self.hebbian.get_connection_strength(pre_neuron_id, post_neuron_id)
        new_weight, plasticity_type = self.plasticity.evaluate_plasticity(
            pre_neuron_id,
            post_neuron_id,
            correlation,
            new_weight
        )
        
        adaptive_lr = self.metaplasticity.get_adaptive_learning_rate(pre_neuron_id)
        new_weight = current_weight + (new_weight - current_weight) * adaptive_lr
        
        return new_weight
    
    def provide_feedback(self, success: bool, active_neurons: List[str], timestamp: Optional[float] = None):
        """Provide feedback on network performance"""
        if timestamp is None:
            timestamp = time.time()
        
        self.reward.record_active_neurons(timestamp, active_neurons)
        
        reward_value = 1.0 if success else -0.5
        self.reward.provide_reward(reward_value, timestamp)
        
        for neuron_id in active_neurons:
            self.metaplasticity.update_learning_rate(neuron_id, success)
    
    def get_learning_statistics(self) -> Dict[str, any]:
        """Get comprehensive learning statistics"""
        return {
            'hebbian_updates': self.hebbian.metrics.total_updates,
            'average_weight_change': self.hebbian.metrics.average_weight_change,
            'potentiated_connections': len(self.plasticity.potentiated_connections),
            'depressed_connections': len(self.plasticity.depressed_connections),
            'neurons_with_rewards': len(self.reward.neuron_rewards),
            'adaptive_learning_rates': len(self.metaplasticity.neuron_learning_rates),
            'global_learning_rate': self.global_learning_rate
        }
