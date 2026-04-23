"""
Simple test script to verify MEO package functionality
Run with: python test_meo.py
"""

def test_imports():
    print("Testing imports...")
    try:
        from meo import WisdomOrchestrator
        from meo.memory import EpisodicMemory, SemanticMemory, StorageBackend
        from meo.evaluators import Evaluator, DefaultRewardEvaluator
        from meo.meta import PolicyAdapter, RuleBasedPolicyAdapter
        from meo.utils import get_logger, embed_text
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_orchestration():
    print("\nTesting basic orchestration...")
    try:
        from meo import WisdomOrchestrator
        
        def simple_agent(input_data):
            return {"result": f"Processed: {input_data}", "success": True}
        
        orchestrator = WisdomOrchestrator()
        result = orchestrator.run(agent=simple_agent, input_data="test")
        
        assert result["success"] == True
        assert "workflow_id" in result
        assert "result" in result
        
        print("✓ Basic orchestration works")
        return True
    except Exception as e:
        print(f"✗ Orchestration failed: {e}")
        return False


def test_memory_system():
    print("\nTesting memory system...")
    try:
        from meo.memory import InMemoryEpisodicMemory, LLMSemanticMemory
        
        episodic = InMemoryEpisodicMemory()
        
        episode = episodic.record_step(
            workflow_id="test_workflow",
            state={"step": 1},
            action="test_action",
            action_input="input",
            action_output="output",
            metrics={"duration": 0.5},
            metadata={"success": True}
        )
        
        episodes = episodic.get_workflow_episodes("test_workflow")
        assert len(episodes) == 1
        assert episodes[0].action == "test_action"
        
        semantic = LLMSemanticMemory()
        insights = semantic.compress_episodes(episodes)
        assert len(insights) > 0
        
        print("✓ Memory system works")
        return True
    except Exception as e:
        print(f"✗ Memory system failed: {e}")
        return False


def test_evaluation():
    print("\nTesting evaluation system...")
    try:
        from meo.evaluators import DefaultRewardEvaluator
        from meo.memory import InMemoryEpisodicMemory
        
        episodic = InMemoryEpisodicMemory()
        
        for i in range(5):
            episodic.record_step(
                workflow_id="eval_test",
                state={},
                action=f"action_{i}",
                action_input=i,
                action_output=i*2,
                metrics={"latency": 0.1, "cost": 0.01},
                metadata={"success": True}
            )
        
        evaluator = DefaultRewardEvaluator()
        episodes = episodic.get_workflow_episodes("eval_test")
        result = evaluator.evaluate(episodes)
        
        assert result.workflow_id == "eval_test"
        assert "reward" in result.to_dict()
        assert "metrics" in result.to_dict()
        
        print("✓ Evaluation system works")
        return True
    except Exception as e:
        print(f"✗ Evaluation failed: {e}")
        return False


def test_policy_adapter():
    print("\nTesting policy adapter...")
    try:
        from meo.meta import RuleBasedPolicyAdapter, PolicyRule
        
        adapter = RuleBasedPolicyAdapter()
        
        rule = PolicyRule(
            rule_id="test_rule",
            rule_type="preference",
            condition="task:analysis",
            action="use_tool_a",
            priority=1,
            confidence=0.9
        )
        
        adapter.add_rule(rule)
        
        decision = adapter.adapt_decision(
            context={"task": "analysis"},
            available_actions=["use_tool_a", "use_tool_b"]
        )
        
        assert "recommended_action" in decision
        assert "action_scores" in decision
        
        print("✓ Policy adapter works")
        return True
    except Exception as e:
        print(f"✗ Policy adapter failed: {e}")
        return False


def test_storage():
    print("\nTesting storage backends...")
    try:
        import os
        import tempfile
        from meo.memory import JSONLStorage, SQLiteStorage
        
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = os.path.join(tmpdir, "test.jsonl")
            jsonl_storage = JSONLStorage(jsonl_path)
            
            jsonl_storage.save("test_key", {"data": "value"})
            loaded = jsonl_storage.load("test_key")
            assert loaded["data"] == "value"
            
            db_path = os.path.join(tmpdir, "test.db")
            sqlite_storage = SQLiteStorage(db_path)
            
            sqlite_storage.save("test_key", {"data": "value"})
            loaded = sqlite_storage.load("test_key")
            assert loaded["data"] == "value"
        
        print("✓ Storage backends work")
        return True
    except Exception as e:
        print(f"✗ Storage failed: {e}")
        return False


def test_integrations():
    print("\nTesting framework integrations...")
    try:
        from meo.integrations.langchain_wrapper import LangChainWrapper
        from meo.integrations.autogen_wrapper import AutogenWrapper
        
        langchain_wrapper = LangChainWrapper()
        autogen_wrapper = AutogenWrapper()
        
        assert langchain_wrapper is not None
        assert autogen_wrapper is not None
        
        print("✓ Integration wrappers available")
        return True
    except Exception as e:
        print(f"✗ Integrations failed: {e}")
        return False


def test_full_workflow():
    print("\nTesting full workflow with all components...")
    try:
        from meo import WisdomOrchestrator
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from meo.config import DefaultConfig
            config = DefaultConfig()
            config.STORAGE_DIR = tmpdir
            config.SEMANTIC_COMPRESSION_THRESHOLD = 2
            
            orchestrator = WisdomOrchestrator(config=config)
            
            def test_agent(input_data):
                return {
                    "result": f"Processed {input_data}",
                    "success": True,
                    "quality": 0.9
                }
            
            for i in range(3):
                result = orchestrator.run(
                    agent=test_agent,
                    input_data=f"task_{i}",
                    metadata={"iteration": i}
                )
                assert result["success"] == True
            
            history = orchestrator.get_workflow_history()
            assert len(history) >= 3
            
            insights = orchestrator.get_insights()
            assert len(insights) > 0
            
            recommendation = orchestrator.get_policy_recommendation(
                context={"task": "test"},
                available_actions=["action_a", "action_b"]
            )
            assert "recommended_action" in recommendation
        
        print("✓ Full workflow integration works")
        return True
    except Exception as e:
        print(f"✗ Full workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("MEO Package Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_orchestration,
        test_memory_system,
        test_evaluation,
        test_policy_adapter,
        test_storage,
        test_integrations,
        test_full_workflow,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! MEO package is working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
