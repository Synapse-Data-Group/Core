import asyncio
import os
from orchestra import (
    Orchestra,
    LLMConfig,
    LLMProvider,
    LLMManager,
    ConsensusStrategy,
    PromptTemplate
)


async def main():
    print("=" * 70)
    print("ORCHESTRA v2.0 - LLM PARALLEL SWARM EXAMPLE")
    print("Full LangChain Alternative with Multi-LLM Coordination")
    print("=" * 70)
    
    llm_manager = LLMManager()
    
    print("\n[1] Creating LLM Agents")
    print("-" * 70)
    
    gpt4_config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY", "your-key-here"),
        temperature=0.7,
        max_tokens=500
    )
    
    claude_config = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-sonnet-20240229",
        api_key=os.getenv("ANTHROPIC_API_KEY", "your-key-here"),
        temperature=0.7,
        max_tokens=500
    )
    
    ollama_config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="llama3",
        api_base="http://localhost:11434",
        temperature=0.7
    )
    
    print("✓ GPT-4 Agent configured")
    print("✓ Claude-3 Sonnet Agent configured")
    print("✓ Llama3 (Ollama) Agent configured")
    
    gpt4_agent = llm_manager.create_agent(
        "gpt4_explorer",
        gpt4_config,
        system_prompt="You are a strategic problem solver focused on innovative solutions."
    )
    
    claude_agent = llm_manager.create_agent(
        "claude_explorer",
        claude_config,
        system_prompt="You are an analytical thinker focused on thorough analysis."
    )
    
    ollama_agent = llm_manager.create_agent(
        "ollama_explorer",
        ollama_config,
        system_prompt="You are a practical problem solver focused on efficient solutions."
    )
    
    print("\n[2] Creating Prompt Template")
    print("-" * 70)
    
    prompt = PromptTemplate.from_template(
        "Solve this problem: {problem}\n\n"
        "Provide a concise solution in 2-3 sentences.\n"
        "Focus on: {focus_area}"
    )
    
    problem_text = prompt.format(
        problem="How to optimize a distributed system for low latency",
        focus_area="practical implementation strategies"
    )
    
    print(f"Prompt generated:\n{problem_text[:100]}...")
    
    print("\n[3] Creating Orchestra with LLM Swarm")
    print("-" * 70)
    
    orchestra = Orchestra(
        clm_config={"threshold": 0.8},
        meo_config={"storage_path": "./llm_memory"},
        default_consensus=ConsensusStrategy.BEST_PERFORMER
    )
    
    swarm = orchestra.create_swarm(
        "llm_swarm",
        consensus_strategy=ConsensusStrategy.VOTING
    )
    
    async def gpt4_executor(context):
        task = context.get("task", {})
        prompt_text = task.get("prompt", "")
        response = await gpt4_agent.execute(prompt_text)
        return {
            "model": "gpt-4",
            "solution": response.content,
            "tokens": response.total_tokens,
            "cost": response.cost_estimate,
            "latency": response.latency
        }
    
    async def claude_executor(context):
        task = context.get("task", {})
        prompt_text = task.get("prompt", "")
        response = await claude_agent.execute(prompt_text)
        return {
            "model": "claude-3-sonnet",
            "solution": response.content,
            "tokens": response.total_tokens,
            "cost": response.cost_estimate,
            "latency": response.latency
        }
    
    async def ollama_executor(context):
        task = context.get("task", {})
        prompt_text = task.get("prompt", "")
        response = await ollama_agent.execute(prompt_text)
        return {
            "model": "llama3",
            "solution": response.content,
            "tokens": response.total_tokens,
            "cost": 0.0,
            "latency": response.latency
        }
    
    swarm.add_agent("gpt4", gpt4_executor, load_threshold=0.8)
    swarm.add_agent("claude", claude_executor, load_threshold=0.8)
    swarm.add_agent("ollama", ollama_executor, load_threshold=0.8)
    
    print("✓ 3 LLM agents added to swarm")
    print("✓ Consensus strategy: VOTING")
    
    print("\n[4] Executing Parallel LLM Swarm")
    print("-" * 70)
    print("All 3 LLMs will solve the problem simultaneously...")
    print("Orchestra will merge results using voting consensus\n")
    
    task = {
        "id": "llm_task_001",
        "description": "Multi-LLM problem solving with parallel swarm",
        "complexity": "complex",
        "swarm_id": "llm_swarm",
        "prompt": problem_text
    }
    
    try:
        result = await orchestra.execute(task)
        
        print("\n[5] Results from Parallel LLM Swarm")
        print("=" * 70)
        
        if result['output']['merged_result']['success']:
            print(f"✓ Success! {result['output']['merged_result']['participating_agents']} LLMs participated\n")
            
            print("Individual LLM Responses:")
            print("-" * 70)
            for agent_id, agent_result in result['output']['merged_result']['agent_results'].items():
                print(f"\n{agent_id.upper()} ({agent_result['model']}):")
                print(f"  Solution: {agent_result['solution'][:150]}...")
                print(f"  Tokens: {agent_result['tokens']}")
                print(f"  Cost: ${agent_result['cost']:.4f}")
                print(f"  Latency: {agent_result['latency']:.2f}s")
            
            print("\n" + "=" * 70)
            print("CONSENSUS RESULT (Voting):")
            print("=" * 70)
            merged = result['output']['merged_result']['merged_output']
            print(f"Winning Solution: {merged['solution'][:200]}...")
            print(f"Model: {merged['model']}")
            
            print("\n[6] Agent Performance Metrics")
            print("-" * 70)
            for agent_id, summary in result['output']['agent_summary'].items():
                print(f"{agent_id}:")
                print(f"  Status: {summary['status']}")
                print(f"  Performance Score: {summary['performance_score']:.3f}")
                print(f"  Cognitive Load: {summary['cognitive_load']:.3f}")
            
            print("\n[7] Cost Analysis")
            print("-" * 70)
            total_cost = sum(
                r['cost'] for r in result['output']['merged_result']['agent_results'].values()
            )
            total_tokens = sum(
                r['tokens'] for r in result['output']['merged_result']['agent_results'].values()
            )
            print(f"Total Cost: ${total_cost:.4f}")
            print(f"Total Tokens: {total_tokens}")
            print(f"Average Latency: {sum(r['latency'] for r in result['output']['merged_result']['agent_results'].values()) / 3:.2f}s")
            
            print("\n[8] LLM Statistics")
            print("-" * 70)
            stats = llm_manager.get_all_statistics()
            for agent_id, agent_stats in stats.items():
                print(f"{agent_id}: {agent_stats['total_requests']} requests, "
                      f"{agent_stats['total_tokens']} tokens, "
                      f"${agent_stats['total_cost']:.4f} cost")
        
        else:
            print("✗ Swarm execution failed")
            print(f"Error: {result['output']['merged_result'].get('error', 'Unknown')}")
    
    except Exception as e:
        print(f"\n✗ Error during execution: {str(e)}")
        print("Note: Make sure to set your API keys as environment variables:")
        print("  export OPENAI_API_KEY='your-key'")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  Or run Ollama locally: ollama serve")
    
    print("\n" + "=" * 70)
    print("✓ LLM Parallel Swarm Example Complete")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Multi-provider LLM support (OpenAI, Anthropic, Ollama)")
    print("  ✓ Parallel execution of multiple LLMs")
    print("  ✓ Consensus-based result merging")
    print("  ✓ Cognitive load monitoring per LLM")
    print("  ✓ Cost and token tracking")
    print("  ✓ Performance-based agent selection")
    print("  ✓ Memory-embedded orchestration")


if __name__ == "__main__":
    asyncio.run(main())
