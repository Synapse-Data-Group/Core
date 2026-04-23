"""
Live Test Suite - Watch Debates Unfold in Real-Time
Shows all debate steps, agent interactions, and decision-making live in console
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentient_debate_system import SentientDebateSystem
from fluid_debate_system import FluidDebateSystem
from coalition_system import CoalitionManager
from knowledge_graph import KnowledgeGraph
from reputation_system import ReputationSystem
from emotion_system import EmotionEngine
from web_fetcher import WebResearchTool
import time


def print_header(title):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_section(title):
    """Print formatted section header"""
    print("\n" + "-"*80)
    print(f"  {title}")
    print("-"*80)


def test_1_basic_debate():
    """
    TEST 1: Basic Three-Agent Debate
    Watch agents propose, challenge, rebut, and reach a decision
    """
    print_header("TEST 1: BASIC THREE-AGENT DEBATE")
    
    problem = "Should companies implement a 4-day work week?"
    
    print(f"📋 Problem: {problem}\n")
    print("🎬 Initializing debate system...")
    
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    print("\n👥 Creating agents with distinct personalities...\n")
    
    alice = debate.create_agent("Alice_Optimist", personality={
        "creativity": 0.8,
        "boldness": 0.7,
        "aggressiveness": 0.4,
        "optimism": 0.9,
        "analytical_depth": 0.6
    })
    print(f"  ✓ Alice (Optimistic, Creative)")
    
    bob = debate.create_agent("Bob_Skeptic", personality={
        "creativity": 0.4,
        "boldness": 0.6,
        "aggressiveness": 0.8,
        "optimism": 0.2,
        "analytical_depth": 0.9
    })
    print(f"  ✓ Bob (Skeptical, Analytical)")
    
    carol = debate.create_agent("Carol_Balanced", personality={
        "creativity": 0.6,
        "boldness": 0.5,
        "aggressiveness": 0.5,
        "optimism": 0.5,
        "analytical_depth": 0.7
    })
    print(f"  ✓ Carol (Balanced, Pragmatic)")
    
    print("\n🚀 Starting debate with 2 rounds...\n")
    print("="*80)
    
    result = debate.run_debate(max_rounds=2)
    
    print("\n" + "="*80)
    print_section("DEBATE RESULTS")
    
    print(f"\n🏆 Winner: {result['final_decision']['decision']}")
    print(f"📊 Confidence: {result['final_decision']['confidence']:.1%}")
    print(f"⏱️  Duration: {result['duration_seconds']:.2f} seconds")
    print(f"💬 Total Messages: {result['total_messages']}")
    
    print("\n📈 Agent Performance:")
    for stats in result['agent_stats']:
        print(f"\n  {stats['name']}:")
        print(f"    Score: {stats['current_score']:.1f}")
        print(f"    Proposals: {stats['proposals_made']}")
        print(f"    Challenges: {stats['challenges_made']}")
        print(f"    Rebuttals: {stats['rebuttals_made']}")
        print(f"    Exploration Rate: {stats['exploration_rate']:.3f}")
    
    debate.export_debate("testing/results/live_test_1_basic.json")
    print("\n💾 Results saved to: testing/results/live_test_1_basic.json")
    
    return result


def test_2_fluid_resourcing():
    """
    TEST 2: Fluid Resourcing in Action
    Watch moderator spawn and terminate agents dynamically
    """
    print_header("TEST 2: FLUID RESOURCING - DYNAMIC AGENT SPAWNING")
    
    problem = "How should we balance economic growth with environmental protection?"
    
    print(f"📋 Problem: {problem}\n")
    print("🎬 Initializing FLUID debate system...")
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    print("\n👥 Starting with only 2 agents...")
    print("   (Moderator will spawn more as needed)\n")
    
    agent1 = debate.create_agent("Initial_Agent_1")
    agent2 = debate.create_agent("Initial_Agent_2")
    
    print(f"  ✓ Created 2 initial agents")
    print(f"  ⚡ Fluid resourcing: ENABLED")
    
    print("\n🚀 Starting debate - watch for agent spawning...\n")
    print("="*80)
    
    result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)
    
    print("\n" + "="*80)
    print_section("FLUID RESOURCING RESULTS")
    
    print(f"\n📊 Started with: 2 agents")
    print(f"📊 Ended with: {result['total_agents']} agents")
    print(f"➕ Spawned: {result['fluid_resourcing_stats']['total_spawned']} agents")
    print(f"➖ Terminated: {result['fluid_resourcing_stats']['total_terminated']} agents")
    
    if result['fluid_resourcing_stats']['spawn_reasons']:
        print("\n🎯 Spawn Reasons:")
        for reason, count in result['fluid_resourcing_stats']['spawn_reasons'].items():
            print(f"  • {reason}: {count} times")
    
    print("\n🔄 Fluid Events Timeline:")
    for event in result['fluid_events']:
        print(f"  [{event['phase']}] {event['type'].upper()}: {event['agent_name']}")
        print(f"      Reason: {event['reason']}")
    
    print(f"\n🏆 Winner: {result['final_decision']['decision']}")
    print(f"📊 Confidence: {result['final_decision']['confidence']:.1%}")
    
    debate.export_debate("testing/results/live_test_2_fluid.json")
    print("\n💾 Results saved to: testing/results/live_test_2_fluid.json")
    
    return result


def test_3_coalition_formation():
    """
    TEST 3: Coalition Formation
    Watch agents form alliances based on proposal alignment
    """
    print_header("TEST 3: COALITION FORMATION - AGENTS FORMING ALLIANCES")
    
    problem = "What is the best strategy for space exploration?"
    
    print(f"📋 Problem: {problem}\n")
    print("🎬 Initializing debate with coalition tracking...")
    
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    coalition_mgr = CoalitionManager()
    
    print("\n👥 Creating 4 agents for coalition dynamics...\n")
    
    agents = []
    for i in range(4):
        agent = debate.create_agent(f"Agent_{chr(65+i)}")
        agents.append(agent)
        print(f"  ✓ Agent_{chr(65+i)} created")
    
    print("\n🚀 Running debate - watch for coalition formation...\n")
    print("="*80)
    
    result = debate.run_debate(max_rounds=2)
    
    print("\n" + "="*80)
    print_section("ANALYZING COALITIONS")
    
    coalition_mgr.update_coalitions(list(debate.agents.values()), debate.proposals, {})
    
    stats = coalition_mgr.get_stats()
    
    print(f"\n🤝 Total Coalitions Formed: {stats['total_coalitions']}")
    print(f"👥 Agents in Coalitions: {stats['agents_in_coalitions']}")
    
    if stats['active_coalitions']:
        print("\n📋 Active Coalitions:")
        for coalition in stats['active_coalitions']:
            print(f"\n  {coalition['name']}:")
            print(f"    Members: {coalition['member_count']}")
            print(f"    Strength: {coalition['strength']:.1f}")
            print(f"    Leader: {coalition['leader_id'][:8]}...")
    
    print(f"\n🏆 Winner: {result['final_decision']['decision']}")
    
    debate.export_debate("testing/results/live_test_3_coalitions.json")
    print("\n💾 Results saved to: testing/results/live_test_3_coalitions.json")
    
    return result


def test_4_knowledge_graph():
    """
    TEST 4: Knowledge Graph Construction
    Watch knowledge accumulate across multiple debates
    """
    print_header("TEST 4: KNOWLEDGE GRAPH - BUILDING PERSISTENT INTELLIGENCE")
    
    print("🎬 Initializing knowledge graph system...\n")
    
    knowledge_graph = KnowledgeGraph()
    
    problems = [
        "How to improve renewable energy adoption?",
        "What are the challenges in renewable energy?",
        "How to make renewable energy economically viable?"
    ]
    
    print("📚 Running 3 related debates to build knowledge...\n")
    
    for idx, problem in enumerate(problems, 1):
        print(f"\n{'='*80}")
        print(f"  DEBATE {idx}/3: {problem}")
        print(f"{'='*80}\n")
        
        debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
        
        for i in range(3):
            debate.create_agent(f"Expert_{chr(65+i)}")
        
        result = debate.run_debate(max_rounds=1)
        
        print(f"\n📊 Extracting concepts from debate {idx}...")
        
        for proposal in debate.proposals:
            knowledge_graph.process_debate_content(
                proposal.content,
                proposal.agent_id,
                "proposal"
            )
        
        stats = knowledge_graph.get_stats()
        print(f"  ✓ Total concepts: {stats['total_nodes']}")
        print(f"  ✓ Total relationships: {stats['total_edges']}")
    
    print("\n" + "="*80)
    print_section("KNOWLEDGE GRAPH ANALYSIS")
    
    stats = knowledge_graph.get_stats()
    
    print(f"\n🧠 Knowledge Graph Statistics:")
    print(f"  Total Concepts: {stats['total_nodes']}")
    print(f"  Total Relationships: {stats['total_edges']}")
    print(f"  Average Connections: {stats['avg_node_degree']:.2f}")
    
    print(f"\n⭐ Most Central Concepts:")
    for concept, degree in stats['most_central']:
        print(f"  • {concept}: {degree} connections")
    
    print("\n🔍 Querying: 'renewable'")
    related = knowledge_graph.query_related_concepts("renewable", max_results=5)
    if related:
        print("  Related concepts:")
        for concept, weight in related:
            print(f"    • {concept} (strength: {weight:.2f})")
    
    knowledge_graph.export_graph("testing/results/live_test_4_knowledge_graph.json")
    print("\n💾 Knowledge graph saved to: testing/results/live_test_4_knowledge_graph.json")
    
    return knowledge_graph


def test_5_ultimate_integration():
    """
    TEST 5: Ultimate Integration
    All features working together - emotions, reputation, web tools, coalitions
    """
    print_header("TEST 5: ULTIMATE INTEGRATION - ALL FEATURES COMBINED")
    
    problem = "How should humanity approach artificial general intelligence (AGI) development?"
    
    print(f"📋 Problem: {problem}\n")
    print("🎬 Initializing ALL systems...")
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    coalition_mgr = CoalitionManager()
    knowledge_graph = KnowledgeGraph()
    reputation_sys = ReputationSystem()
    
    print("  ✓ Fluid debate system")
    print("  ✓ Coalition manager")
    print("  ✓ Knowledge graph")
    print("  ✓ Reputation system")
    
    print("\n👥 Creating agents with emotions and tools...\n")
    
    agent1 = debate.create_agent("Dr_Safety", personality={
        "creativity": 0.6,
        "boldness": 0.4,
        "aggressiveness": 0.5,
        "analytical_depth": 0.9
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    print(f"  ✓ Dr_Safety (Analytical, Cautious) + Emotion Engine")
    
    agent2 = debate.create_agent("Prof_Innovation", personality={
        "creativity": 0.9,
        "boldness": 0.8,
        "aggressiveness": 0.6,
        "optimism": 0.8
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    print(f"  ✓ Prof_Innovation (Creative, Bold) + Emotion Engine")
    
    web_tool = WebResearchTool()
    debate.create_tool_for_agent(agent1.agent_id, web_tool)
    print(f"  ✓ Web Research Tool added to Dr_Safety")
    
    print("\n🚀 Starting ultimate debate with ALL features...\n")
    print("="*80)
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    print("\n" + "="*80)
    print_section("ULTIMATE INTEGRATION RESULTS")
    
    print("\n🎭 Emotional States:")
    print(f"  Dr_Safety: {emotion1.current_state.value} (intensity: {emotion1.emotion_intensity:.2f})")
    print(f"  Prof_Innovation: {emotion2.current_state.value} (intensity: {emotion2.emotion_intensity:.2f})")
    
    print("\n🏆 Reputation Scores:")
    for agent in [agent1, agent2]:
        rep = reputation_sys.get_reputation(agent.agent_id)
        print(f"  {agent.name}: {rep.overall_score:.1f}/100")
    
    print("\n🤝 Coalition Status:")
    coalition_mgr.update_coalitions(list(debate.agents.values()), debate.proposals, {})
    coalition_stats = coalition_mgr.get_stats()
    print(f"  Coalitions Formed: {coalition_stats['total_coalitions']}")
    print(f"  Agents in Coalitions: {coalition_stats['agents_in_coalitions']}")
    
    print("\n🧠 Knowledge Extracted:")
    for proposal in debate.proposals:
        knowledge_graph.process_debate_content(proposal.content, proposal.agent_id, "proposal")
    kg_stats = knowledge_graph.get_stats()
    print(f"  Concepts: {kg_stats['total_nodes']}")
    print(f"  Relationships: {kg_stats['total_edges']}")
    
    print("\n⚡ Fluid Resourcing:")
    print(f"  Spawned: {result['fluid_resourcing_stats']['total_spawned']} agents")
    print(f"  Final Agent Count: {result['total_agents']}")
    
    print(f"\n🏆 Final Decision: {result['final_decision']['decision']}")
    print(f"📊 Confidence: {result['final_decision']['confidence']:.1%}")
    print(f"⏱️  Duration: {result['duration_seconds']:.2f} seconds")
    
    debate.export_debate("testing/results/live_test_5_ultimate.json")
    knowledge_graph.export_graph("testing/results/live_test_5_knowledge.json")
    
    print("\n💾 Results saved to: testing/results/")
    
    return result


def run_all_live_tests():
    """Run all 5 live tests in sequence"""
    
    os.makedirs("testing/results", exist_ok=True)
    
    print("\n" + "🎬"*40)
    print("\n  COUNCIL FRAMEWORK - LIVE TEST SUITE")
    print("  Watch Real-Time Multi-Agent Debates Unfold")
    print("\n" + "🎬"*40)
    
    tests = [
        ("Basic Three-Agent Debate", test_1_basic_debate),
        ("Fluid Resourcing", test_2_fluid_resourcing),
        ("Coalition Formation", test_3_coalition_formation),
        ("Knowledge Graph Building", test_4_knowledge_graph),
        ("Ultimate Integration", test_5_ultimate_integration)
    ]
    
    results = []
    
    for idx, (name, test_func) in enumerate(tests, 1):
        try:
            print(f"\n\n{'🚀'*40}")
            print(f"\n  RUNNING TEST {idx}/5: {name.upper()}")
            print(f"\n{'🚀'*40}")
            
            time.sleep(1)
            
            result = test_func()
            results.append({"test": name, "status": "✅ PASSED", "result": result})
            
            print(f"\n\n{'✅'*40}")
            print(f"\n  TEST {idx}/5 COMPLETED: {name}")
            print(f"\n{'✅'*40}")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"\n\n{'❌'*40}")
            print(f"\n  TEST {idx}/5 FAILED: {name}")
            print(f"  Error: {str(e)}")
            print(f"\n{'❌'*40}")
            results.append({"test": name, "status": "❌ FAILED", "error": str(e)})
    
    print("\n\n" + "="*80)
    print("  LIVE TEST SUITE COMPLETE")
    print("="*80)
    
    print("\n📊 Test Summary:")
    passed = sum(1 for r in results if "PASSED" in r["status"])
    failed = len(results) - passed
    
    for idx, result in enumerate(results, 1):
        print(f"  {idx}. {result['test']}: {result['status']}")
    
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print(f"📈 Success Rate: {passed/len(tests)*100:.1f}%")
    
    print("\n💾 All results saved to: testing/results/")
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n" + "⚡"*40)
    print("\n  STARTING LIVE TEST SUITE")
    print("  All debate steps will be shown in real-time")
    print("\n" + "⚡"*40)
    
    input("\nPress ENTER to begin...")
    
    run_all_live_tests()
    
    print("\n\n🎉 All tests complete! Check testing/results/ for detailed logs.")
