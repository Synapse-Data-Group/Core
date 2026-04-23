"""
CLM - Cognitive Language Model
output/hybrid_renderer.py

Hybrid output renderer — blends LLM and internal rendering based on maturity.
Default renderer used throughout CLM's development lifecycle.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from clm.output.base import OutputGenerator
from clm.output.llm_renderer import LLMRenderer
from clm.output.internal_renderer import InternalRenderer

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal, ActivationVector
    from clm.memory.semantic import SemanticMemory

logger = logging.getLogger(__name__)


class HybridRenderer(OutputGenerator):
    """
    Developmental renderer that transitions from LLM to internal
    as the system matures. Mirrors HybridGrounder logic.

    maturity < llm_only_threshold:      LLM renders
    llm_only <= maturity < internal_only: blend
    maturity >= internal_only_threshold: internal renders (sovereign)
    """

    def __init__(
        self,
        llm_renderer:             Optional[LLMRenderer] = None,
        internal_renderer:        Optional[InternalRenderer] = None,
        maturity_provider=None,
        llm_only_threshold:       float = 0.3,
        internal_only_threshold:  float = 0.8,
    ):
        super().__init__()
        self.llm              = llm_renderer or LLMRenderer()
        self.internal         = internal_renderer or InternalRenderer()
        self.maturity_provider          = maturity_provider
        self.llm_only_threshold         = llm_only_threshold
        self.internal_only_threshold    = internal_only_threshold

    def generate(
        self,
        activation:      "ActivationVector",
        session_signals: List["CognitiveSignal"],
        semantic_memory: "SemanticMemory",
        confidence:      float,
    ) -> Tuple[str, Dict[str, Any]]:
        self.total_calls += 1
        maturity = self._get_maturity()

        # ── Sovereign path
        if maturity >= self.internal_only_threshold:
            self.used_llm_last_call = False
            return self.internal.generate(activation, session_signals, semantic_memory, confidence)

        # ── Infancy path
        if maturity < self.llm_only_threshold:
            self.used_llm_last_call = True
            self.llm_calls += 1
            return self.llm.generate(activation, session_signals, semantic_memory, confidence)

        # ── Blend path: use LLM but inform it with internal insights
        self.used_llm_last_call = True
        self.llm_calls += 1

        # Get internal insights to enrich LLM prompt context
        internal_text, internal_meta = self.internal.generate(
            activation, session_signals, semantic_memory, confidence
        )

        # Inject internal output as additional context for LLM
        enriched_signals = list(session_signals)
        if internal_text:
            from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin
            enriched_signals.append(CognitiveSignal(
                signal_type=SignalType.SEMANTIC,
                origin=SignalOrigin.SELF,
                content=f"Internal reasoning: {internal_text}",
                strength=0.5,
                confidence=confidence,
                metadata={"is_internal_context": True},
            ))

        llm_text, llm_meta = self.llm.generate(
            activation, enriched_signals, semantic_memory, confidence
        )

        span            = self.internal_only_threshold - self.llm_only_threshold
        internal_weight = (maturity - self.llm_only_threshold) / span

        # At high maturity blend, prefer internal text
        final_text = llm_text if internal_weight < 0.5 else internal_text
        meta = {
            **llm_meta,
            "rendered_by":     f"hybrid:maturity={maturity:.2f}",
            "internal_weight": round(internal_weight, 3),
            "internal_text":   internal_text[:100],
        }
        return final_text, meta

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
