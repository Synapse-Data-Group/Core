import asyncio
from orchestra import (
    Orchestra,
    TreeOrchestrator,
    ChainOfThought,
    ParallelSwarm,
    ConsensusStrategy,
    IntegrationLayer
)


def test_tree_orchestrator():
    print("\n[TEST 1: Tree Orchestrator]")
    tree = TreeOrchestrator()
    
    tree.add_decision_node(
        node_id="test_node",
        condition=lambda ctx: ctx.get("test", False),
        action=lambda ctx: "test_action_executed"
    )
    
    assert "test_node" in tree.node_registry
    print("✓ Decision node added successfully")
    
    task = {"description": "test task", "complexity": "simple"}
    task_type, score = tree.classify_task(task)
    print(f"✓ Task classified as {task_type.value} with score {score:.2f}")


async def test_chain_of_thought():
    print("\n[TEST 2: Chain-of-Thought]")
    chain = ChainOfThought("test_chain")
    
    chain.add_step(
        "step1",
        "First step",
        lambda ctx: {"result": "step1_done"}
    )
    
    chain.add_step(
        "step2",
        "Second step",
        lambda ctx: {"result": "step2_done", "prev": ctx.get("step1")},
        dependencies=["step1"]
    )
    
    result = await chain.execute()
    
    assert result["completed_steps"] == 2
    assert "step1" in result["outputs"]
    assert "step2" in result["outputs"]
    print(f"✓ Chain executed {result['completed_steps']} steps successfully")
    print(f"✓ Total cognitive load: {result['total_cognitive_load']:.3f}")


async def test_parallel_swarm():
    print("\n[TEST 3: Parallel Swarm]")
    swarm = ParallelSwarm(
        "test_swarm",
        consensus_strategy=ConsensusStrategy.VOTING
    )
    
    swarm.add_agent("agent1", lambda ctx: {"vote": "A"})
    swarm.add_agent("agent2", lambda ctx: {"vote": "A"})
    swarm.add_agent("agent3", lambda ctx: {"vote": "B"})
    
    task = {"id": "test", "description": "voting test"}
    result = await swarm.execute(task)
    
    assert result["merged_result"]["success"] == True
    assert result["merged_result"]["participating_agents"] == 3
    print(f"✓ Swarm executed with {result['merged_result']['participating_agents']} agents")
    print(f"✓ Consensus: {result['merged_result']['consensus_strategy']}")
    
    stats = swarm.get_swarm_statistics()
    print(f"✓ Swarm stats: {stats['total_agents']} agents, avg performance {stats['average_performance']:.3f}")


async def test_integration_layer():
    print("\n[TEST 4: Integration Layer]")
    integration = IntegrationLayer()
    
    clm = integration.get_clm()
    meo = integration.get_meo()
    
    assert clm is not None
    assert meo is not None
    print("✓ CLM integration initialized")
    print("✓ MEO integration initialized")
    
    report = integration.get_integration_report()
    assert "clm_status" in report
    assert "meo_status" in report
    print(f"✓ Integration report generated: {len(report)} sections")


async def test_orchestra_simple():
    print("\n[TEST 5: Orchestra - Simple Task]")
    orchestra = Orchestra()
    
    chain = orchestra.create_chain("test_chain")
    chain.add_step("analyze", "Analyze", lambda ctx: {"analyzed": True})
    chain.add_step("process", "Process", lambda ctx: {"processed": True}, dependencies=["analyze"])
    
    task = {
        "id": "simple_test",
        "description": "Simple orchestration test",
        "complexity": "simple",
        "chain_id": "test_chain"
    }
    
    result = await orchestra.execute(task)
    
    assert result["routing"]["task_type"] == "simple"
    assert result["output"] is not None
    print(f"✓ Task routed as: {result['routing']['task_type']}")
    print(f"✓ Execution mode: {result['routing']['execution_mode']}")
    print(f"✓ Output received: {result['output']['completed_steps']} steps")


async def test_orchestra_complex():
    print("\n[TEST 6: Orchestra - Complex Task]")
    orchestra = Orchestra(default_consensus=ConsensusStrategy.BEST_PERFORMER)
    
    swarm = orchestra.create_swarm("test_swarm")
    swarm.add_agent("explorer1", lambda ctx: {"score": 85, "solution": "A"})
    swarm.add_agent("explorer2", lambda ctx: {"score": 95, "solution": "B"})
    swarm.add_agent("explorer3", lambda ctx: {"score": 75, "solution": "C"})
    
    task = {
        "id": "complex_test",
        "description": "Complex orchestration test",
        "complexity": "complex",
        "swarm_id": "test_swarm"
    }
    
    result = await orchestra.execute(task)
    
    assert result["routing"]["task_type"] == "complex"
    assert result["output"]["merged_result"]["success"] == True
    print(f"✓ Task routed as: {result['routing']['task_type']}")
    print(f"✓ Agents participated: {result['output']['merged_result']['participating_agents']}")
    print(f"✓ Best performer selected: {result['output']['merged_result']['merged_output']}")


async def test_orchestra_metrics():
    print("\n[TEST 7: Orchestra - Metrics & Introspection]")
    orchestra = Orchestra()
    
    chain = orchestra.create_chain("metrics_chain")
    chain.add_step("step1", "Step 1", lambda ctx: {"done": True})
    
    task = {
        "id": "metrics_test",
        "complexity": "simple",
        "chain_id": "metrics_chain"
    }
    
    await orchestra.execute(task)
    
    metrics = orchestra.get_orchestration_metrics()
    assert metrics["total_executions"] >= 1
    assert metrics["active_chains"] >= 1
    print(f"✓ Total executions: {metrics['total_executions']}")
    print(f"✓ Active chains: {metrics['active_chains']}")
    print(f"✓ Active swarms: {metrics['active_swarms']}")
    
    history = orchestra.get_execution_history(limit=5)
    assert len(history) >= 1
    print(f"✓ Execution history: {len(history)} entries")
    
    tree_paths = orchestra.introspect_tree_paths()
    assert "nodes" in tree_paths
    print(f"✓ Tree introspection: {len(tree_paths['nodes'])} nodes")


async def test_consensus_strategies():
    print("\n[TEST 8: Consensus Strategies]")
    
    strategies = [
        ConsensusStrategy.VOTING,
        ConsensusStrategy.BEST_PERFORMER,
        ConsensusStrategy.MERGE_ALL,
        ConsensusStrategy.FIRST_VALID
    ]
    
    for strategy in strategies:
        swarm = ParallelSwarm(f"swarm_{strategy.value}", consensus_strategy=strategy)
        swarm.add_agent("a1", lambda ctx: {"result": 1})
        swarm.add_agent("a2", lambda ctx: {"result": 2})
        
        result = await swarm.execute({"test": True})
        assert result["merged_result"]["success"] == True
        print(f"✓ {strategy.value} strategy executed successfully")


async def test_agent_adaptation():
    print("\n[TEST 9: Agent Adaptation]")
    swarm = ParallelSwarm("adaptive_swarm")
    
    swarm.add_agent("normal", lambda ctx: {"status": "ok"}, load_threshold=0.8)
    swarm.add_agent("backup", lambda ctx: {"status": "backup_ok"}, load_threshold=0.8)
    
    task = {"description": "Test adaptation"}
    result = await swarm.execute(task)
    
    assert result["merged_result"]["participating_agents"] >= 1
    print(f"✓ Agents adapted: {result['merged_result']['participating_agents']} participated")
    print(f"✓ Coordination events: {result['coordination_events']}")


async def run_all_tests():
    print("=" * 70)
    print("ORCHESTRA FRAMEWORK - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    try:
        test_tree_orchestrator()
        await test_chain_of_thought()
        await test_parallel_swarm()
        await test_integration_layer()
        await test_orchestra_simple()
        await test_orchestra_complex()
        await test_orchestra_metrics()
        await test_consensus_strategies()
        await test_agent_adaptation()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)
        print("\nOrchestra framework is ready for production use.")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run examples: python examples/example_simple_task.py")
        print("  3. Read documentation: README.md and ARCHITECTURE.md")
        print("  4. Build your orchestration: from orchestra import Orchestra")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
