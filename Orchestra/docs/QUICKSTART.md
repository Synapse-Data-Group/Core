# Orchestra Quick Start Guide

Get started with Orchestra in 5 minutes!

## Installation

```bash
# Install dependencies
pip install cognitive-load-monitor
pip install synapse-meo

# Install Orchestra
cd Orchestra
pip install -e .
```

## Your First Orchestration

### 1. Simple Task (Chain-of-Thought)

```python
import asyncio
from orchestra import Orchestra

async def step_1(context):
    return {"result": "Step 1 complete"}

async def step_2(context):
    prev = context.get("step_1", {})
    return {"result": "Step 2 complete", "previous": prev}

async def main():
    # Create orchestra
    orchestra = Orchestra()
    
    # Create chain
    chain = orchestra.create_chain("my_first_chain")
    chain.add_step("step_1", "First step", step_1)
    chain.add_step("step_2", "Second step", step_2, dependencies=["step_1"])
    
    # Execute task
    task = {
        "id": "task_001",
        "description": "My first task",
        "complexity": "simple",
        "chain_id": "my_first_chain"
    }
    
    result = await orchestra.execute(task)
    print(f"✓ Task completed: {result['output']}")

asyncio.run(main())
```

### 2. Complex Task (Parallel Swarm)

```python
import asyncio
from orchestra import Orchestra, ConsensusStrategy

def agent_a(context):
    return {"solution": "Approach A", "score": 85}

def agent_b(context):
    return {"solution": "Approach B", "score": 90}

def agent_c(context):
    return {"solution": "Approach C", "score": 75}

async def main():
    # Create orchestra with CLM/MEO
    orchestra = Orchestra(
        clm_config={"threshold": 0.8},
        meo_config={"storage_path": "./memory"},
        default_consensus=ConsensusStrategy.BEST_PERFORMER
    )
    
    # Create swarm
    swarm = orchestra.create_swarm("my_swarm")
    swarm.add_agent("agent_a", agent_a)
    swarm.add_agent("agent_b", agent_b)
    swarm.add_agent("agent_c", agent_c)
    
    # Execute complex task
    task = {
        "id": "task_002",
        "description": "Find best solution",
        "complexity": "complex",
        "swarm_id": "my_swarm"
    }
    
    result = await orchestra.execute(task)
    merged = result['output']['merged_result']
    print(f"✓ Best solution: {merged['merged_output']}")
    print(f"✓ Agents used: {merged['participating_agents']}")

asyncio.run(main())
```

## Key Concepts

### Task Complexity
- **simple**: Linear execution via Chain-of-Thought
- **moderate**: History-guided routing
- **complex**: Parallel Swarm with multiple agents

### Consensus Strategies
- `VOTING`: Most common result wins
- `BEST_PERFORMER`: Use highest-performing agent
- `WEIGHTED_AVERAGE`: Weight by performance scores
- `MERGE_ALL`: Combine all results

### Integration
- **CLM**: Monitors cognitive load, prevents overload
- **MEO**: Stores history, recalls similar tasks

## Running Examples

```bash
# Example 1: Simple task with CoT
python examples/example_simple_task.py

# Example 2: Parallel Swarm
python examples/example_parallel_swarm.py

# Example 3: Full integration
python examples/example_full_integration.py
```

## Next Steps

1. Read the full [README.md](README.md) for detailed API reference
2. Explore the `examples/` directory
3. Customize routing rules with `orchestra.add_routing_rule()`
4. Monitor metrics with `orchestra.get_orchestration_metrics()`

## Common Patterns

### Custom Routing Rule
```python
orchestra.add_routing_rule(
    node_id="custom_route",
    condition=lambda ctx: ctx["task"].get("priority") == "high",
    action=my_custom_handler,
    metadata={"description": "Handle high priority tasks"}
)
```

### Introspection
```python
# View tree paths
paths = orchestra.introspect_tree_paths()

# View agent outputs
agent_data = orchestra.introspect_agent_outputs("my_swarm")

# Get metrics
metrics = orchestra.get_orchestration_metrics()
```

### Memory-Guided Execution
```python
# MEO automatically stores task history
result = await orchestra.execute(task)

# Future similar tasks benefit from past experience
# Routing is guided by successful historical executions
```

## Tips

- Start with simple tasks to understand the flow
- Use `complexity: "complex"` to trigger Parallel Swarm
- Monitor cognitive load in production environments
- Store task history for continuous improvement
- Inspect metrics regularly to optimize performance

## Troubleshooting

**Issue**: CLM/MEO not found
```bash
pip install cognitive-load-monitor synapse-meo
```

**Issue**: Import errors
```bash
pip install -e .
```

**Issue**: Async errors
- Ensure all executors are async or sync (not mixed incorrectly)
- Use `asyncio.run()` for top-level execution

## Support

Questions? Check the [README.md](README.md) or contact info@synapse.ai
