"""
CLM - Cognitive Language Model
reasoning/metacognition.py

Metacognition — the system's ability to assess its own cognitive state
before committing to output.

"Should I respond now, or do I need more processing?"
"Am I confident enough in this activation pattern?"
"Am I overloaded?"

This is the output gate. Nothing leaves the system without passing
through metacognition first.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal, ActivationVector


@dataclass
class OutputGate:
    """Decision from metacognition about whether to emit output."""
    should_output: bool
    reason:        str          # Why this decision was made
    confidence:    float        # Confidence in the decision
    suggested_action: str       # "output" | "wait" | "clarify" | "shed_load"


class Metacognition:
    """
    The system's self-monitoring layer.

    Mirrors the Cognitive Load Monitor (CLM tool) concept but applied
    internally — the system monitors its own processing state and
    decides when it is ready to respond.

    Checks:
    1. Confidence threshold — is activation settled enough?
    2. Cognitive load — is the system overloaded?
    3. Coherence — is the activation pattern stable?
    4. Minimum content — is there enough to say something meaningful?
    5. Uncertainty — are there too many unresolved signals?
    """

    def __init__(
        self,
        min_confidence:       float = 0.55,
        max_cognitive_load:   float = 0.85,
        min_active_neurons:   int   = 3,
        min_coherence:        float = 0.4,
        max_uncertainty:      float = 0.7,
    ):
        self.min_confidence     = min_confidence
        self.max_cognitive_load = max_cognitive_load
        self.min_active_neurons = min_active_neurons
        self.min_coherence      = min_coherence
        self.max_uncertainty    = max_uncertainty

        self._gate_count        = 0
        self._blocked_count     = 0
        self._overload_count    = 0

    def should_output(
        self,
        activation:      "ActivationVector",
        confidence:      float,
        cognitive_load:  float,
        session_signals: List["CognitiveSignal"],
    ) -> OutputGate:
        """
        Evaluate whether the system is ready to generate output.
        Returns an OutputGate decision.
        """
        self._gate_count += 1

        # ── Check 1: Cognitive overload
        if cognitive_load > self.max_cognitive_load:
            self._blocked_count += 1
            self._overload_count += 1
            return OutputGate(
                should_output=False,
                reason="overloaded",
                confidence=confidence,
                suggested_action="shed_load",
            )

        # ── Check 2: Minimum active neurons
        active_count = len([
            v for v in activation.activations.values() if v > 0.1
        ])
        if active_count < self.min_active_neurons:
            self._blocked_count += 1
            return OutputGate(
                should_output=False,
                reason="insufficient_activation",
                confidence=confidence,
                suggested_action="wait",
            )

        # ── Check 3: Coherence
        if activation.coherence < self.min_coherence:
            self._blocked_count += 1
            return OutputGate(
                should_output=False,
                reason="low_coherence",
                confidence=confidence,
                suggested_action="wait",
            )

        # ── Check 4: Confidence threshold
        if confidence < self.min_confidence:
            self._blocked_count += 1
            # If very low confidence and we have session signals, ask for clarification
            if confidence < 0.3 and session_signals:
                return OutputGate(
                    should_output=False,
                    reason="very_low_confidence",
                    confidence=confidence,
                    suggested_action="clarify",
                )
            return OutputGate(
                should_output=False,
                reason="low_confidence",
                confidence=confidence,
                suggested_action="wait",
            )

        # ── Check 5: Uncertainty from session signals
        uncertainty = self._compute_uncertainty(session_signals)
        if uncertainty > self.max_uncertainty:
            self._blocked_count += 1
            return OutputGate(
                should_output=False,
                reason="high_uncertainty",
                confidence=confidence,
                suggested_action="clarify",
            )

        # ── All checks passed — ready to output
        return OutputGate(
            should_output=True,
            reason="ready",
            confidence=confidence,
            suggested_action="output",
        )

    def _compute_uncertainty(self, session_signals: List["CognitiveSignal"]) -> float:
        """
        Estimate uncertainty from session signals.
        High uncertainty = many low-confidence signals, or question-heavy session.
        """
        if not session_signals:
            return 0.0

        confidences = [s.confidence for s in session_signals[-10:]]
        avg_confidence = sum(confidences) / len(confidences)

        # Count question signals (uncertainty markers)
        question_count = sum(
            1 for s in session_signals[-10:]
            if s.metadata.get("intent") == "question"
        )
        question_ratio = question_count / len(session_signals[-10:])

        uncertainty = (1.0 - avg_confidence) * 0.6 + question_ratio * 0.4
        return min(1.0, uncertainty)

    def get_stats(self) -> Dict[str, Any]:
        block_rate = self._blocked_count / max(self._gate_count, 1)
        return {
            "gate_count":    self._gate_count,
            "blocked_count": self._blocked_count,
            "overload_count": self._overload_count,
            "block_rate":    round(block_rate, 4),
        }
