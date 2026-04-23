import asyncio
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
    RoutingOptimizer
)


async def main():
    print("=" * 70)
    print("ORCHESTRA v4.0 - NEXT-GENERATION INTELLIGENCE")
    print("Wisdom Layer • Advanced CoT • Semantic Similarity • Self-Learning")
    print("=" * 70)
    
    print("\n[1] WISDOM LAYER - Meta-Learning Across Tasks")
    print("-" * 70)
    
    wisdom = WisdomLayer(min_evidence=3, min_confidence=0.6)
    
    print("Recording task executions to build wisdom...")
    
    executions = [
        {
            "task": {"type": "optimization", "id": "task1"},
            "context": {"complexity": "high", "domain": "ml"},
            "decision": {"type": "routing", "route": "parallel_swarm"},
            "result": {"success": True, "performance_score": 0.92}
        },
        {
            "task": {"type": "optimization", "id": "task2"},
            "context": {"complexity": "high", "domain": "ml"},
            "decision": {"type": "routing", "route": "parallel_swarm"},
            "result": {"success": True, "performance_score": 0.88}
        },
        {
            "task": {"type": "optimization", "id": "task3"},
            "context": {"complexity": "high", "domain": "ml"},
            "decision": {"type": "routing", "route": "parallel_swarm"},
            "result": {"success": True, "performance_score": 0.95}
        },
        {
            "task": {"type": "analysis", "id": "task4"},
            "context": {"complexity": "low", "domain": "data"},
            "decision": {"type": "routing", "route": "chain_of_thought"},
            "result": {"success": True, "performance_score": 0.85}
        },
    ]
    
    for execution in executions:
        wisdom.record_execution(
            execution["task"],
            execution["context"],
            execution["decision"],
            execution["result"]
        )
    
    print(f"✓ Recorded {len(executions)} executions")
    
    recommendation = wisdom.get_recommendation(
        PatternType.ROUTING,
        {"complexity": "high", "domain": "ml"}
    )
    
    if recommendation:
        print(f"\n✓ Wisdom recommendation found!")
        print(f"  Recommendation: {recommendation['recommendation']}")
        print(f"  Confidence: {recommendation['confidence']:.2f}")
        print(f"  Success rate: {recommendation['success_rate']:.1%}")
        print(f"  Evidence: {recommendation['evidence_count']} executions")
    
    summary = wisdom.get_wisdom_summary()
    print(f"\nWisdom Summary:")
    print(f"  Total patterns: {summary['total_patterns']}")
    print(f"  Patterns applied: {summary['patterns_applied']}")
    
    print("\n[2] META-LEARNER - Cross-Task Pattern Discovery")
    print("-" * 70)
    
    meta_learner = MetaLearner(min_pattern_count=3)
    
    insights = meta_learner.analyze_cross_task_patterns(executions)
    
    print(f"✓ Discovered {len(insights)} meta-insights")
    
    for insight in insights[:2]:
        print(f"\n  Insight: {insight.insight}")
        print(f"  Category: {insight.category}")
        print(f"  Confidence: {insight.confidence:.2f}")
        print(f"  Generality: {insight.generality_score:.2f}")
    
    print("\n[3] SELF-VERIFYING CHAIN-OF-THOUGHT")
    print("-" * 70)
    
    def step1_executor(context):
        return {"data_loaded": True, "records": 1000}
    
    def step2_executor(context):
        if context.get("data_loaded"):
            return {"data_cleaned": True, "valid_records": 950}
        return {"error": "Data not loaded"}
    
    def step3_executor(context):
        if context.get("data_cleaned"):
            return {"analysis_complete": True, "insights": 5}
        return {"error": "Data not cleaned"}
    
    def verifier(context):
        output = context.get("output")
        
        if output and isinstance(output, dict):
            if "error" in output:
                return {
                    "passed": False,
                    "confidence": 0.0,
                    "issues": [f"Error detected: {output['error']}"],
                    "suggestions": ["Fix the error before proceeding"]
                }
            
            return {
                "passed": True,
                "confidence": 0.9,
                "issues": [],
                "suggestions": []
            }
        
        return {"passed": False, "confidence": 0.0, "issues": ["Invalid output"], "suggestions": []}
    
    cot = SelfVerifyingCoT(verifier=verifier, min_confidence_threshold=0.7, max_retries=2)
    
    cot.add_step("load_data", "Load dataset", step1_executor)
    cot.add_step("clean_data", "Clean and validate data", step2_executor, dependencies=["load_data"])
    cot.add_step("analyze", "Perform analysis", step3_executor, dependencies=["clean_data"])
    
    print("Executing self-verifying chain-of-thought...")
    
    result = await cot.execute()
    
    if result["success"]:
        print(f"\n✓ All steps verified and completed!")
        print(f"  Steps executed: {len(result['execution_order'])}")
        print(f"  Verification rate: {result['statistics']['success_rate']:.1%}")
        
        trace = cot.get_reasoning_trace()
        for step in trace:
            print(f"\n  Step: {step['step_id']}")
            print(f"    Verified: {step['verification_passed']}")
            print(f"    Confidence: {step['confidence']:.2f}")
    
    print("\n[4] BACKTRACKING CHAIN-OF-THOUGHT")
    print("-" * 70)
    
    def risky_step_v1(context):
        import random
        if random.random() > 0.3:
            return {"result": "success_v1", "confidence": 0.5}
        return {"error": "Failed"}
    
    def risky_step_v2(context):
        return {"result": "success_v2", "confidence": 0.9}
    
    def safe_step(context):
        return {"result": "completed"}
    
    backtrack_cot = BacktrackingCoT(confidence_threshold=0.7, max_backtracks=3)
    
    backtrack_cot.add_step(
        "risky_operation",
        "Attempt risky operation",
        risky_step_v1,
        alternatives=[risky_step_v2]
    )
    backtrack_cot.add_step(
        "finalize",
        "Finalize result",
        safe_step,
        dependencies=["risky_operation"]
    )
    
    print("Executing backtracking CoT (will try alternatives if needed)...")
    
    result = await backtrack_cot.execute()
    
    if result["success"]:
        print(f"\n✓ Found successful path!")
        print(f"  Path taken: {' → '.join(result['path_taken'])}")
        print(f"  Backtracks: {result['backtracks']}")
        print(f"  Paths explored: {result['paths_explored']}")
        print(f"  Final confidence: {result['confidence']:.2f}")
    
    print("\n[5] SEMANTIC TASK SIMILARITY")
    print("-" * 70)
    
    task_sim = TaskSimilarity(method=SimilarityMethod.HYBRID)
    
    task_sim.add_task("task1", "Optimize machine learning model performance", {"priority": "high"})
    task_sim.add_task("task2", "Improve neural network accuracy", {"priority": "high"})
    task_sim.add_task("task3", "Analyze customer data trends", {"priority": "medium"})
    task_sim.add_task("task4", "Optimize database query speed", {"priority": "low"})
    task_sim.add_task("task5", "Enhance ML model efficiency", {"priority": "high"})
    
    task_sim.fit_tfidf()
    
    print("✓ Indexed 5 tasks with hybrid similarity (TF-IDF + MinHash + LSH)")
    
    query = "Improve machine learning model"
    similar = task_sim.find_similar(query, k=3, threshold=0.3)
    
    print(f"\nQuery: '{query}'")
    print(f"Similar tasks found:")
    for task_id, score in similar:
        metadata = task_sim.get_task_metadata(task_id)
        print(f"  {task_id}: {score:.3f} (priority: {metadata.get('priority', 'N/A')})")
    
    stats = task_sim.get_statistics()
    print(f"\nSimilarity stats:")
    print(f"  Method: {stats['method']}")
    print(f"  Total tasks: {stats['total_tasks']}")
    if "lsh_stats" in stats:
        print(f"  LSH buckets: {stats['lsh_stats']['total_buckets']}")
    
    print("\n[6] AGENT CAPABILITY DISCOVERY")
    print("-" * 70)
    
    capability_discovery = CapabilityDiscovery(min_samples=2, confidence_threshold=0.6)
    
    print("Agents discovering their capabilities through execution...")
    
    agent_executions = [
        ("agent_alpha", "optimization", True, 0.92),
        ("agent_alpha", "optimization", True, 0.88),
        ("agent_alpha", "optimization", True, 0.95),
        ("agent_alpha", "analysis", False, 0.45),
        ("agent_beta", "analysis", True, 0.85),
        ("agent_beta", "analysis", True, 0.90),
        ("agent_beta", "optimization", True, 0.70),
        ("agent_gamma", "optimization", True, 0.88),
        ("agent_gamma", "analysis", True, 0.82),
        ("agent_gamma", "data_processing", True, 0.91),
    ]
    
    for agent_id, task_type, success, performance in agent_executions:
        capability_discovery.record_execution(agent_id, task_type, success, performance)
    
    print(f"\n✓ Recorded {len(agent_executions)} executions")
    
    for agent_id in ["agent_alpha", "agent_beta", "agent_gamma"]:
        profile = capability_discovery.get_agent_capabilities(agent_id)
        if profile:
            print(f"\n{agent_id}:")
            print(f"  Capabilities discovered: {len(profile.capabilities)}")
            for cap_name, cap in profile.capabilities.items():
                print(f"    • {cap_name}: {cap.confidence:.2f} confidence, {cap.success_rate:.1%} success")
            print(f"  Specialization: {profile.specialization_score:.2f}")
            print(f"  Versatility: {profile.versatility_score:.2f}")
    
    best_for_optimization = capability_discovery.get_best_agent_for_task("optimization")
    print(f"\n✓ Best agent for optimization: {best_for_optimization}")
    
    print("\n[7] CAPABILITY-BASED MATCHING")
    print("-" * 70)
    
    matcher = CapabilityMatcher(capability_discovery)
    
    task = {"type": "optimization", "complexity": "high"}
    available_agents = ["agent_alpha", "agent_beta", "agent_gamma"]
    
    matches = matcher.match_task_to_agents(task, available_agents, strategy="best_fit")
    
    print(f"Task: {task['type']}")
    print(f"Matched agents (best_fit strategy):")
    for agent_id, score in matches[:3]:
        print(f"  {agent_id}: {score:.3f}")
    
    print("\n[8] REINFORCEMENT LEARNING ROUTER")
    print("-" * 70)
    
    rl_router = QLearningRouter(learning_rate=0.1, epsilon=0.2)
    
    print("Training router with Q-learning...")
    
    training_scenarios = [
        (QState("optimization", "high", 3), "parallel_swarm", True, 2.5, 0.1, 0.92),
        (QState("optimization", "high", 3), "parallel_swarm", True, 2.3, 0.1, 0.88),
        (QState("analysis", "low", 1), "chain_of_thought", True, 1.0, 0.0, 0.85),
        (QState("analysis", "low", 1), "chain_of_thought", True, 0.9, 0.0, 0.90),
    ]
    
    for state, decision, success, exec_time, cost, performance in training_scenarios:
        from orchestra.reinforcement.q_learning import QAction
        action = QAction(decision)
        reward = rl_router.compute_reward(success, exec_time, cost, performance)
        rl_router.update(state, action, reward)
    
    print(f"✓ Trained on {len(training_scenarios)} scenarios")
    
    test_state = QState("optimization", "high", 3)
    best_action, q_value = rl_router.get_best_action_for_state(test_state)
    
    print(f"\nLearned policy for {test_state.to_key()}:")
    print(f"  Best action: {best_action.to_key()}")
    print(f"  Q-value: {q_value:.3f}")
    
    q_values = rl_router.get_q_values_for_state(test_state)
    print(f"\n  All Q-values:")
    for action_key, value in sorted(q_values.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    {action_key}: {value:.3f}")
    
    stats = rl_router.get_statistics()
    print(f"\nRouter stats:")
    print(f"  Exploration rate: {stats['exploration_rate']:.1%}")
    print(f"  Current epsilon: {stats['current_epsilon']:.3f}")
    
    print("\n[9] ROUTING OPTIMIZER")
    print("-" * 70)
    
    optimizer = RoutingOptimizer(rl_router)
    
    task = {"type": "optimization", "complexity": "high"}
    context = {"available_agents": 3}
    
    routing = optimizer.get_optimal_routing(task, context)
    
    print(f"Optimal routing for task:")
    print(f"  Decision: {routing['routing_decision']}")
    print(f"  Consensus: {routing['consensus_strategy']}")
    
    result = {"success": True, "execution_time": 2.1, "cost": 0.08, "performance_score": 0.94}
    optimizer.record_execution_result(task, context, routing, result)
    
    print(f"\n✓ Recorded execution result for continuous learning")
    
    print("\n" + "=" * 70)
    print("✓ Orchestra v4.0 Intelligence Features Complete")
    print("=" * 70)
    
    print("\nKey Innovations Demonstrated:")
    print("\n  🧠 WISDOM LAYER:")
    print("    • Learns patterns across tasks")
    print("    • Provides recommendations based on historical success")
    print("    • Auto-discovers what works best")
    
    print("\n  🔍 META-LEARNING:")
    print("    • Finds cross-task patterns")
    print("    • Extracts universal insights")
    print("    • Builds generalized knowledge")
    
    print("\n  ✅ SELF-VERIFYING CoT:")
    print("    • Verifies each reasoning step")
    print("    • Retries failed steps")
    print("    • Ensures correctness")
    
    print("\n  🔄 BACKTRACKING CoT:")
    print("    • Explores alternative paths")
    print("    • Backtracks on low confidence")
    print("    • Finds optimal reasoning path")
    
    print("\n  📊 SEMANTIC SIMILARITY:")
    print("    • TF-IDF + MinHash + LSH")
    print("    • Fast similarity search")
    print("    • No external embeddings needed")
    
    print("\n  🎯 CAPABILITY DISCOVERY:")
    print("    • Agents discover what they're good at")
    print("    • Automatic specialization detection")
    print("    • Smart task-agent matching")
    
    print("\n  🤖 REINFORCEMENT LEARNING:")
    print("    • Q-learning for routing")
    print("    • Learns optimal decisions")
    print("    • Continuous improvement")
    
    print("\n  → Orchestra now learns, adapts, and improves autonomously!")


if __name__ == "__main__":
    asyncio.run(main())
