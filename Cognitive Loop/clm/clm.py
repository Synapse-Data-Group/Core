"""
CLM - Cognitive Language Model
clm.py

Main entry point. Wires all layers together into a single cognitive system.

Usage:
    from clm import CLM, CLMConfig

    # Infancy — with Ollama local LLM
    clm = CLM()
    clm.start()
    response = clm.chat("Hello, what are you?")

    # Infancy — with OpenAI
    clm = CLM(CLMConfig.openai(api_key="sk-..."))

    # Mature/Sovereign — no LLM
    clm = CLM(CLMConfig.sovereign())

    # As a server (OpenAI-compatible API)
    clm.serve(host="0.0.0.0", port=8000)

    # As a local CLI
    clm.cli()
"""

from __future__ import annotations
import logging
import os
from typing import Any, Dict, List, Optional

from clm.config import CLMConfig
from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin
from clm.core.state import CognitiveState
from clm.core.cognitive_loop import CognitiveLoop
from clm.neurons.network import NeuronNetwork
from clm.neurons.hebbian import TriFactorLearner
from clm.grounding.llm_grounder import LLMGrounder
from clm.grounding.internal_grounder import InternalGrounder
from clm.grounding.hybrid_grounder import HybridGrounder
from clm.memory.episodic import EpisodicMemory
from clm.memory.semantic import SemanticMemory
from clm.perception.conversation import ConversationPerception
from clm.perception.web import WebPerception
from clm.perception.feed import FeedPerception
from clm.perception.document import DocumentPerception
from clm.perception.base import PerceptionConfig as PerceptionSourceConfig
from clm.reasoning.contradiction import ContradictionDetector
from clm.reasoning.metacognition import Metacognition
from clm.reasoning.simulation import SimulationWorkspace
from clm.reasoning.concept_graph import ConceptGraph
from clm.reasoning.consolidation import ConsolidationEngine
from clm.perception.trust import SourceTrustManager
from clm.output.llm_renderer import LLMRenderer
from clm.output.internal_renderer import InternalRenderer
from clm.output.hybrid_renderer import HybridRenderer
from clm.development.maturity import MaturityTracker
from clm.development.phases import DevelopmentalPhase


class CLM:
    """
    Cognitive Language Model.

    A self-developing cognitive AI system that:
    - Starts with LLM grounding (infancy)
    - Learns from every conversation and web experience
    - Progressively internalizes its own grounding
    - Eventually operates with zero LLM dependency (sovereign)
    - Runs on commodity hardware — no GPU required at maturity

    The system is always running. Input perturbs state.
    Output emerges when the network settles. Bidirectional by design.
    """

    def __init__(self, config: Optional[CLMConfig] = None):
        self.config = config or CLMConfig.default()
        self._setup_logging()

        # ── Development tracker (first — others depend on it)
        self.maturity_tracker = MaturityTracker(
            storage_path=self.config.storage_path(self.config.memory.maturity_file)
        )

        # ── Memory systems
        self.episodic_memory = EpisodicMemory(
            storage_path=self.config.storage_path(self.config.memory.episodic_file)
        )
        self.semantic_memory = SemanticMemory(
            storage_path=self.config.storage_path(self.config.memory.semantic_file)
        )

        # Sync maturity tracker with loaded memory state
        self.maturity_tracker.sync_from_memory(
            episode_count=self.episodic_memory.count(),
            insight_count=self.semantic_memory.count(),
        )

        # ── Neuron network
        self.network = NeuronNetwork(
            initial_size=self.config.network.initial_size,
            max_size=self.config.network.max_size,
            propagation_decay=self.config.network.propagation_decay,
            growth_threshold=self.config.network.growth_threshold,
            inhibition_ratio=self.config.network.inhibition_ratio,
            output_neuron_count=self.config.network.output_neuron_count,
            hebbian=HebbianLearner(),
        )

        # ── Grounding layer
        self.grounder = self._build_grounder()

        # ── Reasoning layer
        self.contradiction_detector = ContradictionDetector()
        self.metacognition = Metacognition(
            min_confidence=self.config.loop.output_confidence_threshold - 0.1,
        )
        self.simulation_workspace = SimulationWorkspace(
            n_trajectories=5,
            simulation_steps=4,
        )

        # ── Concept graph (internal semantic structure — language decoupled from cognition)
        self.concept_graph = ConceptGraph()

        # ── Consolidation engine (episodic → semantic compression + graph hygiene)
        self.consolidation_engine = ConsolidationEngine(
            episodes_per_cycle=self.config.loop.consolidation_interval_s or 50,
        )

        # ── Trust manager (web/feed source protection)
        self.trust_manager = SourceTrustManager()

        # ── Output layer (pass concept_graph to internal renderer)
        self.output_generator = self._build_output_generator()

        # ── Cognitive state
        self.state = CognitiveState(
            max_propagation_steps=50,
        )

        # ── Cognitive loop
        self.loop = CognitiveLoop(
            state=self.state,
            network=self.network,
            grounder=self.grounder,
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
            contradiction_detector=self.contradiction_detector,
            metacognition=self.metacognition,
            simulation_workspace=self.simulation_workspace,
            output_generator=self.output_generator,
            maturity_tracker=self.maturity_tracker,
            tick_interval=self.config.loop.tick_interval_s,
            reflection_interval=self.config.loop.reflection_interval_s,
            consolidation_interval=self.config.loop.consolidation_interval_s,
            output_confidence_threshold=self.config.loop.output_confidence_threshold,
            max_reflection_depth=self.config.loop.max_reflection_depth,
        )

        # ── Perception sources
        self.conversation_perception = ConversationPerception()
        self.web_perception          = self._build_web_perception()
        self.feed_perception         = self._build_feed_perception()
        self.document_perception     = DocumentPerception() if self.config.perception.document_enabled else None

        self._started = False
        logging.getLogger(__name__).info(
            f"CLM initialized | phase={self.maturity_tracker.phase.value} "
            f"maturity={self.maturity_tracker.score:.1%}"
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> "CLM":
        """Start the cognitive loop. Returns self for chaining."""
        if not self._started:
            self.loop.start()
            self._started = True
        return self

    def stop(self):
        """Stop the cognitive loop and persist state."""
        self.loop.stop()
        self.maturity_tracker.sync_from_memory(
            episode_count=self.episodic_memory.count(),
            insight_count=self.semantic_memory.count(),
        )
        self.maturity_tracker._save()
        self._started = False

    def __enter__(self) -> "CLM":
        return self.start()

    def __exit__(self, *args):
        self.stop()

    # ── Primary interface ─────────────────────────────────────────────────────

    def chat(self, message: str, timeout: float = 30.0) -> Optional[str]:
        """
        Send a message and wait for a response.
        Primary synchronous interface — works like an LLM call.
        """
        if not self._started:
            self.start()

        # Route through conversation perception
        for signal in self.conversation_perception.perceive(message):
            response = self.loop.perceive_and_wait(
                signal.content,
                timeout=timeout,
                metadata=signal.metadata,
            )
            return response

        return None

    def perceive_async(self, message: str) -> str:
        """
        Inject input without waiting for response.
        Register on_output callback to receive response.
        Returns signal_id.
        """
        if not self._started:
            self.start()
        return self.loop.perceive(message)

    def on_output(self, callback):
        """Register callback for streaming output."""
        self.loop.on_output(callback)

    def feedback(self, value: float, was_correct: Optional[bool] = None):
        """
        Inject explicit feedback about the last response.
        value: 0.0=wrong, 0.5=neutral, 1.0=correct/helpful
        Routes to tri-factor learner (neuromodulation) + maturity tracker.
        """
        if not self._started:
            self.start()
        self.loop.feedback(value, was_correct)

    def learn_from_url(self, url: str) -> int:
        """
        Fetch a URL and inject its content as learning experience.
        Returns number of signals injected.
        Gated by developmental phase. Trust-weighted before injection.
        """
        if not self._started:
            self.start()

        phase_cfg = self.maturity_tracker.phase_config
        if not phase_cfg.web_browsing_allowed:
            raise PermissionError(
                f"Web browsing not allowed in {self.maturity_tracker.phase.value} phase. "
                f"System needs more experience first."
            )

        if not self.web_perception:
            raise RuntimeError("Web perception not configured.")

        count = 0
        for signal in self.web_perception.perceive(url):
            # Trust-weight every web signal before injection
            scaled, trust = self.trust_manager.assess(signal, self.semantic_memory)
            if scaled is not None:
                self.state.push_input(scaled)
                count += 1
        return count

    def learn_from_search(self, query: str, max_results: int = 3) -> int:
        """
        Search the web (sovereign — DuckDuckGo HTML, no API key) and learn.
        Returns number of signals injected. Trust-weighted before injection.
        """
        if not self._started:
            self.start()

        phase_cfg = self.maturity_tracker.phase_config
        if not phase_cfg.web_browsing_allowed:
            raise PermissionError(
                f"Autonomous search not allowed in {self.maturity_tracker.phase.value} phase."
            )

        if not self.web_perception:
            raise RuntimeError("Web perception not configured.")

        count = 0
        for signal in self.web_perception.search_and_perceive(query, max_results):
            scaled, trust = self.trust_manager.assess(signal, self.semantic_memory)
            if scaled is not None:
                self.state.push_input(scaled)
                count += 1
        return count

    def learn_from_document(self, path: str) -> int:
        """Read a local document and inject as learning experience."""
        if not self._started:
            self.start()
        if not self.document_perception:
            raise RuntimeError("Document perception not configured.")
        count = 0
        for signal in self.document_perception.perceive(path):
            self.state.push_input(signal)
            count += 1
        return count

    def add_feed(self, url: str):
        """Subscribe to an RSS/Atom feed for continuous learning."""
        if self.feed_perception:
            self.feed_perception.add_feed(url)

    def consolidate(self) -> Dict[str, Any]:
        """
        Trigger a manual consolidation cycle.

        Runs the full consolidation pipeline:
          1. Ebbinghaus decay on episodic memory
          2. TF-IDF concept extraction across episodes
          3. DBSCAN episode clustering → semantic insights
          4. Stable episode promotion to semantic memory
          5. ConceptGraph hygiene (decay + synonym merge + PageRank pruning)
          6. Confidence recalibration

        This is the "sleep cycle" — call it after heavy learning sessions
        or let the cognitive loop trigger it automatically every N episodes.
        """
        report = self.consolidation_engine.run_cycle(
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
            concept_graph=self.concept_graph,
        )
        return report.to_dict()

    # ── Deployment ────────────────────────────────────────────────────────────

    def serve(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Start as an HTTP server with OpenAI-compatible API.
        Apps can use CLM as a drop-in LLM replacement.
        Requires: pip install fastapi uvicorn
        """
        if not self._started:
            self.start()
        from clm.deployment.server import serve as _serve
        _serve(self, host=host, port=port)

    def cli(self):
        """Start interactive CLI session."""
        if not self._started:
            self.start()
        from clm.deployment.local import run_cli
        run_cli(self)

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Full system status."""
        return {
            "running":   self._started,
            "phase":     self.maturity_tracker.phase.value,
            "maturity":  self.maturity_tracker.get_stats(),
            "state":     self.state.snapshot(),
            "network":   self.network.get_stats(),
            "loop":      self.loop.get_stats(),
            "simulation":     self.simulation_workspace.get_stats(),
            "trust":          self.trust_manager.get_stats(),
            "concept_graph":  self.concept_graph.get_stats(),
            "consolidation":  self.consolidation_engine.get_stats(),
            "memory": {
                "episodes": self.episodic_memory.count(),
                "insights": self.semantic_memory.count(),
            },
            "perception": {
                "conversation": self.conversation_perception.get_stats(),
                "web":  self.web_perception.get_stats() if self.web_perception else None,
                "feed": self.feed_perception.get_stats() if self.feed_perception else None,
            },
        }

    def maturity_report(self) -> Dict[str, Any]:
        """Developmental maturity report."""
        return self.maturity_tracker.get_stats()

    # ── Builder helpers ───────────────────────────────────────────────────────

    def _build_grounder(self) -> HybridGrounder:
        provider = self.config.llm.provider

        if provider == "none":
            # Sovereign mode — internal only
            internal = InternalGrounder(semantic_memory=self.semantic_memory)
            grounder = HybridGrounder(
                internal_grounder=internal,
                maturity_provider=self.maturity_tracker,
                llm_only_threshold=0.0,
                internal_only_threshold=0.0,  # Always internal
            )
        else:
            llm = LLMGrounder(
                provider=provider,
                model=self.config.llm.model,
                api_key=self.config.llm.api_key,
                ollama_base_url=self.config.llm.ollama_base_url,
                ollama_model=self.config.llm.ollama_model,
                max_tokens=200,
                temperature=0.1,
            )
            internal = InternalGrounder(semantic_memory=self.semantic_memory)
            grounder = HybridGrounder(
                llm_grounder=llm,
                internal_grounder=internal,
                maturity_provider=self.maturity_tracker,
            )

        return grounder

    def _build_output_generator(self) -> HybridRenderer:
        provider = self.config.llm.provider
        internal = InternalRenderer(concept_graph=self.concept_graph)

        if provider == "none":
            renderer = HybridRenderer(
                internal_renderer=internal,
                maturity_provider=self.maturity_tracker,
                llm_only_threshold=0.0,
                internal_only_threshold=0.0,
            )
        else:
            llm = LLMRenderer(
                provider=provider,
                model=self.config.llm.model,
                api_key=self.config.llm.api_key,
                ollama_base_url=self.config.llm.ollama_base_url,
                ollama_model=self.config.llm.ollama_model,
                max_tokens=self.config.llm.max_tokens,
                temperature=self.config.llm.temperature,
            )
            renderer = HybridRenderer(
                llm_renderer=llm,
                internal_renderer=internal,
                maturity_provider=self.maturity_tracker,
            )

        return renderer

    def _build_web_perception(self) -> Optional[WebPerception]:
        if not self.config.perception.web_enabled:
            return None
        cfg = PerceptionSourceConfig(
            enabled=True,
            max_content_length=self.config.perception.web_chunk_size * 20,
            rate_limit_per_min=30,
            allowed_domains=self.config.perception.web_allowed_domains,
            blocked_domains=self.config.perception.web_blocked_domains,
        )
        return WebPerception(
            config=cfg,
            user_agent=self.config.perception.web_user_agent,
            chunk_size=self.config.perception.web_chunk_size,
        )

    def _build_feed_perception(self) -> Optional[FeedPerception]:
        if not self.config.perception.feed_enabled:
            return None
        fp = FeedPerception()
        for url in self.config.perception.feed_urls:
            fp.add_feed(url)
        return fp

    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config.log_level, logging.WARNING),
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        )
