"""
CLM - Cognitive Language Model
neurons/base.py

Base neuron — pure math, zero LLM calls during firing.
Neurons activate based on weighted input signals and a threshold.
Connections strengthen/weaken via Hebbian learning.

This is the fundamental departure from NEURON (tbn):
  NEURON: each ReasoningNeuron.fire() calls an LLM
  CLM:    neurons fire via activation math only
          LLM is only used at the grounding and output boundaries
"""

from __future__ import annotations
import math
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NeuronType(Enum):
    SENSORY     = "sensory"      # Receives grounded input signals
    ASSOCIATION = "association"  # Connects concepts, forms relationships
    MEMORY      = "memory"       # Stores and retrieves patterns
    INHIBITORY  = "inhibitory"   # Suppresses competing activations
    EXCITATORY  = "excitatory"   # Amplifies related activations
    META        = "meta"         # Monitors network health, spawns specialists
    SPECIALIST  = "specialist"   # Domain-specific, LLM-seeded once at creation
    OUTPUT      = "output"       # Translates activation state to output signal


@dataclass
class SynapticConnection:
    """
    Directed weighted connection between two neurons.
    Weight evolves via Hebbian learning: neurons that fire together wire together.
    """
    source_id:    str
    target_id:    str
    weight:       float = 0.5          # [-1.0, 1.0] negative = inhibitory
    last_updated: float = field(default_factory=time.time)
    fire_count:   int = 0              # How many times this connection transmitted

    def strengthen(self, amount: float = 0.01):
        """Hebbian potentiation."""
        self.weight = min(1.0, self.weight + amount)
        self.last_updated = time.time()
        self.fire_count += 1

    def weaken(self, amount: float = 0.005):
        """Synaptic depression — unused connections decay."""
        self.weight = max(-1.0, self.weight - amount)
        self.last_updated = time.time()

    def is_excitatory(self) -> bool:
        return self.weight > 0

    def is_inhibitory(self) -> bool:
        return self.weight < 0

    def age_seconds(self) -> float:
        return time.time() - self.last_updated


@dataclass
class NeuronState:
    activation:     float = 0.0
    last_fired:     float = 0.0
    fire_count:     int   = 0
    is_active:      bool  = False
    refractory:     bool  = False      # Cannot fire immediately after firing
    refractory_until: float = 0.0


class MicroNeuron(ABC):
    """
    Base class for all CLM neurons.

    Key design constraints:
    - fire() is pure math — no I/O, no LLM calls, no blocking
    - <1KB memory footprint per neuron
    - Sparse: only stores non-zero connections
    - Thread-safe activation (read-only state during propagation)
    """

    def __init__(
        self,
        neuron_id:   Optional[str] = None,
        neuron_type: NeuronType = NeuronType.ASSOCIATION,
        label:       str = "",
        threshold:   float = 0.5,
        decay_rate:  float = 0.05,     # Activation decays each tick if not stimulated
    ):
        self.id          = neuron_id or str(uuid.uuid4())
        self.type        = neuron_type
        self.label       = label       # Human-readable concept label (e.g. "dog", "fast")
        self.threshold   = threshold
        self.decay_rate  = decay_rate

        self.state       = NeuronState()
        self.connections: Dict[str, SynapticConnection] = {}  # target_id → connection
        self.incoming:    Dict[str, float] = {}               # source_id → last signal strength

        self.created_at  = time.time()
        self.last_active = time.time()
        self.metadata:   Dict[str, Any] = {}

        # Semantic feature vector — sparse, built up over time
        # Maps feature_name → weight. Empty in infancy.
        self.features:   Dict[str, float] = {}

    # ── Activation ────────────────────────────────────────────────────────────

    def receive(self, source_id: str, strength: float):
        """Receive an incoming signal from another neuron or grounding layer."""
        self.incoming[source_id] = strength
        self.last_active = time.time()

    def compute_activation(self) -> float:
        """
        Compute activation from weighted incoming signals.
        Uses sigmoid activation function.
        """
        if not self.incoming:
            # Passive decay
            self.state.activation = max(0.0, self.state.activation - self.decay_rate)
            return self.state.activation

        # Weighted sum of incoming signals via connections
        weighted_sum = 0.0
        for source_id, strength in self.incoming.items():
            # Find connection weight (default 0.5 if no explicit connection)
            conn = self.connections.get(source_id)
            weight = conn.weight if conn else 0.3
            weighted_sum += strength * weight

        self.state.activation = self._sigmoid(weighted_sum)
        return self.state.activation

    def should_fire(self) -> bool:
        """Threshold gate — only fire if activation exceeds threshold."""
        now = time.time()
        if self.state.refractory and now < self.state.refractory_until:
            return False
        return self.state.activation >= self.threshold

    @abstractmethod
    def fire(self) -> Dict[str, Any]:
        """
        Execute neuron's function. Must be pure math — no I/O.
        Returns output dict passed to connected neurons.
        """
        pass

    def post_fire(self, refractory_ms: float = 50.0):
        """Update state after firing."""
        self.state.fire_count += 1
        self.state.last_fired = time.time()
        self.state.is_active = True
        self.state.refractory = True
        self.state.refractory_until = time.time() + (refractory_ms / 1000.0)
        self.incoming.clear()

    def tick_decay(self):
        """Called each network tick to decay activation."""
        if not self.state.is_active:
            self.state.activation = max(0.0, self.state.activation - self.decay_rate)
        self.state.is_active = False
        now = time.time()
        if self.state.refractory and now >= self.state.refractory_until:
            self.state.refractory = False

    # ── Connections ───────────────────────────────────────────────────────────

    def connect_to(self, target_id: str, weight: float = 0.5):
        """Add or update outgoing connection."""
        if target_id in self.connections:
            self.connections[target_id].weight = weight
        else:
            self.connections[target_id] = SynapticConnection(
                source_id=self.id,
                target_id=target_id,
                weight=weight,
            )

    def strengthen_connection(self, target_id: str, amount: float = 0.01):
        if target_id in self.connections:
            self.connections[target_id].strengthen(amount)

    def weaken_connection(self, target_id: str, amount: float = 0.005):
        if target_id in self.connections:
            self.connections[target_id].weaken(amount)

    def get_output_targets(self) -> List[str]:
        """Return target neuron IDs for signal propagation."""
        return [
            tid for tid, conn in self.connections.items()
            if conn.weight > 0.05  # Only propagate through meaningful connections
        ]

    def prune_weak_connections(self, threshold: float = 0.05):
        """Remove connections that have decayed below threshold."""
        to_remove = [
            tid for tid, conn in self.connections.items()
            if abs(conn.weight) < threshold
        ]
        for tid in to_remove:
            del self.connections[tid]

    # ── Features ──────────────────────────────────────────────────────────────

    def update_feature(self, feature: str, value: float):
        """Update semantic feature. Features accumulate over experience."""
        current = self.features.get(feature, 0.0)
        # Exponential moving average — recent experience weighted more
        self.features[feature] = 0.8 * current + 0.2 * value

    def feature_similarity(self, other: "MicroNeuron") -> float:
        """Cosine similarity between feature vectors."""
        if not self.features or not other.features:
            return 0.0
        common = set(self.features) & set(other.features)
        if not common:
            return 0.0
        dot = sum(self.features[k] * other.features[k] for k in common)
        mag_a = math.sqrt(sum(v ** 2 for v in self.features.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in other.features.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _sigmoid(self, x: float) -> float:
        try:
            return 1.0 / (1.0 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0

    def memory_bytes(self) -> int:
        """Rough memory footprint estimate."""
        import sys
        return (
            sys.getsizeof(self.__dict__)
            + sys.getsizeof(self.connections)
            + sys.getsizeof(self.features)
            + sys.getsizeof(self.incoming)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":          self.id,
            "type":        self.type.value,
            "label":       self.label,
            "threshold":   self.threshold,
            "activation":  round(self.state.activation, 4),
            "fire_count":  self.state.fire_count,
            "connections": len(self.connections),
            "features":    len(self.features),
            "last_active": self.last_active,
        }


# ── Concrete neuron types ─────────────────────────────────────────────────────

class SensoryNeuron(MicroNeuron):
    """
    Entry point for grounded signals.
    Receives activation directly from the grounding layer.
    One sensory neuron per concept token in the grounded signal.
    """
    def __init__(self, neuron_id: Optional[str] = None, label: str = ""):
        super().__init__(neuron_id, NeuronType.SENSORY, label, threshold=0.1)

    def fire(self) -> Dict[str, Any]:
        self.post_fire()
        return {
            "neuron_id": self.id,
            "type":      "sensory",
            "label":     self.label,
            "strength":  self.state.activation,
        }


class AssociationNeuron(MicroNeuron):
    """
    Forms and strengthens associations between concepts.
    The bulk of the network — these are what grow with experience.
    """
    def __init__(self, neuron_id: Optional[str] = None, label: str = ""):
        super().__init__(neuron_id, NeuronType.ASSOCIATION, label, threshold=0.5)

    def fire(self) -> Dict[str, Any]:
        self.post_fire()
        return {
            "neuron_id": self.id,
            "type":      "association",
            "label":     self.label,
            "strength":  self.state.activation,
            "features":  dict(list(self.features.items())[:5]),  # Top 5 features
        }


class MemoryNeuron(MicroNeuron):
    """
    Stores activation patterns for later recall.
    Lower threshold — activates easily to surface memories.
    """
    def __init__(self, neuron_id: Optional[str] = None, label: str = ""):
        super().__init__(neuron_id, NeuronType.MEMORY, label, threshold=0.3, decay_rate=0.01)
        self.stored_patterns: List[Dict[str, Any]] = []

    def store(self, pattern: Dict[str, Any]):
        pattern["stored_at"] = time.time()
        self.stored_patterns.append(pattern)
        if len(self.stored_patterns) > 100:
            self.stored_patterns.pop(0)

    def fire(self) -> Dict[str, Any]:
        self.post_fire()
        recent = self.stored_patterns[-3:] if self.stored_patterns else []
        return {
            "neuron_id": self.id,
            "type":      "memory",
            "label":     self.label,
            "strength":  self.state.activation,
            "patterns":  recent,
        }


class InhibitoryNeuron(MicroNeuron):
    """
    Suppresses competing activations.
    Critical for preventing runaway excitation and enforcing selectivity.
    """
    def __init__(self, neuron_id: Optional[str] = None, label: str = ""):
        super().__init__(neuron_id, NeuronType.INHIBITORY, label, threshold=0.4)

    def fire(self) -> Dict[str, Any]:
        self.post_fire()
        return {
            "neuron_id": self.id,
            "type":      "inhibitory",
            "label":     self.label,
            "strength":  -self.state.activation,  # Negative — suppresses targets
        }


class OutputNeuron(MicroNeuron):
    """
    Collects and integrates activation from the network.
    The output generator reads these to form responses.
    """
    def __init__(self, neuron_id: Optional[str] = None, label: str = ""):
        super().__init__(neuron_id, NeuronType.OUTPUT, label, threshold=0.35, decay_rate=0.02)
        self.output_history: List[Dict[str, Any]] = []

    def fire(self) -> Dict[str, Any]:
        self.post_fire()
        result = {
            "neuron_id": self.id,
            "type":      "output",
            "label":     self.label,
            "strength":  self.state.activation,
            "features":  self.features.copy(),
        }
        self.output_history.append(result)
        if len(self.output_history) > 50:
            self.output_history.pop(0)
        return result
