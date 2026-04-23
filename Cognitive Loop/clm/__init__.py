"""
CLM — Cognitive Language Model
A self-developing cognitive AI system.

Starts with LLM grounding. Learns from experience.
Progressively becomes sovereign. Eventually runs with zero LLM dependency.
"""

from clm.clm import CLM
from clm.config import CLMConfig, LLMConfig, NetworkConfig, MemoryConfig
from clm.development.phases import DevelopmentalPhase
from clm.development.maturity import MaturityTracker
from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin
from clm.core.state import CognitiveState, CognitiveMode

__version__ = "1.0.0"
__author__  = "Ivan Lluch / Synapse Data"
__license__ = "Apache-2.0"

__all__ = [
    "CLM",
    "CLMConfig",
    "LLMConfig",
    "NetworkConfig",
    "MemoryConfig",
    "DevelopmentalPhase",
    "MaturityTracker",
    "CognitiveSignal",
    "SignalType",
    "SignalOrigin",
    "CognitiveState",
    "CognitiveMode",
]
