"""
CLM - Cognitive Language Model
output/base.py

Output generator ABC.
Converts the network's settled activation state into language.

In infancy:  LLM renders output (expensive, fluent)
At maturity: Internal generator renders output (free, sovereign)
In between:  Hybrid blend
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal, ActivationVector
    from clm.memory.semantic import SemanticMemory


class OutputGenerator(ABC):
    """
    Abstract output generator.
    Converts activation state → natural language response.
    """

    def __init__(self):
        self.used_llm_last_call: bool = False
        self.total_calls: int = 0
        self.llm_calls:   int = 0

    @abstractmethod
    def generate(
        self,
        activation:      "ActivationVector",
        session_signals: List["CognitiveSignal"],
        semantic_memory: "SemanticMemory",
        confidence:      float,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from current cognitive state.
        Returns (response_text, metadata).
        """
        pass

    @property
    def llm_dependency_ratio(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.llm_calls / self.total_calls

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_calls":          self.total_calls,
            "llm_calls":            self.llm_calls,
            "llm_dependency_ratio": round(self.llm_dependency_ratio, 4),
        }
