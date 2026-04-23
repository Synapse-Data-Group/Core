# Council Framework - Sentient Multi-Agent Debate System

A fully self-contained Python framework for **real** multi-agent debates with learning, memory, and evolutionary capabilities. Agents genuinely learn, adapt, and evolve through reinforcement learning and genetic algorithms. **No external dependencies required.**

## 🧠 Key Features

### **True Learning & Adaptation**
- ✅ **Q-Learning Engine**: Agents learn optimal strategies through reinforcement learning
- ✅ **Experience Memory**: Persistent memory system that stores and recalls past debates
- ✅ **Personality Evolution**: Genetic algorithms evolve agent traits based on performance
- ✅ **Adaptive Moderator**: Scoring system that learns from debate outcomes

### **No Rule-Based Limitations**
- ✅ **Dynamic Argument Generation**: No templates - arguments generated from learned patterns
- ✅ **Probabilistic Decision Making**: Agents use learned Q-values, not fixed rules
- ✅ **Cross-Debate Learning**: Knowledge transfers between debates
- ✅ **Emergent Behavior**: Strategies emerge from experience, not pre-programming

### **Agent Lifecycle Management**
- ✅ **Create/Kill Agents**: Dynamic agent management during debates
- ✅ **Tool System**: Agents can use tools for enhanced capabilities
- ✅ **Memory Persistence**: Save and load agent memories across sessions

### **🔥 Fluid Resourcing (Category-Defining)**
- ✅ **Moderator-Driven Spawning**: Moderator detects debate needs and spawns agents autonomously
- ✅ **10 Agent Archetypes**: Devil's advocate, mediator, innovator, analyst, pragmatist, visionary, skeptic, optimist, ethicist, specialist
- ✅ **Intelligent Detection**: Identifies lack of diversity, stalemates, missing perspectives, insufficient challenge
- ✅ **Automatic Termination**: Removes underperforming agents to optimize resources
- ✅ **Late Entry Participation**: Spawned agents immediately join ongoing debates
- ✅ **Zero-Agent Bootstrap**: Can start debates with no agents and spawn everything dynamically

### **🤝 Coalition Formation**
- ✅ **Dynamic Alliances**: Agents form coalitions based on proposal alignment
- ✅ **Coalition Voting**: Coalition members support each other's proposals
- ✅ **Automatic Detection**: System identifies aligned agents and suggests coalitions
- ✅ **Coalition Management**: Track formation, dissolution, and voting power

### **🧠 Knowledge Graph**
- ✅ **Concept Extraction**: Automatically extracts concepts from debate arguments
- ✅ **Relationship Mapping**: Builds semantic relationships between concepts
- ✅ **Persistent Knowledge**: Knowledge accumulates across debates
- ✅ **Concept Queries**: Agents can query related concepts for context
- ✅ **Graph Analytics**: Find shortest paths, central concepts, and patterns

### **🌐 Web Research**
- ✅ **Pure Python HTTP**: Uses urllib (no dependencies) for web fetching
- ✅ **HTML Parsing**: Extracts text content from web pages
- ✅ **Search Simulation**: Framework for integrating search APIs
- ✅ **Caching**: Automatic response caching with TTL
- ✅ **Tool Integration**: Agents use WebResearchTool for information gathering

### **⭐ Reputation & Trust**
- ✅ **Performance Tracking**: Tracks agent success rates and proposal quality
- ✅ **Trust Networks**: Agents build trust relationships over time
- ✅ **Influence Weighting**: High-reputation agents have more influence
- ✅ **Expert Recognition**: System identifies domain experts automatically
- ✅ **Reputation Evolution**: Scores evolve based on debate outcomes

### **😊 Emotion Simulation**
- ✅ **8 Emotional States**: Neutral, confident, frustrated, excited, anxious, satisfied, disappointed, determined
- ✅ **Dynamic Modifiers**: Emotions affect personality traits in real-time
- ✅ **Event Processing**: Emotions change based on debate events
- ✅ **Emotional Contagion**: Emotions spread between agents
- ✅ **Decay System**: Emotions gradually return to neutral

### **🔀 Debate Forking**
- ✅ **Parallel Exploration**: Fork debates to explore multiple solution paths
- ✅ **Stalemate Resolution**: Automatically fork when debates reach impasse
- ✅ **Result Synthesis**: Combine insights from all parallel debates
- ✅ **Consensus Calculation**: Measure agreement across fork outcomes
- ✅ **Best Path Selection**: Choose optimal solution from all explorations

### **🎯 Meta-Debate Layer**
- ✅ **Self-Modification**: Agents debate about debate rules themselves
- ✅ **Rule Proposals**: Agents propose changes to debate protocol
- ✅ **Democratic Voting**: Agents vote on meta-proposals
- ✅ **Dynamic Rules**: Debate rules evolve during execution
- ✅ **Meta-Cognition**: True self-awareness of debate process

### **📊 Argument Quality Metrics**
- ✅ **Logical Structure**: Analyzes argument coherence and flow
- ✅ **Evidence Assessment**: Evaluates strength of supporting evidence
- ✅ **Fallacy Detection**: Identifies logical fallacies in arguments
- ✅ **Clarity Scoring**: Measures argument clarity and readability
- ✅ **Real-Time Feedback**: Quality metrics available during debate

### **📎 Multi-Modal Support**
- ✅ **Text Integration**: Rich text content in arguments
- ✅ **Code Snippets**: Include code examples in proposals
- ✅ **Data Structures**: Embed JSON/structured data
- ✅ **Tool Outputs**: Integrate tool execution results
- ✅ **Reference System**: Link and resolve content references

## 📁 Project Structure

```
Council/
├── council_framework.py          # Legacy framework (basic version)
├── learning_engine.py             # Core learning systems (Q-learning, memory, evolution)
├── sentient_agent.py              # Sentient agent with learning capabilities
├── sentient_moderator.py          # Adaptive moderator with learning
├── sentient_debate_system.py     # Main debate orchestration system
├── agent_factory.py               # Agent factory with 10 archetypes
├── fluid_moderator.py             # Moderator with fluid resourcing capabilities
├── fluid_debate_system.py         # Debate system with dynamic agent spawning
├── coalition_system.py            # Coalition formation and management
├── knowledge_graph.py             # Knowledge graph construction and queries
├── web_fetcher.py                 # Pure Python web fetching (no dependencies)
├── reputation_system.py           # Reputation and trust network
├── emotion_system.py              # Emotion simulation engine
├── debate_forking.py              # Parallel debate exploration
├── meta_debate.py                 # Meta-debate layer and argument quality
├── multimodal_support.py          # Multi-modal content support
├── example_basic.py               # Basic usage example
├── example_advanced.py            # Advanced features demonstration
├── example_sentient.py            # Full sentient system demonstration
├── example_fluid.py               # Fluid resourcing demonstration
├── testing/
│   ├── test_runner.py            # Comprehensive test suite
│   ├── metrics_analyzer.py       # Performance analysis tools
│   ├── conversation_recorder.py  # Debate conversation tracking
│   ├── results/                  # Test results and debate logs
│   ├── conversations/            # Recorded debate transcripts
│   └── memories/                 # Persistent agent memories
└── README.md                      # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from sentient_debate_system import SentientDebateSystem

# Create a debate system
debate = SentientDebateSystem(
    problem="How should we approach climate change?",
    moderator_strategy="adaptive"
)

# Create agents (personalities are randomly initialized)
alice = debate.create_agent("Alice")
bob = debate.create_agent("Bob")
carol = debate.create_agent("Carol")

# Run the debate
result = debate.run_debate(max_rounds=2)
```

### Fluid Resourcing (Category-Defining Feature)

```python
from fluid_debate_system import FluidDebateSystem

# Create fluid debate system
debate = FluidDebateSystem(
    problem="Balance innovation with safety in AI?",
    moderator_strategy="adaptive"
)

# Start with just 2 agents - moderator spawns more as needed
debate.create_agent("Agent_1")
debate.create_agent("Agent_2")

# Moderator will:
# - Detect lack of diversity → spawn innovator
# - Detect stalemate → spawn mediator  
# - Detect insufficient challenge → spawn devil's advocate
# - Terminate underperforming agents
result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)

print(f"Started with 2, ended with {result['total_agents']} agents")
print(f"Spawned: {result['fluid_resourcing_stats']['total_spawned']}")
print(f"Terminated: {result['fluid_resourcing_stats']['total_terminated']}")

# Export results
debate.export_debate("debate_results.json")
debate.save_agent_memories("./memories")
```

### Learning Across Debates

```python
# First debate - agents learn from scratch
debate1 = SentientDebateSystem("Problem 1")
agent_a = debate1.create_agent("Agent_A")
result1 = debate1.run_debate(max_rounds=2)
debate1.save_agent_memories("./memories")

# Second debate - agents use learned knowledge
debate2 = SentientDebateSystem("Problem 2")
agent_a2 = debate2.create_agent(
    "Agent_A", 
    memory_path=f"./memories/agent_{agent_a.agent_id}_memory.pkl"
)
result2 = debate2.run_debate(max_rounds=2)
```

### Agent Lifecycle Management

```python
debate = SentientDebateSystem("Resource allocation problem")

# Create initial agents
agent1 = debate.create_agent("Agent_1")
agent2 = debate.create_agent("Agent_2")

# Run initial debate
debate.run_debate(max_rounds=1)

# Add new agent mid-process
agent3 = debate.create_agent("Agent_3")

# Remove underperforming agent
debate.kill_agent(agent1.agent_id)

# Continue debate with updated agent pool
```

### Personality Evolution

```python
debate = SentientDebateSystem("Economic strategy")

# Create agents
for i in range(3):
    debate.create_agent(f"Agent_{i}")

# Run debate
debate.run_debate(max_rounds=2)

# Evolve agent personalities based on performance
debate.evolve_agents()

# Agents now have evolved traits optimized for success
```

## 🧪 Running Tests

### Complete Test Suite

```bash
cd testing
python test_runner.py
```

This runs 7 comprehensive tests:
1. **Basic Three-Agent Debate** - Standard debate functionality
2. **Learning Progression** - Multi-debate learning demonstration
3. **Agent Lifecycle** - Create/kill agents dynamically
4. **Personality Evolution** - Genetic algorithm evolution
5. **Tool Usage** - Agent tool creation and management
6. **High-Intensity Debate** - 5 agents, 4 rounds
7. **Moderator Strategies** - Different scoring approaches

### Analyze Results

```bash
python metrics_analyzer.py
```

Generates comprehensive analysis:
- Agent performance statistics
- Debate dynamics metrics
- Learning progression tracking
- Moderator performance evaluation

### Record Conversations

```bash
python conversation_recorder.py
```

Creates:
- JSON conversation logs
- Human-readable transcripts
- Interaction pattern analysis

## 📊 Understanding the Output

### Debate Summary

```json
{
  "system_id": "unique-debate-id",
  "problem": "The debate question",
  "duration_seconds": 2.45,
  "total_agents": 3,
  "total_proposals": 3,
  "total_messages": 12,
  "final_decision": {
    "decision": "Accept proposal from Alice",
    "confidence": 0.78,
    "reasoning": "Detailed reasoning..."
  },
  "agent_stats": [...],
  "learning_insights": {...}
}
```

### Agent Statistics

```json
{
  "name": "Alice",
  "current_score": 72.5,
  "win_rate": 0.67,
  "debates_participated": 3,
  "wins": 2,
  "losses": 1,
  "memory_size": 156,
  "exploration_rate": 0.245,
  "personality": {
    "creativity": 0.78,
    "boldness": 0.65,
    "aggressiveness": 0.54
  }
}
```

## 🔧 Architecture

### Learning Engine (`learning_engine.py`)

**ExperienceMemory**
- Stores debate experiences with context
- Builds concept graphs for semantic understanding
- Tracks success patterns for different strategies
- Supports save/load for persistence

**QLearningEngine**
- Implements Q-learning for strategy optimization
- Exploration vs exploitation balance
- State-action value learning
- Adaptive exploration decay

**GeneticEvolution**
- Mutates personality traits based on performance
- Crossover between successful agents
- Fitness-based selection
- Generation tracking

**ArgumentGenerator**
- Generates dynamic arguments from learned patterns
- No fixed templates - uses component composition
- Personality-driven style adaptation
- Memory-informed content generation

### Sentient Agent (`sentient_agent.py`)

- **Learning**: Updates Q-values based on debate outcomes
- **Memory**: Recalls similar past situations
- **Evolution**: Personality traits mutate and evolve
- **Adaptation**: Strategies improve over time
- **Tools**: Can use external tools for enhanced capabilities

### Sentient Moderator (`sentient_moderator.py`)

- **Adaptive Scoring**: Learns optimal evaluation criteria
- **Confidence Calculation**: Assesses decision certainty
- **Dynamic Weighting**: Adjusts scoring weights based on outcomes
- **Memory-Informed**: Uses past evaluations to improve

### Debate System (`sentient_debate_system.py`)

- **Phase Management**: Proposal → Challenge → Rebuttal → Scoring → Resolution
- **Learning Phase**: Post-debate learning and evolution
- **Agent Lifecycle**: Dynamic creation and termination
- **Comprehensive Logging**: Detailed debate tracking

## 🎯 Use Cases

### 1. Research & Experimentation
- Study emergent behavior in multi-agent systems
- Test learning algorithms in debate contexts
- Analyze argument evolution over time

### 2. Decision Support
- Explore multiple perspectives on complex problems
- Generate diverse solution proposals
- Evaluate arguments systematically

### 3. AI Training
- Train agents through debate experience
- Develop argumentation strategies
- Test reinforcement learning approaches

### 4. Integration Foundation
- Pure Python - easy to integrate anywhere
- Modular design - extend with custom components
- JSON export - connect to other systems
- Memory persistence - long-term learning

## 🔌 Integration Examples

### As a Python Module

```python
from sentient_debate_system import SentientDebateSystem

def solve_problem_with_council(problem: str) -> dict:
    debate = SentientDebateSystem(problem)
    
    # Create expert agents
    for expert in ["Technical", "Business", "User"]:
        debate.create_agent(f"{expert}_Expert")
    
    result = debate.run_debate(max_rounds=3)
    
    return {
        "solution": result["final_decision"]["decision"],
        "confidence": result["final_decision"]["confidence"],
        "reasoning": result["final_decision"]["reasoning"]
    }
```

### With External APIs

```python
from sentient_debate_system import Tool

class APITool(Tool):
    def __init__(self, api_endpoint: str):
        super().__init__("api_tool", "API Tool")
        self.endpoint = api_endpoint
    
    def execute(self, query: str) -> str:
        # Call external API
        # return api_response
        pass

# Use in debate
debate = SentientDebateSystem("Problem")
agent = debate.create_agent("API_Agent")
api_tool = APITool("https://api.example.com")
debate.create_tool_for_agent(agent.agent_id, api_tool)
```

### Data Pipeline Integration

```python
import json

# Run debate
debate = SentientDebateSystem("Optimize pipeline")
# ... create agents and run ...

# Export for downstream processing
debate.export_debate("pipeline_debate.json")

# Load in another system
with open("pipeline_debate.json") as f:
    debate_data = json.load(f)
    # Process debate results
```

## 📈 Performance Characteristics

- **Memory Usage**: ~10-50MB per agent (depends on memory size)
- **Debate Duration**: 1-5 seconds for 3 agents, 2 rounds
- **Learning Speed**: Noticeable improvement after 3-5 debates
- **Scalability**: Tested up to 10 agents, 5 rounds

## 🛠️ Customization

### Custom Agent Personality

```python
custom_personality = {
    "creativity": 0.9,
    "boldness": 0.8,
    "aggressiveness": 0.3,
    "defensiveness": 0.5,
    "supportiveness": 0.7,
    "analytical_depth": 0.8,
    "evidence_reliance": 0.9,
    "confidence": 0.7,
    "optimism": 0.6,
    "verbosity": 0.5,
    "formality": 0.7
}

agent = debate.create_agent("Custom_Agent", personality=custom_personality)
```

### Custom Tools

```python
from sentient_debate_system import Tool

class CustomTool(Tool):
    def __init__(self):
        super().__init__("custom_001", "Custom Tool")
    
    def execute(self, *args, **kwargs):
        # Your custom logic
        return "Tool result"

tool = CustomTool()
debate.create_tool_for_agent(agent.agent_id, tool)
```

### Custom Moderator Strategy

Modify `sentient_moderator.py` scoring weights:

```python
moderator.scoring_weights = {
    "content_length": 0.15,
    "challenge_penalty": 0.10,
    "rebuttal_bonus": 0.25,
    "keyword_quality": 0.20,
    "coherence": 0.15,
    "novelty": 0.15
}
```

## 🔬 Technical Details

### Q-Learning Implementation
- **State Space**: Hashed from debate context (phase, counts, scores)
- **Action Space**: Strategy choices (propose types, challenge types, etc.)
- **Reward**: Normalized score difference (-1 to +1)
- **Learning Rate**: 0.1 (configurable)
- **Discount Factor**: 0.95 (configurable)
- **Exploration**: ε-greedy with decay

### Memory System
- **Capacity**: 10,000 experiences per agent
- **Retrieval**: Semantic similarity based on word overlap
- **Concept Graph**: Word-to-word association strengths
- **Success Patterns**: Rolling window of 100 outcomes per action

### Genetic Evolution
- **Mutation Rate**: 10% of traits
- **Mutation Strength**: ±20% Gaussian noise
- **Selection**: Fitness-proportional crossover
- **Elitism**: Top 25% preserved

## 📝 License & Usage

This is a foundational framework designed for integration into other projects. Use freely, extend as needed, and integrate into your systems.

## 🤝 Contributing

To extend the framework:

1. **Add new learning algorithms**: Extend `learning_engine.py`
2. **Create custom agents**: Inherit from `SentientAgent`
3. **Implement new moderators**: Inherit from `SentientModerator`
4. **Add tools**: Inherit from `Tool` class
5. **Enhance argument generation**: Modify `ArgumentGenerator`

## 📞 Support

For issues or questions:
- Check the examples in `example_*.py`
- Review test cases in `testing/test_runner.py`
- Examine debate logs in `testing/results/`
- Analyze conversation transcripts in `testing/conversations/`

## 🎓 Research Applications

This framework is suitable for:
- Multi-agent reinforcement learning research
- Argumentation theory studies
- Emergent behavior analysis
- Collective intelligence experiments
- Debate strategy evolution
- Decision-making system development

---

**Built with pure Python 3 - No dependencies required**
