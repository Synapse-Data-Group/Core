import asyncio
from orchestra import Orchestra, ConsensusStrategy


def agent_explorer_1(context):
    print("  Agent 1: Exploring solution path A...")
    task = context.get("task", {})
    return {
        "agent_id": "explorer_1",
        "solution": "Path A: Use iterative approach",
        "confidence": 0.85,
        "estimated_time": 10
    }


def agent_explorer_2(context):
    print("  Agent 2: Exploring solution path B...")
    task = context.get("task", {})
    return {
        "agent_id": "explorer_2",
        "solution": "Path B: Use recursive approach",
        "confidence": 0.75,
        "estimated_time": 15
    }


def agent_explorer_3(context):
    print("  Agent 3: Exploring solution path C...")
    task = context.get("task", {})
    return {
        "agent_id": "explorer_3",
        "solution": "Path C: Use dynamic programming",
        "confidence": 0.90,
        "estimated_time": 12
    }


def agent_explorer_4(context):
    print("  Agent 4: Exploring solution path D...")
    task = context.get("task", {})
    return {
        "agent_id": "explorer_4",
        "solution": "Path D: Use greedy algorithm",
        "confidence": 0.70,
        "estimated_time": 8
    }


async def main():
    print("=" * 60)
    print("Example 2: Complex Task with Parallel Swarm")
    print("=" * 60)
    
    orchestra = Orchestra(
        clm_config={"threshold": 0.8},
        meo_config={"storage_path": "./memory"},
        default_consensus=ConsensusStrategy.BEST_PERFORMER
    )
    
    swarm = orchestra.create_swarm(
        "optimization_swarm",
        consensus_strategy=ConsensusStrategy.BEST_PERFORMER
    )
    
    swarm.add_agent(
        agent_id="explorer_1",
        executor=agent_explorer_1,
        load_threshold=0.8,
        metadata={"specialty": "iterative_solutions"}
    )
    
    swarm.add_agent(
        agent_id="explorer_2",
        executor=agent_explorer_2,
        load_threshold=0.8,
        metadata={"specialty": "recursive_solutions"}
    )
    
    swarm.add_agent(
        agent_id="explorer_3",
        executor=agent_explorer_3,
        load_threshold=0.8,
        metadata={"specialty": "dynamic_programming"}
    )
    
    swarm.add_agent(
        agent_id="explorer_4",
        executor=agent_explorer_4,
        load_threshold=0.8,
        metadata={"specialty": "greedy_algorithms"}
    )
    
    task = {
        "id": "task_002",
        "description": "Find optimal algorithm for large-scale data processing",
        "complexity": "complex",
        "complexity_score": 0.9,
        "requires_parallel": True,
        "swarm_id": "optimization_swarm",
        "max_agents": 4,
        "timeout": 30
    }
    
    print("\n[Executing Complex Task with Parallel Swarm]")
    print(f"Task: {task['description']}")
    print(f"Agents deployed: 4")
    print(f"Consensus strategy: {ConsensusStrategy.BEST_PERFORMER.value}\n")
    
    result = await orchestra.execute(task)
    
    print("\n[Routing Information]")
    print(f"Task Type: {result['routing']['task_type']}")
    print(f"Execution Mode: {result['routing']['execution_mode']}")
    print(f"Complexity Score: {result['routing']['complexity_score']}")
    
    print("\n[Swarm Execution Results]")
    swarm_result = result['output']
    print(f"Success: {swarm_result['merged_result']['success']}")
    print(f"Participating Agents: {swarm_result['merged_result']['participating_agents']}")
    print(f"Consensus Strategy: {swarm_result['merged_result']['consensus_strategy']}")
    
    print("\n[Merged Output (Best Performer)]")
    merged_output = swarm_result['merged_result']['merged_output']
    print(f"  Solution: {merged_output.get('solution', 'N/A')}")
    print(f"  Confidence: {merged_output.get('confidence', 0):.2f}")
    print(f"  Estimated Time: {merged_output.get('estimated_time', 0)} units")
    
    print("\n[Individual Agent Results]")
    for agent_id, agent_result in swarm_result['merged_result']['agent_results'].items():
        print(f"  {agent_id}:")
        print(f"    Solution: {agent_result.get('solution', 'N/A')}")
        print(f"    Confidence: {agent_result.get('confidence', 0):.2f}")
    
    print("\n[Agent Performance Summary]")
    for agent_id, agent_summary in swarm_result['agent_summary'].items():
        print(f"  {agent_id}:")
        print(f"    Status: {agent_summary['status']}")
        print(f"    Performance Score: {agent_summary['performance_score']:.3f}")
        print(f"    Cognitive Load: {agent_summary['cognitive_load']:.3f}")
        print(f"    Success Rate: {agent_summary['success_rate']:.2%}")
    
    print("\n[Swarm Statistics]")
    stats = swarm.get_swarm_statistics()
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Active Agents: {stats['active_agents']}")
    print(f"  Overloaded Agents: {stats['overloaded_agents']}")
    print(f"  Average Performance: {stats['average_performance']:.3f}")
    print(f"  Average Cognitive Load: {stats['average_cognitive_load']:.3f}")
    print(f"  Coordination Events: {stats['coordination_events']}")
    
    print("\n[CLM Report]")
    clm_report = result['clm_report']
    print(f"  Status: {clm_report.get('status', 'N/A')}")
    
    print("\n[MEO Stats]")
    meo_stats = result['meo_stats']
    print(f"  Status: {meo_stats.get('status', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
