# Synapse Core — Research Tools for AI Systems

**Author**: Ivan Luch / Synapse Data Group LTD.  
**License**: Apache 2.0 (Free for commercial use)  
**Status**: Research tools with production-ready implementations  

---

## What This Is

A collection of 7 independent tools for building AI systems. While these tools originated from research into continuous learning and sovereign AI, they are **fully functional, production-ready, and free to use** under Apache 2.0 license.

**Research Origins → Production Tools**

Each tool started as a research experiment to answer specific questions about AI systems:
- Can we measure cognitive load in AI agents?
- Can agents learn from experience across sessions?
- Can resilience be cognitive-aware?
- Can systems grow from LLM-dependent to sovereign?
- Which learning mechanisms actually work?

**But they're real tools you can use today** to build better AI systems.

---

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/Synapse-Data-Group/Core.git
cd Core
pip install -e .

# Or install individual tools
pip install cognitive-load-monitor
pip install synapse-meo
pip install smart-resilience
pip install synapse-clm
pip install synapse-orchestra
```

### Getting Started

Each tool includes comprehensive documentation with examples:

- **[Cognitive Load Monitor](./Cognitive%20Load%20Monitor/README.md)** - Add observability to AI agents
- **[MEO](./MEO/README.md)** - Add memory and learning to existing frameworks
- **[Smart Resilience](./Smart%20Resilience/README.md)** - Make agents resilient with cognitive awareness
- **[Orchestra](./Orchestra/README.md)** - Build production multi-agent systems
- **[Council](./Council/README.md)** - Add adversarial deliberation to decisions
- **[CLM](./Cognitive%20Loop/README.md)** - Explore sovereign AI systems
- **[NEURON](./NEURON/README.md)** - Research platform for learning mechanisms

---

## The Tools

### 🧠 **Cognitive Load Monitor**
**Research Question**: Can we measure cognitive load in AI agents?

**What it does**: Real-time monitoring of AI agent stress with 5 metrics
- Context pressure (token consumption)
- Reasoning complexity (steps + backtracking)
- Temporal stress (latency vs expected)
- Uncertainty (unresolved assumptions)
- Error recovery (self-corrections)

**Use for**: Production monitoring, load balancing, preventing failures

**Installation**: `pip install cognitive-load-monitor`

---

### 🧠 **MEO** (Memory, Evolution, Optimization)
**Research Question**: Can agents learn from experience across sessions?

**What it does**: Persistent memory and self-improvement for existing agents
- Episodic memory (workflow steps)
- Semantic memory (compressed insights)
- Policy adaptation (learns optimal strategies)

**Use for**: Making LangChain/Autogen agents learn from experience

**Installation**: `pip install synapse-meo`

---

### 🛡️ **Smart Resilience**
**Research Question**: Can resilience be cognitive-aware?

**What it does**: Resilience primitives that adapt based on system state
- Retry with 6 backoff strategies
- Circuit breaker with learning
- Rate limiting with cognitive awareness
- Timeout and fallback patterns

**Use for**: Production stability, preventing cascading failures

**Installation**: `pip install smart-resilience`

---

### 🧬 **CLM** (Cognitive Loop)
**Research Question**: Can systems grow from LLM-dependent to sovereign?

**What it does**: Self-developing cognitive system with continuous learning
- Tri-factor Hebbian learning
- ConceptGraph (typed relations)
- Maturity tracking (Infancy → Sovereign)
- Simulation workspace

**Use for**: Exploring sovereign AI, reducing LLM dependency

**Installation**: `pip install synapse-clm`

---

### 🔬 **NEURON**
**Research Question**: Which learning mechanisms actually work?

**What it does**: Research platform for validating learning mechanisms
- Self-organizing neural networks
- STDP (spike-timing-dependent plasticity)
- Evolutionary algorithms
- Metaplasticity

**Use for**: Research, validating new learning algorithms

**Installation**: Clone repository (not published to PyPI)

---

### 🎼 **Orchestra**
**Research Question**: How to orchestrate multi-agent systems with cognitive primitives?

**What it does**: Production multi-agent orchestration framework
- ParallelSwarm (5 consensus strategies)
- TreeOrchestrator (intelligent routing)
- WisdomLayer (meta-learning)
- CLM/MEO integration

**Use for**: Building production multi-agent systems

**Installation**: `pip install synapse-orchestra`

---

### 🏛️ **Council**
**Research Question**: Can adversarial deliberation improve decision quality?

**What it does**: Multi-agent debate framework
- Structured debate (proposal → challenge → rebuttal → vote)
- Fluid resourcing (dynamic agent spawning)
- Coalition formation
- Q-learning agents

**Use for**: Strategic decisions, adversarial reasoning

**Installation**: Clone repository (not published to PyPI)

---

## Research Context (Optional Reading)

### The Core Research Questions

1. **Continuous Learning**: Can AI systems learn from their own experience without retraining?
2. **Sovereign Intelligence**: Can systems reduce dependency on external LLM APIs?
3. **Cognitive Awareness**: Can we measure and manage cognitive load in AI agents?
4. **Adversarial Reasoning**: Can structured debate improve decision quality?

### Research-to-Production Pipeline

```
NEURON (Research Lab) → CLM (Production) → Users (Real World)
```

- **NEURON**: Validate new learning mechanisms
- **CLM**: Hardened mechanisms for production
- **Users**: Real-world deployment and feedback

### Current Research Status

**Validated (Production Ready)**:
- ✅ Cognitive Load Monitor (5 metrics, <25μs overhead)
- ✅ MEO (memory + learning, framework integration)
- ✅ Smart Resilience (cognitive-aware patterns)
- ✅ Orchestra (multi-agent orchestration)
- ✅ Council (structured debate)

**Research Stage**:
- 🔄 CLM (maturity tracking, sovereign capabilities)
- 🔄 NEURON (learning mechanism validation)

**What this means**: Most tools are production-ready. CLM and NEURON are experimental but functional.

---

## Production Use Cases

### Use Case 1: Add Observability to Existing Agents
Monitor cognitive load in real-time to prevent overload and optimize routing. Perfect for production AI systems handling high-volume transactions.

### Use Case 2: Make Agents Learn from Experience
Add persistent memory and self-improvement to LangChain, Autogen, or CrewAI agents. Agents learn optimal strategies over time without retraining.

### Use Case 3: Build Multi-Agent Systems
Coordinate multiple agents with parallel execution, consensus strategies, and intelligent routing. Ideal for complex tasks requiring specialized expertise.

### Use Case 4: Explore Sovereign AI
Build systems that reduce dependency on external LLM APIs through continuous learning. Perfect for data sovereignty and cost optimization.

### Use Case 5: Add Adversarial Reasoning
Implement structured debate for strategic decisions. Minority positions and devil's advocate perspectives improve decision quality.

### Use Case 6: Research New Learning Mechanisms
Validate STDP, evolutionary algorithms, and other learning approaches before production deployment.

---

## License and Usage Rights

**Apache 2.0 License** - You are free to:
- ✅ Use in commercial projects
- ✅ Modify and redistribute
- ✅ Create derivative works
- ✅ Use in production without attribution
- ✅ Sublicense and embed in your products

**No restrictions**: No commercial use limitations, no attribution required, no copyleft.

**Research Origin**: These tools originated from research but are released as production-ready software under Apache 2.0.

---

## Installation

### Individual Tools
```bash
# Core infrastructure
pip install cognitive-load-monitor
pip install synapse-meo
pip install smart-resilience

# Orchestration and intelligence
pip install synapse-orchestra
pip install synapse-clm

# Research tools (clone from repository)
git clone https://github.com/yourusername/synapse-core
cd synapse-core/Council
pip install -e .
cd ../NEURON
pip install -e .
```

### Full Repository
```bash
git clone https://github.com/yourusername/synapse-core
cd synapse-core
pip install -e .
```

### Requirements
- Python 3.8+
- Dependencies vary by tool (most have zero/minimal deps)
- CLM and NEURON: Zero dependencies (sovereign design)

---

## Documentation

- [Cognitive Load Monitor](./Cognitive%20Load%20Monitor/README.md)
- [MEO](./MEO/README.md)
- [Smart Resilience](./Smart%20Resilience/README.md)
- [CLM](./Cognitive%20Loop/README.md)
- [NEURON](./NEURON/README.md)
- [Orchestra](./Orchestra/README.md)
- [Council](./Council/README.md)

---

## Contributing

**Research Contributions**:
- New learning mechanisms (NEURON → CLM pipeline)
- Validation studies and experiments
- Performance benchmarks and improvements

**Production Contributions**:
- Bug fixes and stability improvements
- Documentation and examples
- Integration with other frameworks

**Process**:
1. Fork the repository
2. Create a feature branch
3. Add tests and documentation
4. Submit a pull request

---

## Support

**Community Support**:
- GitHub Issues (bug reports, feature requests)
- Discussions (questions, ideas)
- Community examples and tutorials

**Research Collaboration**:
- Academic partnerships
- Research grants and collaborations
- Joint publications and studies

---

## Citation

If you use Synapse Core in research, please cite:

```bibtex
@software{synapse_core,
  title={Synapse Core: Research Tools for AI Systems},
  author={Ivan Luch},
  year={2025},
  license={Apache-2.0},
  url={https://github.com/Synapse-Data-Group/Core}
}
```

---

**Last updated**: 2025-04-23  
**Version**: 1.0.0  
**License**: Apache 2.0  

---

*These tools originated from research into continuous learning and sovereign AI, but are released as production-ready software. Use them to build better AI systems today.*
