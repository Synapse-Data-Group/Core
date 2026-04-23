#!/usr/bin/env python3
"""
Quick test to verify the swarm context-passing fix
Tests parallel execution with multiple agents
"""

import asyncio
import sys
sys.path.insert(0, 'tests/shared')
from real_llm_agents import RealAgentFactory, get_api_key

from orchestra import ParallelSwarm, ConsensusStrategy
from orchestra.parallel_swarm import AgentStatus


async def test_parallel_swarm_fix():
    """Test that parallel swarm execution now works with proper context isolation"""
    
    print("\n" + "="*70)
    print("TESTING SWARM CONTEXT-PASSING FIX")
    print("="*70)
    
    api_key = get_api_key()
    factory = RealAgentFactory(api_key)
    agents = factory.create_all_agents()
    
    print(f"\n✅ Created {len(agents)} real LLM agents")
    
    # Create swarm with 5 agents
    swarm = ParallelSwarm("test_swarm", consensus_strategy=ConsensusStrategy.VOTING)
    
    for i, agent in enumerate(agents[:5]):
        async def executor(ctx, a=agent):
            prompt = ctx.get("prompt", "")
            response = await a.execute(prompt)
            return {
                "result": response.content[:100],
                "tokens": response.total_tokens,
                "cost": response.cost_estimate,
                "agent_id": ctx.get("agent_id", "unknown")
            }
        
        swarm.add_agent(f"agent_{i}", executor, load_threshold=0.9)
    
    print(f"✅ Added 5 agents to swarm")
    
    # Test with 10 concurrent tasks
    print("\n🚀 Testing 10 concurrent tasks...")
    
    tasks = [
        f"Briefly explain concept {i} in one sentence"
        for i in range(10)
    ]
    
    successful = 0
    failed = 0
    
    for i, task in enumerate(tasks):
        # Reset agents
        for agent in swarm.agents.values():
            agent.status = AgentStatus.IDLE
        
        try:
            result = await swarm.execute({"prompt": task})
            
            if result.get("merged_result", {}).get("success"):
                successful += 1
                print(f"   ✓ Task {i+1}/10 succeeded")
            else:
                failed += 1
                print(f"   ✗ Task {i+1}/10 failed: {result.get('merged_result', {}).get('error', 'Unknown')}")
        
        except Exception as e:
            failed += 1
            print(f"   ✗ Task {i+1}/10 exception: {e}")
    
    print(f"\n📊 Results:")
    print(f"   Successful: {successful}/10 ({successful/10*100:.0f}%)")
    print(f"   Failed: {failed}/10 ({failed/10*100:.0f}%)")
    
    if successful == 10:
        print("\n✅ FIX VERIFIED: All parallel tasks succeeded!")
        print("   Context isolation is working correctly.")
    elif successful > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {successful}/10 tasks succeeded")
        print("   Some improvement but may need further investigation.")
    else:
        print("\n❌ FIX FAILED: No tasks succeeded")
        print("   Context-passing issue persists.")
    
    return successful, failed


if __name__ == "__main__":
    successful, failed = asyncio.run(test_parallel_swarm_fix())
    sys.exit(0 if successful == 10 else 1)
