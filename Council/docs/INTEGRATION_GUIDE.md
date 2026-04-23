# Council Framework - Integration Guide

## Overview

The Council Framework is a **pure Python** multi-agent debate system designed as a foundational component for other technologies. This guide explains how to integrate it into your projects.

## Core Principles

### 1. **No External Dependencies**
- Pure Python 3 - runs anywhere
- No pip installations required
- Self-contained learning algorithms
- Built-in persistence (pickle)

### 2. **Modular Architecture**
- Each component is independently usable
- Extend through inheritance
- Plugin-style tool system
- JSON-based data exchange

### 3. **Learning & Adaptation**
- Agents learn from experience (Q-learning)
- Persistent memory across sessions
- Personality evolution (genetic algorithms)
- Adaptive scoring (moderator learning)

## Integration Patterns

### Pattern 1: Decision Support System

```python
from sentient_debate_system import SentientDebateSystem

class DecisionEngine:
    def __init__(self):
        self.memory_dir = "./decision_memories"
        self.agent_pool = {}
    
    def make_decision(self, problem: str, expert_types: list) -> dict:
        debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
        
        # Load or create expert agents
        for expert_type in expert_types:
            agent_id = self.agent_pool.get(expert_type)
            memory_path = f"{self.memory_dir}/{expert_type}_memory.pkl" if agent_id else None
            
            agent = debate.create_agent(expert_type, memory_path=memory_path)
            self.agent_pool[expert_type] = agent.agent_id
        
        # Run debate
        result = debate.run_debate(max_rounds=2)
        
        # Save learned knowledge
        debate.save_agent_memories(self.memory_dir)
        
        return {
            "decision": result["final_decision"]["decision"],
            "confidence": result["final_decision"]["confidence"],
            "reasoning": result["final_decision"]["reasoning"],
            "alternatives": [
                {"agent": p["agent_name"], "score": p["score"]}
                for p in result["proposals"]
            ]
        }

# Usage
engine = DecisionEngine()
decision = engine.make_decision(
    "Should we migrate to microservices?",
    ["Technical_Expert", "Business_Expert", "Operations_Expert"]
)
```

### Pattern 2: API Service Wrapper

```python
from flask import Flask, request, jsonify
from sentient_debate_system import SentientDebateSystem
import threading
import queue

app = Flask(__name__)
debate_queue = queue.Queue()

class DebateService:
    def __init__(self):
        self.active_debates = {}
        self.memory_dir = "./api_memories"
    
    def start_debate(self, debate_id: str, problem: str, agents: list):
        debate = SentientDebateSystem(problem)
        
        for agent_config in agents:
            memory_path = f"{self.memory_dir}/{agent_config['name']}_memory.pkl"
            debate.create_agent(
                agent_config['name'],
                personality=agent_config.get('personality'),
                memory_path=memory_path
            )
        
        result = debate.run_debate(max_rounds=agent_config.get('rounds', 2))
        debate.save_agent_memories(self.memory_dir)
        
        return result

service = DebateService()

@app.route('/debate/start', methods=['POST'])
def start_debate():
    data = request.json
    debate_id = data['debate_id']
    
    # Run debate in background
    result = service.start_debate(
        debate_id,
        data['problem'],
        data['agents']
    )
    
    return jsonify({
        "debate_id": debate_id,
        "status": "completed",
        "result": result
    })

# Run: python api_service.py
```

### Pattern 3: Data Pipeline Component

```python
from sentient_debate_system import SentientDebateSystem
import json

class DebatePipelineStage:
    def __init__(self, config: dict):
        self.config = config
        self.memory_dir = config.get('memory_dir', './pipeline_memories')
    
    def process(self, input_data: dict) -> dict:
        """
        Input: {"problem": str, "context": dict, "constraints": list}
        Output: {"solution": str, "confidence": float, "metadata": dict}
        """
        problem = input_data['problem']
        context = input_data.get('context', {})
        
        debate = SentientDebateSystem(problem)
        
        # Create agents based on context
        agent_count = context.get('agent_count', 3)
        for i in range(agent_count):
            memory_path = f"{self.memory_dir}/agent_{i}_memory.pkl"
            debate.create_agent(f"Agent_{i}", memory_path=memory_path)
        
        result = debate.run_debate(max_rounds=2)
        debate.save_agent_memories(self.memory_dir)
        
        return {
            "solution": result["final_decision"]["decision"],
            "confidence": result["final_decision"]["confidence"],
            "metadata": {
                "proposals_evaluated": result["total_proposals"],
                "debate_duration": result["duration_seconds"],
                "agent_stats": result["agent_stats"]
            }
        }

# Usage in pipeline
stage = DebatePipelineStage({"memory_dir": "./pipeline_mem"})
output = stage.process({
    "problem": "Optimize database query performance",
    "context": {"agent_count": 3},
    "constraints": ["low_latency", "high_throughput"]
})
```

### Pattern 4: Custom Agent Extension

```python
from sentient_agent import SentientAgent
from sentient_debate_system import SentientDebateSystem

class DomainExpertAgent(SentientAgent):
    def __init__(self, agent_id: str, name: str, domain_knowledge: dict, **kwargs):
        super().__init__(agent_id, name, **kwargs)
        self.domain_knowledge = domain_knowledge
    
    def propose_solution(self, problem: str, context: dict) -> str:
        # Inject domain knowledge into proposal
        base_proposal = super().propose_solution(problem, context)
        
        # Enhance with domain-specific insights
        relevant_knowledge = self._get_relevant_knowledge(problem)
        if relevant_knowledge:
            base_proposal += f" Based on domain expertise: {relevant_knowledge}"
        
        return base_proposal
    
    def _get_relevant_knowledge(self, problem: str) -> str:
        problem_words = set(problem.lower().split())
        
        for topic, knowledge in self.domain_knowledge.items():
            if topic.lower() in problem.lower():
                return knowledge
        
        return ""

# Usage
debate = SentientDebateSystem("Medical diagnosis problem")

medical_knowledge = {
    "diagnosis": "Consider differential diagnosis and rule out common conditions first",
    "treatment": "Evidence-based protocols should guide treatment decisions"
}

# Create custom agent
agent_id = "expert_001"
expert = DomainExpertAgent(
    agent_id,
    "Medical_Expert",
    domain_knowledge=medical_knowledge
)

# Manually add to debate system
debate.agents[agent_id] = expert
```

### Pattern 5: Tool Integration

```python
from sentient_debate_system import Tool, SentientDebateSystem
import requests

class WebSearchTool(Tool):
    def __init__(self, api_key: str):
        super().__init__("web_search", "Web Search Tool")
        self.api_key = api_key
    
    def execute(self, query: str) -> str:
        # Simulate web search
        # In production: call actual search API
        return f"Search results for '{query}': [relevant information]"

class DatabaseTool(Tool):
    def __init__(self, db_connection):
        super().__init__("database", "Database Query Tool")
        self.db = db_connection
    
    def execute(self, query: str) -> str:
        # Execute database query
        # In production: actual DB query
        return f"Database query result: [data]"

# Usage
debate = SentientDebateSystem("Data analysis problem")

agent = debate.create_agent("Data_Analyst")

# Add tools to agent
web_tool = WebSearchTool(api_key="your_key")
db_tool = DatabaseTool(db_connection=None)

debate.create_tool_for_agent(agent.agent_id, web_tool)
debate.create_tool_for_agent(agent.agent_id, db_tool)

result = debate.run_debate(max_rounds=2)
```

## Advanced Integration Scenarios

### Scenario 1: Multi-Tenant System

```python
class MultiTenantDebateSystem:
    def __init__(self):
        self.tenant_memories = {}
    
    def get_debate_for_tenant(self, tenant_id: str, problem: str):
        memory_dir = f"./memories/tenant_{tenant_id}"
        
        debate = SentientDebateSystem(problem)
        
        # Load tenant-specific agent memories
        for agent_name in ["Agent_A", "Agent_B", "Agent_C"]:
            memory_path = f"{memory_dir}/{agent_name}_memory.pkl"
            debate.create_agent(agent_name, memory_path=memory_path)
        
        result = debate.run_debate(max_rounds=2)
        debate.save_agent_memories(memory_dir)
        
        return result

# Each tenant gets isolated learning
system = MultiTenantDebateSystem()
result_tenant1 = system.get_debate_for_tenant("tenant_001", "Problem A")
result_tenant2 = system.get_debate_for_tenant("tenant_002", "Problem A")
```

### Scenario 2: Continuous Learning System

```python
import schedule
import time

class ContinuousLearningSystem:
    def __init__(self):
        self.debate_history = []
        self.memory_dir = "./continuous_memories"
    
    def run_periodic_debates(self):
        problems = self.get_pending_problems()
        
        for problem in problems:
            debate = SentientDebateSystem(problem)
            
            # Load evolved agents
            for i in range(3):
                memory_path = f"{self.memory_dir}/agent_{i}_memory.pkl"
                debate.create_agent(f"Agent_{i}", memory_path=memory_path)
            
            result = debate.run_debate(max_rounds=2)
            
            # Evolve agents periodically
            if len(self.debate_history) % 10 == 0:
                debate.evolve_agents()
            
            debate.save_agent_memories(self.memory_dir)
            self.debate_history.append(result)
    
    def get_pending_problems(self):
        # Fetch from queue, database, etc.
        return ["Problem 1", "Problem 2"]

# Schedule debates
system = ContinuousLearningSystem()
schedule.every(1).hour.do(system.run_periodic_debates)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Scenario 3: Hybrid Human-AI System

```python
class HybridDebateSystem:
    def __init__(self):
        self.debate = None
        self.human_inputs = []
    
    def start_debate(self, problem: str):
        self.debate = SentientDebateSystem(problem)
        
        # Create AI agents
        for i in range(2):
            self.debate.create_agent(f"AI_Agent_{i}")
        
        # Run proposal phase
        self.debate._proposal_phase()
        
        return {
            "proposals": [p.to_dict() for p in self.debate.proposals],
            "awaiting_human_input": True
        }
    
    def add_human_proposal(self, human_name: str, proposal_content: str):
        from sentient_debate_system import Proposal
        
        proposal = Proposal(
            agent_id="human_001",
            agent_name=human_name,
            content=proposal_content,
            timestamp=time.time()
        )
        
        self.debate.proposals.append(proposal)
    
    def continue_debate(self):
        # Continue with challenge and rebuttal phases
        self.debate._challenge_phase()
        self.debate._rebuttal_phase()
        self.debate._scoring_phase()
        self.debate._resolution_phase()
        
        return self.debate.get_debate_summary()

# Usage
hybrid = HybridDebateSystem()

# Start debate
status = hybrid.start_debate("Strategic planning problem")

# Human adds their proposal
hybrid.add_human_proposal("John", "My strategic proposal...")

# Continue debate
result = hybrid.continue_debate()
```

## Data Format Specifications

### Input Format

```python
debate_input = {
    "problem": "string - the problem to debate",
    "moderator_strategy": "adaptive|conservative|aggressive",
    "agents": [
        {
            "name": "string",
            "personality": {
                "creativity": 0.0-1.0,
                "boldness": 0.0-1.0,
                # ... other traits
            },
            "memory_path": "optional string path"
        }
    ],
    "max_rounds": 1-10
}
```

### Output Format

```python
debate_output = {
    "system_id": "uuid",
    "problem": "string",
    "duration_seconds": float,
    "final_decision": {
        "decision": "string",
        "confidence": 0.0-1.0,
        "reasoning": "string",
        "winning_proposal": {...}
    },
    "agent_stats": [...],
    "proposals": [...],
    "learning_insights": {...}
}
```

## Performance Optimization

### Memory Management

```python
# Limit memory size for production
from learning_engine import ExperienceMemory

# Create agent with limited memory
agent = debate.create_agent("Agent")
agent.memory = ExperienceMemory(capacity=1000)  # Smaller capacity
```

### Batch Processing

```python
def process_batch(problems: list) -> list:
    results = []
    
    # Reuse agents across problems
    debate = SentientDebateSystem(problems[0])
    for i in range(3):
        debate.create_agent(f"Agent_{i}")
    
    for problem in problems:
        debate.problem = problem
        debate.proposals = []
        debate.messages = []
        
        result = debate.run_debate(max_rounds=1)
        results.append(result)
    
    return results
```

## Error Handling

```python
from sentient_debate_system import SentientDebateSystem

def safe_debate(problem: str, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            debate = SentientDebateSystem(problem)
            
            # Create agents
            for i in range(3):
                debate.create_agent(f"Agent_{i}")
            
            result = debate.run_debate(max_rounds=2)
            
            # Validate result
            if result["final_decision"] is None:
                raise ValueError("No decision reached")
            
            return result
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
    
    return {"error": "Max retries exceeded"}
```

## Testing Integration

```python
import unittest
from sentient_debate_system import SentientDebateSystem

class TestDebateIntegration(unittest.TestCase):
    def setUp(self):
        self.debate = SentientDebateSystem("Test problem")
        for i in range(3):
            self.debate.create_agent(f"Agent_{i}")
    
    def test_debate_completes(self):
        result = self.debate.run_debate(max_rounds=1)
        self.assertIsNotNone(result["final_decision"])
        self.assertGreater(result["total_proposals"], 0)
    
    def test_learning_persists(self):
        result1 = self.debate.run_debate(max_rounds=1)
        self.debate.save_agent_memories("./test_mem")
        
        # Create new debate with same agents
        debate2 = SentientDebateSystem("Test problem 2")
        for i in range(3):
            debate2.create_agent(
                f"Agent_{i}",
                memory_path=f"./test_mem/agent_{list(self.debate.agents.keys())[i]}_memory.pkl"
            )
        
        result2 = debate2.run_debate(max_rounds=1)
        
        # Check that agents have memory
        for agent in debate2.agents.values():
            self.assertGreater(len(agent.memory.experiences), 0)

if __name__ == '__main__':
    unittest.main()
```

## Deployment Considerations

### 1. File System Access
- Ensure write permissions for memory directory
- Use absolute paths in production
- Implement cleanup for old memory files

### 2. Concurrency
- Each debate instance is independent
- Safe for multi-threading (separate instances)
- Use process pools for parallel debates

### 3. Monitoring
- Export debate logs for analysis
- Track agent performance metrics
- Monitor memory growth

### 4. Scaling
- Horizontal: Multiple debate instances
- Vertical: Increase agent count per debate
- Caching: Reuse trained agents

## Best Practices

1. **Start Simple**: Begin with 3 agents, 2 rounds
2. **Monitor Learning**: Track exploration rates and memory sizes
3. **Persist Memories**: Always save agent memories after debates
4. **Evolve Periodically**: Run evolution every 10-20 debates
5. **Validate Outputs**: Check confidence scores before using decisions
6. **Handle Errors**: Wrap debate calls in try-except blocks
7. **Test Integration**: Write unit tests for your integration
8. **Document Customizations**: Keep track of personality tweaks

## Support & Resources

- **Examples**: See `example_*.py` files
- **Tests**: Review `testing/test_runner.py`
- **Documentation**: Read `README.md`
- **Source Code**: All code is documented inline

---

**The Council Framework is designed to be a building block, not a standalone application. Integrate it into your systems to add intelligent multi-agent debate capabilities.**
