"""
CLM - Cognitive Language Model
core/cognitive_loop.py

The central cognitive loop. Persistent, bidirectional, asynchronous.
The loop does not wait for input — it is always running.
Input perturbs state. Output emerges when state settles.
The system's own output re-enters as input (bidirectionality).
"""

from __future__ import annotations
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from clm.core.signal import CognitiveSignal, ActivationVector, SignalType, SignalOrigin
from clm.core.state import CognitiveState, CognitiveMode, SettlementStatus

if TYPE_CHECKING:
    from clm.neurons.network import NeuronNetwork
    from clm.grounding.base import GroundingProvider
    from clm.memory.episodic import EpisodicMemory
    from clm.memory.semantic import SemanticMemory
    from clm.reasoning.contradiction import ContradictionDetector
    from clm.reasoning.metacognition import Metacognition
    from clm.reasoning.simulation import SimulationWorkspace
    from clm.output.base import OutputGenerator
    from clm.development.maturity import MaturityTracker

logger = logging.getLogger(__name__)


class CognitiveLoop:
    """
    The persistent, bidirectional cognitive loop.

    Phases per tick:
      1. PERCEIVE    — ground incoming external signals
      2. PROPAGATE   — spread activation through network
      3. DELIBERATE  — resolve contradictions if detected
      4. SETTLE      — wait for activation to stabilize
      5. GENERATE    — emit output when confident enough
      6. REFLECT     — output re-enters as self-signal (bidirectionality)
      7. CONSOLIDATE — compress experience to memory (background thread)
    """

    def __init__(
        self,
        state: CognitiveState,
        network: "NeuronNetwork",
        grounder: "GroundingProvider",
        episodic_memory: "EpisodicMemory",
        semantic_memory: "SemanticMemory",
        contradiction_detector: "ContradictionDetector",
        metacognition: "Metacognition",
        simulation_workspace: "SimulationWorkspace",
        output_generator: "OutputGenerator",
        maturity_tracker: "MaturityTracker",
        tick_interval: float = 0.05,
        reflection_interval: float = 5.0,
        consolidation_interval: float = 30.0,
        output_confidence_threshold: float = 0.65,
        max_reflection_depth: int = 3,
    ):
        self.state = state
        self.network = network
        self.grounder = grounder
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self.contradiction_detector = contradiction_detector
        self.metacognition = metacognition
        self.simulation_workspace = simulation_workspace
        self.output_generator = output_generator
        self.maturity_tracker = maturity_tracker

        self.tick_interval = tick_interval
        self.reflection_interval = reflection_interval
        self.consolidation_interval = consolidation_interval
        self.output_confidence_threshold = output_confidence_threshold
        self.max_reflection_depth = max_reflection_depth

        self._output_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._consolidation_thread: Optional[threading.Thread] = None

        self._last_reflection_time = 0.0
        self._last_consolidation_time = 0.0
        self._reflection_depth = 0

        # Feedback tracking for prediction outcome recording
        self._last_output_confidence: float = 0.0
        self._last_output_time: float = 0.0
        self._pending_feedback: bool = False

        self.total_ticks = 0
        self.total_inputs = 0
        self.total_outputs = 0
        self.total_reflections = 0

    # ── Public interface ──────────────────────────────────────────────────────

    def start(self):
        """Start the cognitive loop in background threads."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, name="CLM-CognitiveLoop", daemon=True
        )
        self._consolidation_thread = threading.Thread(
            target=self._run_consolidation, name="CLM-Consolidation", daemon=True
        )
        self._thread.start()
        self._consolidation_thread.start()
        logger.info("Cognitive loop started.")

    def stop(self):
        """Gracefully stop the cognitive loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._consolidation_thread:
            self._consolidation_thread.join(timeout=2.0)
        logger.info("Cognitive loop stopped.")

    def perceive(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Inject an external signal. Non-blocking.
        Returns signal_id for tracking.
        """
        # Infer feedback from this new input before processing it
        # (new input = implicit signal about quality of previous output)
        if self._pending_feedback and metadata and metadata.get("role") == "user":
            self.infer_feedback_from_next_input(text)

        signal = CognitiveSignal(
            signal_type=SignalType.PERCEPTUAL,
            origin=SignalOrigin.EXTERNAL,
            content=text,
            strength=1.0,
            confidence=1.0,
            metadata=metadata or {},
        )
        self.state.push_input(signal)
        self.total_inputs += 1
        logger.debug(f"Perceived: '{text[:60]}' id={signal.signal_id[:8]}")
        return signal.signal_id

    def perceive_and_wait(
        self,
        text: str,
        timeout: float = 30.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Inject input and block until output emerges or timeout.
        Used by deployment layer for synchronous request/response.
        """
        result_holder: List[Optional[str]] = [None]
        event = threading.Event()

        def _capture(out_text: str, meta: Dict[str, Any]):
            result_holder[0] = out_text
            event.set()

        self._output_callbacks.append(_capture)
        self.perceive(text, metadata)

        try:
            event.wait(timeout=timeout)
        finally:
            if _capture in self._output_callbacks:
                self._output_callbacks.remove(_capture)

        return result_holder[0]

    def on_output(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register a persistent output callback (streaming-compatible)."""
        self._output_callbacks.append(callback)

    def remove_output_callback(self, callback: Callable):
        if callback in self._output_callbacks:
            self._output_callbacks.remove(callback)

    def feedback(self, value: float, was_correct: Optional[bool] = None):
        """
        Inject explicit feedback into the learning system.

        value:       [0.0, 1.0] — how useful/correct was the last output?
                     1.0 = correct/helpful, 0.5 = neutral, 0.0 = wrong/harmful
        was_correct: Optional explicit correctness signal.
                     If None, inferred from value (value >= 0.6 = correct).

        This routes to:
          1. Tri-factor learner (neuromodulation — strengthens/weakens recent patterns)
          2. Maturity tracker (prediction outcome — calibration scoring)
          3. Replay consolidation (retroactive pattern reinforcement)
        """
        value = max(0.0, min(1.0, value))

        # 1. Inject into tri-factor learner (dopamine-equivalent signal)
        self.network.hebbian.inject_value_signal(value)

        # 2. Retroactive replay with this value signal
        self.network.hebbian.replay_with_feedback(self.network.neurons, value)

        # 3. Record prediction outcome in maturity tracker
        if self._pending_feedback:
            correct = was_correct if was_correct is not None else (value >= 0.6)
            self.maturity_tracker.record_prediction_outcome(
                confidence=self._last_output_confidence,
                was_correct=correct,
            )
            self.maturity_tracker.record_feedback(value)
            self._pending_feedback = False

        logger.debug(f"Feedback injected: value={value:.2f}")

    def infer_feedback_from_next_input(self, next_input: str):
        """
        Heuristic: infer feedback from the user's next message.
        Called automatically by perceive() when _pending_feedback is True.

        Signals of correctness:
          - User continues conversation normally → likely correct (value=0.7)
          - User says "no", "wrong", "that's not right" → incorrect (value=0.2)
          - User repeats the same question → incorrect (value=0.3)
          - User says "yes", "correct", "thanks" → correct (value=0.9)
        """
        if not self._pending_feedback:
            return

        text = next_input.lower().strip()

        # Explicit negative signals
        negative_markers = ["no,", "no.", "wrong", "that's not", "incorrect",
                            "not right", "that is wrong", "you're wrong", "nope"]
        if any(m in text for m in negative_markers):
            self.feedback(0.2, was_correct=False)
            return

        # Explicit positive signals
        positive_markers = ["yes", "correct", "exactly", "right", "thanks",
                            "perfect", "great", "that's it", "good"]
        if any(text.startswith(m) or f" {m}" in text for m in positive_markers):
            self.feedback(0.85, was_correct=True)
            return

        # Repetition detection — same question asked again
        if self.state.session_signals:
            last_inputs = [
                s.content.lower() for s in self.state.session_signals[-3:]
                if s.metadata.get("role") == "user"
            ]
            if any(text[:40] in prev[:40] for prev in last_inputs):
                self.feedback(0.3, was_correct=False)
                return

        # Default: user continued → assume neutral-positive
        self.feedback(0.65, was_correct=True)

    def get_state_snapshot(self) -> Dict[str, Any]:
        return self.state.snapshot()

    # ── Main loop ─────────────────────────────────────────────────────────────

    def _run_loop(self):
        while self._running:
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Loop tick error: {e}", exc_info=True)
            time.sleep(self.tick_interval)

    def _tick(self):
        self.total_ticks += 1
        now = time.time()

        if self.state.has_pending_input():
            self._perceive_phase()

        if self.state.mode in (CognitiveMode.PERCEIVING, CognitiveMode.PROCESSING):
            self._propagate_phase()

        if self.state.contradiction_detected:
            self._deliberate_phase()

        if (
            self.state.settlement == SettlementStatus.SETTLED
            and self.state.confidence >= self.output_confidence_threshold
            and self.state.mode == CognitiveMode.PROCESSING
        ):
            self._generate_phase()

        if (
            self.state.mode == CognitiveMode.IDLE
            and now - self._last_reflection_time > self.reflection_interval
            and self._reflection_depth < self.max_reflection_depth
        ):
            self._reflect_phase()
            self._last_reflection_time = now

        self._update_cognitive_load()

    # ── Phases ────────────────────────────────────────────────────────────────

    def _perceive_phase(self):
        self.state.set_mode(CognitiveMode.PERCEIVING)
        self.state.reset_propagation()

        while self.state.has_pending_input():
            raw = self.state.pop_input()
            if raw is None:
                break

            memories = self.episodic_memory.recall_relevant(raw.content, k=5)
            semantic_ctx = self.semantic_memory.get_relevant_insights(raw.content, k=3)

            grounded = self.grounder.ground(
                signal=raw,
                memories=memories,
                semantic_context=semantic_ctx,
            )

            activation = self.network.inject(grounded)
            self.state.update_activation(activation)

            self.episodic_memory.record(
                signal=raw,
                grounded=grounded,
                activation=activation,
            )

            self.maturity_tracker.record_grounding_call(
                used_llm=self.grounder.used_llm_last_call
            )

        self.state.set_mode(CognitiveMode.PROCESSING)

    def _propagate_phase(self):
        if self.state.is_propagation_exhausted():
            self.state.set_settlement(SettlementStatus.SETTLED)
            self.state.confidence = max(self.state.confidence, 0.4)
            return

        new_activation = self.network.propagate(self.state.activation)
        self.state.update_activation(new_activation)
        self.state.increment_propagation()

        contradictions = self.contradiction_detector.detect(
            self.state.activation,
            self.network.get_active_neurons(),
        )
        if contradictions:
            self.state.flag_contradiction(contradictions)

        # Bidirectionality: process self-generated signals
        while self.state.internal_queue:
            internal = self.state.pop_internal()
            if internal:
                internal_activation = self.network.inject(internal)
                merged = self.state.activation.merge(internal_activation, weight=0.3)
                self.state.update_activation(merged)

    def _deliberate_phase(self):
        self.state.set_mode(CognitiveMode.DELIBERATING)

        resolved = self.contradiction_detector.resolve(
            signals=self.state.contradiction_signals,
            activation=self.state.activation,
            semantic_memory=self.semantic_memory,
        )

        if resolved:
            res_activation = self.network.inject(resolved)
            merged = self.state.activation.merge(res_activation, weight=0.4)
            self.state.update_activation(merged)

        self.state.clear_contradiction()
        self.state.set_mode(CognitiveMode.PROCESSING)

    def _generate_phase(self):
        self.state.set_mode(CognitiveMode.GENERATING)

        gate = self.metacognition.should_output(
            activation=self.state.activation,
            confidence=self.state.confidence,
            cognitive_load=self.state.cognitive_load,
            session_signals=self.state.session_signals,
        )

        if not gate.should_output:
            if gate.reason == "overloaded":
                self.network.shed_load(self.state.activation)
            self.state.set_mode(CognitiveMode.PROCESSING)
            self.state.reset_propagation()
            return

        # ── SIMULATION: think before speaking
        # Run forward simulation to find the best activation trajectory
        # before committing to output generation.
        sim_result = self.simulation_workspace.simulate(
            activation=self.state.activation,
            network=self.network,
            semantic_memory=self.semantic_memory,
            current_value=self.network.hebbian._current_value,
        )

        # If simulation found a better trajectory, use its activation
        if sim_result.ran and sim_result.selected_activation:
            from clm.core.signal import ActivationVector
            simulated_activation = ActivationVector(
                activations=sim_result.selected_activation,
                timestamp=time.time(),
            )
            # Blend simulated with current: simulation guides, current grounds
            blended = self.state.activation.merge(simulated_activation, weight=0.4)
            generate_from = blended
        else:
            generate_from = self.state.activation

        output_text, output_meta = self.output_generator.generate(
            activation=generate_from,
            session_signals=self.state.session_signals,
            semantic_memory=self.semantic_memory,
            confidence=self.state.confidence,
        )

        if sim_result.ran:
            output_meta["simulation"] = {
                "ran": True,
                "reason": sim_result.reason,
                "time_ms": sim_result.simulation_time_ms,
            }

        self.maturity_tracker.record_output_call(
            used_llm=self.output_generator.used_llm_last_call
        )

        # Track for prediction outcome recording
        self._last_output_confidence = self.state.confidence
        self._last_output_time = time.time()
        self._pending_feedback = True

        if output_text:
            self._emit_output(output_text, output_meta)

            # ── BIDIRECTIONALITY: output re-enters as self-signal
            self_signal = CognitiveSignal(
                signal_type=SignalType.REFLEXIVE,
                origin=SignalOrigin.SELF,
                content=output_text,
                strength=0.4,
                confidence=self.state.confidence,
                metadata={"is_self_output": True},
            )
            self.state.push_internal(self_signal)
            self.total_outputs += 1

        # Reset for next input
        self.state.set_mode(CognitiveMode.IDLE)
        self._reflection_depth = 0

    def _reflect_phase(self):
        """
        Self-stimulation when idle.
        The system thinks about what it has recently experienced
        without any external prompt — internal monologue.
        """
        self.state.set_mode(CognitiveMode.REFLECTING)
        self._reflection_depth += 1
        self.total_reflections += 1

        # Pull a recent semantic insight to reflect on
        insights = self.semantic_memory.get_recent_insights(k=1)
        if not insights:
            self.state.set_mode(CognitiveMode.IDLE)
            return

        reflection_content = insights[0].get("content", "")
        if not reflection_content:
            self.state.set_mode(CognitiveMode.IDLE)
            return

        reflect_signal = CognitiveSignal(
            signal_type=SignalType.REFLEXIVE,
            origin=SignalOrigin.SELF,
            content=reflection_content,
            strength=0.3,
            confidence=0.5,
            metadata={"is_reflection": True},
        )
        self.state.push_internal(reflect_signal)
        self.state.set_mode(CognitiveMode.IDLE)

    # ── Background consolidation ──────────────────────────────────────────────

    def _run_consolidation(self):
        """Background thread: compress episodic memory to semantic memory."""
        while self._running:
            time.sleep(self.consolidation_interval)
            try:
                self._consolidate()
            except Exception as e:
                logger.error(f"Consolidation error: {e}", exc_info=True)

    def _consolidate(self):
        self.state.set_mode(CognitiveMode.CONSOLIDATING)
        episodes = self.episodic_memory.get_unconsolidated(limit=50)
        if episodes:
            insights = self.semantic_memory.compress(episodes)
            self.episodic_memory.mark_consolidated(
                [ep.get("episode_id") for ep in episodes]
            )
            logger.debug(f"Consolidated {len(episodes)} episodes → {len(insights)} insights")
        if self.state.mode == CognitiveMode.CONSOLIDATING:
            self.state.set_mode(CognitiveMode.IDLE)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _emit_output(self, text: str, meta: Dict[str, Any]):
        for cb in list(self._output_callbacks):
            try:
                cb(text, meta)
            except Exception as e:
                logger.error(f"Output callback error: {e}")

    def _update_cognitive_load(self):
        """Update cognitive load metric from current state."""
        load = (
            0.3 * min(self.state.propagation_steps / max(self.state.max_propagation_steps, 1), 1.0)
            + 0.3 * (1.0 - self.state.confidence)
            + 0.2 * (len(self.state.input_queue) / 10.0)
            + 0.2 * (1.0 if self.state.contradiction_detected else 0.0)
        )
        self.state.cognitive_load = min(1.0, load)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_ticks":       self.total_ticks,
            "total_inputs":      self.total_inputs,
            "total_outputs":     self.total_outputs,
            "total_reflections": self.total_reflections,
            "running":           self._running,
            "state":             self.state.snapshot(),
        }
