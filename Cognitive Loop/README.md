# CLM — Cognitive Language Model

**A self-developing cognitive AI system. Not a better LLM — a different kind of intelligence.**

---

## What CLM Is

Current LLMs are sophisticated pattern matchers over static training data. They are stateless, expensive to run, and incapable of genuine learning after training.

CLM is an alternative architecture built on a different premise:

> **Intelligence should be earned through experience, not downloaded from training data.**

CLM starts in infancy — bootstrapped by an LLM for grounding — and progressively internalizes its own cognitive capabilities until it operates with **zero LLM dependency** on commodity hardware.

---

## The Developmental Model

```
INFANCY         ADOLESCENT        MATURE           SOVEREIGN
─────────────────────────────────────────────────────────────
LLM grounds     LLM grounds       Internal mostly  No LLM at all
LLM renders     Internal renders  LLM for novelty  Pure cognition
No web access   Supervised web    Autonomous web   Fully open
maturity < 0.2  maturity < 0.6    maturity < 0.9   maturity ≥ 0.9
```

**Maturity score** is a composite of four measured dimensions — not just LLM independence:

```
maturity = 0.25 × independence_score      (LLM call reduction)
         + 0.30 × prediction_accuracy     (was output correct?)
         + 0.25 × calibration_score       (does confidence match correctness?)
         + 0.20 × compression_gain        (abstracting, not just memorizing?)
```

A system that stops calling the LLM but is always wrong scores **low**. Sovereignty must be earned through demonstrated competence.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       COGNITIVE LOOP                             │
│  (persistent, bidirectional, asynchronous)                       │
│                                                                  │
│  PERCEIVE → PROPAGATE → DELIBERATE → SIMULATE → GENERATE        │
│      ↑                                                  │        │
│      └────────────── REFLECT (self-signal) ─────────────┘        │
└──────────────────────────────────────────────────────────────────┘
         │                                         │
         ▼                                         ▼
┌──────────────────┐                   ┌───────────────────────┐
│  PERCEPTION      │                   │  OUTPUT               │
│  conversation    │                   │  LLM renderer         │
│  web (sovereign) │◀── trust filter ──│  → Internal renderer  │
│  RSS feeds       │                   │    (proposition-based)│
│  documents       │                   └───────────────────────┘
└──────────────────┘                              ▲
         │                                        │
         ▼                                        │
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  GROUNDING       │    │  NEURON NETWORK  │    │  REASONING          │
│  LLM (infancy)   │───▶│  Tri-factor      │───▶│  Simulation         │
│  → Internal      │    │  learning        │    │  (forward model)    │
│  (maturity)      │    │  Sparse, grows   │    │  Contradiction      │
└──────────────────┘    └──────────────────┘    │  Metacognition      │
                                │                │  Concept graph      │
                                ▼                └─────────────────────┘
                    ┌──────────────────────┐
                    │  MEMORY              │
                    │  Episodic (JSONL)    │
                    │  Semantic (JSONL)    │
                    └──────────────────────┘
```

---

## Core Design Principles

**1. LLM is a plugin, not a dependency**
The LLM is used only at the grounding boundary (input) and output boundary (rendering) during infancy. It never reasons. The network does the reasoning. At maturity, it is removed entirely.

**2. Tri-factor learning, not pure Hebbian**
Pure Hebbian learning memorizes correlations but fails at abstraction. CLM uses:
```
Δw = η × cofire × surprise × value
```
- `cofire` — Hebbian association (neurons fire together)
- `surprise` — prediction error (learn more from the unexpected)
- `value` — usefulness signal (dopamine-equivalent neuromodulation)

The network learns not just what co-occurs, but **what matters**.

**3. Think before speaking — Viterbi simulation**
Before generating output, the system runs the Viterbi algorithm over its `ConceptGraph` to find the most probable concept sequence given current activations. This is a Hidden Markov Model where hidden states are concepts, transitions are graph edges, and emissions are activation weights. Beam search provides diverse alternatives. The system is deliberative, not reactive.

```
State      = active concept node
Transition = edge_weight × relation_type_prior × stability
Emission   = alignment with current activation pattern
Score      = log P(path) = Σ log(transition) + Σ log(emission)
```

**4. Language is output formatting, not cognition**
The system builds a `ConceptGraph` of typed semantic relations (`IS_A`, `CAUSES`, `HAS`, etc.) from activation patterns. The internal renderer translates graph propositions into sentences. Language competence is not required for cognitive competence.

**5. ConceptGraph hygiene prevents representation collapse**
A closed cognitive loop amplifies noise without structural regularization. Four mechanisms prevent this:

| Mechanism | Algorithm | Purpose |
|---|---|---|
| Edge decay | Ebbinghaus `R = e^(-t/S)` | Unused relations fade |
| Stability growth | FSRS `S_new = S × (1 + 0.1 × R)` | Reinforced edges become permanent |
| Synonym merge | Jaccard + Levenshtein + Union-Find | Collapse duplicate concepts |
| Sparsification | PageRank power iteration | Prune peripheral low-evidence edges |
| Evidence gate | `provisional` flag | Single observations can't create permanent edges |

**6. Consolidation — the sleep cycle**
Knowledge is restructured periodically, not just accumulated. The `ConsolidationEngine` runs:
- **Ebbinghaus decay** on episodic memory — faded episodes are pruned
- **Online TF-IDF** across episodes — identifies domain-specific concepts worth promoting
- **DBSCAN clustering** of similar episodes — compresses clusters into semantic insights
- **Stable episode promotion** — high-stability individual episodes enter semantic memory
- **Confidence recalibration** — insight confidence updated by episodic support count

**7. Web learning is trust-weighted**
Every signal from the web passes through `SourceTrustManager` before injection:
- Domain reputation priors (Wikipedia=0.85, Reddit=0.25)
- Content quality signals
- Contradiction detection against existing beliefs
- Quarantine buffer for cross-validation of low-trust content

**8. Maturity is earned, not declared**
The system cannot advance phases by simply reducing LLM calls. It must demonstrate prediction accuracy, confidence calibration, and knowledge compression.

**9. Bidirectional by default**
Output re-enters the system as a self-signal. The system reflects on what it just said.

**10. Persistent across sessions**
Episodic memory, semantic memory, concept graph, maturity score, and consolidation state survive restarts.

---

## File Structure

```
clm/
├── core/
│   ├── signal.py          CognitiveSignal, ActivationVector
│   ├── state.py           CognitiveState (thread-safe)
│   └── cognitive_loop.py  Persistent bidirectional loop
│
├── neurons/
│   ├── base.py            MicroNeuron, neuron types, SynapticConnection
│   ├── hebbian.py         TriFactorLearner (Δw = cofire × surprise × value)
│   └── network.py         NeuronNetwork (propagation, growth, pruning)
│
├── grounding/
│   ├── base.py            GroundingProvider ABC
│   ├── llm_grounder.py    LLM-based grounding (infancy)
│   ├── internal_grounder.py  Semantic memory grounding (maturity)
│   └── hybrid_grounder.py Blends by maturity score
│
├── memory/
│   ├── episodic.py        Raw experience log (JSONL)
│   └── semantic.py        Compressed insights (JSONL)
│
├── perception/
│   ├── base.py            PerceptionSource ABC
│   ├── conversation.py    User input
│   ├── web.py             Sovereign web (urllib + html.parser, no APIs)
│   ├── feed.py            RSS/Atom feeds (xml.etree.ElementTree)
│   ├── document.py        Local files (txt, md, json, csv, html)
│   └── trust.py           SourceTrustManager (misinformation protection)
│
├── reasoning/
│   ├── contradiction.py   Contradiction detection and resolution
│   ├── metacognition.py   Output gate (confidence, load, coherence)
│   ├── simulation.py      SimulationWorkspace (Viterbi + beam search over ConceptGraph)
│   ├── concept_graph.py   ConceptGraph (typed relations + 4 hygiene mechanisms)
│   └── consolidation.py   ConsolidationEngine (TF-IDF + DBSCAN + Ebbinghaus + PageRank)
│
├── output/
│   ├── base.py            OutputGenerator ABC
│   ├── llm_renderer.py    LLM output (infancy)
│   ├── internal_renderer.py  Proposition-based sovereign output
│   └── hybrid_renderer.py Blends by maturity score
│
├── development/
│   ├── phases.py          DevelopmentalPhase, PhaseConfig, permissions
│   └── maturity.py        MaturityTracker (composite competence score)
│
├── deployment/
│   ├── server.py          FastAPI server (OpenAI-compatible API)
│   └── local.py           Interactive CLI
│
├── clm.py                 Main CLM class (wires all layers)
├── config.py              CLMConfig, all tuneable parameters
├── __init__.py            Public API
└── __main__.py            python -m clm entry point
```

---

## Installation

```bash
# Minimal — pure Python stdlib, zero mandatory dependencies
pip install synapse-clm

# With Ollama (recommended — local, sovereign LLM for infancy)
# Install Ollama: https://ollama.ai
ollama pull llama3.2

# With OpenAI for grounding
pip install synapse-clm openai

# With server deployment
pip install synapse-clm fastapi uvicorn
```

---

## Quick Start

### Basic conversation (Ollama local LLM)
```python
from clm import CLM

clm = CLM()  # Default: Ollama + llama3.2
clm.start()

response = clm.chat("Hello, what are you?")
print(response)

print(clm.maturity_report())
clm.stop()
```

### With OpenAI grounding
```python
from clm import CLM, CLMConfig

clm = CLM(CLMConfig.openai(api_key="sk-..."))
clm.start()
response = clm.chat("Explain quantum entanglement")
```

### Providing feedback (neuromodulation)
```python
response = clm.chat("What causes rain?")
print(response)

# Explicit feedback — routes to tri-factor learner
clm.feedback(1.0)   # correct/helpful
clm.feedback(0.0)   # wrong/harmful
clm.feedback(0.5)   # neutral

# Implicit feedback is inferred automatically from the next message
# ("no, that's wrong" → 0.2, "yes exactly" → 0.85, continuation → 0.65)
```

### As a drop-in LLM replacement (OpenAI-compatible API)
```python
clm = CLM()
clm.serve(host="0.0.0.0", port=8000)
# POST http://localhost:8000/v1/chat/completions
```

### Existing OpenAI apps — zero code changes
```python
from openai import OpenAI

client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:8000/v1"
)
response = client.chat.completions.create(
    model="clm-1",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Interactive CLI
```bash
python -m clm
# or
clm
```

### Teaching the system
```python
clm = CLM()
clm.start()

# Trust-weighted web learning (adolescent phase+)
clm.learn_from_url("https://en.wikipedia.org/wiki/Cognitive_science")
clm.learn_from_search("predictive coding neuroscience")

# Local documents
clm.learn_from_document("./research_paper.txt")

# Continuous RSS feed subscription
clm.add_feed("https://arxiv.org/rss/cs.AI")
```

### Manual consolidation (sleep cycle)
```python
# Run after heavy learning sessions to compress and restructure knowledge
report = clm.consolidate()
print(report)
# {
#   "episodes_processed": 87,
#   "episodes_promoted":  12,
#   "episodes_pruned":     3,
#   "insights_created":    8,
#   "clusters_found":      5,
#   "graph_hygiene": {"decayed": 14, "merged": 2, "pruned": 6},
#   "duration_ms":       42.1
# }
```

### Context manager
```python
with CLM() as clm:
    response = clm.chat("What is consciousness?")
    print(response)
# Automatically stops and saves state on exit
```

---

## Configuration

```python
from clm import CLM, CLMConfig

config = CLMConfig()

# LLM provider (infancy grounding only)
config.llm.provider        = "ollama"   # "ollama" | "openai" | "anthropic" | "none"
config.llm.ollama_model    = "llama3.2"
config.llm.ollama_base_url = "http://localhost:11434"

# Neuron network
config.network.initial_size = 500
config.network.max_size     = 50_000

# Memory storage
config.memory.storage_dir = "./my_clm_data"

# Web perception
config.perception.web_enabled         = True
config.perception.web_allowed_domains = ["wikipedia.org", "arxiv.org"]

# Cognitive loop
config.loop.output_confidence_threshold = 0.65
config.loop.tick_interval_s             = 0.05

clm = CLM(config)
```

---

## Developmental Phases

| Phase | Maturity | Episodes | Insights | LLM | Web |
|-------|----------|----------|----------|-----|-----|
| INFANCY | 0–20% | 0+ | 0+ | Always | No |
| ADOLESCENT | 20–60% | 100+ | 20+ | Grounding | Supervised |
| MATURE | 60–90% | 1,000+ | 200+ | Rarely | Autonomous |
| SOVEREIGN | 90%+ | 10,000+ | 1,000+ | Never | Fully open |

Track progress:
```python
print(clm.maturity_report())
# {
#   "maturity_score": 0.41,
#   "phase": "adolescent",
#   "score_breakdown": {
#     "independence":       0.55,
#     "prediction_accuracy": 0.62,
#     "calibration":        0.48,
#     "compression_gain":   0.21
#   },
#   "episode_count": 312,
#   "insight_count": 71,
#   "milestone_progress": {
#     "next_phase": "mature",
#     "maturity_score": {"current": 0.41, "required": 0.6, "pct": 68},
#     "episodes":       {"current": 312,  "required": 1000, "pct": 31},
#     "insights":       {"current": 71,   "required": 200,  "pct": 35}
#   }
# }
```

---

## API Endpoints (Server Mode)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat |
| `POST` | `/v1/perceive` | Raw signal injection |
| `GET`  | `/v1/status` | Full system state |
| `GET`  | `/v1/maturity` | Developmental report |
| `POST` | `/v1/perceive/web` | Trigger web learning |
| `POST` | `/v1/perceive/feed` | Add RSS feed |
| `GET`  | `/v1/memory/insights` | Semantic memory |
| `DELETE` | `/v1/session` | Clear session |
| `GET`  | `/health` | Health check |

---

## CLI Commands

```
You: /status      — System state snapshot
You: /maturity    — Developmental progress with milestone bars
You: /memory      — Recent semantic insights
You: /network     — Neuron network statistics
You: /web <url>   — Fetch URL and learn (trust-weighted)
You: /search <q>  — Sovereign web search (DuckDuckGo, no API key)
You: /quit        — Stop and save
```

---

## Sovereignty Principles

CLM is built on the same sovereign code philosophy as the Synapse ecosystem:

- **Zero mandatory dependencies** — pure Python stdlib for all core functionality
- **No search API keys** — DuckDuckGo HTML interface, direct HTTP
- **No cloud lock-in** — Ollama runs locally; at maturity, no LLM needed at all
- **No GPU required** — sparse neuron activation, commodity CPU at maturity
- **Persistent state** — JSONL files, no database required
- **Robots.txt respected** — ethical web crawling
- **Trust-weighted ingestion** — web content assessed before injection, not blindly absorbed

---

## How It Differs From LLMs

| | LLM | CLM |
|--|-----|-----|
| **Knowledge source** | Pre-training corpus | Lived experience |
| **Learning** | Offline, expensive | Continuous, free |
| **Learning rule** | Backpropagation | Tri-factor (cofire × surprise × value) |
| **State** | Stateless per call | Persistent, always evolving |
| **Reasoning** | Pattern completion | Viterbi simulation over concept graph |
| **Hardware** | GPU cluster | CPU at maturity |
| **Cost** | Per token, forever | Decreases over time |
| **Sovereignty** | Cloud dependent | Fully sovereign at maturity |
| **Failure mode** | Confidently wrong | Calibrated uncertainty |
| **Internet** | RAG (doesn't stick) | Trust-weighted, learns and retains |
| **Maturity metric** | N/A | Competence score (accuracy + calibration) |
| **Knowledge hygiene** | None (static) | Ebbinghaus decay + synonym merge + PageRank |
| **Consolidation** | None | DBSCAN clustering + TF-IDF compression |

---

## Part of the Synapse Ecosystem

```
CLM (this)             — Cognitive Language Model
Cognitive Load Monitor — Operational visibility for AI agents
MEO                    — Memory Embedded Orchestration
Orchestra              — AI orchestration framework
Council                — Multi-agent debate framework
Smart Resilience       — Cognitive-aware resilience primitives
NEURON                 — Self-organizing neural intelligence
```

---

*Author: Ivan Lluch / Synapse Data | License: Apache 2.0*
