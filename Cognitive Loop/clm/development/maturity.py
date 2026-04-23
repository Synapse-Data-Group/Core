"""
CLM - Cognitive Language Model
development/maturity.py

Maturity tracker — measures how sovereign the system has become.

maturity_score = 1.0 - llm_dependency_ratio

Tracks LLM calls vs total cognitive operations.
As the system learns, LLM dependency drops and maturity rises.
Persisted to disk so maturity survives restarts.
"""

from __future__ import annotations
import json
import os
import time
from typing import Any, Dict, Optional

from clm.development.phases import DevelopmentalPhase, determine_phase, get_phase_config

_DEFAULT_STORAGE = "./clm_data/maturity.json"


class MaturityTracker:
    """
    Tracks the system's developmental maturity over time.

    Core metric:
        maturity_score = 1.0 - (llm_calls / total_cognitive_ops)

    Secondary metrics:
        - episode_count: total experiences recorded
        - insight_count: total semantic insights formed
        - network_growth: neuron count over time
        - phase: current developmental phase

    All metrics persisted to JSON. Survives restarts.
    """

    def __init__(self, storage_path: str = _DEFAULT_STORAGE):
        self.storage_path = storage_path

        # LLM call tracking
        self._total_grounding_calls: int = 0
        self._llm_grounding_calls:   int = 0
        self._total_output_calls:    int = 0
        self._llm_output_calls:      int = 0

        # Experience tracking
        self._episode_count:  int = 0
        self._insight_count:  int = 0
        self._neuron_count:   int = 0

        # Competence tracking — maturity must be EARNED, not just declared
        # prediction_accuracy: fraction of output cycles where confidence was justified
        #   (confidence >= 0.6 AND user didn't immediately correct/repeat)
        self._prediction_attempts:  int   = 0
        self._prediction_successes: int   = 0

        # calibration_score: how well confidence correlates with actual correctness
        #   tracked as running mean of |confidence - actual_outcome|
        self._calibration_errors: list = []   # deque of abs(confidence - outcome)

        # compression_gain: ratio of semantic insights to episodes
        #   high compression = system is abstracting, not just memorizing
        # (computed on-the-fly from episode/insight counts)

        # feedback_scores: explicit value signals from tri-factor learner
        self._feedback_scores: list = []      # recent value signals [0,1]

        # Phase
        self._phase: DevelopmentalPhase = DevelopmentalPhase.INFANCY

        # History for trend analysis
        self._score_history: list = []
        self._phase_transitions: list = []

        self._started_at: float = time.time()
        self._load()

    # ── Recording ─────────────────────────────────────────────────────────────

    def record_grounding_call(self, used_llm: bool):
        self._total_grounding_calls += 1
        if used_llm:
            self._llm_grounding_calls += 1
        self._maybe_save()

    def record_output_call(self, used_llm: bool):
        self._total_output_calls += 1
        if used_llm:
            self._llm_output_calls += 1
        self._maybe_save()

    def record_episode(self):
        self._episode_count += 1

    def record_insight(self):
        self._insight_count += 1

    def update_neuron_count(self, count: int):
        self._neuron_count = count

    def sync_from_memory(self, episode_count: int, insight_count: int):
        """Sync counts from memory systems."""
        self._episode_count = episode_count
        self._insight_count = insight_count
        self._update_phase()

    # ── Competence recording ──────────────────────────────────────────────────

    def record_prediction_outcome(self, confidence: float, was_correct: bool):
        """
        Record whether a prediction/output was correct.
        Called by the cognitive loop after output is emitted and
        feedback is available (user continued conversation = likely correct,
        user corrected = incorrect, user repeated question = incorrect).
        """
        self._prediction_attempts += 1
        if was_correct:
            self._prediction_successes += 1
        # Calibration: how far was confidence from actual outcome
        actual = 1.0 if was_correct else 0.0
        self._calibration_errors.append(abs(confidence - actual))
        if len(self._calibration_errors) > 200:
            self._calibration_errors = self._calibration_errors[-200:]

    def record_feedback(self, value: float):
        """Record a value signal from the tri-factor learner."""
        self._feedback_scores.append(value)
        if len(self._feedback_scores) > 100:
            self._feedback_scores = self._feedback_scores[-100:]

    # ── Score ─────────────────────────────────────────────────────────────────

    @property
    def score(self) -> float:
        """
        Composite maturity score [0.0, 1.0].

        Maturity = weighted combination of:
          1. independence_score  (0.25) — LLM call reduction
          2. prediction_accuracy (0.30) — fraction of outputs that were correct
          3. calibration_score   (0.25) — confidence correlates with correctness
          4. compression_gain    (0.20) — abstracting experience, not just memorizing

        A system that stops calling LLM but is always wrong scores LOW.
        Sovereignty must be earned through demonstrated competence.
        """
        return round(
            0.25 * self._independence_score()
            + 0.30 * self._prediction_accuracy_score()
            + 0.25 * self._calibration_score()
            + 0.20 * self._compression_gain_score(),
            4
        )

    def _independence_score(self) -> float:
        """Fraction of cognitive operations done without LLM."""
        total_ops = self._total_grounding_calls + self._total_output_calls
        if total_ops == 0:
            return 0.0
        llm_ops = self._llm_grounding_calls + self._llm_output_calls
        return 1.0 - (llm_ops / total_ops)

    def _prediction_accuracy_score(self) -> float:
        """Fraction of outputs that were correct/useful."""
        if self._prediction_attempts < 5:
            return 0.3   # Insufficient data — assume baseline
        return self._prediction_successes / self._prediction_attempts

    def _calibration_score(self) -> float:
        """
        How well-calibrated is the system's confidence?
        Perfect calibration = 1.0 (confidence always matches correctness).
        Poor calibration = 0.0 (always over/under-confident).
        """
        if len(self._calibration_errors) < 5:
            return 0.3   # Insufficient data
        mean_error = sum(self._calibration_errors) / len(self._calibration_errors)
        return max(0.0, 1.0 - mean_error * 2)   # error of 0.5 → score of 0

    def _compression_gain_score(self) -> float:
        """
        Ratio of semantic insights to episodes.
        High compression = system is abstracting, not just memorizing.
        Target: 1 insight per 10 episodes = score of 1.0
        """
        if self._episode_count < 10:
            return 0.0
        ratio = self._insight_count / self._episode_count
        # Normalize: ratio of 0.1 (1 insight per 10 episodes) = 1.0
        return min(1.0, ratio / 0.1)

    @property
    def independence_ratio(self) -> float:
        """Raw LLM independence (old metric — kept for reference)."""
        return self._independence_score()

    @property
    def phase(self) -> DevelopmentalPhase:
        return self._phase

    @property
    def phase_config(self):
        return get_phase_config(self._phase)

    @property
    def llm_dependency_ratio(self) -> float:
        return 1.0 - self._independence_score()

    def is_sovereign(self) -> bool:
        return self._phase == DevelopmentalPhase.SOVEREIGN

    def get_milestone_progress(self) -> Dict[str, Any]:
        """Progress toward next phase transition."""
        next_phase = self._next_phase()
        if next_phase is None:
            return {"phase": "sovereign", "complete": True}

        from clm.development.phases import PHASE_CONFIGS
        cfg = PHASE_CONFIGS[next_phase]

        return {
            "current_phase":    self._phase.value,
            "next_phase":       next_phase.value,
            "maturity_score":   {"current": self.score,           "required": cfg.min_maturity_score,    "pct": min(100, int(self.score / max(cfg.min_maturity_score, 0.001) * 100))},
            "episodes":         {"current": self._episode_count,  "required": cfg.min_episodes,          "pct": min(100, int(self._episode_count / max(cfg.min_episodes, 1) * 100))},
            "insights":         {"current": self._insight_count,  "required": cfg.min_semantic_insights, "pct": min(100, int(self._insight_count / max(cfg.min_semantic_insights, 1) * 100))},
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "maturity_score":         self.score,
            "phase":                  self._phase.value,
            "llm_dependency_ratio":   round(self.llm_dependency_ratio, 4),
            "score_breakdown": {
                "independence":       round(self._independence_score(), 4),
                "prediction_accuracy": round(self._prediction_accuracy_score(), 4),
                "calibration":        round(self._calibration_score(), 4),
                "compression_gain":   round(self._compression_gain_score(), 4),
            },
            "total_grounding_calls":  self._total_grounding_calls,
            "llm_grounding_calls":    self._llm_grounding_calls,
            "total_output_calls":     self._total_output_calls,
            "llm_output_calls":       self._llm_output_calls,
            "prediction_attempts":    self._prediction_attempts,
            "prediction_successes":   self._prediction_successes,
            "episode_count":          self._episode_count,
            "insight_count":          self._insight_count,
            "neuron_count":           self._neuron_count,
            "uptime_hours":           round((time.time() - self._started_at) / 3600, 2),
            "phase_transitions":      len(self._phase_transitions),
            "milestone_progress":     self.get_milestone_progress(),
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _update_phase(self):
        new_phase = determine_phase(
            maturity_score=self.score,
            episode_count=self._episode_count,
            insight_count=self._insight_count,
        )
        if new_phase != self._phase:
            self._phase_transitions.append({
                "from":      self._phase.value,
                "to":        new_phase.value,
                "timestamp": time.time(),
                "score":     self.score,
            })
            self._phase = new_phase
            self._save()

    def _next_phase(self) -> Optional[DevelopmentalPhase]:
        order = [
            DevelopmentalPhase.INFANCY,
            DevelopmentalPhase.ADOLESCENT,
            DevelopmentalPhase.MATURE,
            DevelopmentalPhase.SOVEREIGN,
        ]
        idx = order.index(self._phase)
        if idx < len(order) - 1:
            return order[idx + 1]
        return None

    _save_counter = 0

    def _maybe_save(self):
        self._save_counter += 1
        if self._save_counter % 50 == 0:
            self._update_phase()
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "total_grounding_calls":  self._total_grounding_calls,
            "llm_grounding_calls":    self._llm_grounding_calls,
            "total_output_calls":     self._total_output_calls,
            "llm_output_calls":       self._llm_output_calls,
            "episode_count":          self._episode_count,
            "insight_count":          self._insight_count,
            "neuron_count":           self._neuron_count,
            "prediction_attempts":    self._prediction_attempts,
            "prediction_successes":   self._prediction_successes,
            "calibration_errors":     self._calibration_errors[-50:],
            "phase":                  self._phase.value,
            "phase_transitions":      self._phase_transitions,
            "started_at":             self._started_at,
            "saved_at":               time.time(),
        }
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._total_grounding_calls  = data.get("total_grounding_calls", 0)
            self._llm_grounding_calls    = data.get("llm_grounding_calls", 0)
            self._total_output_calls     = data.get("total_output_calls", 0)
            self._llm_output_calls       = data.get("llm_output_calls", 0)
            self._episode_count          = data.get("episode_count", 0)
            self._insight_count          = data.get("insight_count", 0)
            self._neuron_count           = data.get("neuron_count", 0)
            self._prediction_attempts    = data.get("prediction_attempts", 0)
            self._prediction_successes   = data.get("prediction_successes", 0)
            self._calibration_errors     = data.get("calibration_errors", [])
            self._phase_transitions      = data.get("phase_transitions", [])
            self._started_at             = data.get("started_at", self._started_at)
            phase_str = data.get("phase", "infancy")
            self._phase = DevelopmentalPhase(phase_str)
        except Exception:
            pass
