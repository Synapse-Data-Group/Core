import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from datetime import datetime
from typing import List, Dict, Any
from sentient_debate_system import SentientDebateSystem, Tool


class TestMetrics:
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    def record_debate(self, debate_summary: Dict[str, Any], test_name: str):
        metrics = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "duration": debate_summary["duration_seconds"],
            "total_agents": debate_summary["total_agents"],
            "total_proposals": debate_summary["total_proposals"],
            "total_messages": debate_summary["total_messages"],
            "rounds": debate_summary["rounds_completed"],
            "winner": debate_summary["final_decision"]["decision"] if debate_summary["final_decision"] else "None",
            "confidence": debate_summary["final_decision"]["confidence"] if debate_summary["final_decision"] else 0,
            "agent_performance": [],
            "moderator_stats": debate_summary["moderator_stats"]
        }
        
        for agent_stats in debate_summary["agent_stats"]:
            metrics["agent_performance"].append({
                "name": agent_stats["name"],
                "score": agent_stats["current_score"],
                "win_rate": agent_stats["win_rate"],
                "debates": agent_stats["debates_participated"],
                "proposals": agent_stats["proposals_made"],
                "challenges": agent_stats["challenges_made"],
                "rebuttals": agent_stats["rebuttals_made"],
                "memory_size": agent_stats["memory_size"],
                "exploration_rate": agent_stats["exploration_rate"]
            })
        
        self.test_results.append(metrics)
        
    def save_results(self, filepath: str):
        report = {
            "test_suite_start": datetime.fromtimestamp(self.start_time).isoformat(),
            "test_suite_duration": time.time() - self.start_time,
            "total_tests": len(self.test_results),
            "results": self.test_results
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nTest results saved to: {filepath}")
    
    def print_summary(self):
        print("\n" + "="*80)
        print("TEST SUITE SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {len(self.test_results)}")
        print(f"Total Duration: {time.time() - self.start_time:.2f}s")
        
        total_debates = sum(r["total_agents"] for r in self.test_results)
        avg_confidence = sum(r["confidence"] for r in self.test_results) / len(self.test_results) if self.test_results else 0
        
        print(f"Total Agent Instances: {total_debates}")
        print(f"Average Decision Confidence: {avg_confidence:.1%}")
        
        print("\n" + "="*80)
        print("PER-TEST RESULTS")
        print("="*80)
        
        for result in self.test_results:
            print(f"\n{result['test_name']}:")
            print(f"  Duration: {result['duration']:.2f}s")
            print(f"  Winner: {result['winner']}")
            print(f"  Confidence: {result['confidence']:.1%}")
            print(f"  Messages: {result['total_messages']}")
            print(f"  Top Agent: {max(result['agent_performance'], key=lambda x: x['score'])['name']} "
                  f"({max(result['agent_performance'], key=lambda x: x['score'])['score']:.1f} pts)")


def test_basic_debate():
    print("\n" + "="*80)
    print("TEST 1: Basic Three-Agent Debate")
    print("="*80)
    
    problem = "How should we approach climate change mitigation?"
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    debate.create_agent("Agent_A")
    debate.create_agent("Agent_B")
    debate.create_agent("Agent_C")
    
    result = debate.run_debate(max_rounds=2)
    debate.export_debate("testing/results/test1_basic_debate.json")
    
    return result, "Basic Three-Agent Debate"


def test_learning_progression():
    print("\n" + "="*80)
    print("TEST 2: Learning Progression Over Multiple Debates")
    print("="*80)
    
    problems = [
        "How to improve education systems?",
        "What's the best approach to healthcare reform?",
        "How should we regulate artificial intelligence?"
    ]
    
    agent_ids = []
    
    for idx, problem in enumerate(problems, 1):
        print(f"\n--- Debate {idx}/{len(problems)} ---")
        debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
        
        if idx == 1:
            agent_a = debate.create_agent("Learner_A")
            agent_b = debate.create_agent("Learner_B")
            agent_c = debate.create_agent("Learner_C")
            agent_ids = [agent_a.agent_id, agent_b.agent_id, agent_c.agent_id]
        else:
            agent_a = debate.create_agent("Learner_A", memory_path=f"testing/memories/agent_{agent_ids[0]}_memory.pkl")
            agent_b = debate.create_agent("Learner_B", memory_path=f"testing/memories/agent_{agent_ids[1]}_memory.pkl")
            agent_c = debate.create_agent("Learner_C", memory_path=f"testing/memories/agent_{agent_ids[2]}_memory.pkl")
            agent_ids = [agent_a.agent_id, agent_b.agent_id, agent_c.agent_id]
        
        result = debate.run_debate(max_rounds=1)
        debate.save_agent_memories("testing/memories")
        debate.export_debate(f"testing/results/test2_learning_debate_{idx}.json")
    
    return result, "Learning Progression"


def test_agent_lifecycle():
    print("\n" + "="*80)
    print("TEST 3: Agent Lifecycle Management")
    print("="*80)
    
    problem = "How to optimize resource allocation?"
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    agent1 = debate.create_agent("Agent_1")
    agent2 = debate.create_agent("Agent_2")
    agent3 = debate.create_agent("Agent_3")
    
    print("\n--- Initial debate with 3 agents ---")
    result = debate.run_debate(max_rounds=1)
    
    print("\n--- Adding new agent mid-process ---")
    agent4 = debate.create_agent("Agent_4")
    
    print("\n--- Removing underperforming agent ---")
    lowest_score_agent = min(debate.agents.values(), key=lambda a: a.score)
    debate.kill_agent(lowest_score_agent.agent_id)
    
    print(f"\n--- Continuing with {len(debate.agents)} agents ---")
    
    debate.export_debate("testing/results/test3_lifecycle.json")
    
    return result, "Agent Lifecycle Management"


def test_personality_evolution():
    print("\n" + "="*80)
    print("TEST 4: Personality Evolution")
    print("="*80)
    
    problem = "What's the best strategy for economic growth?"
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    agent_a = debate.create_agent("Evolver_A")
    agent_b = debate.create_agent("Evolver_B")
    agent_c = debate.create_agent("Evolver_C")
    
    print("\n--- Initial personalities ---")
    for agent in [agent_a, agent_b, agent_c]:
        print(f"{agent.name}: creativity={agent.personality['creativity']:.2f}, "
              f"boldness={agent.personality['boldness']:.2f}")
    
    result = debate.run_debate(max_rounds=2)
    
    print("\n--- Evolving population ---")
    debate.evolve_agents()
    
    print("\n--- Evolved personalities ---")
    for agent in [agent_a, agent_b, agent_c]:
        print(f"{agent.name}: creativity={agent.personality['creativity']:.2f}, "
              f"boldness={agent.personality['boldness']:.2f}")
    
    debate.export_debate("testing/results/test4_evolution.json")
    
    return result, "Personality Evolution"


def test_tool_usage():
    print("\n" + "="*80)
    print("TEST 5: Tool Creation and Usage")
    print("="*80)
    
    class ResearchTool(Tool):
        def execute(self, topic: str) -> str:
            return f"Research data on {topic}: Positive correlation found"
    
    class CalculatorTool(Tool):
        def execute(self, expr: str) -> str:
            return f"Calculation result: {expr} = computed"
    
    problem = "How to balance innovation and stability?"
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    agent_a = debate.create_agent("Tool_User_A")
    agent_b = debate.create_agent("Tool_User_B")
    agent_c = debate.create_agent("Tool_User_C")
    
    research_tool = ResearchTool("research_001", "Research Tool")
    calc_tool = CalculatorTool("calc_001", "Calculator")
    
    debate.create_tool_for_agent(agent_a.agent_id, research_tool)
    debate.create_tool_for_agent(agent_b.agent_id, calc_tool)
    
    result = debate.run_debate(max_rounds=2)
    
    print("\n--- Removing tool from agent ---")
    debate.remove_tool_from_agent(agent_a.agent_id, research_tool.tool_id)
    
    debate.export_debate("testing/results/test5_tools.json")
    
    return result, "Tool Usage"


def test_high_intensity_debate():
    print("\n" + "="*80)
    print("TEST 6: High-Intensity Debate (5 agents, 4 rounds)")
    print("="*80)
    
    problem = "How should humanity approach space exploration and colonization?"
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    for i in range(5):
        debate.create_agent(f"Agent_{chr(65+i)}")
    
    result = debate.run_debate(max_rounds=4)
    debate.export_debate("testing/results/test6_high_intensity.json")
    
    return result, "High-Intensity Debate"


def test_moderator_strategies():
    print("\n" + "="*80)
    print("TEST 7: Different Moderator Strategies")
    print("="*80)
    
    problem = "What's the optimal work-life balance policy?"
    strategies = ["adaptive", "conservative", "aggressive"]
    
    results = []
    
    for strategy in strategies:
        print(f"\n--- Testing {strategy} strategy ---")
        debate = SentientDebateSystem(problem, moderator_strategy=strategy)
        
        debate.create_agent("Agent_X")
        debate.create_agent("Agent_Y")
        debate.create_agent("Agent_Z")
        
        result = debate.run_debate(max_rounds=2)
        debate.export_debate(f"testing/results/test7_{strategy}_strategy.json")
        
        results.append(result)
    
    return results[-1], "Moderator Strategies Comparison"


def run_all_tests():
    os.makedirs("testing/results", exist_ok=True)
    os.makedirs("testing/memories", exist_ok=True)
    
    metrics = TestMetrics()
    
    tests = [
        test_basic_debate,
        test_learning_progression,
        test_agent_lifecycle,
        test_personality_evolution,
        test_tool_usage,
        test_high_intensity_debate,
        test_moderator_strategies
    ]
    
    for test_func in tests:
        try:
            result, test_name = test_func()
            metrics.record_debate(result, test_name)
            print(f"\n✓ {test_name} completed successfully")
        except Exception as e:
            print(f"\n✗ {test_func.__name__} failed: {str(e)}")
    
    metrics.print_summary()
    metrics.save_results("testing/results/test_suite_summary.json")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
    print("\nResults saved in: testing/results/")
    print("Agent memories saved in: testing/memories/")


if __name__ == "__main__":
    run_all_tests()
