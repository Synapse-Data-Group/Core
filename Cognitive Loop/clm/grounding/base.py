"""
CLM - Cognitive Language Model
grounding/base.py

Grounding provider ABC.
Grounding converts raw language signals into structured feature vectors
that the neuron network can process.

In infancy:  LLM does the grounding (expensive, accurate)
At maturity: Internal semantic memory does the grounding (free, sovereign)
In between:  Hybrid — blend based on maturity score
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal


class GroundingProvider(ABC):
    """
    Abstract grounding provider.

    Converts a raw CognitiveSignal (text content) into a grounded signal
    with populated feature vectors that the neuron network can activate on.
    """

    def __init__(self):
        self.used_llm_last_call: bool = False
        self.total_calls: int = 0
        self.llm_calls: int = 0

    @abstractmethod
    def ground(
        self,
        signal: "CognitiveSignal",
        memories: List[Dict[str, Any]],
        semantic_context: List[Dict[str, Any]],
    ) -> "CognitiveSignal":
        """
        Ground a raw signal into a feature-rich signal.

        Args:
            signal:           Raw perceptual signal with text content
            memories:         Relevant episodic memories
            semantic_context: Relevant semantic insights

        Returns:
            Grounded signal with populated features dict
        """
        pass

    @property
    def llm_dependency_ratio(self) -> float:
        """Fraction of calls that used LLM. Tracks toward sovereignty."""
        if self.total_calls == 0:
            return 1.0
        return self.llm_calls / self.total_calls

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_calls":          self.total_calls,
            "llm_calls":            self.llm_calls,
            "llm_dependency_ratio": round(self.llm_dependency_ratio, 4),
        }
