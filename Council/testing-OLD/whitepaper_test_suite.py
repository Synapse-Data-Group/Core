"""
Whitepaper Test Suite - Full Documentation Mode
Generates detailed conversation logs and vitals tracking for research documentation
Each test outputs:
  - {test_name}_conversation.txt - Complete debate transcript
  - {test_name}_vitals.json - Metrics tracked over time with timestamps
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentient_debate_system import SentientDebateSystem
from fluid_debate_system import FluidDebateSystem
from whitepaper_logger import WhitepaperDocumenter
import time


def test_1_basic_debate_documented():
    """Test 1: Basic Three-Agent Debate with Full Documentation"""
    
    print("\n" + "="*80)
    print("TEST 1: BASIC THREE-AGENT DEBATE (DOCUMENTED)")
    print("="*80 + "\n")
    
    problem = "Should companies implement a 4-day work week?"
    doc = WhitepaperDocumenter("test1_basic_debate")
    
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    alice = debate.create_agent("Alice_Optimist", personality={
        "creativity": 0.8, "boldness": 0.7, "aggressiveness": 0.4,
        "optimism": 0.9, "analytical_depth": 0.6
    })
    
    bob = debate.create_agent("Bob_Skeptic", personality={
        "creativity": 0.4, "boldness": 0.6, "aggressiveness": 0.8,
        "optimism": 0.2, "analytical_depth": 0.9
    })
    
    carol = debate.create_agent("Carol_Balanced", personality={
        "creativity": 0.6, "boldness": 0.5, "aggressiveness": 0.5,
        "optimism": 0.5, "analytical_depth": 0.7
    })
    
    doc.start_debate(problem, 3)
    doc.take_snapshot(list(debate.agents.values()), [], {"phase": "initialization"})
    
    print("🚀 Running debate with full documentation...\n")
    
    doc.log_phase_start("PROPOSAL", list(debate.agents.values()), [])
    debate._proposal_phase()
    
    for proposal in debate.proposals:
        doc.log_proposal(proposal.agent_name, proposal.content, {
            "proposal_id": proposal.proposal_id,
            "timestamp": proposal.timestamp
        })
    
    doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"phase": "post_proposal"})
    
    for round_num in range(2):
        print(f"\n--- Round {round_num + 1} ---")
        
        doc.log_phase_start("CHALLENGE", list(debate.agents.values()), debate.proposals)
        debate._challenge_phase()
        
        for proposal in debate.proposals:
            for challenge in proposal.challenges:
                doc.log_challenge(challenge.agent_name, proposal.agent_name, challenge.content)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"round": round_num + 1, "phase": "post_challenge"})
        
        doc.log_phase_start("REBUTTAL", list(debate.agents.values()), debate.proposals)
        debate._rebuttal_phase()
        
        for proposal in debate.proposals:
            for rebuttal in proposal.rebuttals:
                target = rebuttal.metadata.get("challenge_agent", "Unknown")
                doc.log_rebuttal(rebuttal.agent_name, target, rebuttal.content)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"round": round_num + 1, "phase": "post_rebuttal"})
    
    doc.log_phase_start("SCORING", list(debate.agents.values()), debate.proposals)
    debate._scoring_phase()
    
    scores = {p.agent_name: p.score for p in debate.proposals}
    doc.log_scoring(scores)
    
    doc.log_phase_start("RESOLUTION", list(debate.agents.values()), debate.proposals)
    debate._resolution_phase()
    
    doc.log_final_decision(debate.final_decision, list(debate.agents.values()), debate.proposals)
    
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    
    return debate.get_debate_summary()


def test_2_fluid_resourcing_documented():
    """Test 2: Fluid Resourcing with Full Documentation"""
    
    print("\n" + "="*80)
    print("TEST 2: FLUID RESOURCING (DOCUMENTED)")
    print("="*80 + "\n")
    
    problem = "How should we balance economic growth with environmental protection?"
    doc = WhitepaperDocumenter("test2_fluid_resourcing")
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    agent1 = debate.create_agent("Initial_Agent_1")
    agent2 = debate.create_agent("Initial_Agent_2")
    
    doc.start_debate(problem, 2)
    doc.take_snapshot(list(debate.agents.values()), [], {"phase": "initialization", "fluid_enabled": True})
    
    print("🚀 Running fluid debate with full documentation...\n")
    
    original_spawn = debate.moderator.spawn_agent
    def documented_spawn(role, debate_sys, reason):
        agent = original_spawn(role, debate_sys, reason)
        if agent:
            archetype = debate.moderator.agent_factory.get_agent_info(agent.agent_id)
            doc.log_agent_spawn(agent.name, reason, archetype["archetype"] if archetype else "unknown")
            doc.take_snapshot(list(debate_sys.agents.values()), debate_sys.proposals, {
                "event": "agent_spawned",
                "agent": agent.name
            })
        return agent
    
    debate.moderator.spawn_agent = documented_spawn
    
    original_terminate = debate.moderator.terminate_agent
    def documented_terminate(agent_id, debate_sys, reason):
        agent = debate_sys.agents.get(agent_id)
        agent_name = agent.name if agent else "Unknown"
        result = original_terminate(agent_id, debate_sys, reason)
        if result:
            doc.log_agent_termination(agent_name, reason)
            doc.take_snapshot(list(debate_sys.agents.values()), debate_sys.proposals, {
                "event": "agent_terminated",
                "agent": agent_name
            })
        return result
    
    debate.moderator.terminate_agent = documented_terminate
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    doc.log_final_decision(result["final_decision"], list(debate.agents.values()), debate.proposals)
    
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    
    return result


def test_3_coalition_formation_documented():
    """Test 3: Coalition Formation with Full Documentation"""
    
    print("\n" + "="*80)
    print("TEST 3: COALITION FORMATION (DOCUMENTED)")
    print("="*80 + "\n")
    
    from coalition_system import CoalitionManager
    
    problem = "What is the best strategy for space exploration?"
    doc = WhitepaperDocumenter("test3_coalition_formation")
    
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    coalition_mgr = CoalitionManager()
    
    agents = []
    for i in range(4):
        agent = debate.create_agent(f"Agent_{chr(65+i)}")
        agents.append(agent)
    
    doc.start_debate(problem, 4)
    doc.take_snapshot(list(debate.agents.values()), [], {"phase": "initialization"})
    
    print("🚀 Running coalition debate with full documentation...\n")
    
    result = debate.run_debate(max_rounds=2)
    
    coalition_mgr.update_coalitions(list(debate.agents.values()), debate.proposals, {})
    
    for coalition in coalition_mgr.coalitions.values():
        doc.vitals.log_event("coalition_formed", {
            "coalition_id": coalition.coalition_id,
            "members": list(coalition.members),
            "strength": coalition.strength
        })
    
    doc.log_final_decision(result["final_decision"], list(debate.agents.values()), debate.proposals)
    
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    
    return result


def test_4_knowledge_graph_documented():
    """Test 4: Knowledge Graph Building with Full Documentation"""
    
    print("\n" + "="*80)
    print("TEST 4: KNOWLEDGE GRAPH BUILDING (DOCUMENTED)")
    print("="*80 + "\n")
    
    from knowledge_graph import KnowledgeGraph
    
    doc = WhitepaperDocumenter("test4_knowledge_graph")
    knowledge_graph = KnowledgeGraph()
    
    problems = [
        "How to improve renewable energy adoption?",
        "What are the challenges in renewable energy?",
        "How to make renewable energy economically viable?"
    ]
    
    for idx, problem in enumerate(problems, 1):
        print(f"\n--- Debate {idx}/3: {problem} ---")
        
        debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
        
        for i in range(3):
            debate.create_agent(f"Expert_{chr(65+i)}")
        
        if idx == 1:
            doc.start_debate("Knowledge Graph Series", 3)
        
        result = debate.run_debate(max_rounds=1)
        
        for proposal in debate.proposals:
            knowledge_graph.process_debate_content(proposal.content, proposal.agent_id, "proposal")
        
        kg_stats = knowledge_graph.get_stats()
        doc.vitals.log_event(f"debate_{idx}_completed", {
            "problem": problem,
            "concepts": kg_stats["total_nodes"],
            "relationships": kg_stats["total_edges"]
        })
        
        doc.take_snapshot([], [], {
            "debate": idx,
            "knowledge_graph": kg_stats
        })
    
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    knowledge_graph.export_graph("testing/whitepaper_output/test4_knowledge_graph_data.json")
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    print(f"   🧠 Knowledge Graph: testing/whitepaper_output/test4_knowledge_graph_data.json")
    
    return knowledge_graph


def test_5_ultimate_integration_documented():
    """Test 5: Ultimate Integration with Full Documentation"""
    
    print("\n" + "="*80)
    print("TEST 5: ULTIMATE INTEGRATION (DOCUMENTED)")
    print("="*80 + "\n")
    
    from emotion_system import EmotionEngine
    from reputation_system import ReputationSystem
    from web_fetcher import WebResearchTool
    
    problem = "How should humanity approach artificial general intelligence (AGI) development?"
    doc = WhitepaperDocumenter("test5_ultimate_integration")
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    reputation_sys = ReputationSystem()
    
    agent1 = debate.create_agent("Dr_Safety", personality={
        "creativity": 0.6, "boldness": 0.4, "aggressiveness": 0.5, "analytical_depth": 0.9
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    
    agent2 = debate.create_agent("Prof_Innovation", personality={
        "creativity": 0.9, "boldness": 0.8, "aggressiveness": 0.6, "optimism": 0.8
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    
    web_tool = WebResearchTool()
    debate.create_tool_for_agent(agent1.agent_id, web_tool)
    
    doc.start_debate(problem, 2)
    doc.take_snapshot(list(debate.agents.values()), [], {
        "phase": "initialization",
        "features": ["fluid_resourcing", "emotions", "reputation", "web_tools"]
    })
    
    print("🚀 Running ultimate integration with full documentation...\n")
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    doc.vitals.log_event("emotions_final", {
        "Dr_Safety": emotion1.to_dict(),
        "Prof_Innovation": emotion2.to_dict()
    })
    
    doc.vitals.log_event("reputation_final", {
        "Dr_Safety": reputation_sys.get_reputation(agent1.agent_id).to_dict(),
        "Prof_Innovation": reputation_sys.get_reputation(agent2.agent_id).to_dict()
    })
    
    doc.log_final_decision(result["final_decision"], list(debate.agents.values()), debate.proposals)
    
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    
    return result


def run_whitepaper_test_suite():
    """Run all tests with full whitepaper documentation"""
    
    os.makedirs("testing/whitepaper_output", exist_ok=True)
    
    print("\n" + "📚"*40)
    print("\n  WHITEPAPER DOCUMENTATION TEST SUITE")
    print("  Full Transparency: Conversations + Vitals Over Time")
    print("\n" + "📚"*40)
    
    tests = [
        ("Basic Three-Agent Debate", test_1_basic_debate_documented),
        ("Fluid Resourcing", test_2_fluid_resourcing_documented),
        ("Coalition Formation", test_3_coalition_formation_documented),
        ("Knowledge Graph Building", test_4_knowledge_graph_documented),
        ("Ultimate Integration", test_5_ultimate_integration_documented)
    ]
    
    results = []
    
    for idx, (name, test_func) in enumerate(tests, 1):
        try:
            print(f"\n\n{'🚀'*40}")
            print(f"\n  RUNNING TEST {idx}/5: {name.upper()}")
            print(f"\n{'🚀'*40}")
            
            time.sleep(1)
            
            result = test_func()
            results.append({"test": name, "status": "✅ PASSED"})
            
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
            import traceback
            traceback.print_exc()
    
    print("\n\n" + "="*80)
    print("  WHITEPAPER TEST SUITE COMPLETE")
    print("="*80)
    
    print("\n📊 Test Summary:")
    passed = sum(1 for r in results if "PASSED" in r["status"])
    
    for idx, result in enumerate(results, 1):
        print(f"  {idx}. {result['test']}: {result['status']}")
    
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    print(f"📈 Success Rate: {passed/len(tests)*100:.1f}%")
    
    print("\n📁 All documentation saved to: testing/whitepaper_output/")
    print("\nFor each test you have:")
    print("  📄 {test_name}_conversation.txt - Full debate transcript")
    print("  📊 {test_name}_vitals.json - Metrics over time with timestamps")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n" + "⚡"*40)
    print("\n  STARTING WHITEPAPER DOCUMENTATION SUITE")
    print("  Generating detailed logs for research documentation")
    print("\n" + "⚡"*40)
    
    input("\nPress ENTER to begin...")
    
    run_whitepaper_test_suite()
    
    print("\n\n🎉 All tests complete!")
    print("📚 Check testing/whitepaper_output/ for your whitepaper documentation")
