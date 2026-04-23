"""
CLM - Cognitive Language Model
reasoning/contradiction.py

Contradiction detection and resolution.
When the network activates conflicting patterns simultaneously,
this module detects the conflict and resolves it through
internal deliberation — no LLM needed.

Example contradictions:
- "safe" and "dangerous" both highly activated
- "yes" and "no" both strongly present
- Valence conflict: strong positive AND strong negative signals
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal, ActivationVector
    from clm.neurons.base import MicroNeuron
    from clm.memory.semantic import SemanticMemory

logger = logging.getLogger(__name__)

# Antonym pairs — built-in minimal knowledge
# The system will expand this through experience
_ANTONYM_PAIRS = [
    ("yes", "no"), ("true", "false"), ("good", "bad"),
    ("safe", "dangerous"), ("fast", "slow"), ("hot", "cold"),
    ("up", "down"), ("left", "right"), ("open", "closed"),
    ("start", "stop"), ("add", "remove"), ("increase", "decrease"),
    ("positive", "negative"), ("agree", "disagree"),
    ("correct", "incorrect"), ("success", "failure"),
    ("love", "hate"), ("happy", "sad"), ("light", "dark"),
    ("strong", "weak"), ("big", "small"), ("new", "old"),
]

# Build bidirectional lookup
_ANTONYM_MAP: Dict[str, str] = {}
for a, b in _ANTONYM_PAIRS:
    _ANTONYM_MAP[a] = b
    _ANTONYM_MAP[b] = a


@dataclass
class ContradictionReport:
    detected:       bool
    conflict_pairs: List[tuple]   # [(label_a, label_b, strength_a, strength_b)]
    valence_conflict: bool
    severity:       float         # 0.0 = no conflict, 1.0 = severe


class ContradictionDetector:
    """
    Detects and resolves activation contradictions in the network.

    Detection methods:
    1. Antonym co-activation: known antonyms both strongly active
    2. Valence conflict: strong positive AND negative signals simultaneously
    3. Feature opposition: features with negative correlation both active

    Resolution:
    - Inhibit the weaker of the conflicting pair
    - Emit a resolution signal that re-enters the network
    - Log the contradiction for semantic memory
    """

    def __init__(
        self,
        activation_threshold: float = 0.5,   # Min activation to consider conflicting
        severity_threshold:   float = 0.3,   # Min severity to flag as contradiction
    ):
        self.activation_threshold = activation_threshold
        self.severity_threshold   = severity_threshold
        self._contradiction_count = 0

    def detect(
        self,
        activation: "ActivationVector",
        active_neurons: List["MicroNeuron"],
    ) -> List["CognitiveSignal"]:
        """
        Detect contradictions in current activation state.
        Returns list of conflicting signals (empty if no contradiction).
        """
        if not active_neurons:
            return []

        report = self._analyze(activation, active_neurons)

        if not report.detected or report.severity < self.severity_threshold:
            return []

        self._contradiction_count += 1
        logger.debug(
            f"Contradiction detected (severity={report.severity:.2f}): "
            f"{report.conflict_pairs}"
        )

        # Convert conflict pairs to signals
        from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin
        signals = []
        for label_a, label_b, str_a, str_b in report.conflict_pairs:
            signals.append(CognitiveSignal(
                signal_type=SignalType.AFFECTIVE,
                origin=SignalOrigin.NETWORK,
                content=f"Conflict: {label_a} vs {label_b}",
                strength=report.severity,
                confidence=0.6,
                metadata={
                    "label_a": label_a, "strength_a": str_a,
                    "label_b": label_b, "strength_b": str_b,
                    "type": "antonym_conflict",
                },
            ))

        if report.valence_conflict:
            signals.append(CognitiveSignal(
                signal_type=SignalType.AFFECTIVE,
                origin=SignalOrigin.NETWORK,
                content="Valence conflict: simultaneous positive and negative activation",
                strength=report.severity * 0.8,
                confidence=0.5,
                metadata={"type": "valence_conflict"},
            ))

        return signals

    def resolve(
        self,
        signals: List["CognitiveSignal"],
        activation: "ActivationVector",
        semantic_memory: "SemanticMemory",
    ) -> Optional["CognitiveSignal"]:
        """
        Resolve detected contradictions.
        Returns a resolution signal to inject back into the network.
        """
        if not signals:
            return None

        # Strategy: pick the interpretation with more semantic support
        # Check semantic memory for which side has more evidence
        resolution_content = self._find_resolution(signals, semantic_memory)

        from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin
        return CognitiveSignal(
            signal_type=SignalType.SEMANTIC,
            origin=SignalOrigin.NETWORK,
            content=resolution_content,
            strength=0.6,
            confidence=0.55,
            metadata={"type": "contradiction_resolution"},
        )

    def _analyze(
        self,
        activation: "ActivationVector",
        active_neurons: List["MicroNeuron"],
    ) -> ContradictionReport:
        """Analyze active neurons for contradictions."""
        # Build label → activation map for active neurons
        label_activation: Dict[str, float] = {}
        for neuron in active_neurons:
            if neuron.label and neuron.state.activation >= self.activation_threshold:
                label_activation[neuron.label.lower()] = neuron.state.activation

        conflict_pairs = []
        for label, strength in label_activation.items():
            antonym = _ANTONYM_MAP.get(label)
            if antonym and antonym in label_activation:
                antonym_strength = label_activation[antonym]
                # Only flag if both are meaningfully active
                if strength >= self.activation_threshold and antonym_strength >= self.activation_threshold:
                    conflict_pairs.append((label, antonym, strength, antonym_strength))

        # Deduplicate pairs
        seen = set()
        unique_pairs = []
        for pair in conflict_pairs:
            key = tuple(sorted([pair[0], pair[1]]))
            if key not in seen:
                seen.add(key)
                unique_pairs.append(pair)

        # Valence conflict: check if signals have both strong positive and negative
        valences = [
            n.features.get("valence", 0.0)
            for n in active_neurons
            if n.state.activation >= self.activation_threshold
        ]
        pos_sum = sum(v for v in valences if v > 0.3)
        neg_sum = sum(abs(v) for v in valences if v < -0.3)
        valence_conflict = pos_sum > 0.5 and neg_sum > 0.5

        severity = 0.0
        if unique_pairs:
            avg_conflict = sum(
                min(p[2], p[3]) for p in unique_pairs
            ) / len(unique_pairs)
            severity = max(severity, avg_conflict)
        if valence_conflict:
            severity = max(severity, min(pos_sum, neg_sum) / max(pos_sum + neg_sum, 1))

        return ContradictionReport(
            detected=bool(unique_pairs) or valence_conflict,
            conflict_pairs=unique_pairs,
            valence_conflict=valence_conflict,
            severity=min(1.0, severity),
        )

    def _find_resolution(
        self,
        signals: List["CognitiveSignal"],
        semantic_memory: "SemanticMemory",
    ) -> str:
        """Find resolution content from semantic memory."""
        # Collect all mentioned labels
        labels = []
        for sig in signals:
            meta = sig.metadata
            if "label_a" in meta:
                labels.extend([meta["label_a"], meta["label_b"]])

        if not labels:
            return "Contradiction detected — maintaining uncertainty"

        # Query semantic memory for context
        query = " ".join(labels)
        insights = semantic_memory.get_relevant_insights(query, k=3)

        if insights:
            # Use most confident insight as resolution guide
            best = max(insights, key=lambda x: x.get("confidence", 0))
            return f"Resolving via memory: {best.get('content', query)}"

        # No memory — default to uncertainty acknowledgment
        return f"Conflicting signals ({', '.join(labels[:4])}) — holding ambiguity"

    def get_stats(self) -> Dict[str, Any]:
        return {"contradiction_count": self._contradiction_count}
