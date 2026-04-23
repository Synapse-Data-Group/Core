# MEO Quick Start Guide

## Installation

```bash
pip install synapse-meo
```

## 5-Minute Tutorial

### 1. Basic Agent Wrapping

```python
from meo import WisdomOrchestrator

# Create orchestrator
orchestrator = WisdomOrchestrator()

# Define your agent
def my_agent(input_data):
    return {"result": f"Processed: {input_data}", "success": True}

# Run with MEO
result = orchestrator.run(agent=my_agent, input_data="Hello!")
print(result)
```

### 2. View Learning Progress

```python
# Get workflow history
history = orchestrator.get_workflow_history()
for eval in history:
    print(f"Workflow: reward={eval['reward']:.2f}, success={eval['success']}")

# Get learned insights
insights = orchestrator.get_insights()
for insight in insights:
    print(f"[{insight['insight_type']}] {insight['content']}")
```

### 3. Get Policy Recommendations

```python
# Ask for recommendations based on learned patterns
recommendation = orchestrator.get_policy_recommendation(
    context={"task": "data_processing"},
    available_actions=["method_a", "method_b", "method_c"]
)

print(f"Recommended: {recommendation['recommended_action']}")
print(f"Scores: {recommendation['action_scores']}")
```

## Framework Integration

### LangChain

```python
from meo.integrations.langchain_wrapper import LangChainWrapper

wrapper = LangChainWrapper()
enhanced_chain = wrapper.wrap_chain(my_langchain_chain)

# Use normally - MEO tracks everything
result = enhanced_chain.invoke({"input": "data"})
```

### Autogen

```python
from meo.integrations.autogen_wrapper import AutogenWrapper

wrapper = AutogenWrapper()
enhanced_agent = wrapper.wrap_agent(my_autogen_agent)

# Agent now learns from interactions
response = enhanced_agent.generate_reply(messages)
```

## Custom Components

### Custom Evaluator

```python
from meo.evaluators import Evaluator, EvaluationResult

class MyEvaluator(Evaluator):
    def evaluate(self, episodes, workflow_result=None):
        # Your evaluation logic
        return EvaluationResult(
            workflow_id=episodes[0].workflow_id,
            reward=1.0,
            success=True,
            metrics={"custom": "value"}
        )

orchestrator = WisdomOrchestrator(evaluator=MyEvaluator())
```

### Custom Semantic Memory

```python
from meo.memory import SemanticMemory, SemanticInsight

class MySemanticMemory(SemanticMemory):
    def __init__(self):
        self._insights = []
    
    def compress_episodes(self, episodes):
        # Extract patterns from episodes
        insight = SemanticInsight(
            insight_type="pattern",
            content="Discovered pattern...",
            confidence=0.9
        )
        self._insights.append(insight)
        return [insight]
    
    def get_insights(self, insight_type=None, limit=None):
        return self._insights
    
    def add_insight(self, insight):
        self._insights.append(insight)
    
    def clear(self):
        self._insights.clear()

orchestrator = WisdomOrchestrator(semantic_memory=MySemanticMemory())
```

## Configuration

```python
from meo.config import DefaultConfig

config = DefaultConfig()
config.STORAGE_DIR = "./my_data"
config.REWARD_WEIGHTS = {
    "success": 2.0,
    "cost": -0.2,
    "latency": -0.1,
    "error_rate": -1.0,
}
config.SEMANTIC_COMPRESSION_THRESHOLD = 5

orchestrator = WisdomOrchestrator(config=config)
```

## Storage Options

### JSONL Storage (Default)

```python
from meo.memory import JSONLStorage

storage = JSONLStorage("./memory.jsonl")
orchestrator = WisdomOrchestrator(storage_backend=storage)
```

### SQLite Storage

```python
from meo.memory import SQLiteStorage

storage = SQLiteStorage("./memory.db")
orchestrator = WisdomOrchestrator(storage_backend=storage)
```

## Tool Call Interception

```python
def expensive_api_call(data):
    # Some expensive operation
    return process(data)

# MEO tracks cost, latency, success/failure
result = orchestrator.intercept_tool_call(
    tool_name="api_call",
    tool_input=data,
    tool_function=expensive_api_call
)
```

## Next Steps

1. Run the examples: `python examples/basic_usage.py`
2. Read the full README for advanced features
3. Check STRUCTURE.md for package architecture
4. Customize components for your use case

## Common Patterns

### Pattern 1: Multi-Run Learning

```python
orchestrator = WisdomOrchestrator()

# Run multiple times
for i in range(10):
    result = orchestrator.run(agent=my_agent, input_data=f"Task {i}")
    
# MEO automatically learns and improves
insights = orchestrator.get_insights()
print(f"Learned {len(insights)} insights")
```

### Pattern 2: A/B Testing with Policy

```python
# Get recommendation
rec = orchestrator.get_policy_recommendation(
    context={"scenario": "high_load"},
    available_actions=["strategy_a", "strategy_b"]
)

# Use recommended strategy
chosen_strategy = rec["recommended_action"]
result = execute_strategy(chosen_strategy)
```

### Pattern 3: Monitoring Performance

```python
history = orchestrator.get_workflow_history(limit=20)

avg_reward = sum(h["reward"] for h in history) / len(history)
success_rate = sum(1 for h in history if h["success"]) / len(history)

print(f"Average reward: {avg_reward:.2f}")
print(f"Success rate: {success_rate:.1%}")
```

## Troubleshooting

### Issue: No insights generated
**Solution**: Ensure you've run enough workflows (default threshold: 10)

### Issue: Storage file not found
**Solution**: MEO creates directories automatically, but check permissions

### Issue: Custom components not working
**Solution**: Ensure your custom classes inherit from the correct ABC

## Support

- Documentation: README.md
- Examples: examples/ directory
- Issues: GitHub Issues
