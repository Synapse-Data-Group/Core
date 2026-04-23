"""
CLM - Cognitive Language Model
neurons/hebbian.py

Tri-factor learning engine.

Pure Hebbian learning (cofire only) is insufficient for high-level cognition.
It memorizes correlations but fails at abstraction, causal inference,
and compositional reasoning. This has been demonstrated repeatedly since the 1980s.

Tri-factor rule:
    Δw = cofire × surprise × value

Where:
    cofire   = Hebbian association (neurons fire together)
    surprise = prediction error (how unexpected was this activation?)
    value    = usefulness signal (did this lead to a good outcome?)

This mirrors:
    - Dopamine-modulated synaptic plasticity (neuromodulation)
    - Predictive coding (error-driven learning)
    - Reinforcement-modulated Hebbian learning

The result: the network learns not just what co-occurs,
but what matters and what was unexpected.
That distinction is the difference between correlation and understanding.
"""

from __future__ import annotations
import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.neurons.base import MicroNeuron
    from clm.core.signal import ActivationVector


@dataclass
class PredictionRecord:
    """
    Tracks a neuron's prediction about what should activate next.
    Used to compute surprise (prediction error).
    """
    neuron_id:        str
    predicted_targets: Dict[str, float]   # target_id → predicted activation
    actual_targets:    Dict[str, float]   # filled in after activation
    timestamp:         float = field(default_factory=time.time)
    resolved:          bool  = False

    def compute_error(self) -> float:
        """
        Mean squared prediction error across predicted targets.
        High error = high surprise = stronger learning signal.
        """
        if not self.predicted_targets:
            return 0.5   # No prediction = moderate surprise
        errors = []
        for target_id, predicted in self.predicted_targets.items():
            actual = self.actual_targets.get(target_id, 0.0)
            errors.append((predicted - actual) ** 2)
        return math.sqrt(sum(errors) / len(errors)) if errors else 0.0


class TriFactorLearner:
    """
    Tri-factor synaptic plasticity engine.

    Δw = η × cofire × surprise × value

    Factor 1 — cofire (Hebbian):
        Standard co-activation. Neurons that fire together.
        Range: [0, 1]

    Factor 2 — surprise (prediction error):
        How unexpected was this activation pattern?
        Computed as deviation from the neuron's running prediction.
        High surprise → stronger weight update (learn from the unexpected).
        Low surprise → weak update (already knew this).
        Range: [0, 1]

    Factor 3 — value (usefulness signal):
        Was this activation pattern useful?
        Injected externally when the system gets feedback
        (e.g., user confirms response was correct, output was coherent).
        Defaults to 0.5 (neutral) when no feedback available.
        Range: [0, 1]

    Additional mechanisms:
        - Synaptic decay (unused connections weaken)
        - Homeostatic scaling (prevents runaway excitation)
        - Prediction tracking (each neuron maintains activation predictions)
        - Structured replay (periodically re-activates important patterns)
    """

    def __init__(
        self,
        base_lr:           float = 0.02,    # Base learning rate η
        surprise_weight:   float = 0.6,     # How much surprise amplifies learning
        value_weight:      float = 0.4,     # How much value signal amplifies learning
        ltd_rate:          float = 0.004,   # Long-term depression rate
        decay_rate:        float = 0.001,   # Per-tick connection decay
        decay_interval_s:  float = 60.0,
        homeostatic_ceil:  float = 3.0,
        min_weight:        float = 0.05,
        feature_lr:        float = 0.04,
        prediction_window: int   = 5,       # How many past activations to predict from
    ):
        self.base_lr           = base_lr
        self.surprise_weight   = surprise_weight
        self.value_weight      = value_weight
        self.ltd_rate          = ltd_rate
        self.decay_rate        = decay_rate
        self.decay_interval_s  = decay_interval_s
        self.homeostatic_ceil  = homeostatic_ceil
        self.min_weight        = min_weight
        self.feature_lr        = feature_lr
        self.prediction_window = prediction_window

        # Per-neuron activation history for prediction
        self._activation_history: Dict[str, deque] = {}

        # Per-neuron running predictions
        self._predictions: Dict[str, PredictionRecord] = {}

        # Global value signal — injected by feedback system
        # Default 0.5 = neutral. 1.0 = very useful. 0.0 = useless/harmful.
        self._current_value: float = 0.5
        self._value_history: deque = deque(maxlen=100)

        # Replay buffer — stores important activation patterns for consolidation
        self._replay_buffer: deque = deque(maxlen=200)

        self._update_count = 0

    # ── Public interface ──────────────────────────────────────────────────────

    def inject_value_signal(self, value: float):
        """
        Inject a value/usefulness signal from external feedback.
        Call this when the system gets feedback that its output was
        correct (value=1.0), neutral (value=0.5), or wrong (value=0.0).
        This is the neuromodulation channel — equivalent to dopamine.
        """
        value = max(0.0, min(1.0, value))
        self._current_value = value
        self._value_history.append((time.time(), value))

    def update(
        self,
        neurons: Dict[str, "MicroNeuron"],
        fired_ids: Set[str],
        activation: "ActivationVector",
    ):
        """
        Apply tri-factor learning for one activation cycle.

        Δw = η × cofire × surprise × value

        Args:
            neurons:    All neurons in the network
            fired_ids:  Set of neuron IDs that fired this cycle
            activation: Current activation vector
        """
        self._update_count += 1

        # 1. Resolve predictions from previous cycle → compute surprise
        surprise_map = self._resolve_predictions(neurons, fired_ids, activation)

        # 2. Tri-factor weight updates
        self._apply_trifactor(neurons, fired_ids, activation, surprise_map)

        # 3. Update predictions for next cycle
        self._update_predictions(neurons, fired_ids, activation)

        # 4. Feature vector sharing (semantic association)
        self._update_features(neurons, fired_ids, activation)

        # 5. Store important patterns in replay buffer
        if len(fired_ids) > 3:
            self._replay_buffer.append({
                "fired_ids": set(fired_ids),
                "activation_snapshot": dict(list(activation.activations.items())[:20]),
                "value": self._current_value,
                "timestamp": time.time(),
            })

        # 6. Periodic maintenance
        if self._update_count % 100 == 0:
            self._apply_decay(neurons)
        if self._update_count % 50 == 0:
            self._apply_homeostasis(neurons)
        if self._update_count % 200 == 0:
            self._prune(neurons)

        # 7. Structured replay — consolidate important patterns
        if self._update_count % 500 == 0:
            self._structured_replay(neurons)

    def replay_with_feedback(
        self,
        neurons: Dict[str, "MicroNeuron"],
        value: float,
    ):
        """
        Replay recent activation patterns with a value signal.
        Called after feedback is received to retroactively strengthen
        or weaken the patterns that led to the outcome.
        This is the consolidation mechanism — equivalent to sleep replay.
        """
        self.inject_value_signal(value)
        recent = list(self._replay_buffer)[-10:]
        for pattern in recent:
            fired_ids = pattern["fired_ids"]
            # Replay strengthening: apply value signal to stored patterns
            for nid in fired_ids:
                neuron = neurons.get(nid)
                if neuron is None:
                    continue
                for target_id, conn in neuron.connections.items():
                    if target_id in fired_ids:
                        # Reinforce if value > 0.5, weaken if value < 0.5
                        delta = (value - 0.5) * self.base_lr * 0.5
                        if delta > 0:
                            conn.strengthen(delta)
                        else:
                            conn.weaken(abs(delta))

    # ── Tri-factor core ───────────────────────────────────────────────────────

    def _apply_trifactor(
        self,
        neurons: Dict[str, "MicroNeuron"],
        fired_ids: Set[str],
        activation: "ActivationVector",
        surprise_map: Dict[str, float],
    ):
        """
        Core tri-factor update: Δw = η × cofire × surprise × value
        """
        value = self._current_value

        for nid in fired_ids:
            neuron = neurons.get(nid)
            if neuron is None:
                continue

            surprise = surprise_map.get(nid, 0.5)
            a_strength = activation.activations.get(nid, 0.5)

            for target_id, conn in neuron.connections.items():
                if target_id in fired_ids:
                    # ── LTP path: both fired
                    b_strength = activation.activations.get(target_id, 0.5)

                    # Factor 1: cofire (Hebbian)
                    cofire = a_strength * b_strength

                    # Factor 2: surprise (prediction error — amplifies learning)
                    # High surprise = learn more. Low surprise = already knew this.
                    surprise_factor = 1.0 + self.surprise_weight * surprise

                    # Factor 3: value (usefulness — gates whether to strengthen)
                    # value > 0.5: strengthen. value < 0.5: weaken even on cofire.
                    value_factor = value

                    delta = self.base_lr * cofire * surprise_factor * value_factor
                    conn.strengthen(delta)

                else:
                    # ── LTD path: A fired, B didn't
                    # Modulate depression by value: if outcome was bad,
                    # depress more aggressively (this path was wrong)
                    depression = self.ltd_rate * (1.0 + (1.0 - value) * self.value_weight)
                    conn.weaken(depression)

    # ── Prediction tracking ───────────────────────────────────────────────────

    def _update_predictions(
        self,
        neurons: Dict[str, "MicroNeuron"],
        fired_ids: Set[str],
        activation: "ActivationVector",
    ):
        """
        Each fired neuron predicts what its targets will activate to next cycle.
        Prediction = weighted sum of connection weights × current activation.
        """
        for nid in fired_ids:
            neuron = neurons.get(nid)
            if neuron is None:
                continue

            predicted: Dict[str, float] = {}
            for target_id, conn in neuron.connections.items():
                if conn.weight > 0.1:
                    current_act = activation.activations.get(nid, 0.5)
                    predicted[target_id] = min(1.0, current_act * conn.weight)

            self._predictions[nid] = PredictionRecord(
                neuron_id=nid,
                predicted_targets=predicted,
                actual_targets={},
            )

            # Update activation history
            if nid not in self._activation_history:
                self._activation_history[nid] = deque(maxlen=self.prediction_window)
            self._activation_history[nid].append(
                activation.activations.get(nid, 0.0)
            )

    def _resolve_predictions(
        self,
        neurons: Dict[str, "MicroNeuron"],
        fired_ids: Set[str],
        activation: "ActivationVector",
    ) -> Dict[str, float]:
        """
        Compare previous predictions against actual activations.
        Returns surprise_map: neuron_id → surprise [0, 1]
        """
        surprise_map: Dict[str, float] = {}

        for nid, pred in self._predictions.items():
            if pred.resolved:
                continue
            # Fill in actual activations
            for target_id in pred.predicted_targets:
                pred.actual_targets[target_id] = activation.activations.get(target_id, 0.0)
            pred.resolved = True
            surprise_map[nid] = min(1.0, pred.compute_error())

        # Clear resolved predictions
        self._predictions = {
            nid: p for nid, p in self._predictions.items() if not p.resolved
        }

        return surprise_map

    # ── Feature sharing ───────────────────────────────────────────────────────

    def _update_features(
        self,
        neurons: Dict[str, "MicroNeuron"],
        fired_ids: Set[str],
        activation: "ActivationVector",
    ):
        """
        Co-firing neurons share semantic features proportional to
        connection weight × value signal.
        High-value co-activations build stronger semantic associations.
        """
        value = self._current_value
        fired_neurons = [neurons[nid] for nid in fired_ids if nid in neurons]

        for neuron in fired_neurons:
            strength = activation.activations.get(neuron.id, 0.5)
            if strength < 0.3:
                continue

            for target_id in neuron.get_output_targets():
                if target_id not in fired_ids:
                    continue
                target = neurons.get(target_id)
                if target is None:
                    continue

                conn_weight = neuron.connections[target_id].weight
                if conn_weight < 0.2:
                    continue

                # Feature sharing scaled by value — high-value interactions
                # build stronger semantic associations
                share_rate = self.feature_lr * conn_weight * value
                for feat, val in target.features.items():
                    current = neuron.features.get(feat, 0.0)
                    neuron.features[feat] = current + share_rate * val

                if target.label:
                    neuron.update_feature(f"assoc:{target.label}", conn_weight * value)

    # ── Maintenance ───────────────────────────────────────────────────────────

    def _apply_decay(self, neurons: Dict[str, "MicroNeuron"]):
        now = time.time()
        for neuron in neurons.values():
            for conn in neuron.connections.values():
                if now - conn.last_updated > self.decay_interval_s:
                    conn.weaken(self.decay_rate)

    def _apply_homeostasis(self, neurons: Dict[str, "MicroNeuron"]):
        incoming_totals: Dict[str, float] = {}
        for neuron in neurons.values():
            for target_id, conn in neuron.connections.items():
                incoming_totals[target_id] = (
                    incoming_totals.get(target_id, 0.0) + abs(conn.weight)
                )
        for neuron in neurons.values():
            total = incoming_totals.get(neuron.id, 0.0)
            if total > self.homeostatic_ceil:
                scale = self.homeostatic_ceil / total
                for src_neuron in neurons.values():
                    if neuron.id in src_neuron.connections:
                        src_neuron.connections[neuron.id].weight *= scale

    def _prune(self, neurons: Dict[str, "MicroNeuron"]):
        for neuron in neurons.values():
            neuron.prune_weak_connections(self.min_weight)

    def _structured_replay(self, neurons: Dict[str, "MicroNeuron"]):
        """
        Replay high-value patterns from the replay buffer.
        Consolidates important experiences — equivalent to memory consolidation
        during sleep in biological systems.
        """
        if not self._replay_buffer:
            return
        # Select top-value patterns
        patterns = sorted(
            self._replay_buffer,
            key=lambda p: p["value"],
            reverse=True,
        )[:10]
        for pattern in patterns:
            if pattern["value"] < 0.6:
                continue
            fired_ids = pattern["fired_ids"]
            for nid in fired_ids:
                neuron = neurons.get(nid)
                if neuron is None:
                    continue
                for target_id, conn in neuron.connections.items():
                    if target_id in fired_ids:
                        # Gentle consolidation strengthening
                        conn.strengthen(self.base_lr * 0.1 * pattern["value"])

    def get_stats(self) -> Dict[str, Any]:
        avg_value = (
            sum(v for _, v in self._value_history) / len(self._value_history)
            if self._value_history else 0.5
        )
        return {
            "update_count":    self._update_count,
            "current_value":   round(self._current_value, 3),
            "avg_value":       round(avg_value, 3),
            "replay_buffer":   len(self._replay_buffer),
            "active_predictions": len(self._predictions),
        }
