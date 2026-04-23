"""
CLM - Cognitive Language Model
perception/conversation.py

Conversation perception — the primary input source during infancy.
Converts user messages into CognitiveSignal objects.
Tracks conversation history for context.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Iterator, List, Optional

from clm.perception.base import PerceptionSource, PerceptionSourceType, PerceptionConfig
from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin


class ConversationPerception(PerceptionSource):
    """
    Converts user conversation turns into CognitiveSignal objects.
    Always enabled — this is the primary learning channel.
    """

    def __init__(self, config: Optional[PerceptionConfig] = None):
        super().__init__(config)
        self.source_type = PerceptionSourceType.CONVERSATION
        self.history: List[Dict[str, Any]] = []
        self.turn_count = 0

    def perceive(self, input_data: Any) -> Iterator[CognitiveSignal]:
        """
        input_data: str (user message) or dict {"role": str, "content": str}
        """
        if isinstance(input_data, str):
            role    = "user"
            content = input_data
        elif isinstance(input_data, dict):
            role    = input_data.get("role", "user")
            content = input_data.get("content", "")
        else:
            return

        if not content.strip():
            return

        self.turn_count += 1
        self.history.append({
            "turn":      self.turn_count,
            "role":      role,
            "content":   content,
            "timestamp": time.time(),
        })

        # Trim history to last 20 turns
        if len(self.history) > 20:
            self.history = self.history[-20:]

        # Strength: user messages are full strength, system slightly less
        strength = 1.0 if role == "user" else 0.8

        signal = CognitiveSignal(
            signal_type=SignalType.PERCEPTUAL,
            origin=SignalOrigin.EXTERNAL,
            content=content,
            strength=strength,
            confidence=1.0,
            metadata={
                "role":       role,
                "turn":       self.turn_count,
                "perception": "conversation",
                "history_len": len(self.history),
            },
        )
        self.total_signals += 1
        yield signal

    def get_context_window(self, k: int = 5) -> List[Dict[str, Any]]:
        """Return last k turns for context."""
        return self.history[-k:]
