#!/usr/bin/env python3
"""
Batch 2: Memory Cache Benchmark
Orchestra Memory-Aware Agents vs No Caching

Tests Orchestra's unique agent-embedded memory for 10-100x speedup.
Estimated cost: ~$0.15 (first run), ~$0.01 (cached runs)
"""

import asyncio
import time
import os
import json
from typing import List, Dict, Any


async def benchmark_memory_cache():
    """
    Benchmark: 10 similar LLM tasks with caching
    Orchestra: MemoryAwareAgent with LRU cache
    Baseline: No caching (every call hits API)
    """
    
    print("=" * 70)
    print("BATCH 2: MEMORY CACHE BENCHMARK")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY not set")
        return
    
    print(f"\n✅ API Key found: {api_key[:8]}...")
    
    # Test tasks - similar prompts that should benefit from caching
    test_tasks = [
        {"id": "task1", "query": "What are the benefits of exercise?"},
        {"id": "task2", "query": "What are the benefits of exercise?"},  # Exact duplicate
        {"id": "task3", "query": "What are the benefits of exercise?"},  # Exact duplicate
        {"id": "task4", "query": "What are health benefits of working out?"},  # Similar
        {"id": "task5", "query": "What are the benefits of exercise?"},  # Exact duplicate
        {"id": "task6", "query": "Explain benefits of physical activity"},  # Similar
        {"id": "task7", "query": "What are the benefits of exercise?"},  # Exact duplicate
        {"id": "task8", "query": "What are the benefits of exercise?"},  # Exact duplicate
        {"id": "task9", "query": "What are the benefits of exercise?"},  # Exact duplicate
        {"id": "task10", "query": "What are the benefits of exercise?"},  # Exact duplicate
    ]
    
    results = {
        "test": "Memory Cache",
        "tasks": len(test_tasks),
        "orchestra": {},
        "baseline": {},
        "comparison": {}
    }
    
    # Test 1: Orchestra with Memory Cache
    print("\n[1/2] Testing Orchestra Memory-Aware Agent...")
    print("-" * 70)
    
    try:
        from orchestra.agent_memory import EmbeddedMemory, MemoryAwareAgent, MemoryCache, CacheStrategy
        from orchestra.llm import OpenAIProvider, LLMConfig
        
        # Create memory-aware agent
        memory = EmbeddedMemory(agent_id="cache_agent")
        cache = MemoryCache(max_size=50, strategy=CacheStrategy.LRU)
        
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",  # Cheaper for cache testing
            api_key=api_key,
            temperature=0.7,
            max_tokens=150
        )
        provider = OpenAIProvider(config)
        
        async def llm_executor(context):
            # Extract query from enriched context
            task = context.get("task", {}) if isinstance(context, dict) else {}
            query = task.get("query", "") if task else ""
            
            if not query:
                return {"response": "No query", "tokens": 0}
            
            response = await provider.generate(query)
            return {
                "response": response.content,
                "tokens": response.total_tokens
            }
        
        agent = MemoryAwareAgent(
            "cache_agent",
            llm_executor,
            embedded_memory=memory,
            cache=cache
        )
        
        start_time = time.time()
        total_tokens = 0
        cache_hits = 0
        
        for task in test_tasks:
            result = await agent.execute(task, {})
            if result and result.get("from_cache"):
                cache_hits += 1
            elif result and result.get("result"):
                total_tokens += result.get("result", {}).get("tokens", 0)
        
        orchestra_time = time.time() - start_time
        
        stats = agent.get_statistics()
        total_cost = total_tokens * 0.000002  # GPT-3.5-turbo pricing
        
        results["orchestra"] = {
            "execution_time": orchestra_time,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "cache_hits": stats.get("cache_hits", cache_hits),
            "cache_misses": stats.get("cache_misses", len(test_tasks) - cache_hits),
            "cache_hit_rate": stats.get("cache_hit_rate", cache_hits / len(test_tasks))
        }
        
        print(f"✅ Orchestra completed in {orchestra_time:.2f}s")
        print(f"   Cache hits: {results['orchestra']['cache_hits']}/{len(test_tasks)}")
        print(f"   Cache hit rate: {results['orchestra']['cache_hit_rate']:.1%}")
        print(f"   Tokens: {total_tokens}")
        print(f"   Cost: ${total_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Orchestra test failed: {e}")
        import traceback
        traceback.print_exc()
        results["orchestra"]["error"] = str(e)
    
    # Test 2: Baseline (No Caching)
    print("\n[2/2] Testing Baseline (No Cache)...")
    print("-" * 70)
    
    try:
        from orchestra.llm import OpenAIProvider, LLMConfig
        
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=api_key,
            temperature=0.7,
            max_tokens=150
        )
        provider = OpenAIProvider(config)
        
        start_time = time.time()
        total_tokens = 0
        
        for task in test_tasks:
            query = task.get("query", "")
            response = await provider.generate(query)
            total_tokens += response.total_tokens
        
        baseline_time = time.time() - start_time
        total_cost = total_tokens * 0.000002
        
        results["baseline"] = {
            "execution_time": baseline_time,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "cache_hits": 0,
            "api_calls": len(test_tasks)
        }
        
        print(f"✅ Baseline completed in {baseline_time:.2f}s")
        print(f"   API calls: {len(test_tasks)} (no cache)")
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
        cost_savings = ((results["baseline"]["total_cost"] - results["orchestra"]["total_cost"]) / 
                       results["baseline"]["total_cost"] * 100) if results["baseline"]["total_cost"] > 0 else 0
        
        results["comparison"] = {
            "speedup": speedup,
            "time_saved": results["baseline"]["execution_time"] - results["orchestra"]["execution_time"],
            "cost_savings_percent": cost_savings,
            "cost_saved": results["baseline"]["total_cost"] - results["orchestra"]["total_cost"]
        }
        
        print(f"\n⚡ Speedup: {speedup:.2f}x")
        print(f"⏱️  Time saved: {results['comparison']['time_saved']:.2f}s")
        print(f"💰 Cost savings: {cost_savings:.1f}% (${results['comparison']['cost_saved']:.4f})")
        print(f"📊 Cache hit rate: {results['orchestra']['cache_hit_rate']:.1%}")
        print(f"\n✅ Orchestra is {speedup:.2f}x FASTER with {cost_savings:.0f}% cost reduction!")
    
    # Save results
    with open("batch2_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: batch2_results.json")
    
    return results


if __name__ == "__main__":
    asyncio.run(benchmark_memory_cache())
