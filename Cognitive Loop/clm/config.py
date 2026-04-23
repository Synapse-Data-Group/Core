"""
CLM - Cognitive Language Model
config.py

Central configuration. All tuneable parameters in one place.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LLMConfig:
    """LLM provider configuration (used during infancy only)."""
    provider:        str   = "ollama"          # "ollama" | "openai" | "anthropic"
    model:           Optional[str] = None
    api_key:         Optional[str] = None
    ollama_base_url: str   = "http://localhost:11434"
    ollama_model:    str   = "llama3.2"
    max_tokens:      int   = 400
    temperature:     float = 0.3


@dataclass
class NetworkConfig:
    """Neuron network configuration."""
    initial_size:       int   = 500
    max_size:           int   = 50_000
    propagation_decay:  float = 0.85
    growth_threshold:   float = 0.7
    inhibition_ratio:   float = 0.15
    output_neuron_count: int  = 20


@dataclass
class MemoryConfig:
    """Memory system configuration."""
    storage_dir:      str   = "./clm_data"
    episodic_file:    str   = "episodic.jsonl"
    semantic_file:    str   = "semantic.jsonl"
    maturity_file:    str   = "maturity.json"
    max_in_memory:    int   = 2_000
    consolidation_interval_s: float = 30.0


@dataclass
class PerceptionConfig:
    """Perception layer configuration."""
    web_enabled:          bool  = True
    web_user_agent:       str   = "CLM-Cognitive/1.0"
    web_chunk_size:       int   = 500
    web_allowed_domains:  List[str] = field(default_factory=list)
    web_blocked_domains:  List[str] = field(default_factory=list)
    feed_enabled:         bool  = True
    feed_urls:            List[str] = field(default_factory=list)
    document_enabled:     bool  = True
    document_chunk_size:  int   = 600


@dataclass
class CognitiveLoopConfig:
    """Cognitive loop timing configuration."""
    tick_interval_s:              float = 0.05
    reflection_interval_s:        float = 5.0
    consolidation_interval_s:     float = 30.0
    output_confidence_threshold:  float = 0.65
    max_reflection_depth:         int   = 3
    output_timeout_s:             float = 30.0


@dataclass
class CLMConfig:
    """
    Master configuration for the CLM system.
    Pass this to CLM() to customize behavior.
    """
    llm:        LLMConfig        = field(default_factory=LLMConfig)
    network:    NetworkConfig    = field(default_factory=NetworkConfig)
    memory:     MemoryConfig     = field(default_factory=MemoryConfig)
    perception: PerceptionConfig = field(default_factory=PerceptionConfig)
    loop:       CognitiveLoopConfig = field(default_factory=CognitiveLoopConfig)

    # Logging
    log_level:  str = "WARNING"

    def storage_path(self, filename: str) -> str:
        import os
        return os.path.join(self.memory.storage_dir, filename)

    @classmethod
    def default(cls) -> "CLMConfig":
        """Default config — Ollama local LLM, conservative settings."""
        return cls()

    @classmethod
    def openai(cls, api_key: str, model: str = "gpt-4o-mini") -> "CLMConfig":
        """Config preset for OpenAI grounding."""
        cfg = cls()
        cfg.llm.provider = "openai"
        cfg.llm.api_key  = api_key
        cfg.llm.model    = model
        return cfg

    @classmethod
    def anthropic(cls, api_key: str, model: str = "claude-haiku-20240307") -> "CLMConfig":
        """Config preset for Anthropic grounding."""
        cfg = cls()
        cfg.llm.provider = "anthropic"
        cfg.llm.api_key  = api_key
        cfg.llm.model    = model
        return cfg

    @classmethod
    def sovereign(cls) -> "CLMConfig":
        """
        Fully sovereign config — no LLM at all.
        Only valid for mature/sovereign phase systems loading saved state.
        """
        cfg = cls()
        cfg.llm.provider = "none"
        return cfg
