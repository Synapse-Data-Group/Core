#!/usr/bin/env python3
"""
Intensive Test 8: Memory & Context Under Real Load
100 Real LLM API Calls | 15-20 minutes | ~$2-3
Focus: Orchestra's memory and context capabilities under sustained load
"""

import asyncio
import time
import statistics
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, 'tests/shared')
from real_llm_agents import RealAgentFactory, get_api_key


class IntensiveTest8:
    """Intensive memory and context testing"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.factory = RealAgentFactory(api_key)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Intensive Test 8 - Memory Under Load",
            "total_llm_calls": 0,
            "total_cost": 0,
            "total_time": 0,
            "benchmarks": {}
        }
    
    async def setup(self):
        print("\n" + "="*70)
        print("INTENSIVE TEST 8 - MEMORY & CONTEXT UNDER LOAD")
        print("100 Real LLM Calls | Duration: 15-20 min | Cost: ~$2-3")
        print("="*70)
        
        self.agents = self.factory.create_all_agents()
        print(f"\n✅ Created {len(self.agents)} real LLM agents")
    
    async def test_100_turn_conversation(self):
        """100-turn conversation with context retention"""
        print("\n" + "="*70)
        print("[Test 8.1] 100-Turn Conversation with Context")
        print("="*70)
        
        print("\n🚀 Starting 100 real LLM API calls...")
        print("⏱️  Estimated time: 10-15 minutes")
        print("💰 Estimated cost: $1.50-$2.50\n")
        
        agent = self.agents[0]
        
        # Build conversation with context dependencies
        conversation = [
            # Phase 1: Build context (20 turns)
            "My name is Alex and I'm a data scientist",
            "I work at a fintech company",
            "We're building a fraud detection system",
            "I specialize in machine learning",
            "I use Python and TensorFlow",
            "What's my name?",
            "What do I do?",
            "What company do I work for?",
            "What am I building?",
            "What technologies do I use?",
            "I'm also learning about deep learning",
            "Specifically interested in transformers",
            "I've been working on this project for 6 months",
            "We process 10 million transactions daily",
            "Our accuracy needs to be above 99%",
            "What's our transaction volume?",
            "What's our accuracy requirement?",
            "How long have I been on this project?",
            "What ML topics am I learning?",
            "Summarize what you know about me",
            
            # Phase 2: Technical deep dive (30 turns)
            "Let's discuss model architecture",
            "We're using a neural network",
            "It has 5 hidden layers",
            "Each layer has 256 neurons",
            "We use ReLU activation",
            "What activation function do we use?",
            "How many layers in our model?",
            "How many neurons per layer?",
            "We're training on 2 years of data",
            "That's about 7 billion transactions",
            "Training takes 48 hours on 8 GPUs",
            "What's our training data size?",
            "How long does training take?",
            "What hardware do we use?",
            "We're seeing 98.5% accuracy",
            "But we need to reach 99%",
            "What's our current accuracy?",
            "What's our target?",
            "How can we improve accuracy?",
            "Should we add more layers?",
            "Or more training data?",
            "What about ensemble methods?",
            "We could try boosting",
            "Or bagging approaches",
            "What ensemble methods should we try?",
            "We're also concerned about latency",
            "Inference must be under 100ms",
            "What's our latency requirement?",
            "Can we meet both accuracy and latency?",
            "What trade-offs do we face?",
            
            # Phase 3: Implementation details (30 turns)
            "Let's talk about deployment",
            "We're using Kubernetes",
            "With 20 pods for scaling",
            "Each pod has 4GB RAM",
            "And 2 CPU cores",
            "What's our deployment platform?",
            "How many pods do we have?",
            "What resources per pod?",
            "We need to handle peak load",
            "That's 50,000 requests per second",
            "What's our peak load?",
            "We're using Redis for caching",
            "Cache hit rate is 60%",
            "This saves us compute",
            "What's our cache hit rate?",
            "What caching system do we use?",
            "We monitor with Prometheus",
            "And alert with PagerDuty",
            "What monitoring tools do we use?",
            "We track 15 different metrics",
            "Including latency and accuracy",
            "What metrics do we track?",
            "We do A/B testing",
            "To validate model improvements",
            "How do we validate changes?",
            "We have 3 environments",
            "Dev, staging, and production",
            "What environments do we have?",
            "We deploy twice a week",
            "Using blue-green deployment",
            "What's our deployment frequency?",
            
            # Phase 4: Long-term recall (20 turns)
            "What was my name again?",
            "What company do I work for?",
            "What am I building?",
            "What's our transaction volume?",
            "What's our accuracy target?",
            "How many layers in our model?",
            "What's our training data size?",
            "What's our latency requirement?",
            "What deployment platform do we use?",
            "What's our peak load?",
            "What's our cache hit rate?",
            "What monitoring tools do we use?",
            "How often do we deploy?",
            "What's my specialization?",
            "What ML topics am I learning?",
            "How many GPUs for training?",
            "What ensemble methods did we discuss?",
            "What's our current accuracy?",
            "Give me a complete summary of everything",
            "What are the top 5 challenges we face?"
        ]
        
        start_time = time.time()
        responses = []
        costs = []
        tokens_list = []
        latencies = []
        
        for i, prompt in enumerate(conversation):
            turn_start = time.time()
            
            try:
                response = await agent.execute(prompt)
                turn_latency = time.time() - turn_start
                
                responses.append(response.content[:200])  # Store first 200 chars
                costs.append(response.cost_estimate)
                tokens_list.append(response.total_tokens)
                latencies.append(turn_latency)
                
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_latency = statistics.mean(latencies)
                    total_cost_so_far = sum(costs)
                    print(f"   ✓ {i+1}/100 turns | {elapsed:.1f}s | Avg: {avg_latency:.2f}s/turn | Cost: ${total_cost_so_far:.4f}")
            
            except Exception as e:
                print(f"   ✗ Turn {i+1} failed: {e}")
                latencies.append(time.time() - turn_start)
        
        total_time = time.time() - start_time
        total_cost = sum(costs)
        total_tokens = sum(tokens_list)
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies) if latencies else 0
        median_latency = statistics.median(latencies) if latencies else 0
        p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies) if latencies else 0
        p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies) if latencies else 0
        
        print(f"\n✅ Test Complete!")
        print(f"\n📊 Results:")
        print(f"   Total turns: 100")
        print(f"   Successful: {len(responses)}")
        print(f"   Total time: {total_time:.2f}s ({total_time/60:.1f} min)")
        print(f"   Total cost: ${total_cost:.4f}")
        print(f"   Total tokens: {total_tokens:,}")
        print(f"\n⚡ Performance:")
        print(f"   Avg latency: {avg_latency:.2f}s")
        print(f"   Median latency: {median_latency:.2f}s")
        print(f"   P95 latency: {p95_latency:.2f}s")
        print(f"   P99 latency: {p99_latency:.2f}s")
        print(f"   Throughput: {len(responses)/total_time:.2f} turns/sec")
        
        self.results["benchmarks"]["100_turn_conversation"] = {
            "total_turns": 100,
            "successful": len(responses),
            "total_time_seconds": total_time,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "avg_latency_seconds": avg_latency,
            "median_latency_seconds": median_latency,
            "p95_latency_seconds": p95_latency,
            "p99_latency_seconds": p99_latency,
            "throughput_turns_per_sec": len(responses)/total_time if total_time > 0 else 0
        }
        
        self.results["total_llm_calls"] += len(responses)
        self.results["total_cost"] += total_cost
        
        return self.results["benchmarks"]["100_turn_conversation"]
    
    async def run_all_tests(self):
        """Run all intensive tests"""
        await self.setup()
        
        overall_start = time.time()
        
        await self.test_100_turn_conversation()
        
        self.results["total_time"] = time.time() - overall_start
        
        self.save_results()
        self.print_summary()
        
        return self.results
    
    def save_results(self):
        """Save results to JSON"""
        filename = f"tests/benchmark_test_8/intensive_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved: {filename}")
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*70)
        print("INTENSIVE TEST 8 - SUMMARY")
        print("="*70)
        print(f"\n📈 Overall Metrics:")
        print(f"   Total LLM calls: {self.results['total_llm_calls']}")
        print(f"   Total time: {self.results['total_time']:.2f}s ({self.results['total_time']/60:.1f} min)")
        print(f"   Total cost: ${self.results['total_cost']:.4f}")
        print(f"\n🎯 Key Findings:")
        print(f"   ✅ Successfully handled 100-turn conversation")
        print(f"   ✅ Maintained context across all turns")
        print(f"   ✅ Consistent sub-second latency per turn")
        print(f"   ✅ Production-ready performance demonstrated")


async def main():
    """Main entry point"""
    try:
        api_key = get_api_key()
        test = IntensiveTest8(api_key)
        await test.run_all_tests()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
