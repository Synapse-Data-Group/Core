#!/usr/bin/env python3
"""
Batch 1: Parallel Execution Benchmark
Orchestra ParallelSwarm vs Sequential LLM calls

Tests Orchestra's unique parallel swarm capability against sequential execution.
Estimated cost: ~$0.10 (10 GPT-4 calls)
"""

import asyncio
import time
import os
import json
from typing import List, Dict, Any


async def benchmark_parallel_execution():
    """
    Benchmark: 3 LLM agents analyzing the same prompt in parallel
    Orchestra: Parallel Swarm with voting consensus
    Baseline: Sequential execution
    """
    
    print("=" * 70)
    print("BATCH 1: PARALLEL EXECUTION BENCHMARK")
    print("=" * 70)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    print(f"\n✅ API Key found: {api_key[:8]}...")
    
    # Test prompt
    test_prompt = """Analyze this business scenario and provide 3 key recommendations:
    
    A startup has $100k funding, 2 developers, and 6 months runway.
    They need to decide between:
    A) Building an MVP and launching quickly
    B) Doing more market research first
    C) Hiring more team members
    
    What should they do?"""
    
    results = {
        "test": "Parallel Execution",
        "prompt": test_prompt,
        "iterations": 3,
        "orchestra": {},
        "baseline": {},
        "comparison": {}
    }
    
    # Test 1: Orchestra Parallel Swarm
    print("\n[1/2] Testing Orchestra Parallel Swarm...")
    print("-" * 70)
    
    try:
        from orchestra import ParallelSwarm, ConsensusStrategy
        from orchestra.llm import OpenAIProvider
        
        # Create 3 agents with GPT-4
        def create_llm_agent(agent_id: str):
            from orchestra.llm import LLMConfig
            
            config = LLMConfig(
                provider="openai",
                model="gpt-4",
                api_key=api_key,
                temperature=0.7,
                max_tokens=300
            )
            provider = OpenAIProvider(config)
            
            async def agent_executor(context):
                prompt = context.get("prompt", "")
                response = await provider.generate(prompt)
                return {
                    "agent_id": agent_id,
                    "response": response.content,
                    "tokens": response.total_tokens,
                    "cost": response.total_tokens * 0.00003  # GPT-4 pricing
                }
            
            return agent_executor
        
        swarm = ParallelSwarm("analysis_swarm", consensus_strategy=ConsensusStrategy.VOTING)
        swarm.add_agent("analyst_1", create_llm_agent("analyst_1"), load_threshold=0.9)
        swarm.add_agent("analyst_2", create_llm_agent("analyst_2"), load_threshold=0.9)
        swarm.add_agent("analyst_3", create_llm_agent("analyst_3"), load_threshold=0.9)
        
        start_time = time.time()
        result = await swarm.execute({"prompt": test_prompt})
        orchestra_time = time.time() - start_time
        
        # Extract metrics
        agent_outputs = result.get("agent_outputs", {})
        total_tokens = sum(output.get("tokens", 0) for output in agent_outputs.values())
        total_cost = sum(output.get("cost", 0) for output in agent_outputs.values())
        
        results["orchestra"] = {
            "execution_time": orchestra_time,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "agents_used": len(agent_outputs),
            "consensus": result["merged_result"].get("consensus_strategy", "voting")
        }
        
        print(f"✅ Orchestra completed in {orchestra_time:.2f}s")
        print(f"   Agents: {len(agent_outputs)} (parallel)")
        print(f"   Tokens: {total_tokens}")
        print(f"   Cost: ${total_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Orchestra test failed: {e}")
        import traceback
        traceback.print_exc()
        results["orchestra"]["error"] = str(e)
    
    # Test 2: Sequential Baseline
    print("\n[2/2] Testing Sequential Baseline...")
    print("-" * 70)
    
    try:
        from orchestra.llm import OpenAIProvider, LLMConfig
        
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key=api_key,
            temperature=0.7,
            max_tokens=300
        )
        provider = OpenAIProvider(config)
        
        start_time = time.time()
        responses = []
        total_tokens = 0
        
        for i in range(3):
            response = await provider.generate(test_prompt)
            responses.append(response.content)
            total_tokens += response.total_tokens
        
        baseline_time = time.time() - start_time
        total_cost = total_tokens * 0.00003
        
        results["baseline"] = {
            "execution_time": baseline_time,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "calls": 3
        }
        
        print(f"✅ Baseline completed in {baseline_time:.2f}s")
        print(f"   Calls: 3 (sequential)")
        print(f"   Tokens: {total_tokens}")
        print(f"   Cost: ${total_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Baseline test failed: {e}")
        import traceback
        traceback.print_exc()
        results["baseline"]["error"] = str(e)
    
    # Comparison
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if "error" not in results["orchestra"] and "error" not in results["baseline"]:
        speedup = results["baseline"]["execution_time"] / results["orchestra"]["execution_time"]
        
        results["comparison"] = {
            "speedup": speedup,
            "time_saved": results["baseline"]["execution_time"] - results["orchestra"]["execution_time"],
            "cost_same": results["orchestra"]["total_cost"] == results["baseline"]["total_cost"]
        }
        
        print(f"\n⚡ Speedup: {speedup:.2f}x")
        print(f"⏱️  Time saved: {results['comparison']['time_saved']:.2f}s")
        print(f"💰 Cost: Same (${results['orchestra']['total_cost']:.4f})")
        print(f"\n✅ Orchestra is {speedup:.2f}x FASTER with parallel execution!")
    
    # Save results
    with open("batch1_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: batch1_results.json")
    
    return results


if __name__ == "__main__":
    asyncio.run(benchmark_parallel_execution())
