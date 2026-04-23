"""
CLM - Cognitive Language Model
development/phases.py

Developmental phases of the CLM system.
The system progresses through phases automatically based on
measurable criteria — not by a switch you flip.

INFANCY    → Heavy LLM dependency. Learning basic grounding.
ADOLESCENT → Partial internal capability. LLM still grounds input.
MATURE     → Mostly internal. LLM only for novel/rare concepts.
SOVEREIGN  → Zero LLM calls. Fully self-sufficient.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DevelopmentalPhase(Enum):
    INFANCY    = "infancy"
    ADOLESCENT = "adolescent"
    MATURE     = "mature"
    SOVEREIGN  = "sovereign"


@dataclass
class PhaseConfig:
    """
    Configuration and permissions for each developmental phase.
    Controls what the system is allowed to do at each stage.
    """
    phase: DevelopmentalPhase

    # Grounding
    llm_grounding_allowed:      bool  = True
    internal_grounding_allowed: bool  = False

    # Output
    llm_rendering_allowed:      bool  = True
    internal_rendering_allowed: bool  = False

    # Perception permissions
    conversation_allowed:       bool  = True
    web_browsing_allowed:       bool  = False
    web_requires_approval:      bool  = True
    feed_allowed:               bool  = False
    document_allowed:           bool  = True
    autonomous_search_allowed:  bool  = False

    # Network behavior
    max_network_size:           int   = 5_000
    hebbian_learning_rate:      float = 0.02
    pruning_allowed:            bool  = False

    # Reflection
    reflection_allowed:         bool  = False
    reflection_interval_s:      float = 60.0

    # Maturity thresholds to enter this phase
    min_maturity_score:         float = 0.0
    min_episodes:               int   = 0
    min_semantic_insights:      int   = 0


# Phase definitions — ordered by progression
PHASE_CONFIGS: Dict[DevelopmentalPhase, PhaseConfig] = {

    DevelopmentalPhase.INFANCY: PhaseConfig(
        phase=DevelopmentalPhase.INFANCY,
        llm_grounding_allowed=True,
        internal_grounding_allowed=False,
        llm_rendering_allowed=True,
        internal_rendering_allowed=False,
        conversation_allowed=True,
        web_browsing_allowed=False,
        web_requires_approval=True,
        feed_allowed=False,
        document_allowed=True,
        autonomous_search_allowed=False,
        max_network_size=5_000,
        hebbian_learning_rate=0.03,   # Learn fast in infancy
        pruning_allowed=False,
        reflection_allowed=False,
        reflection_interval_s=120.0,
        min_maturity_score=0.0,
        min_episodes=0,
        min_semantic_insights=0,
    ),

    DevelopmentalPhase.ADOLESCENT: PhaseConfig(
        phase=DevelopmentalPhase.ADOLESCENT,
        llm_grounding_allowed=True,
        internal_grounding_allowed=True,
        llm_rendering_allowed=True,
        internal_rendering_allowed=True,
        conversation_allowed=True,
        web_browsing_allowed=True,
        web_requires_approval=True,      # Still needs approval
        feed_allowed=True,
        document_allowed=True,
        autonomous_search_allowed=False,
        max_network_size=20_000,
        hebbian_learning_rate=0.02,
        pruning_allowed=True,
        reflection_allowed=True,
        reflection_interval_s=30.0,
        min_maturity_score=0.2,
        min_episodes=100,
        min_semantic_insights=20,
    ),

    DevelopmentalPhase.MATURE: PhaseConfig(
        phase=DevelopmentalPhase.MATURE,
        llm_grounding_allowed=True,      # Only for truly novel concepts
        internal_grounding_allowed=True,
        llm_rendering_allowed=True,      # Fallback only
        internal_rendering_allowed=True,
        conversation_allowed=True,
        web_browsing_allowed=True,
        web_requires_approval=False,     # Autonomous within allowed domains
        feed_allowed=True,
        document_allowed=True,
        autonomous_search_allowed=True,
        max_network_size=50_000,
        hebbian_learning_rate=0.015,
        pruning_allowed=True,
        reflection_allowed=True,
        reflection_interval_s=10.0,
        min_maturity_score=0.6,
        min_episodes=1_000,
        min_semantic_insights=200,
    ),

    DevelopmentalPhase.SOVEREIGN: PhaseConfig(
        phase=DevelopmentalPhase.SOVEREIGN,
        llm_grounding_allowed=False,     # No LLM
        internal_grounding_allowed=True,
        llm_rendering_allowed=False,     # No LLM
        internal_rendering_allowed=True,
        conversation_allowed=True,
        web_browsing_allowed=True,
        web_requires_approval=False,
        feed_allowed=True,
        document_allowed=True,
        autonomous_search_allowed=True,
        max_network_size=200_000,
        hebbian_learning_rate=0.01,      # Slower, more stable learning
        pruning_allowed=True,
        reflection_allowed=True,
        reflection_interval_s=5.0,
        min_maturity_score=0.9,
        min_episodes=10_000,
        min_semantic_insights=1_000,
    ),
}


def get_phase_config(phase: DevelopmentalPhase) -> PhaseConfig:
    return PHASE_CONFIGS[phase]


def determine_phase(
    maturity_score:    float,
    episode_count:     int,
    insight_count:     int,
) -> DevelopmentalPhase:
    """
    Determine the current developmental phase from measurable criteria.
    All three criteria must be met to advance to a phase.
    """
    # Check from highest to lowest
    for phase in [
        DevelopmentalPhase.SOVEREIGN,
        DevelopmentalPhase.MATURE,
        DevelopmentalPhase.ADOLESCENT,
        DevelopmentalPhase.INFANCY,
    ]:
        cfg = PHASE_CONFIGS[phase]
        if (
            maturity_score  >= cfg.min_maturity_score
            and episode_count   >= cfg.min_episodes
            and insight_count   >= cfg.min_semantic_insights
        ):
            return phase

    return DevelopmentalPhase.INFANCY
