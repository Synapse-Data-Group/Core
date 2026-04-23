"""
CLM - Cognitive Language Model
core/signal.py

Internal signal and activation types that flow through the cognitive system.
These are the fundamental units of information — not tokens, not embeddings,
but structured cognitive signals with source, strength, type, and context.
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SignalType(Enum):
    """Types of signals that flow through the cognitive network."""
    PERCEPTUAL   = "perceptual"    # Raw input from environment/user
    SEMANTIC     = "semantic"      # Meaning-bearing signal
    MNEMONIC     = "mnemonic"      # Memory retrieval signal
    AFFECTIVE    = "affective"     # Confidence / uncertainty signal
    MOTOR        = "motor"         # Output-directed signal
    REFLEXIVE    = "reflexive"     # Self-generated (internal monologue)
    INHIBITORY   = "inhibitory"    # Suppresses other activations
    EXCITATORY   = "excitatory"    # Amplifies other activations


class SignalOrigin(Enum):
    """Where the signal originated."""
    EXTERNAL     = "external"      # From user / environment
    MEMORY       = "memory"        # From memory retrieval
    NETWORK      = "network"       # From another neuron
    GROUNDING    = "grounding"     # From grounding layer (LLM or internal)
    SELF         = "self"          # Self-generated (reflection, output feedback)


@dataclass
class CognitiveSignal:
    """
    Fundamental unit of information in the CLM system.

    A signal carries meaning, strength, type, and provenance.
    It is not a token. It is not a vector. It is a structured
    cognitive event that perturbs the network state.
    """
    signal_id:   str        = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: SignalType = SignalType.PERCEPTUAL
    origin:      SignalOrigin = SignalOrigin.EXTERNAL

    # Core content
    content:     str        = ""           # Human-readable content
    strength:    float      = 1.0          # Activation strength [0.0, 1.0]
    valence:     float      = 0.0          # Positive/negative [-1.0, 1.0]
    confidence:  float      = 1.0          # How certain is the source [0.0, 1.0]

    # Semantic features — sparse key-value representation
    # Built up over time as the system learns. Empty in infancy.
    features:    Dict[str, float] = field(default_factory=dict)

    # Provenance
    source_id:   Optional[str] = None      # Neuron or component that emitted this
    parent_id:   Optional[str] = None      # Signal that caused this one (for tracing)
    timestamp:   float = field(default_factory=time.time)

    # Routing
    target_ids:  List[str] = field(default_factory=list)  # Specific targets (empty = broadcast)
    ttl:         int = 10                  # Time-to-live in propagation hops

    # Metadata
    metadata:    Dict[str, Any] = field(default_factory=dict)

    def decay(self, factor: float = 0.9) -> "CognitiveSignal":
        """Return a decayed copy of this signal (for propagation)."""
        return CognitiveSignal(
            signal_id=str(uuid.uuid4()),
            signal_type=self.signal_type,
            origin=SignalOrigin.NETWORK,
            content=self.content,
            strength=self.strength * factor,
            valence=self.valence,
            confidence=self.confidence * factor,
            features=self.features.copy(),
            source_id=self.signal_id,
            parent_id=self.parent_id or self.signal_id,
            timestamp=time.time(),
            target_ids=[],
            ttl=self.ttl - 1,
            metadata=self.metadata.copy(),
        )

    def is_alive(self) -> bool:
        """Signal is still propagating."""
        return self.ttl > 0 and self.strength > 0.01

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id":   self.signal_id,
            "signal_type": self.signal_type.value,
            "origin":      self.origin.value,
            "content":     self.content,
            "strength":    round(self.strength, 4),
            "valence":     round(self.valence, 4),
            "confidence":  round(self.confidence, 4),
            "features":    {k: round(v, 4) for k, v in self.features.items()},
            "source_id":   self.source_id,
            "timestamp":   self.timestamp,
            "ttl":         self.ttl,
        }


@dataclass
class ActivationVector:
    """
    Sparse representation of network activation state.

    Maps neuron_id → activation_strength.
    Used to represent what the network is currently "thinking about."
    Sparse by design — only active neurons are stored.
    """
    activations: Dict[str, float] = field(default_factory=dict)
    timestamp:   float = field(default_factory=time.time)
    coherence:   float = 0.0   # How settled/stable is this activation pattern [0,1]
    source_signal_id: Optional[str] = None

    def top_k(self, k: int = 10) -> List[tuple]:
        """Return top-k most activated neurons."""
        sorted_items = sorted(self.activations.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:k]

    def mean_activation(self) -> float:
        if not self.activations:
            return 0.0
        return sum(self.activations.values()) / len(self.activations)

    def sparsity(self) -> float:
        """Fraction of neurons that are inactive (0.0 activation)."""
        if not self.activations:
            return 1.0
        active = sum(1 for v in self.activations.values() if v > 0.01)
        return 1.0 - (active / len(self.activations))

    def merge(self, other: "ActivationVector", weight: float = 0.5) -> "ActivationVector":
        """Blend two activation vectors."""
        merged = {}
        all_keys = set(self.activations) | set(other.activations)
        for k in all_keys:
            a = self.activations.get(k, 0.0)
            b = other.activations.get(k, 0.0)
            merged[k] = a * (1 - weight) + b * weight
        return ActivationVector(
            activations=merged,
            timestamp=time.time(),
            coherence=(self.coherence + other.coherence) / 2,
        )
