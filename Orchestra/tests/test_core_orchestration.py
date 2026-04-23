import asyncio
import pytest
from orchestra import (
    Orchestra,
    TreeOrchestrator,
    ChainOfThought,
    ParallelSwarm,
    ConsensusStrategy,
    IntegrationLayer
)


class TestTreeOrchestrator:
    def test_decision_node_creation(self):
        tree = TreeOrchestrator()
        tree.add_decision_node(
            node_id="test_node",
            condition=lambda ctx: ctx.get("test", False),
            action=lambda ctx: "test_action"
        )
        assert "test_node" in tree.node_registry
    
    def test_task_classification(self):
        tree = TreeOrchestrator()
        task = {"description": "test task", "complexity": "simple"}
        task_type, score = tree.classify_task(task)
        assert task_type is not None
        assert 0 <= score <= 1


class TestChainOfThought:
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        chain = ChainOfThought("test_chain")
        
        chain.add_step("step1", "First", lambda ctx: {"result": "step1_done"})
        chain.add_step("step2", "Second", lambda ctx: {"result": "step2_done"}, dependencies=["step1"])
        
        result = await chain.execute()
        
        assert result["completed_steps"] == 2
        assert "step1" in result["outputs"]
        assert "step2" in result["outputs"]
    
    @pytest.mark.asyncio
    async def test_dependency_resolution(self):
        chain = ChainOfThought("dep_chain")
        
        chain.add_step("a", "Step A", lambda ctx: {"a": 1})
        chain.add_step("b", "Step B", lambda ctx: {"b": 2}, dependencies=["a"])
        chain.add_step("c", "Step C", lambda ctx: {"c": 3}, dependencies=["a", "b"])
        
        result = await chain.execute()
        
        assert result["completed_steps"] == 3
        assert result["execution_order"] == ["a", "b", "c"]


class TestParallelSwarm:
    @pytest.mark.asyncio
    async def test_voting_consensus(self):
        swarm = ParallelSwarm("vote_swarm", consensus_strategy=ConsensusStrategy.VOTING)
        
        swarm.add_agent("a1", lambda ctx: {"vote": "A"})
        swarm.add_agent("a2", lambda ctx: {"vote": "A"})
        swarm.add_agent("a3", lambda ctx: {"vote": "B"})
        
        result = await swarm.execute({"test": True})
        
        assert result["merged_result"]["success"] == True
        assert result["merged_result"]["participating_agents"] == 3
    
    @pytest.mark.asyncio
    async def test_best_performer_consensus(self):
        swarm = ParallelSwarm("best_swarm", consensus_strategy=ConsensusStrategy.BEST_PERFORMER)
        
        swarm.add_agent("low", lambda ctx: {"score": 70})
        swarm.add_agent("high", lambda ctx: {"score": 95})
        swarm.add_agent("mid", lambda ctx: {"score": 80})
        
        result = await swarm.execute({"test": True})
        
        assert result["merged_result"]["success"] == True
    
    @pytest.mark.asyncio
    async def test_parallel_execution_speed(self):
        import time
        
        def slow_agent(ctx):
            time.sleep(0.1)
            return {"done": True}
        
        swarm = ParallelSwarm("speed_swarm")
        for i in range(5):
            swarm.add_agent(f"agent_{i}", slow_agent)
        
        start = time.time()
        result = await swarm.execute({"test": True})
        duration = time.time() - start
        
        # Should be ~0.1s (parallel) not ~0.5s (sequential)
        assert duration < 0.3
        assert result["merged_result"]["participating_agents"] == 5


class TestOrchestra:
    @pytest.mark.asyncio
    async def test_simple_task_routing(self):
        orchestra = Orchestra()
        
        chain = orchestra.create_chain("simple_chain")
        chain.add_step("step1", "Step 1", lambda ctx: {"done": True})
        
        task = {
            "id": "test_simple",
            "complexity": "simple",
            "chain_id": "simple_chain"
        }
        
        result = await orchestra.execute(task)
        
        assert result["routing"]["task_type"] == "simple"
        assert result["output"] is not None
    
    @pytest.mark.asyncio
    async def test_complex_task_routing(self):
        orchestra = Orchestra()
        
        swarm = orchestra.create_swarm("complex_swarm")
        swarm.add_agent("a1", lambda ctx: {"result": 1})
        swarm.add_agent("a2", lambda ctx: {"result": 2})
        
        task = {
            "id": "test_complex",
            "complexity": "complex",
            "swarm_id": "complex_swarm"
        }
        
        result = await orchestra.execute(task)
        
        assert result["routing"]["task_type"] == "complex"
        assert result["output"]["merged_result"]["success"] == True
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        orchestra = Orchestra()
        
        chain = orchestra.create_chain("metrics_chain")
        chain.add_step("step1", "Step 1", lambda ctx: {"done": True})
        
        task = {"id": "metrics_test", "complexity": "simple", "chain_id": "metrics_chain"}
        await orchestra.execute(task)
        
        metrics = orchestra.get_orchestration_metrics()
        
        assert metrics["total_executions"] >= 1
        assert metrics["active_chains"] >= 1
        
        history = orchestra.get_execution_history(limit=5)
        assert len(history) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
