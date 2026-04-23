"""
CLM - Cognitive Language Model
grounding/llm_grounder.py

LLM-based grounding — used during infancy.
Converts raw text into structured feature vectors by asking an LLM
to decompose the meaning into semantic components.

This is the ONLY place in CLM where an LLM is used for grounding.
As maturity increases, this is replaced by internal_grounder.py.

Sovereign design: supports OpenAI, Anthropic, Ollama (local).
No mandatory cloud dependency — Ollama works fully offline.
"""

from __future__ import annotations
import json
import re
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from clm.grounding.base import GroundingProvider

if TYPE_CHECKING:
    from clm.core.signal import CognitiveSignal

logger = logging.getLogger(__name__)

_GROUNDING_PROMPT = """You are a semantic grounding system for a cognitive AI.
Your task: decompose the following text into semantic features.

Text: "{text}"

Context from memory:
{memory_context}

Return ONLY a JSON object with this exact structure:
{{
  "features": {{
    "feature_name": weight_0_to_1,
    ...
  }},
  "valence": -1.0_to_1.0,
  "confidence": 0.0_to_1.0,
  "core_concepts": ["concept1", "concept2"],
  "intent": "question|statement|command|expression"
}}

Rules:
- features: 5-15 semantic concepts present in the text, each with a weight 0.0-1.0
- valence: emotional tone (-1=very negative, 0=neutral, 1=very positive)
- confidence: how clear/unambiguous the text is
- core_concepts: 2-5 most important concepts (single words or short phrases)
- intent: the communicative intent

JSON only, no explanation:"""


class LLMGrounder(GroundingProvider):
    """
    Grounds signals using an LLM during the infancy phase.

    Supports:
    - OpenAI (gpt-4o-mini by default — cheapest capable model)
    - Anthropic (claude-haiku — cheapest)
    - Ollama (local, fully sovereign — preferred when available)
    """

    def __init__(
        self,
        provider: str = "ollama",          # "ollama" | "openai" | "anthropic"
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2",    # Small, fast local model
        max_tokens: int = 300,
        temperature: float = 0.1,          # Low temp for consistent grounding
    ):
        super().__init__()
        self.provider        = provider
        self.api_key         = api_key
        self.ollama_base_url = ollama_base_url
        self.ollama_model    = ollama_model
        self.max_tokens      = max_tokens
        self.temperature     = temperature

        # Set default models per provider
        if model:
            self.model = model
        elif provider == "openai":
            self.model = "gpt-4o-mini"
        elif provider == "anthropic":
            self.model = "claude-haiku-20240307"
        elif provider == "ollama":
            self.model = ollama_model
        else:
            self.model = "gpt-4o-mini"

        self._client = None

    def ground(
        self,
        signal: "CognitiveSignal",
        memories: List[Dict[str, Any]],
        semantic_context: List[Dict[str, Any]],
    ) -> "CognitiveSignal":
        """Ground signal using LLM."""
        self.total_calls += 1
        self.used_llm_last_call = True
        self.llm_calls += 1

        memory_context = self._format_memory_context(memories, semantic_context)
        prompt = _GROUNDING_PROMPT.format(
            text=signal.content[:500],
            memory_context=memory_context,
        )

        try:
            raw_response = self._call_llm(prompt)
            parsed = self._parse_response(raw_response)
            return self._apply_grounding(signal, parsed)
        except Exception as e:
            logger.warning(f"LLM grounding failed: {e}. Using fallback.")
            return self._fallback_ground(signal)

    def _call_llm(self, prompt: str) -> str:
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama — fully sovereign, no API key needed."""
        try:
            import urllib.request
            import urllib.error
            payload = json.dumps({
                "model":  self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": self.max_tokens,
                    "temperature": self.temperature,
                }
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.ollama_base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {e}")

    def _call_openai(self, prompt: str) -> str:
        try:
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
        except ImportError:
            raise RuntimeError("openai package not installed: pip install openai")

    def _call_anthropic(self, prompt: str) -> str:
        try:
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
        except ImportError:
            raise RuntimeError("anthropic package not installed: pip install anthropic")

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM response")
        return json.loads(match.group())

    def _apply_grounding(
        self, signal: "CognitiveSignal", parsed: Dict[str, Any]
    ) -> "CognitiveSignal":
        """Apply parsed grounding to signal."""
        from clm.core.signal import CognitiveSignal, SignalOrigin
        grounded = CognitiveSignal(
            signal_type=signal.signal_type,
            origin=SignalOrigin.GROUNDING,
            content=signal.content,
            strength=signal.strength,
            valence=float(parsed.get("valence", 0.0)),
            confidence=float(parsed.get("confidence", 0.7)),
            features=parsed.get("features", {}),
            source_id=signal.signal_id,
            parent_id=signal.signal_id,
            metadata={
                **signal.metadata,
                "core_concepts": parsed.get("core_concepts", []),
                "intent":        parsed.get("intent", "statement"),
                "grounded_by":   f"llm:{self.provider}:{self.model}",
            },
        )
        return grounded

    def _fallback_ground(self, signal: "CognitiveSignal") -> "CognitiveSignal":
        """Minimal fallback grounding using word tokenization."""
        from clm.core.signal import CognitiveSignal, SignalOrigin
        words = [w.lower().strip(".,!?;:") for w in signal.content.split()]
        features = {w: 1.0 / max(len(words), 1) for w in words[:15] if len(w) > 2}
        return CognitiveSignal(
            signal_type=signal.signal_type,
            origin=SignalOrigin.GROUNDING,
            content=signal.content,
            strength=signal.strength * 0.6,
            valence=0.0,
            confidence=0.3,
            features=features,
            source_id=signal.signal_id,
            parent_id=signal.signal_id,
            metadata={**signal.metadata, "grounded_by": "fallback"},
        )

    def _format_memory_context(
        self,
        memories: List[Dict[str, Any]],
        semantic_context: List[Dict[str, Any]],
    ) -> str:
        parts = []
        for m in memories[:3]:
            content = m.get("content", m.get("signal_content", ""))
            if content:
                parts.append(f"- Past: {content[:80]}")
        for s in semantic_context[:2]:
            insight = s.get("content", "")
            if insight:
                parts.append(f"- Insight: {insight[:80]}")
        return "\n".join(parts) if parts else "No relevant context."
