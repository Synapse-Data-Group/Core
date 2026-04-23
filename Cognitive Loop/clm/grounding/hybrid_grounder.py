"""
CLM - Cognitive Language Model
grounding/hybrid_grounder.py

Hybrid grounder — blends LLM and internal grounding based on maturity score.
This is the default grounder used by CLM throughout its development.

As maturity increases, the blend shifts automatically:
  maturity=0.0 → 100% LLM
  maturity=0.5 → 50/50 blend
  maturity=1.0 → 100% internal (sovereign)

The blend is not just a weighted average — at high maturity the LLM
is not called at all, saving cost and removing the dependency entirely.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from clm.grounding.base import GroundingProvider
from clm.grounding.llm_grounder import LLMGrounder
from clm.grounding.internal_grounder import InternalGrounder

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal

logger = logging.getLogger(__name__)


class HybridGrounder(GroundingProvider):
    """
    Developmental grounder that transitions from LLM to internal
    as the system matures.

    Thresholds:
      maturity < llm_only_threshold:    use LLM only
      llm_only_threshold <= maturity
        < internal_only_threshold:      blend both
      maturity >= internal_only_threshold: use internal only (sovereign)
    """

    def __init__(
        self,
        llm_grounder: Optional[LLMGrounder] = None,
        internal_grounder: Optional[InternalGrounder] = None,
        maturity_provider=None,              # MaturityTracker injected at runtime
        llm_only_threshold: float = 0.2,
        internal_only_threshold: float = 0.75,
    ):
        super().__init__()
        self.llm      = llm_grounder or LLMGrounder()
        self.internal = internal_grounder or InternalGrounder()
        self.maturity_provider       = maturity_provider
        self.llm_only_threshold      = llm_only_threshold
        self.internal_only_threshold = internal_only_threshold

    def ground(
        self,
        signal: "CognitiveSignal",
        memories: List[Dict[str, Any]],
        semantic_context: List[Dict[str, Any]],
    ) -> "CognitiveSignal":
        self.total_calls += 1
        maturity = self._get_maturity()

        # ── Sovereign path: internal only
        if maturity >= self.internal_only_threshold:
            self.used_llm_last_call = False
            return self.internal.ground(signal, memories, semantic_context)

        # ── Infancy path: LLM only
        if maturity < self.llm_only_threshold:
            self.used_llm_last_call = True
            self.llm_calls += 1
            return self.llm.ground(signal, memories, semantic_context)

        # ── Blend path: run both, merge features
        self.used_llm_last_call = True
        self.llm_calls += 1

        llm_result      = self.llm.ground(signal, memories, semantic_context)
        internal_result = self.internal.ground(signal, memories, semantic_context)

        # Blend weight: how much to trust internal vs LLM
        # At maturity=0.2 → internal_weight=0.0
        # At maturity=0.75 → internal_weight=1.0
        span = self.internal_only_threshold - self.llm_only_threshold
        internal_weight = (maturity - self.llm_only_threshold) / span
        llm_weight      = 1.0 - internal_weight

        merged_features: Dict[str, float] = {}
        all_keys = set(llm_result.features) | set(internal_result.features)
        for k in all_keys:
            llm_val      = llm_result.features.get(k, 0.0)
            internal_val = internal_result.features.get(k, 0.0)
            merged_features[k] = llm_val * llm_weight + internal_val * internal_weight

        # Blend scalar values
        merged_valence    = llm_result.valence    * llm_weight + internal_result.valence    * internal_weight
        merged_confidence = llm_result.confidence * llm_weight + internal_result.confidence * internal_weight

        # Prefer LLM core concepts early, internal later
        core_concepts = (
            llm_result.metadata.get("core_concepts", [])
            if llm_weight > 0.5
            else internal_result.metadata.get("core_concepts", [])
        )

        from clm.core.signal import CognitiveSignal as CS, SignalOrigin
        return CS(
            signal_type=signal.signal_type,
            origin=SignalOrigin.GROUNDING,
            content=signal.content,
            strength=signal.strength,
            valence=merged_valence,
            confidence=merged_confidence,
            features=merged_features,
            source_id=signal.signal_id,
            parent_id=signal.signal_id,
            metadata={
                **signal.metadata,
                "core_concepts":   core_concepts,
                "intent":          llm_result.metadata.get("intent", "statement"),
                "grounded_by":     f"hybrid:maturity={maturity:.2f}",
                "internal_weight": round(internal_weight, 3),
            },
        )

    def _get_maturity(self) -> float:
        if self.maturity_provider is None:
            return 0.0
        return self.maturity_provider.score

    def get_stats(self) -> Dict[str, Any]:
        return {
            **super().get_stats(),
            "maturity":       round(self._get_maturity(), 4),
            "llm_stats":      self.llm.get_stats(),
            "internal_stats": self.internal.get_stats(),
        }
