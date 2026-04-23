"""
CLM - Cognitive Language Model
output/internal_renderer.py

Internal output renderer — used at maturity. Zero LLM calls.

Key architectural shift from the original design:
  Language generation is NOT the core cognitive skill.
  The cognitive system builds internal semantic structures (ConceptGraph).
  This renderer translates those structures into language.

  graph → language   (this file)
  experience → graph (concept_graph.py + network)

This separation means:
  - The system doesn't need to learn grammar from scratch
  - It learns MEANING first, expression second
  - The renderer can be swapped (grammar-based, distilled LM, etc.)
    without touching the cognitive core

Pipeline:
  1. ActivationVector → active concept IDs
  2. ConceptGraph.get_summary_structure() → propositions + causal chains
  3. SemanticMemory → supporting insights
  4. Proposition serializer → natural language sentences
  5. Discourse assembler → coherent paragraph
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from clm.output.base import OutputGenerator

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal, ActivationVector
    from clm.memory.semantic import SemanticMemory
    from clm.reasoning.concept_graph import ConceptGraph


# ── Relation-to-language mapping ─────────────────────────────────────────────
# Maps typed semantic relations to natural language phrases.
# This is the only "language knowledge" hardcoded here — everything else
# comes from the concept graph and semantic memory.

_RELATION_PHRASES = {
    "is_a":        ["{s} is a type of {t}", "{s} is {t}", "{s} belongs to {t}"],
    "has":         ["{s} has {t}", "{s} contains {t}", "{s} includes {t}"],
    "causes":      ["{s} causes {t}", "{s} leads to {t}", "{s} results in {t}"],
    "part_of":     ["{s} is part of {t}", "{s} belongs to {t}"],
    "opposite_of": ["{s} is the opposite of {t}", "{s} contrasts with {t}"],
    "similar_to":  ["{s} is similar to {t}", "{s} resembles {t}"],
    "precedes":    ["{s} comes before {t}", "{s} precedes {t}"],
    "follows":     ["{s} follows {t}", "{s} comes after {t}"],
    "used_for":    ["{s} is used for {t}", "{s} helps with {t}"],
    "located_in":  ["{s} is located in {t}", "{s} is found in {t}"],
    "created_by":  ["{s} was created by {t}", "{s} comes from {t}"],
    "associated":  ["{s} relates to {t}", "{s} is connected to {t}"],
}

_CONFIDENCE_OPENERS = {
    "high":   ["Based on what I know,", "I'm confident that", "Clearly,", "From experience,"],
    "medium": ["From what I understand,", "It seems that", "Based on my knowledge,"],
    "low":    ["I'm not fully certain, but", "My current understanding suggests",
               "I think, though I'm still learning, that"],
}

_CAUSAL_CONNECTORS = ["This leads to", "As a result,", "Consequently,", "This causes"]
_ADDITIVE_CONNECTORS = ["Furthermore,", "Additionally,", "Also,", "Moreover,"]


class InternalRenderer(OutputGenerator):
    """
    Sovereign output renderer. Zero LLM calls.

    Translates internal semantic structures (ConceptGraph propositions,
    causal chains, semantic memory insights) into natural language.

    Language is the output format, not the cognitive substrate.
    The system thinks in propositions and relations, speaks in sentences.
    """

    def __init__(self, concept_graph: Optional["ConceptGraph"] = None):
        super().__init__()
        self.concept_graph = concept_graph   # Injected by CLM; may be None early on

    def generate(
        self,
        activation:      "ActivationVector",
        session_signals: List["CognitiveSignal"],
        semantic_memory: "SemanticMemory",
        confidence:      float,
        concept_graph:   Optional["ConceptGraph"] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        self.total_calls += 1
        self.used_llm_last_call = False

        graph = concept_graph or self.concept_graph
        intent = self._get_intent(session_signals)

        # ── Path 1: ConceptGraph available → proposition-based rendering
        if graph is not None and graph.concept_count() > 0:
            response, meta = self._render_from_graph(
                activation, graph, semantic_memory, intent, confidence
            )
            if response:
                return response, meta

        # ── Path 2: Semantic memory only → insight-based rendering
        concepts = self._extract_concept_labels(activation, session_signals)
        if concepts:
            response, meta = self._render_from_memory(
                concepts, semantic_memory, intent, confidence
            )
            if response:
                return response, meta

        # ── Path 3: Fallback
        return self._uncertainty_response(confidence), {
            "rendered_by": "internal:fallback",
            "confidence": confidence,
        }

    # ── Graph-based rendering ─────────────────────────────────────────────────

    def _render_from_graph(
        self,
        activation:      "ActivationVector",
        graph:           "ConceptGraph",
        semantic_memory: "SemanticMemory",
        intent:          str,
        confidence:      float,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Primary rendering path: ConceptGraph → natural language.

        1. Get active concept IDs from activation
        2. Extract propositions and causal chains from graph
        3. Serialize propositions to sentences
        4. Assemble into coherent discourse
        """
        # Map activation to concept IDs via labels
        top_activation = activation.top_k(k=20)
        active_labels = [
            sig.metadata.get("label", "")
            for sig in []  # Will be populated from session signals
        ]

        # Get structured summary from graph
        active_ids = [nid for nid, strength in top_activation if strength > 0.25]
        summary = graph.get_summary_structure(active_ids, max_concepts=8)

        propositions = summary.get("propositions", [])
        causal_chains = summary.get("causal_chains", [])
        core_concepts = summary.get("core_concepts", [])

        if not propositions and not core_concepts:
            return "", {}

        # Serialize propositions to sentences
        sentences = self._propositions_to_sentences(propositions, confidence)

        # Add causal chain sentences
        causal_sentences = self._causal_chains_to_sentences(causal_chains)

        # Enrich with semantic memory insights
        if core_concepts:
            query = " ".join(c["label"] for c in core_concepts[:4])
            insights = semantic_memory.get_relevant_insights(query, k=3)
            insight_sentences = [
                ins.get("content", "") for ins in insights
                if ins.get("confidence", 0) > 0.5 and ins.get("content")
            ]
        else:
            insight_sentences = []

        # Assemble discourse
        response = self._assemble_discourse(
            sentences, causal_sentences, insight_sentences, confidence, intent
        )

        meta = {
            "rendered_by":    "internal:graph",
            "propositions":   len(propositions),
            "causal_chains":  len(causal_chains),
            "core_concepts":  [c["label"] for c in core_concepts[:5]],
            "confidence":     confidence,
        }
        return response, meta

    def _propositions_to_sentences(
        self,
        propositions: List[Tuple[str, str, str]],
        confidence:   float,
    ) -> List[str]:
        """Convert (subject, relation, object) triples to natural language sentences."""
        sentences = []
        seen_subjects = set()

        for subject, relation, obj in propositions[:6]:
            if not subject or not obj:
                continue
            # Avoid repeating the same subject too many times
            if subject in seen_subjects and len(seen_subjects) > 2:
                continue
            seen_subjects.add(subject)

            phrases = _RELATION_PHRASES.get(relation, _RELATION_PHRASES["associated"])
            phrase = random.choice(phrases)
            sentence = phrase.format(s=subject, t=obj)
            # Capitalize first letter
            sentence = sentence[0].upper() + sentence[1:] + "."
            sentences.append(sentence)

        return sentences

    def _causal_chains_to_sentences(
        self, chains: List[List[str]]
    ) -> List[str]:
        """Convert causal chains to narrative sentences."""
        sentences = []
        for chain in chains[:2]:
            if len(chain) < 3:
                continue
            # chain = [concept, "causes", effect, "causes", ...]
            parts = []
            i = 0
            while i < len(chain):
                if i == 0:
                    parts.append(chain[i].capitalize())
                elif chain[i] == "causes" and i + 1 < len(chain):
                    connector = random.choice(_CAUSAL_CONNECTORS)
                    parts.append(f". {connector} {chain[i+1]}")
                    i += 1
                i += 1
            if parts:
                sentences.append("".join(parts) + ".")
        return sentences

    def _assemble_discourse(
        self,
        sentences:         List[str],
        causal_sentences:  List[str],
        insight_sentences: List[str],
        confidence:        float,
        intent:            str,
    ) -> str:
        if not sentences and not insight_sentences:
            return ""

        # Choose confidence opener
        if confidence >= 0.75:
            opener = random.choice(_CONFIDENCE_OPENERS["high"])
        elif confidence >= 0.5:
            opener = random.choice(_CONFIDENCE_OPENERS["medium"])
        else:
            opener = random.choice(_CONFIDENCE_OPENERS["low"])

        parts = []

        # Lead with the strongest proposition
        if sentences:
            lead = sentences[0]
            # Prepend opener to lead sentence
            lead_lower = lead[0].lower() + lead[1:]
            parts.append(f"{opener} {lead_lower}")
            # Add remaining proposition sentences
            for s in sentences[1:3]:
                parts.append(s)

        # Add causal reasoning
        for s in causal_sentences[:1]:
            parts.append(s)

        # Add insight enrichment
        for s in insight_sentences[:2]:
            if s and s not in parts:
                connector = random.choice(_ADDITIVE_CONNECTORS)
                parts.append(f"{connector} {s[0].lower()}{s[1:]}")

        return " ".join(parts).strip()

    # ── Memory-based rendering (fallback) ─────────────────────────────────────

    def _render_from_memory(
        self,
        concepts:        List[str],
        semantic_memory: "SemanticMemory",
        intent:          str,
        confidence:      float,
    ) -> Tuple[str, Dict[str, Any]]:
        """Fallback: render from semantic memory insights when graph is sparse."""
        query = " ".join(concepts[:5])
        insights = semantic_memory.get_relevant_insights(query, k=5)

        if not insights:
            return "", {}

        best = max(insights, key=lambda x: x.get("confidence", 0))
        insight_text = best.get("content", "")
        if not insight_text:
            return "", {}

        if confidence >= 0.75:
            opener = random.choice(_CONFIDENCE_OPENERS["high"])
        elif confidence >= 0.5:
            opener = random.choice(_CONFIDENCE_OPENERS["medium"])
        else:
            opener = random.choice(_CONFIDENCE_OPENERS["low"])

        response = f"{opener} {insight_text[0].lower()}{insight_text[1:]}"

        if len(insights) > 1 and confidence > 0.6:
            second = insights[1].get("content", "")
            if second and second != insight_text:
                connector = random.choice(_ADDITIVE_CONNECTORS)
                response += f" {connector} {second[0].lower()}{second[1:]}"

        meta = {
            "rendered_by":   "internal:memory",
            "concepts":      concepts[:5],
            "insights_used": len(insights),
            "confidence":    confidence,
        }
        return response.strip(), meta

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_concept_labels(
        self,
        activation:      "ActivationVector",
        session_signals: List["CognitiveSignal"],
    ) -> List[str]:
        """Extract concept labels from activation and session signals."""
        labels = []
        # From session signals (grounding provides labels via metadata)
        for sig in reversed(session_signals[-5:]):
            label = sig.metadata.get("label") or sig.metadata.get("concept")
            if label:
                labels.append(label)
        # From top active neuron IDs (use label metadata if available)
        top = activation.top_k(k=10)
        for nid, strength in top:
            if strength > 0.3:
                labels.append(nid[:12])
        return labels[:10]

    def _get_intent(self, session_signals: List["CognitiveSignal"]) -> str:
        for sig in reversed(session_signals[-5:]):
            intent = sig.metadata.get("intent")
            if intent:
                return intent
        return "statement"

    def _uncertainty_response(self, confidence: float) -> str:
        if confidence < 0.3:
            return "I don't have enough knowledge about this yet to respond meaningfully."
        return random.choice([
            "My cognitive state hasn't settled on a clear response.",
            "I'm still developing my understanding of this topic.",
            "I have limited knowledge here — could you provide more context?",
        ])
