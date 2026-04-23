"""
CLM - Cognitive Language Model
grounding/internal_grounder.py

Internal grounding — used at maturity. Zero LLM calls.
Grounds signals using the system's own accumulated semantic memory.

This is the sovereign grounding path.
The system grounds new input against what it already knows —
exactly how a mature mind interprets new information through
the lens of accumulated experience.
"""

from __future__ import annotations
import math
import re
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from clm.grounding.base import GroundingProvider

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal

logger = logging.getLogger(__name__)

# Common English stop words — filtered out during feature extraction
_STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "up",
    "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again", "then",
    "once", "and", "but", "or", "nor", "so", "yet", "both", "either",
    "neither", "not", "only", "own", "same", "than", "too", "very",
    "just", "because", "as", "until", "while", "i", "me", "my", "we",
    "our", "you", "your", "he", "she", "it", "they", "them", "their",
    "what", "which", "who", "this", "that", "these", "those", "am",
}

# Valence lexicon — built-in minimal sentiment
_POSITIVE_WORDS = {
    "good", "great", "excellent", "wonderful", "amazing", "fantastic",
    "love", "like", "enjoy", "happy", "joy", "pleasure", "success",
    "win", "best", "better", "positive", "helpful", "useful", "correct",
    "right", "true", "yes", "agree", "beautiful", "perfect", "safe",
}
_NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "hate", "dislike", "sad",
    "pain", "fail", "failure", "worst", "worse", "negative", "wrong",
    "false", "no", "disagree", "ugly", "broken", "error", "problem",
    "issue", "danger", "risk", "fear", "angry", "frustrat",
}

# Intent patterns
_INTENT_PATTERNS = {
    "question":   [r"\?$", r"^(what|who|where|when|why|how|is|are|can|do|does|did)\b"],
    "command":    [r"^(please|do|make|create|build|show|tell|give|find|help|stop|start)\b"],
    "expression": [r"^(i feel|i think|i believe|i want|i need|i love|i hate)\b"],
}


class InternalGrounder(GroundingProvider):
    """
    Sovereign grounding using accumulated semantic memory.
    Zero LLM calls. Pure Python stdlib.

    Grounding strategy:
    1. Tokenize and clean input text
    2. Extract TF-IDF-like features from tokens
    3. Match tokens against semantic memory for enrichment
    4. Compute valence from lexicon + learned associations
    5. Detect intent from pattern matching
    6. Return fully grounded signal
    """

    def __init__(self, semantic_memory=None):
        super().__init__()
        self.semantic_memory = semantic_memory  # Injected after construction
        self._idf_cache: Dict[str, float] = {}
        self._doc_count: int = 0

    def ground(
        self,
        signal: "CognitiveSignal",
        memories: List[Dict[str, Any]],
        semantic_context: List[Dict[str, Any]],
    ) -> "CognitiveSignal":
        """Ground signal using internal semantic memory. No LLM."""
        self.total_calls += 1
        self.used_llm_last_call = False

        text = signal.content.lower().strip()
        tokens = self._tokenize(text)

        # Base features from token frequency
        features = self._extract_features(tokens)

        # Enrich from semantic memory matches
        features = self._enrich_from_memory(features, tokens, semantic_context)

        # Compute valence
        valence = self._compute_valence(tokens, features)

        # Detect intent
        intent = self._detect_intent(signal.content)

        # Confidence based on how many tokens matched known concepts
        known_ratio = sum(
            1 for t in tokens if t in self._idf_cache
        ) / max(len(tokens), 1)
        confidence = 0.4 + 0.5 * known_ratio  # 0.4 minimum, up to 0.9

        # Core concepts = highest-weight features
        sorted_feats = sorted(features.items(), key=lambda x: x[1], reverse=True)
        core_concepts = [f for f, _ in sorted_feats[:5]]

        from clm.core.signal import CognitiveSignal as CS, SignalOrigin
        return CS(
            signal_type=signal.signal_type,
            origin=SignalOrigin.GROUNDING,
            content=signal.content,
            strength=signal.strength,
            valence=valence,
            confidence=confidence,
            features=features,
            source_id=signal.signal_id,
            parent_id=signal.signal_id,
            metadata={
                **signal.metadata,
                "core_concepts": core_concepts,
                "intent":        intent,
                "grounded_by":   "internal",
                "known_ratio":   round(known_ratio, 3),
            },
        )

    def update_idf(self, token: str, doc_count_containing: int, total_docs: int):
        """Update IDF score for a token as more documents are processed."""
        if doc_count_containing > 0 and total_docs > 0:
            self._idf_cache[token] = math.log(total_docs / doc_count_containing)
        self._doc_count = total_docs

    def _tokenize(self, text: str) -> List[str]:
        """Clean tokenization — removes punctuation, stop words, short tokens."""
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        return [
            t for t in tokens
            if t not in _STOP_WORDS and len(t) > 2
        ]

    def _extract_features(self, tokens: List[str]) -> Dict[str, float]:
        """
        TF-IDF-like feature extraction.
        TF: term frequency in this signal
        IDF: inverse document frequency from accumulated experience
        """
        if not tokens:
            return {}

        # Term frequency
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        features: Dict[str, float] = {}
        max_tf = max(tf.values())

        for token, count in tf.items():
            tf_score = count / max_tf
            idf_score = self._idf_cache.get(token, 1.0)  # Default IDF=1 for unknown
            tfidf = tf_score * idf_score
            # Normalize to [0, 1]
            features[token] = min(1.0, tfidf / 5.0)

        return features

    def _enrich_from_memory(
        self,
        features: Dict[str, float],
        tokens: List[str],
        semantic_context: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Enrich features using semantic memory insights.
        If a token matches a known concept, pull in its associated features.
        """
        enriched = features.copy()

        for insight in semantic_context:
            content = insight.get("content", "")
            confidence = insight.get("confidence", 0.5)
            if not content:
                continue

            insight_tokens = self._tokenize(content.lower())
            overlap = set(tokens) & set(insight_tokens)

            if overlap:
                # This insight is relevant — add its tokens as weak features
                for t in insight_tokens:
                    if t not in enriched and t not in _STOP_WORDS:
                        enriched[t] = enriched.get(t, 0.0) + 0.1 * confidence

        return enriched

    def _compute_valence(
        self, tokens: List[str], features: Dict[str, float]
    ) -> float:
        """Compute emotional valence from lexicon."""
        pos_score = sum(features.get(t, 0.3) for t in tokens if t in _POSITIVE_WORDS)
        neg_score = sum(features.get(t, 0.3) for t in tokens if t in _NEGATIVE_WORDS)

        total = pos_score + neg_score
        if total == 0:
            return 0.0

        return (pos_score - neg_score) / total

    def _detect_intent(self, text: str) -> str:
        """Detect communicative intent from pattern matching."""
        text_lower = text.lower().strip()
        for intent, patterns in _INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        return "statement"
