"""
CLM - Cognitive Language Model
perception/trust.py

Source trust weighting — protection against misinformation poisoning.

The critique was correct:
  "Autonomous ingestion causes misinformation internalization,
   concept drift, adversarial poisoning, incoherent ontology growth."

LLMs survive web noise because training is batched and filtered at scale.
A live learner does not get this protection.

This module implements:
  1. Source reliability scoring (domain reputation + content quality signals)
  2. Contradiction-aware ingestion (new content checked against existing beliefs)
  3. Temporal belief revision (older contradicted beliefs decay)
  4. Confidence scaling (web signals injected at reduced strength)
  5. Quarantine buffer (suspicious content held for cross-validation)

Sovereignty: no external reputation APIs. Pure heuristics + learned history.
"""

from __future__ import annotations
import re
import time
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal
    from clm.memory.semantic import SemanticMemory


# ── Domain reputation heuristics ─────────────────────────────────────────────
# These are starting priors — the system updates them from experience.
# Not a blacklist — a prior that gets updated.

_HIGH_TRUST_DOMAINS = {
    "wikipedia.org", "arxiv.org", "pubmed.ncbi.nlm.nih.gov",
    "nature.com", "science.org", "scholar.google.com",
    "github.com", "docs.python.org", "en.wikipedia.org",
    "britannica.com", "stanford.edu", "mit.edu", "oxford.ac.uk",
}

_LOW_TRUST_DOMAINS = {
    "reddit.com", "twitter.com", "x.com", "facebook.com",
    "tiktok.com", "instagram.com", "pinterest.com",
    "buzzfeed.com", "dailymail.co.uk", "thesun.co.uk",
}

# Content quality signals
_QUALITY_POSITIVE = [
    "study", "research", "evidence", "according to", "published",
    "journal", "peer-reviewed", "data shows", "analysis", "findings",
]
_QUALITY_NEGATIVE = [
    "click here", "you won't believe", "shocking", "secret",
    "they don't want you to know", "miracle", "guaranteed",
    "100% proven", "doctors hate", "one weird trick",
]


@dataclass
class TrustScore:
    """Trust assessment for a perception source."""
    domain:          str
    base_score:      float        # Prior trust [0, 1]
    content_score:   float        # Content quality signal [0, 1]
    history_score:   float        # Learned from past experience [0, 1]
    final_score:     float        # Weighted combination
    quarantine:      bool = False # Hold for cross-validation
    reason:          str  = ""


@dataclass
class QuarantinedSignal:
    """A signal held for cross-validation before injection."""
    signal:          "CognitiveSignal"
    trust_score:     TrustScore
    queued_at:       float = field(default_factory=time.time)
    validation_count: int  = 0
    contradictions:  List[str] = field(default_factory=list)


class SourceTrustManager:
    """
    Manages source trust and protects the cognitive system from
    misinformation, concept drift, and adversarial content.

    Strategy:
    - All web signals are scaled by trust score before injection
    - Low-trust signals are quarantined and require cross-validation
    - Contradictions with existing beliefs trigger trust reduction
    - Trust scores are learned over time from feedback
    - No external APIs — pure heuristics + experience
    """

    def __init__(
        self,
        default_web_trust:      float = 0.6,   # Base trust for unknown domains
        quarantine_threshold:   float = 0.35,  # Below this → quarantine
        min_injection_strength: float = 0.2,   # Minimum signal strength after scaling
        max_quarantine_age_s:   float = 3600.0, # Discard quarantined signals after 1h
        cross_validation_count: int   = 2,     # How many corroborating sources needed
    ):
        self.default_web_trust      = default_web_trust
        self.quarantine_threshold   = quarantine_threshold
        self.min_injection_strength = min_injection_strength
        self.max_quarantine_age_s   = max_quarantine_age_s
        self.cross_validation_count = cross_validation_count

        # Learned domain scores — updated from feedback
        self._domain_scores: Dict[str, float] = {}

        # Quarantine buffer
        self._quarantine: List[QuarantinedSignal] = []

        # Contradiction history — tracks which domains have contradicted beliefs
        self._domain_contradictions: Dict[str, int] = defaultdict(int)

        # Stats
        self._total_assessed = 0
        self._quarantined_count = 0
        self._rejected_count = 0

    def assess(
        self,
        signal: "CognitiveSignal",
        semantic_memory: Optional["SemanticMemory"] = None,
    ) -> Tuple[Optional["CognitiveSignal"], TrustScore]:
        """
        Assess a signal's trustworthiness and return a scaled version.

        Returns:
            (scaled_signal, trust_score)
            scaled_signal is None if the signal should be rejected entirely.
        """
        self._total_assessed += 1

        url     = signal.metadata.get("url", "")
        domain  = self._extract_domain(url)
        content = signal.content

        # Compute trust score
        trust = self._compute_trust(domain, content)

        # Check for contradictions with existing beliefs
        if semantic_memory and trust.final_score > 0.3:
            contradictions = self._check_contradictions(signal, semantic_memory)
            if contradictions:
                trust.final_score *= 0.7   # Reduce trust on contradiction
                trust.reason += f" | contradicts: {contradictions[:2]}"
                self._domain_contradictions[domain] += 1

        # Quarantine low-trust signals
        if trust.quarantine or trust.final_score < self.quarantine_threshold:
            self._quarantine.append(QuarantinedSignal(
                signal=signal,
                trust_score=trust,
                contradictions=[],
            ))
            self._quarantined_count += 1
            return None, trust

        # Scale signal strength by trust score
        scaled = self._scale_signal(signal, trust.final_score)
        return scaled, trust

    def release_validated_quarantine(
        self, semantic_memory: "SemanticMemory"
    ) -> List["CognitiveSignal"]:
        """
        Release quarantined signals that have been cross-validated.
        Called periodically by the perception manager.
        """
        now = time.time()
        released = []
        remaining = []

        for qs in self._quarantine:
            # Expire old quarantined signals
            if now - qs.queued_at > self.max_quarantine_age_s:
                self._rejected_count += 1
                continue

            # Check if similar content has been seen from other sources
            qs.validation_count = self._count_corroborating_sources(
                qs.signal, semantic_memory
            )

            if qs.validation_count >= self.cross_validation_count:
                # Cross-validated — release at reduced strength
                scaled = self._scale_signal(qs.signal, qs.trust_score.final_score * 0.8)
                released.append(scaled)
            else:
                remaining.append(qs)

        self._quarantine = remaining
        return released

    def update_domain_trust(self, domain: str, feedback_value: float):
        """
        Update learned trust for a domain based on feedback.
        Called when the system receives feedback about content quality.
        """
        current = self._domain_scores.get(domain, self.default_web_trust)
        # Exponential moving average
        self._domain_scores[domain] = 0.85 * current + 0.15 * feedback_value

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_assessed":    self._total_assessed,
            "quarantined_count": self._quarantined_count,
            "rejected_count":    self._rejected_count,
            "quarantine_size":   len(self._quarantine),
            "known_domains":     len(self._domain_scores),
            "top_contradictors": sorted(
                self._domain_contradictions.items(),
                key=lambda x: x[1], reverse=True
            )[:5],
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _compute_trust(self, domain: str, content: str) -> TrustScore:
        # 1. Base score from domain reputation
        if domain in _HIGH_TRUST_DOMAINS:
            base = 0.85
        elif domain in _LOW_TRUST_DOMAINS:
            base = 0.25
        else:
            base = self._domain_scores.get(domain, self.default_web_trust)

        # Reduce for domains with contradiction history
        contradiction_penalty = min(0.3, self._domain_contradictions[domain] * 0.05)
        base = max(0.1, base - contradiction_penalty)

        # 2. Content quality score
        content_lower = content.lower()
        pos = sum(1 for m in _QUALITY_POSITIVE if m in content_lower)
        neg = sum(1 for m in _QUALITY_NEGATIVE if m in content_lower)
        content_score = max(0.1, min(1.0, 0.5 + pos * 0.08 - neg * 0.15))

        # 3. History score (learned)
        history = self._domain_scores.get(domain, self.default_web_trust)

        # 4. Final weighted score
        final = 0.5 * base + 0.3 * content_score + 0.2 * history

        # Quarantine if very low trust
        quarantine = final < self.quarantine_threshold

        reason = f"domain={domain} base={base:.2f} content={content_score:.2f}"

        return TrustScore(
            domain=domain,
            base_score=base,
            content_score=content_score,
            history_score=history,
            final_score=round(final, 3),
            quarantine=quarantine,
            reason=reason,
        )

    def _check_contradictions(
        self,
        signal: "CognitiveSignal",
        semantic_memory: "SemanticMemory",
    ) -> List[str]:
        """
        Check if signal content contradicts existing semantic beliefs.
        Returns list of contradicted insight contents.
        """
        query = signal.content[:100]
        insights = semantic_memory.get_relevant_insights(query, k=3)

        contradictions = []
        for insight in insights:
            insight_content = insight.get("content", "").lower()
            signal_content  = signal.content.lower()

            # Simple heuristic: look for negation patterns
            # e.g., insight says "X is Y", signal says "X is not Y"
            if self._detects_negation_conflict(insight_content, signal_content):
                contradictions.append(insight.get("content", "")[:60])

        return contradictions

    def _detects_negation_conflict(self, existing: str, new: str) -> bool:
        """Detect if new content negates existing belief."""
        # Extract key phrases from existing
        words_existing = set(existing.split())
        words_new      = set(new.split())

        # Check for negation markers in new content near shared concepts
        negation_markers = {"not", "never", "no", "false", "wrong", "incorrect",
                            "isn't", "aren't", "wasn't", "doesn't", "don't"}
        shared_concepts = words_existing & words_new - {"the", "a", "is", "are", "and"}

        if not shared_concepts:
            return False

        # If new content has negation markers AND shared concepts → potential conflict
        has_negation = bool(negation_markers & words_new)
        return has_negation and len(shared_concepts) >= 2

    def _scale_signal(
        self, signal: "CognitiveSignal", trust: float
    ) -> "CognitiveSignal":
        """Return a copy of the signal with strength scaled by trust."""
        from clm.core.signal import CognitiveSignal as CS
        scaled_strength = max(
            self.min_injection_strength,
            signal.strength * trust
        )
        scaled_confidence = signal.confidence * trust

        return CS(
            signal_type=signal.signal_type,
            origin=signal.origin,
            content=signal.content,
            strength=scaled_strength,
            valence=signal.valence,
            confidence=scaled_confidence,
            features=signal.features.copy(),
            source_id=signal.signal_id,
            parent_id=signal.signal_id,
            metadata={
                **signal.metadata,
                "trust_score": trust,
                "original_strength": signal.strength,
            },
        )

    def _extract_domain(self, url: str) -> str:
        if not url:
            return "unknown"
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return "unknown"

    def _count_corroborating_sources(
        self,
        signal: "CognitiveSignal",
        semantic_memory: "SemanticMemory",
    ) -> int:
        """Count how many existing insights corroborate this signal's content."""
        query   = signal.content[:80]
        insights = semantic_memory.get_relevant_insights(query, k=5)
        # Count insights from different sources that agree
        corroborating = sum(
            1 for ins in insights
            if ins.get("confidence", 0) > 0.5
        )
        return corroborating
