import asyncio
import pytest
from orchestra import (
    WisdomLayer,
    PatternType,
    MetaLearner,
    SelfVerifyingCoT,
    BacktrackingCoT,
    TaskSimilarity,
    SimilarityMethod,
    CapabilityDiscovery,
    CapabilityMatcher,
    QLearningRouter,
    QState,
    QAction,
    RoutingOptimizer
)


class TestWisdomLayer:
    def test_pattern_recording(self):
        wisdom = WisdomLayer(min_evidence=2, min_confidence=0.5)
        
        executions = [
            {
                "task": {"type": "optimization"},
                "context": {"complexity": "high"},
                "decision": {"route": "parallel_swarm"},
                "result": {"success": True, "performance_score": 0.9}
            },
            {
                "task": {"type": "optimization"},
                "context": {"complexity": "high"},
                "decision": {"route": "parallel_swarm"},
                "result": {"success": True, "performance_score": 0.85}
            }
        ]
        
        for execution in executions:
            wisdom.record_execution(
                execution["task"],
                execution["context"],
                execution["decision"],
                execution["result"]
            )
        
        recommendation = wisdom.get_recommendation(
            PatternType.ROUTING,
            {"complexity": "high"}
        )
        
        assert recommendation is not None
        assert recommendation["confidence"] >= 0.5
    
    def test_wisdom_summary(self):
        wisdom = WisdomLayer()
        
        wisdom.record_execution(
            {"type": "test"},
            {"env": "prod"},
            {"action": "execute"},
            {"success": True}
        )
        
        summary = wisdom.get_wisdom_summary()
        
        assert "total_patterns" in summary
        assert "patterns_applied" in summary


class TestMetaLearner:
    def test_cross_task_analysis(self):
        meta_learner = MetaLearner(min_pattern_count=2)
        
        executions = [
            {
                "task": {"type": "optimization"},
                "context": {"complexity": "high"},
                "decision": {"route": "parallel"},
                "result": {"success": True, "performance_score": 0.9}
            },
            {
                "task": {"type": "analysis"},
                "context": {"complexity": "high"},
                "decision": {"route": "parallel"},
                "result": {"success": True, "performance_score": 0.85}
            }
        ]
        
        insights = meta_learner.analyze_cross_task_patterns(executions)
        
        assert isinstance(insights, list)


class TestSelfVerifyingCoT:
    @pytest.mark.asyncio
    async def test_verification_success(self):
        def verifier(context):
            return {
                "passed": True,
                "confidence": 0.9,
                "issues": [],
                "suggestions": []
            }
        
        cot = SelfVerifyingCoT(verifier=verifier, min_confidence_threshold=0.7)
        
        cot.add_step("step1", "Step 1", lambda ctx: {"result": "done"})
        
        result = await cot.execute()
        
        assert result["success"] == True
        assert result["statistics"]["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_verification_retry(self):
        call_count = {"count": 0}
        
        def failing_executor(ctx):
            call_count["count"] += 1
            if call_count["count"] < 2:
                return {"error": "failed"}
            return {"result": "success"}
        
        def verifier(context):
            output = context.get("output", {})
            if "error" in output:
                return {"passed": False, "confidence": 0.0, "issues": ["Error"], "suggestions": []}
            return {"passed": True, "confidence": 0.9, "issues": [], "suggestions": []}
        
        cot = SelfVerifyingCoT(verifier=verifier, max_retries=2)
        cot.add_step("step1", "Step 1", failing_executor)
        
        result = await cot.execute()
        
        assert call_count["count"] == 2


class TestBacktrackingCoT:
    @pytest.mark.asyncio
    async def test_alternative_paths(self):
        def primary_executor(ctx):
            return {"result": "primary", "confidence": 0.5}
        
        def alternative_executor(ctx):
            return {"result": "alternative", "confidence": 0.9}
        
        cot = BacktrackingCoT(confidence_threshold=0.7)
        
        cot.add_step(
            "step1",
            "Step 1",
            primary_executor,
            alternatives=[alternative_executor]
        )
        
        result = await cot.execute()
        
        assert result["success"] == True
        assert result["backtracks"] >= 0


class TestTaskSimilarity:
    def test_tfidf_similarity(self):
        task_sim = TaskSimilarity(method=SimilarityMethod.TFIDF)
        
        task_sim.add_task("task1", "optimize machine learning model", {})
        task_sim.add_task("task2", "improve neural network performance", {})
        task_sim.add_task("task3", "analyze customer data", {})
        
        task_sim.fit_tfidf()
        
        similar = task_sim.find_similar("optimize ML model", k=2)
        
        assert len(similar) <= 2
        assert all(isinstance(score, float) for _, score in similar)
    
    def test_hybrid_similarity(self):
        task_sim = TaskSimilarity(method=SimilarityMethod.HYBRID)
        
        task_sim.add_task("task1", "machine learning optimization", {})
        task_sim.add_task("task2", "ML model improvement", {})
        
        task_sim.fit_tfidf()
        
        similar = task_sim.find_similar("optimize machine learning", k=1)
        
        assert len(similar) >= 1


class TestCapabilityDiscovery:
    def test_capability_recording(self):
        discovery = CapabilityDiscovery(min_samples=2, confidence_threshold=0.6)
        
        discovery.record_execution("agent1", "optimization", True, 0.9)
        discovery.record_execution("agent1", "optimization", True, 0.85)
        discovery.record_execution("agent1", "optimization", True, 0.92)
        
        profile = discovery.get_agent_capabilities("agent1")
        
        assert profile is not None
        assert "optimization" in profile.capabilities
        assert profile.capabilities["optimization"].confidence >= 0.6
    
    def test_best_agent_selection(self):
        discovery = CapabilityDiscovery(min_samples=2)
        
        discovery.record_execution("agent1", "task_a", True, 0.95)
        discovery.record_execution("agent1", "task_a", True, 0.92)
        
        discovery.record_execution("agent2", "task_a", True, 0.70)
        discovery.record_execution("agent2", "task_a", True, 0.75)
        
        best = discovery.get_best_agent_for_task("task_a")
        
        assert best == "agent1"


class TestCapabilityMatcher:
    def test_best_fit_matching(self):
        discovery = CapabilityDiscovery(min_samples=1)
        
        discovery.record_execution("agent1", "optimization", True, 0.9)
        discovery.record_execution("agent2", "analysis", True, 0.8)
        
        matcher = CapabilityMatcher(discovery)
        
        task = {"type": "optimization"}
        available = ["agent1", "agent2"]
        
        matches = matcher.match_task_to_agents(task, available, strategy="best_fit")
        
        assert len(matches) > 0
        assert matches[0][0] == "agent1"


class TestQLearningRouter:
    def test_q_learning_update(self):
        router = QLearningRouter(learning_rate=0.1, epsilon=0.2)
        
        state = QState("optimization", "high", 3)
        action = QAction("parallel_swarm")
        
        reward = router.compute_reward(True, 2.0, 0.1, 0.9)
        
        router.update(state, action, reward)
        
        stats = router.get_statistics()
        
        assert stats["total_updates"] == 1
        assert stats["q_table_size"] >= 1
    
    def test_action_selection(self):
        router = QLearningRouter(epsilon=0.0)  # No exploration
        
        state = QState("test", "low", 1)
        action = QAction("chain_of_thought")
        
        # Train with high reward
        router.update(state, action, 10.0)
        
        selected = router.select_action(state)
        
        assert selected.routing_decision == "chain_of_thought"


class TestRoutingOptimizer:
    def test_optimal_routing(self):
        router = QLearningRouter()
        optimizer = RoutingOptimizer(router)
        
        task = {"type": "optimization", "complexity": "high"}
        context = {"available_agents": 3}
        
        routing = optimizer.get_optimal_routing(task, context)
        
        assert "routing_decision" in routing
        assert "state" in routing
        assert "action" in routing
    
    def test_continuous_learning(self):
        optimizer = RoutingOptimizer()
        
        task = {"type": "test"}
        context = {"available_agents": 2}
        
        routing = optimizer.get_optimal_routing(task, context)
        
        result = {"success": True, "execution_time": 1.5, "cost": 0.05, "performance_score": 0.9}
        optimizer.record_execution_result(task, context, routing, result)
        
        stats = optimizer.get_statistics()
        
        assert stats["total_optimizations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
