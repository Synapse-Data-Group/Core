"""
Test 4: REAL LLM-Powered Debate with Real Web Search
Agents use OpenAI GPT for actual reasoning
Web search uses real internet queries
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_powered_agent import LLMPoweredAgent
from real_web_search import RealWebResearchTool
from coalition_system import CoalitionManager
from knowledge_graph import KnowledgeGraph
from reputation_system import ReputationSystem
from emotion_system import EmotionEngine
from meta_debate import ArgumentQualityMetrics
from whitepaper_logger import WhitepaperDocumenter
import time
from datetime import datetime


# OpenAI API Key
OPENAI_API_KEY = "sk-your-api-key-here"


def run_test4():
    # Create unique folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_folder = f"testing/debates/test4_{timestamp}"
    os.makedirs(test_folder, exist_ok=True)
    
    print("\n" + "🤖"*40)
    print("\n  TEST 4: REAL LLM-POWERED DEBATE")
    print("  Using OpenAI GPT for Actual Reasoning")
    print("  Using Real Web Search")
    print(f"  Output: {test_folder}")
    print("\n" + "🤖"*40 + "\n")
    
    problem = "Should governments mandate transparency requirements for AI systems used in critical decision-making (healthcare, criminal justice, finance)?"
    
    print("🔧 Initializing systems...\n")
    time.sleep(1)
    
    doc = WhitepaperDocumenter("test4_llm_powered")
    knowledge_graph = KnowledgeGraph()
    reputation_sys = ReputationSystem()
    quality_metrics = ArgumentQualityMetrics()
    coalition_mgr = CoalitionManager()
    
    print("  ✓ Knowledge Graph")
    print("  ✓ Reputation System")
    print("  ✓ Quality Metrics")
    print("  ✓ Coalition Manager")
    time.sleep(1)
    
    print("\n🤖 Creating LLM-powered agents...\n")
    
    # Agent 1: Privacy Advocate
    agent1 = LLMPoweredAgent("Privacy_Advocate", OPENAI_API_KEY, personality={
        "creativity": 0.7,
        "boldness": 0.8,
        "aggressiveness": 0.6,
        "analytical_depth": 0.85,
        "evidence_reliance": 0.8
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    web_tool1 = RealWebResearchTool()
    agent1.tools.append(web_tool1)
    print(f"  ✓ {agent1.name} (GPT-powered) + Real Web Search")
    time.sleep(0.5)
    
    # Agent 2: Transparency Proponent
    agent2 = LLMPoweredAgent("Transparency_Proponent", OPENAI_API_KEY, personality={
        "creativity": 0.6,
        "boldness": 0.7,
        "aggressiveness": 0.5,
        "analytical_depth": 0.9,
        "evidence_reliance": 0.95
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    web_tool2 = RealWebResearchTool()
    agent2.tools.append(web_tool2)
    print(f"  ✓ {agent2.name} (GPT-powered) + Real Web Search")
    time.sleep(0.5)
    
    # Agent 3: Industry Representative
    agent3 = LLMPoweredAgent("Industry_Rep", OPENAI_API_KEY, personality={
        "creativity": 0.75,
        "boldness": 0.6,
        "aggressiveness": 0.7,
        "analytical_depth": 0.75,
        "optimism": 0.8
    })
    emotion3 = EmotionEngine(agent3.agent_id)
    print(f"  ✓ {agent3.name} (GPT-powered)")
    time.sleep(0.5)
    
    agents = [agent1, agent2, agent3]
    
    doc.start_debate(problem, 3)
    doc.take_snapshot(agents, [], {"phase": "initialization", "llm_powered": True})
    
    print("\n" + "="*80)
    print("DEBATE STARTING - REAL AI REASONING")
    print("="*80 + "\n")
    time.sleep(1)
    
    # WEB RESEARCH PHASE
    print("\n" + "="*80)
    print("PHASE: WEB RESEARCH (REAL INTERNET SEARCH)")
    print("="*80 + "\n")
    
    web_research_results = {}
    
    print(f"[{agent1.name}] Searching web: 'AI transparency regulations privacy concerns'\n")
    time.sleep(1)
    research1 = web_tool1.execute("AI transparency regulations privacy concerns", action="search")
    print(research1)
    web_research_results[agent1.agent_id] = research1
    doc.vitals.log_event("real_web_search", {
        "agent": agent1.name,
        "query": "AI transparency regulations privacy concerns",
        "results": research1[:300]
    })
    time.sleep(2)
    
    print(f"\n[{agent2.name}] Searching web: 'AI accountability transparency requirements'\n")
    time.sleep(1)
    research2 = web_tool2.execute("AI accountability transparency requirements", action="search")
    print(research2)
    web_research_results[agent2.agent_id] = research2
    doc.vitals.log_event("real_web_search", {
        "agent": agent2.name,
        "query": "AI accountability transparency requirements",
        "results": research2[:300]
    })
    time.sleep(2)
    
    # PROPOSAL PHASE
    print("\n" + "="*80)
    print("PHASE: PROPOSALS (GPT GENERATING REAL ARGUMENTS)")
    print("="*80 + "\n")
    
    doc.log_phase_start("PROPOSAL", agents, [])
    
    proposals = []
    
    for agent in agents:
        print(f"[{agent.name}] Thinking and formulating proposal using GPT...\n")
        time.sleep(2)
        
        context = {}
        if agent.agent_id in web_research_results:
            context['web_research'] = web_research_results[agent.agent_id]
        
        proposal_content = agent.generate_proposal(problem, context)
        
        print(f"[{agent.name}] PROPOSES:\n")
        print(f"{proposal_content}\n")
        print("="*80 + "\n")
        time.sleep(2)
        
        proposals.append({
            "agent": agent,
            "content": proposal_content,
            "challenges": [],
            "rebuttals": []
        })
        
        doc.log_proposal(agent.name, proposal_content, {
            "llm_generated": True,
            "has_web_research": agent.agent_id in web_research_results
        })
        
        # Extract knowledge
        knowledge_graph.process_debate_content(proposal_content, agent.agent_id, "proposal")
        
        # Quality analysis
        print(f"📊 Analyzing argument quality...\n")
        time.sleep(1)
        quality = quality_metrics.evaluate_argument(proposal_content, {})
        print(f"   Quality Score: {quality['overall_quality']:.2f}")
        print(f"   Strengths: {', '.join(quality['strengths']) if quality['strengths'] else 'None'}")
        print(f"   Weaknesses: {', '.join(quality['weaknesses']) if quality['weaknesses'] else 'None'}\n")
        time.sleep(1)
    
    doc.take_snapshot(agents, [], {"phase": "post_proposal", "proposals": len(proposals)})
    
    # Coalition check
    print("🤝 Checking for coalition formation...\n")
    time.sleep(1)
    # Note: Coalition system expects framework agents, so we skip for now
    print("  (Coalition detection requires framework integration)\n")
    
    # CHALLENGE PHASE
    print("\n" + "="*80)
    print("ROUND 1: CHALLENGES (GPT GENERATING CRITIQUES)")
    print("="*80 + "\n")
    
    doc.log_phase_start("CHALLENGE", agents, [])
    
    for proposal in proposals:
        for agent in agents:
            if agent.agent_id != proposal["agent"].agent_id:
                print(f"[{agent.name}] Analyzing {proposal['agent'].name}'s proposal using GPT...\n")
                time.sleep(2)
                
                challenge_content = agent.generate_challenge(
                    proposal["content"],
                    proposal["agent"].name,
                    {}
                )
                
                print(f"[{agent.name}] CHALLENGES [{proposal['agent'].name}]:\n")
                print(f"{challenge_content}\n")
                print("="*80 + "\n")
                time.sleep(2)
                
                proposal["challenges"].append({
                    "agent": agent,
                    "content": challenge_content
                })
                
                doc.log_challenge(agent.name, proposal["agent"].name, challenge_content)
    
    doc.take_snapshot(agents, [], {"phase": "post_challenge", "round": 1})
    
    # REBUTTAL PHASE
    print("\n" + "="*80)
    print("ROUND 1: REBUTTALS (GPT DEFENDING PROPOSALS)")
    print("="*80 + "\n")
    
    doc.log_phase_start("REBUTTAL", agents, [])
    
    for proposal in proposals:
        if proposal["challenges"]:
            # Rebut first challenge
            challenge = proposal["challenges"][0]
            
            print(f"[{proposal['agent'].name}] Formulating rebuttal using GPT...\n")
            time.sleep(2)
            
            rebuttal_content = proposal["agent"].generate_rebuttal(
                challenge["content"],
                challenge["agent"].name,
                proposal["content"],
                {}
            )
            
            print(f"[{proposal['agent'].name}] REBUTS [{challenge['agent'].name}]:\n")
            print(f"{rebuttal_content}\n")
            print("="*80 + "\n")
            time.sleep(2)
            
            proposal["rebuttals"].append({
                "agent": proposal["agent"],
                "content": rebuttal_content,
                "target": challenge["agent"].name
            })
            
            doc.log_rebuttal(proposal["agent"].name, challenge["agent"].name, rebuttal_content)
    
    doc.take_snapshot(agents, [], {"phase": "post_rebuttal", "round": 1})
    
    # FINAL ANALYSIS
    print("\n" + "="*80)
    print("FINAL ANALYSIS")
    print("="*80 + "\n")
    
    print("🧠 Knowledge Graph:")
    kg_stats = knowledge_graph.get_stats()
    print(f"  Concepts extracted: {kg_stats['total_nodes']}")
    print(f"  Relationships: {kg_stats['total_edges']}")
    if kg_stats['most_central']:
        print(f"  Central concepts: {[c[0] for c in kg_stats['most_central'][:5]]}")
    
    print(f"\n📊 Debate Statistics:")
    print(f"  Agents: {len(agents)}")
    print(f"  Proposals: {len(proposals)}")
    print(f"  Total Challenges: {sum(len(p['challenges']) for p in proposals)}")
    print(f"  Total Rebuttals: {sum(len(p['rebuttals']) for p in proposals)}")
    print(f"  Web Searches: 2 (real internet queries)")
    print(f"  LLM API Calls: ~{len(agents) * 3} (proposals + challenges + rebuttals)")
    
    print(f"\n🎭 Final Emotional States:")
    for agent, emotion in [(agent1, emotion1), (agent2, emotion2), (agent3, emotion3)]:
        print(f"  {agent.name}: {emotion.current_state.value} ({emotion.emotion_intensity:.2f})")
    
    # Save everything
    conv_file, vitals_file = doc.save_all(test_folder)
    knowledge_graph.export_graph(f"{test_folder}/knowledge_graph.json")
    
    # Save proposals for review
    with open(f"{test_folder}/llm_generated_content.txt", 'w', encoding='utf-8') as f:
        f.write("LLM-GENERATED DEBATE CONTENT\n")
        f.write("="*80 + "\n\n")
        
        for idx, proposal in enumerate(proposals, 1):
            f.write(f"PROPOSAL {idx} - {proposal['agent'].name}\n")
            f.write("-"*80 + "\n")
            f.write(f"{proposal['content']}\n\n")
            
            for challenge in proposal['challenges']:
                f.write(f"  CHALLENGE by {challenge['agent'].name}:\n")
                f.write(f"  {challenge['content']}\n\n")
            
            for rebuttal in proposal['rebuttals']:
                f.write(f"  REBUTTAL by {rebuttal['agent'].name}:\n")
                f.write(f"  {rebuttal['content']}\n\n")
            
            f.write("\n" + "="*80 + "\n\n")
    
    print(f"\n\n" + "="*80)
    print("TEST 4 COMPLETE - REAL AI REASONING DEMONSTRATED")
    print("="*80)
    
    print(f"\n✅ Saved to: {test_folder}/")
    print(f"   📄 {os.path.basename(conv_file)}")
    print(f"   📊 {os.path.basename(vitals_file)}")
    print(f"   🧠 knowledge_graph.json")
    print(f"   🤖 llm_generated_content.txt (GPT outputs)")
    
    print("\n🎉 This was REAL AI reasoning - not templates!")
    print("   - GPT generated all arguments")
    print("   - Real web searches performed")
    print("   - Actual intelligent debate")
    
    return {
        "agents": len(agents),
        "proposals": len(proposals),
        "llm_powered": True,
        "web_searches": 2
    }


if __name__ == "__main__":
    print("\n⚠️  NOTE: This test makes real OpenAI API calls (costs money)")
    print("⚠️  This test performs real web searches")
    input("\nPress ENTER to proceed with Test 4...")
    
    result = run_test4()
    print("\n🎉 Test 4 complete - Real LLM reasoning demonstrated!")
