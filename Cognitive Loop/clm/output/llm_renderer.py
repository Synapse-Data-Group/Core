"""
CLM - Cognitive Language Model
output/llm_renderer.py

LLM-based output renderer — used during infancy.
Converts the network's activation state into fluent language
by asking an LLM to articulate what the network is "thinking."

The LLM doesn't reason here — it only translates.
The reasoning already happened in the network.
"""

from __future__ import annotations
import json
import re
import logging
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from clm.output.base import OutputGenerator

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal, ActivationVector
    from clm.memory.semantic import SemanticMemory

logger = logging.getLogger(__name__)

_RENDER_PROMPT = """You are a language renderer for a cognitive AI system.
The system has processed an input and reached the following cognitive state.
Your job: articulate this state as a natural, helpful response.
Do NOT add new reasoning. Only express what the cognitive state contains.

Active concepts (most to least active):
{active_concepts}

Semantic context (what the system knows):
{semantic_context}

Original input: "{original_input}"

Confidence level: {confidence:.0%}
Emotional valence: {valence}

Generate a natural response that expresses this cognitive state.
Be concise. Match the confidence level in your tone.
Response:"""


class LLMRenderer(OutputGenerator):
    """
    Renders output using an LLM during infancy.
    Supports Ollama (local/sovereign), OpenAI, Anthropic.
    """

    def __init__(
        self,
        provider:        str = "ollama",
        model:           Optional[str] = None,
        api_key:         Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model:    str = "llama3.2",
        max_tokens:      int = 400,
        temperature:     float = 0.7,
    ):
        super().__init__()
        self.provider        = provider
        self.api_key         = api_key
        self.ollama_base_url = ollama_base_url
        self.ollama_model    = ollama_model
        self.max_tokens      = max_tokens
        self.temperature     = temperature
        self.model           = model or (
            "gpt-4o-mini"           if provider == "openai"
            else "claude-haiku-20240307" if provider == "anthropic"
            else ollama_model
        )
        self._client = None

    def generate(
        self,
        activation:      "ActivationVector",
        session_signals: List["CognitiveSignal"],
        semantic_memory: "SemanticMemory",
        confidence:      float,
    ) -> Tuple[str, Dict[str, Any]]:
        self.total_calls += 1
        self.used_llm_last_call = True
        self.llm_calls += 1

        # Build context for the prompt
        active_concepts = self._format_active_concepts(activation)
        original_input  = self._get_last_input(session_signals)
        valence         = self._get_valence(session_signals)
        semantic_ctx    = self._format_semantic_context(
            semantic_memory, original_input
        )

        prompt = _RENDER_PROMPT.format(
            active_concepts=active_concepts,
            semantic_context=semantic_ctx,
            original_input=original_input[:200],
            confidence=confidence,
            valence=self._valence_label(valence),
        )

        try:
            text = self._call_llm(prompt).strip()
            meta = {
                "rendered_by": f"llm:{self.provider}",
                "confidence":  confidence,
                "valence":     valence,
            }
            return text, meta
        except Exception as e:
            logger.warning(f"LLM render failed: {e}. Using fallback.")
            return self._fallback_render(activation, confidence), {"rendered_by": "fallback"}

    def _call_llm(self, prompt: str) -> str:
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _call_ollama(self, prompt: str) -> str:
        import urllib.request
        payload = json.dumps({
            "model":  self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": self.max_tokens, "temperature": self.temperature},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read()).get("response", "")

    def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return resp.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        from anthropic import Anthropic
        if self._client is None:
            self._client = Anthropic(api_key=self.api_key)
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    def _format_active_concepts(self, activation: "ActivationVector") -> str:
        top = activation.top_k(k=10)
        if not top:
            return "No strongly active concepts."
        lines = []
        for nid, strength in top:
            lines.append(f"  - {nid[:8]}... (strength={strength:.2f})")
        return "\n".join(lines)

    def _format_semantic_context(
        self, semantic_memory: "SemanticMemory", query: str
    ) -> str:
        insights = semantic_memory.get_relevant_insights(query, k=3)
        if not insights:
            return "No relevant semantic context yet."
        return "\n".join(
            f"  - {ins.get('content', '')}" for ins in insights
        )

    def _get_last_input(self, session_signals: List["CognitiveSignal"]) -> str:
        for sig in reversed(session_signals):
            if sig.metadata.get("role") == "user" or sig.metadata.get("perception") == "conversation":
                return sig.content
        return session_signals[-1].content if session_signals else ""

    def _get_valence(self, session_signals: List["CognitiveSignal"]) -> float:
        if not session_signals:
            return 0.0
        valences = [s.valence for s in session_signals[-5:]]
        return sum(valences) / len(valences)

    def _valence_label(self, valence: float) -> str:
        if valence > 0.3:
            return "positive"
        if valence < -0.3:
            return "negative"
        return "neutral"

    def _fallback_render(self, activation: "ActivationVector", confidence: float) -> str:
        top = activation.top_k(k=5)
        if not top:
            return "I'm processing but haven't formed a clear response yet."
        concepts = [nid[:8] for nid, _ in top]
        return f"My current cognitive state involves: {', '.join(concepts)}. (confidence: {confidence:.0%})"
