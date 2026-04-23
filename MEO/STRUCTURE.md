# MEO Package Structure

```
MEO/
├── meo/
│   ├── __init__.py                    # Main package exports
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── default_settings.py        # Configuration settings
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── episodic.py                # Episode and EpisodicMemory classes
│   │   ├── semantic.py                # SemanticInsight and SemanticMemory classes
│   │   └── storage.py                 # StorageBackend implementations (JSONL, SQLite)
│   │
│   ├── evaluators/
│   │   ├── __init__.py
│   │   ├── reward.py                  # Evaluator and reward calculation
│   │   └── metrics.py                 # Helper metrics functions
│   │
│   ├── meta/
│   │   ├── __init__.py
│   │   └── policy_adapter.py          # PolicyAdapter and rule-based adaptation
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── hooks.py                   # Hook classes for interception
│   │   └── wrappers.py                # WisdomOrchestrator main class
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── encoders.py                # Embedding utilities
│   │   └── logging.py                 # Structured logging
│   │
│   └── integrations/
│       ├── __init__.py
│       ├── langchain_wrapper.py       # LangChain integration
│       └── autogen_wrapper.py         # Autogen integration
│
├── examples/
│   ├── basic_usage.py                 # Simple agent wrapping example
│   ├── langchain_example.py           # LangChain integration example
│   ├── autogen_example.py             # Autogen integration example
│   └── custom_components.py           # Custom evaluators/memory example
│
├── pyproject.toml                     # Package configuration (PEP 518)
├── setup.py                           # Setup script
├── MANIFEST.in                        # Package manifest
├── README.md                          # Main documentation
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore rules
└── STRUCTURE.md                       # This file
```

## Module Descriptions

### Core Modules

#### `meo/memory/`
- **episodic.py**: Records individual workflow steps with state, action, I/O, and metrics
- **semantic.py**: Compresses episodic memories into high-level insights and patterns
- **storage.py**: Persistent storage backends (JSONL files or SQLite database)

#### `meo/evaluators/`
- **reward.py**: Evaluates workflow performance and assigns reward scores
- **metrics.py**: Utility functions for computing success rates, latency, cost, etc.

#### `meo/meta/`
- **policy_adapter.py**: Adapts agent decisions based on learned insights and rules

#### `meo/orchestrator/`
- **hooks.py**: Interception points for tool calls, agent calls, and planning
- **wrappers.py**: Main `WisdomOrchestrator` class that coordinates all components

#### `meo/utils/`
- **encoders.py**: Text embedding utilities for semantic similarity
- **logging.py**: Structured logging for episodes, workflows, and evaluations

#### `meo/integrations/`
- **langchain_wrapper.py**: Wrapper for LangChain chains, agents, and tools
- **autogen_wrapper.py**: Wrapper for Autogen agents and group chats

### Configuration

#### `meo/config/`
- **default_settings.py**: Default configuration values for storage, evaluation, and behavior

## Key Classes

### Abstract Base Classes
- `EpisodicMemory` - Interface for episodic memory storage
- `SemanticMemory` - Interface for semantic compression
- `StorageBackend` - Interface for persistent storage
- `Evaluator` - Interface for workflow evaluation
- `PolicyAdapter` - Interface for policy adaptation
- `Hook` - Interface for interception hooks

### Concrete Implementations
- `InMemoryEpisodicMemory` - In-memory episodic storage
- `LLMSemanticMemory` - LLM-based semantic compression
- `JSONLStorage` - JSONL file storage
- `SQLiteStorage` - SQLite database storage
- `DefaultRewardEvaluator` - Weighted reward evaluator
- `RuleBasedPolicyAdapter` - Rule-based policy adaptation
- `WisdomOrchestrator` - Main orchestrator class

### Data Classes
- `Episode` - Single workflow step record
- `SemanticInsight` - Compressed semantic knowledge
- `EvaluationResult` - Workflow evaluation result
- `PolicyRule` - Policy adaptation rule

## Usage Flow

1. **Initialize** `WisdomOrchestrator` with optional custom components
2. **Wrap** your agent/framework using `orchestrator.run()` or integration wrappers
3. **Execute** workflows - MEO automatically intercepts and records all steps
4. **Evaluate** - After completion, evaluator assigns rewards and success labels
5. **Compress** - Semantic memory extracts patterns from episodic logs
6. **Store** - Insights are persisted for future runs
7. **Adapt** - Policy adapter uses insights to guide future decisions

## Installation

```bash
# Install from source
cd MEO
pip install -e .

# Or build and install
python -m build
pip install dist/meo-0.1.0-py3-none-any.whl
```

## Running Examples

```bash
# Basic usage
python examples/basic_usage.py

# LangChain integration
python examples/langchain_example.py

# Autogen integration
python examples/autogen_example.py

# Custom components
python examples/custom_components.py
```
