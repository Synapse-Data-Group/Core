"""
CLM - Cognitive Language Model
core/state.py

Global cognitive state of the CLM system.
This is the "mind" at any given moment — what the system is currently
processing, what it remembers from this session, and how settled it is.

Unlike LLMs which are stateless between calls, CLM state persists
and evolves continuously. Every interaction changes it.
"""

from __future__ import annotations
import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from clm.core.signal import CognitiveSignal, ActivationVector, SignalType


class CognitiveMode(Enum):
    """
    What the system is currently doing.
    The loop transitions between these automatically.
    """
    IDLE         = "idle"          # No active processing
    PERCEIVING   = "perceiving"    # Receiving and grounding input
    PROCESSING   = "processing"    # Network activation propagating
    DELIBERATING = "deliberating"  # Contradiction detected, resolving
    CONSOLIDATING= "consolidating" # Writing experience to memory
    GENERATING   = "generating"    # Forming output
    REFLECTING   = "reflecting"    # Self-stimulated internal reasoning


class SettlementStatus(Enum):
    """
    Whether the network has reached a stable activation pattern.
    Output is only emitted when SETTLED.
    """
    UNSETTLED  = "unsettled"   # Still propagating, not ready
    SETTLING   = "settling"    # Converging
    SETTLED    = "settled"     # Stable — ready to generate output
    DIVERGING  = "diverging"   # Activation growing, not converging (problem)


@dataclass
class CognitiveState:
    """
    Complete snapshot of the CLM system's cognitive state at a moment in time.

    This is the central shared object. The cognitive loop reads and writes it.
    All layers (neurons, memory, reasoning, output) observe it.
    Thread-safe via internal lock.
    """

    # Current processing mode
    mode: CognitiveMode = CognitiveMode.IDLE
    settlement: SettlementStatus = SettlementStatus.UNSETTLED

    # Current activation pattern across the network
    activation: ActivationVector = field(default_factory=ActivationVector)

    # Signal queues
    input_queue:    List[CognitiveSignal] = field(default_factory=list)
    internal_queue: List[CognitiveSignal] = field(default_factory=list)  # self-generated
    output_queue:   List[CognitiveSignal] = field(default_factory=list)

    # Working context — what this conversation/session is about
    working_context: Dict[str, Any] = field(default_factory=dict)

    # Current session signals (short-term, cleared between conversations)
    session_signals: List[CognitiveSignal] = field(default_factory=list)

    # Confidence in current activation state [0.0, 1.0]
    confidence: float = 0.0

    # Cognitive load [0.0, 1.0] — mirrors CLM tool concept
    cognitive_load: float = 0.0

    # Contradiction flag — triggers deliberation mode
    contradiction_detected: bool = False
    contradiction_signals: List[CognitiveSignal] = field(default_factory=list)

    # Timing
    last_input_time:  float = 0.0
    last_output_time: float = 0.0
    session_start:    float = field(default_factory=time.time)

    # Iteration counter for this activation cycle
    propagation_steps: int = 0
    max_propagation_steps: int = 50

    # Internal lock for thread safety
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    def push_input(self, signal: CognitiveSignal):
        with self._lock:
            self.input_queue.append(signal)
            self.session_signals.append(signal)
            self.last_input_time = time.time()

    def push_internal(self, signal: CognitiveSignal):
        with self._lock:
            self.internal_queue.append(signal)

    def push_output(self, signal: CognitiveSignal):
        with self._lock:
            self.output_queue.append(signal)
            self.last_output_time = time.time()

    def pop_input(self) -> Optional[CognitiveSignal]:
        with self._lock:
            return self.input_queue.pop(0) if self.input_queue else None

    def pop_internal(self) -> Optional[CognitiveSignal]:
        with self._lock:
            return self.internal_queue.pop(0) if self.internal_queue else None

    def pop_output(self) -> Optional[CognitiveSignal]:
        with self._lock:
            return self.output_queue.pop(0) if self.output_queue else None

    def has_pending_input(self) -> bool:
        with self._lock:
            return len(self.input_queue) > 0

    def has_pending_output(self) -> bool:
        with self._lock:
            return len(self.output_queue) > 0

    def set_mode(self, mode: CognitiveMode):
        with self._lock:
            self.mode = mode

    def set_settlement(self, status: SettlementStatus):
        with self._lock:
            self.settlement = status

    def update_activation(self, new_activation: ActivationVector):
        with self._lock:
            # Compute settlement: compare with previous activation
            if self.activation.activations:
                prev = self.activation.activations
                curr = new_activation.activations
                all_keys = set(prev) | set(curr)
                if all_keys:
                    delta = sum(
                        abs(curr.get(k, 0.0) - prev.get(k, 0.0))
                        for k in all_keys
                    ) / len(all_keys)
                    new_activation.coherence = max(0.0, 1.0 - delta * 10)
                    if new_activation.coherence > 0.85:
                        self.settlement = SettlementStatus.SETTLED
                    elif new_activation.coherence > 0.5:
                        self.settlement = SettlementStatus.SETTLING
                    elif delta > 0.2:
                        self.settlement = SettlementStatus.DIVERGING
                    else:
                        self.settlement = SettlementStatus.UNSETTLED
            self.activation = new_activation
            self.confidence = new_activation.coherence

    def flag_contradiction(self, signals: List[CognitiveSignal]):
        with self._lock:
            self.contradiction_detected = True
            self.contradiction_signals = signals

    def clear_contradiction(self):
        with self._lock:
            self.contradiction_detected = False
            self.contradiction_signals = []

    def reset_propagation(self):
        with self._lock:
            self.propagation_steps = 0
            self.settlement = SettlementStatus.UNSETTLED

    def increment_propagation(self):
        with self._lock:
            self.propagation_steps += 1

    def is_propagation_exhausted(self) -> bool:
        with self._lock:
            return self.propagation_steps >= self.max_propagation_steps

    def clear_session(self):
        """Clear session-level state between conversations."""
        with self._lock:
            self.session_signals.clear()
            self.working_context.clear()
            self.input_queue.clear()
            self.internal_queue.clear()
            self.output_queue.clear()
            self.contradiction_detected = False
            self.contradiction_signals.clear()
            self.propagation_steps = 0
            self.settlement = SettlementStatus.UNSETTLED
            self.activation = ActivationVector()
            self.session_start = time.time()

    def snapshot(self) -> Dict[str, Any]:
        """Non-locking snapshot for monitoring/logging."""
        return {
            "mode":                  self.mode.value,
            "settlement":            self.settlement.value,
            "confidence":            round(self.confidence, 4),
            "cognitive_load":        round(self.cognitive_load, 4),
            "contradiction":         self.contradiction_detected,
            "active_neurons":        len(self.activation.activations),
            "mean_activation":       round(self.activation.mean_activation(), 4),
            "input_queue_depth":     len(self.input_queue),
            "internal_queue_depth":  len(self.internal_queue),
            "output_queue_depth":    len(self.output_queue),
            "propagation_steps":     self.propagation_steps,
            "session_signals":       len(self.session_signals),
        }
