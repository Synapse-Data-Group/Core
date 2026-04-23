#!/usr/bin/env python3
"""
LangChain Implementation for Comparison Benchmarks
Creates equivalent LangChain implementations to compare against Orchestra
"""

import asyncio
import time
import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class LangChainAgents:
    """LangChain agent implementations for benchmarking"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = []
        
    def create_agents(self, num_agents: int = 10) -> List[ChatOpenAI]:
        """Create LangChain agents equivalent to Orchestra agents"""
        
        agent_configs = [
            {"model": "gpt-4", "temperature": 0.7, "max_tokens": 500},
            {"model": "gpt-4-turbo-preview", "temperature": 0.5, "max_tokens": 400},
            {"model": "gpt-3.5-turbo", "temperature": 0.6, "max_tokens": 300},
            {"model": "gpt-4", "temperature": 0.9, "max_tokens": 600},
            {"model": "gpt-3.5-turbo", "temperature": 0.3, "max_tokens": 350},
            {"model": "gpt-4", "temperature": 0.4, "max_tokens": 500},
            {"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 250},
            {"model": "gpt-4", "temperature": 0.6, "max_tokens": 700},
            {"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 400},
            {"model": "gpt-4", "temperature": 0.5, "max_tokens": 450},
        ]
        
        for i, config in enumerate(agent_configs[:num_agents]):
            agent = ChatOpenAI(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                openai_api_key=self.api_key
            )
            self.agents.append(agent)
        
        return self.agents
    
    async def sequential_execution(self, agents: List[ChatOpenAI], prompt: str) -> Dict[str, Any]:
        """Execute agents sequentially (LangChain's typical pattern)"""
        results = []
        total_tokens = 0
        start_time = time.time()
        
        for i, agent in enumerate(agents):
            try:
                response = await agent.ainvoke([HumanMessage(content=prompt)])
                results.append({
                    "agent_id": f"agent_{i}",
                    "content": response.content,
                    "success": True
                })
                # Estimate tokens (LangChain doesn't always provide this)
                total_tokens += len(prompt.split()) + len(response.content.split())
            except Exception as e:
                results.append({
                    "agent_id": f"agent_{i}",
                    "error": str(e),
                    "success": False
                })
        
        elapsed = time.time() - start_time
        
        return {
            "results": results,
            "total_time": elapsed,
            "total_tokens": total_tokens,
            "success_count": sum(1 for r in results if r.get("success", False))
        }
    
    async def parallel_execution_langchain(self, agents: List[ChatOpenAI], prompt: str) -> Dict[str, Any]:
        """
        Parallel execution with LangChain (requires manual implementation)
        LangChain doesn't have built-in parallel swarm coordination
        """
        start_time = time.time()
        
        async def execute_agent(agent, idx):
            try:
                response = await agent.ainvoke([HumanMessage(content=prompt)])
                return {
                    "agent_id": f"agent_{idx}",
                    "content": response.content,
                    "success": True
                }
            except Exception as e:
                return {
                    "agent_id": f"agent_{idx}",
                    "error": str(e),
                    "success": False
                }
        
        # Manual parallel execution using asyncio.gather
        tasks = [execute_agent(agent, i) for i, agent in enumerate(agents)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        
        # LangChain has NO consensus strategy - need to implement manually
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        
        return {
            "results": results,
            "total_time": elapsed,
            "success_count": len(successful_results),
            "note": "Manual parallel implementation - no built-in consensus"
        }


class LangChainBenchmarks:
    """Benchmark LangChain implementations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.langchain_agents = LangChainAgents(api_key)
        
    async def benchmark_sequential(self, num_agents: int = 3, num_tasks: int = 2) -> Dict[str, Any]:
        """Benchmark LangChain sequential execution"""
        agents = self.langchain_agents.create_agents(num_agents)
        
        test_prompts = [
            "Explain the benefits of microservices architecture in 2 sentences.",
            "What are the key principles of clean code? Answer briefly."
        ]
        
        times = []
        total_tokens = 0
        
        for prompt in test_prompts[:num_tasks]:
            result = await self.langchain_agents.sequential_execution(agents, prompt)
            times.append(result["total_time"])
            total_tokens += result["total_tokens"]
        
        import statistics
        return {
            "avg_time": statistics.mean(times),
            "total_tokens": total_tokens,
            "framework": "LangChain"
        }
    
    async def benchmark_parallel_manual(self, num_agents: int = 3, num_tasks: int = 2) -> Dict[str, Any]:
        """Benchmark LangChain with manual parallel implementation"""
        agents = self.langchain_agents.create_agents(num_agents)
        
        test_prompts = [
            "Explain the benefits of microservices architecture in 2 sentences.",
            "What are the key principles of clean code? Answer briefly."
        ]
        
        times = []
        
        for prompt in test_prompts[:num_tasks]:
            result = await self.langchain_agents.parallel_execution_langchain(agents, prompt)
            times.append(result["total_time"])
        
        import statistics
        return {
            "avg_time": statistics.mean(times),
            "framework": "LangChain (manual parallel)",
            "note": "No built-in consensus or coordination"
        }


if __name__ == "__main__":
    async def test():
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not set")
            return
        
        print("Testing LangChain implementations...")
        benchmarks = LangChainBenchmarks(api_key)
        
        print("\n[1] Sequential Execution")
        result1 = await benchmarks.benchmark_sequential(num_agents=2, num_tasks=1)
        print(f"   Avg Time: {result1['avg_time']:.2f}s")
        
        print("\n[2] Manual Parallel Execution")
        result2 = await benchmarks.benchmark_parallel_manual(num_agents=2, num_tasks=1)
        print(f"   Avg Time: {result2['avg_time']:.2f}s")
        
        print("\n✅ LangChain tests complete")
    
    asyncio.run(test())
