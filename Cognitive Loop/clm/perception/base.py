"""
CLM - Cognitive Language Model
perception/base.py

Perception source ABC.
All input to CLM — whether from a user, a webpage, an RSS feed,
or a local document — flows through a PerceptionSource.

Every source produces CognitiveSignal objects.
The network doesn't care where the signal came from.
Unified perception.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal
    from clm.development.phases import DevelopmentalPhase


class PerceptionSourceType(Enum):
    CONVERSATION = "conversation"   # User chat
    WEB          = "web"            # Web page fetch
    FEED         = "feed"           # RSS / Atom feed
    DOCUMENT     = "document"       # Local file
    SELF         = "self"           # Internal reflection


@dataclass
class PerceptionConfig:
    """Controls what a perception source is allowed to do per phase."""
    enabled:             bool  = True
    max_content_length:  int   = 10_000   # chars per signal
    rate_limit_per_min:  int   = 60
    requires_approval:   bool  = False    # User must approve before fetching
    allowed_domains:     List[str] = field(default_factory=list)  # empty = all
    blocked_domains:     List[str] = field(default_factory=list)


class PerceptionSource(ABC):
    """
    Abstract perception source.
    Produces a stream of CognitiveSignal objects.
    """

    def __init__(self, config: Optional[PerceptionConfig] = None):
        self.config        = config or PerceptionConfig()
        self.source_type   = PerceptionSourceType.CONVERSATION
        self.total_signals = 0
        self._call_times: List[float] = []

    @abstractmethod
    def perceive(self, input_data: Any) -> Iterator["CognitiveSignal"]:
        """
        Convert input into a stream of CognitiveSignal objects.
        Must be a generator (yield signals one at a time).
        """
        pass

    def is_allowed(self) -> bool:
        return self.config.enabled

    def _check_rate_limit(self) -> bool:
        import time
        now = time.time()
        self._call_times = [t for t in self._call_times if now - t < 60]
        if len(self._call_times) >= self.config.rate_limit_per_min:
            return False
        self._call_times.append(now)
        return True

    def get_stats(self) -> Dict[str, Any]:
        return {
            "source_type":   self.source_type.value,
            "total_signals": self.total_signals,
            "enabled":       self.config.enabled,
        }
