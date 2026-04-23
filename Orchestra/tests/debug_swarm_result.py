#!/usr/bin/env python3
"""Debug script to see what the swarm actually returns"""

import asyncio
import sys
sys.path.insert(0, 'tests/shared')
from real_llm_agents import RealAgentFactory, get_api_key

from orchestra import ParallelSwarm, ConsensusStrategy
from orchestra.parallel_swarm import AgentStatus
import json


async def debug_swarm_result():
    api_key = get_api_key()
    factory = RealAgentFactory(api_key)
    agents = factory.create_all_agents()
    
    swarm = ParallelSwarm("debug_swarm", consensus_strategy=ConsensusStrategy.FIRST_VALID)
    
    # Add 1 agent
    agent = agents[0]
    async def executor(ctx, a=agent):
        prompt = ctx.get("prompt", "")
        response = await a.execute(prompt)
        return {
            "result": response.content[:100],
            "tokens": response.total_tokens,
            "cost": response.cost_estimate
        }
    
    swarm.add_agent("agent_0", executor)
    
    # Execute one task
    print("Executing task...")
    result = await swarm.execute({"prompt": "Explain AI in one sentence"})
    
    print("\n" + "="*70)
    print("SWARM RESULT STRUCTURE:")
    print("="*70)
    print(json.dumps(result, indent=2, default=str))
    
    print("\n" + "="*70)
    print("CHECKING FIELDS:")
    print("="*70)
    print(f"result.get('success'): {result.get('success')}")
    print(f"result.get('merged_result'): {result.get('merged_result')}")
    
    merged = result.get('merged_result', {})
    print(f"\nmerged.get('success'): {merged.get('success')}")
    print(f"merged.get('agent_results'): {merged.get('agent_results')}")


if __name__ == "__main__":
    asyncio.run(debug_swarm_result())
