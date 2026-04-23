import asyncio
from orchestra import Orchestra, ConsensusStrategy


def data_collector_agent(context):
    task = context.get("task", {})
    return {"collected_data": ["item1", "item2", "item3"], "source": "agent_collector"}


def data_analyzer_agent(context):
    task = context.get("task", {})
    return {"analysis": "Pattern detected", "confidence": 0.88, "source": "agent_analyzer"}


def data_validator_agent(context):
    task = context.get("task", {})
    return {"validation": "passed", "errors": 0, "source": "agent_validator"}


async def preprocessing_step(context):
    print("  [CoT] Preprocessing data...")
    return {"preprocessed": True, "records": 1000}


async def transformation_step(context):
    print("  [CoT] Transforming data...")
    preprocessed = context.get("preprocessing", {})
    return {"transformed": True, "records": preprocessed.get("records", 0)}


async def aggregation_step(context):
    print("  [CoT] Aggregating results...")
    transformed = context.get("transformation", {})
    return {"aggregated": True, "final_count": transformed.get("records", 0)}


async def main():
    print("=" * 60)
    print("Example 3: Full Integration - CLM, MEO, and Emergent Coordination")
    print("=" * 60)
    
    orchestra = Orchestra(
        clm_config={"threshold": 0.75, "monitoring_enabled": True},
        meo_config={"storage_path": "./orchestra_memory", "max_entries": 1000},
        default_consensus=ConsensusStrategy.MERGE_ALL
    )
    
    print("\n[Scenario 1: Moderate Task - Memory-Guided Routing]")
    print("-" * 60)
    
    moderate_task = {
        "id": "task_003",
        "description": "Data pipeline with moderate complexity",
        "complexity": "moderate",
        "complexity_score": 0.6,
        "chain_id": "pipeline_chain"
    }
    
    chain = orchestra.create_chain("pipeline_chain")
    chain.add_step("preprocessing", "Preprocess raw data", preprocessing_step)
    chain.add_step("transformation", "Transform data format", transformation_step, dependencies=["preprocessing"])
    chain.add_step("aggregation", "Aggregate final results", aggregation_step, dependencies=["transformation"])
    
    result_1 = await orchestra.execute(moderate_task)
    
    print(f"\nRouting Decision: {result_1['routing']['execution_mode']}")
    print(f"Routing Path: {result_1['routing']['path']}")
    print(f"Guidance: {result_1['routing'].get('routing_guidance', {})}")
    
    print("\n[Scenario 2: Complex Task - Parallel Swarm with CLM/MEO]")
    print("-" * 60)
    
    swarm = orchestra.create_swarm(
        "data_processing_swarm",
        consensus_strategy=ConsensusStrategy.MERGE_ALL
    )
    
    swarm.add_agent("collector", data_collector_agent, load_threshold=0.7)
    swarm.add_agent("analyzer", data_analyzer_agent, load_threshold=0.7)
    swarm.add_agent("validator", data_validator_agent, load_threshold=0.7)
    
    complex_task = {
        "id": "task_004",
        "description": "Multi-agent data processing with validation",
        "complexity": "complex",
        "complexity_score": 0.85,
        "requires_parallel": True,
        "swarm_id": "data_processing_swarm",
        "max_agents": 3
    }
    
    print("\n[Executing with Parallel Swarm]")
    result_2 = await orchestra.execute(complex_task)
    
    print(f"\nSwarm Execution:")
    print(f"  Participating Agents: {result_2['output']['merged_result']['participating_agents']}")
    print(f"  Success: {result_2['output']['merged_result']['success']}")
    
    print("\n[Merged Results from All Agents]")
    merged = result_2['output']['merged_result']['merged_output']
    if isinstance(merged, list):
        for item in merged:
            print(f"  - {item}")
    
    print("\n[Agent Load Monitoring (CLM Integration)]")
    for agent_id, summary in result_2['output']['agent_summary'].items():
        status_indicator = "✓" if summary['status'] == 'completed' else "✗"
        load_indicator = "⚠" if summary['cognitive_load'] > 0.7 else "✓"
        print(f"  {status_indicator} {agent_id}:")
        print(f"      Load: {summary['cognitive_load']:.3f} {load_indicator}")
        print(f"      Performance: {summary['performance_score']:.3f}")
    
    print("\n[Memory Updates (MEO Integration)]")
    meo_stats = result_2['meo_stats']
    print(f"  Memory Status: {meo_stats.get('status', 'N/A')}")
    print(f"  Total Entries: {meo_stats.get('total_entries', 0)}")
    
    print("\n[Scenario 3: Emergent Coordination - Agent Adaptation]")
    print("-" * 60)
    
    def overloaded_agent(context):
        import time
        time.sleep(0.1)
        return {"result": "slow_computation", "load": "high"}
    
    def fast_agent(context):
        return {"result": "fast_computation", "load": "low"}
    
    adaptive_swarm = orchestra.create_swarm(
        "adaptive_swarm",
        consensus_strategy=ConsensusStrategy.VOTING
    )
    
    adaptive_swarm.add_agent("slow_agent", overloaded_agent, load_threshold=0.5)
    adaptive_swarm.add_agent("fast_agent_1", fast_agent, load_threshold=0.8)
    adaptive_swarm.add_agent("fast_agent_2", fast_agent, load_threshold=0.8)
    
    adaptive_task = {
        "id": "task_005",
        "description": "Task requiring adaptive coordination",
        "complexity": "complex",
        "swarm_id": "adaptive_swarm",
        "max_agents": 3
    }
    
    result_3 = await orchestra.execute(adaptive_task)
    
    print("\n[Coordination Events]")
    coordination_count = result_3['output'].get('coordination_events', 0)
    print(f"  Total Coordination Events: {coordination_count}")
    
    print("\n[Final Agent States]")
    for agent_id, summary in result_3['output']['agent_summary'].items():
        print(f"  {agent_id}:")
        print(f"    Final Status: {summary['status']}")
        print(f"    Cognitive Load: {summary['cognitive_load']:.3f}")
        if summary.get('error'):
            print(f"    Error: {summary['error']}")
    
    print("\n[Overall Orchestration Metrics]")
    print("-" * 60)
    metrics = orchestra.get_orchestration_metrics()
    print(f"Total Executions: {metrics['total_executions']}")
    print(f"Active Chains: {metrics['active_chains']}")
    print(f"Active Swarms: {metrics['active_swarms']}")
    
    print("\n[Integration Layer Report]")
    integration_report = metrics['integration_report']
    print(f"Integration Events: {integration_report['integration_events']}")
    print(f"CLM Status: {integration_report['clm_status'].get('status', 'N/A')}")
    print(f"MEO Status: {integration_report['meo_status'].get('status', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✓ Full Integration Example Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
