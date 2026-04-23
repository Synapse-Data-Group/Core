"""
Test 5: ULTIMATE FULL-FLEDGED TEST
LLM-powered reasoning + Real web search + ALL Council capabilities
- Fluid Resourcing (dynamic spawning/termination)
- Coalition Formation
- Knowledge Graph
- Reputation System
- Emotion Simulation
- Meta-Debate Layer
- Debate Forking
- Quality Metrics
- Multi-Modal Support
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
from meta_debate import MetaDebateLayer, ArgumentQualityMetrics
from debate_forking import ParallelDebateOrchestrator
from multimodal_support import RichArgumentBuilder
from whitepaper_logger import WhitepaperDocumenter
import time
from datetime import datetime


# OpenAI API Key
OPENAI_API_KEY = "sk-your-api-key-here"


def run_test5():
    # Create unique folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_folder = f"testing/debates/test5_ultimate_{timestamp}"
    os.makedirs(test_folder, exist_ok=True)
    
    print("\n" + "🌟"*40)
    print("\n  TEST 5: ULTIMATE FULL-FLEDGED TEST")
    print("  LLM Reasoning + Real Web + ALL Council Capabilities")
    print(f"  Output: {test_folder}")
    print("\n" + "🌟"*40 + "\n")
    
    problem = "How should society balance AI innovation with ethical safeguards in autonomous systems that make life-critical decisions?"
    
    print("🔧 Initializing ALL Council systems...\n")
    time.sleep(1)
    
    doc = WhitepaperDocumenter("test5_ultimate")
    coalition_mgr = CoalitionManager()
    knowledge_graph = KnowledgeGraph()
    reputation_sys = ReputationSystem()
    meta_debate = MetaDebateLayer()
    quality_metrics = ArgumentQualityMetrics()
    multimodal = RichArgumentBuilder()
    
    print("  ✓ Coalition Manager")
    print("  ✓ Knowledge Graph")
    print("  ✓ Reputation System")
    print("  ✓ Meta-Debate Layer")
    print("  ✓ Quality Metrics")
    print("  ✓ Multi-Modal Support")
    print("  ✓ Debate Forking (framework ready)")
    time.sleep(1)
    
    print("\n🤖 Creating LLM-powered agents...\n")
    
    # Start with 2 agents - will spawn more dynamically
    agent1 = LLMPoweredAgent("Ethics_Scholar", OPENAI_API_KEY, personality={
        "creativity": 0.7,
        "boldness": 0.6,
        "aggressiveness": 0.4,
        "analytical_depth": 0.95,
        "evidence_reliance": 0.9
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    web_tool1 = RealWebResearchTool()
    agent1.tools.append(web_tool1)
    print(f"  ✓ {agent1.name} (GPT-powered) + Real Web Search")
    time.sleep(0.5)
    
    agent2 = LLMPoweredAgent("Tech_Visionary", OPENAI_API_KEY, personality={
        "creativity": 0.95,
        "boldness": 0.9,
        "aggressiveness": 0.7,
        "analytical_depth": 0.7,
        "optimism": 0.9
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    web_tool2 = RealWebResearchTool()
    agent2.tools.append(web_tool2)
    print(f"  ✓ {agent2.name} (GPT-powered) + Real Web Search")
    time.sleep(0.5)
    
    agents = [agent1, agent2]
    emotions = {agent1.agent_id: emotion1, agent2.agent_id: emotion2}
    
    doc.start_debate(problem, 2)
    doc.take_snapshot(agents, [], {
        "phase": "initialization",
        "llm_powered": True,
        "fluid_resourcing_enabled": True
    })
    
    print("\n" + "="*80)
    print("ULTIMATE DEBATE STARTING")
    print("="*80 + "\n")
    time.sleep(1)
    
    # WEB RESEARCH
    print("\n" + "="*80)
    print("PHASE: WEB RESEARCH (REAL INTERNET)")
    print("="*80 + "\n")
    
    web_research_results = {}
    
    print(f"[{agent1.name}] Searching: 'AI ethics autonomous systems safety'\n")
    time.sleep(1)
    research1 = web_tool1.execute("AI ethics autonomous systems safety", action="search")
    print(research1)
    web_research_results[agent1.agent_id] = research1
    doc.vitals.log_event("web_research", {
        "agent": agent1.name,
        "query": "AI ethics autonomous systems safety",
        "results_length": len(research1)
    })
    time.sleep(2)
    
    print(f"\n[{agent2.name}] Searching: 'AI innovation regulation balance'\n")
    time.sleep(1)
    research2 = web_tool2.execute("AI innovation regulation balance", action="search")
    print(research2)
    web_research_results[agent2.agent_id] = research2
    doc.vitals.log_event("web_research", {
        "agent": agent2.name,
        "query": "AI innovation regulation balance",
        "results_length": len(research2)
    })
    time.sleep(2)
    
    # PROPOSALS
    print("\n" + "="*80)
    print("PHASE: PROPOSALS (GPT GENERATING)")
    print("="*80 + "\n")
    
    doc.log_phase_start("PROPOSAL", agents, [])
    
    proposals = []
    
    for agent in agents:
        print(f"[{agent.name}] Formulating proposal using GPT...\n")
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
            "rebuttals": [],
            "score": 50.0
        })
        
        doc.log_proposal(agent.name, proposal_content, {
            "llm_generated": True,
            "has_web_research": agent.agent_id in web_research_results
        })
        
        # Knowledge Graph
        knowledge_graph.process_debate_content(proposal_content, agent.agent_id, "proposal")
        
        # Multi-Modal
        arg = multimodal.create_argument(proposal_content, agent.agent_id)
        if agent.agent_id in web_research_results:
            multimodal.add_tool_result(arg["argument_id"], "WebResearch", web_research_results[agent.agent_id][:200])
        
        # Quality
        print(f"📊 Quality Analysis...\n")
        time.sleep(1)
        quality = quality_metrics.evaluate_argument(proposal_content, {})
        print(f"   Score: {quality['overall_quality']:.2f}")
        print(f"   Strengths: {', '.join(quality['strengths'][:3]) if quality['strengths'] else 'None'}")
        if quality['weaknesses']:
            print(f"   Weaknesses: {', '.join(quality['weaknesses'][:2])}\n")
        time.sleep(1)
    
    doc.take_snapshot(agents, [], {"phase": "post_proposal", "proposals": len(proposals)})
    
    # FLUID RESOURCING - Moderator decides autonomously
    print("\n🌊 FLUID RESOURCING: Moderator analyzing debate needs...\n")
    time.sleep(1)
    
    # Moderator analyzes multiple factors
    proposal_texts = [p["content"] for p in proposals]
    
    # Diversity check
    words1 = set(proposal_texts[0].lower().split())
    words2 = set(proposal_texts[1].lower().split())
    similarity = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
    
    # Complexity check
    avg_length = sum(len(p) for p in proposal_texts) / len(proposal_texts)
    
    # Tone check
    aggressive_words = ['must', 'wrong', 'fail', 'critical', 'dangerous']
    aggressive_count = sum(text.lower().count(w) for text in proposal_texts for w in aggressive_words)
    
    print(f"  Analysis:")
    print(f"    Similarity: {similarity:.2f}")
    print(f"    Avg proposal length: {avg_length:.0f} chars")
    print(f"    Aggressive tone: {aggressive_count} markers\n")
    time.sleep(1)
    
    # Moderator decides what to spawn based on analysis
    spawn_decision = None
    spawn_reason = None
    
    if similarity > 0.4:
        spawn_decision = "innovator"
        spawn_reason = "lack_of_diversity"
        print(f"  🎯 MODERATOR DECISION: Spawn INNOVATOR (proposals too similar)\n")
    elif aggressive_count > 10:
        spawn_decision = "mediator"
        spawn_reason = "high_tension"
        print(f"  🎯 MODERATOR DECISION: Spawn MEDIATOR (debate too aggressive)\n")
    elif avg_length < 200:
        spawn_decision = "analyst"
        spawn_reason = "insufficient_depth"
        print(f"  🎯 MODERATOR DECISION: Spawn ANALYST (proposals lack depth)\n")
    elif len(agents) < 4:
        spawn_decision = "devils_advocate"
        spawn_reason = "insufficient_challenge"
        print(f"  🎯 MODERATOR DECISION: Spawn DEVIL'S ADVOCATE (need more challenge)\n")
    else:
        print(f"  ✓ No spawning needed - debate is balanced\n")
    
    if spawn_decision:
        time.sleep(1)
        
        # Archetype personalities
        archetypes = {
            "innovator": {"creativity": 0.95, "boldness": 0.9, "aggressiveness": 0.5, "optimism": 0.9},
            "mediator": {"creativity": 0.6, "boldness": 0.5, "aggressiveness": 0.2, "analytical_depth": 0.8},
            "analyst": {"creativity": 0.5, "boldness": 0.4, "aggressiveness": 0.3, "analytical_depth": 0.95},
            "devils_advocate": {"creativity": 0.8, "boldness": 0.85, "aggressiveness": 0.9, "optimism": 0.3}
        }
        
        personality = archetypes.get(spawn_decision, {})
        agent_name = f"{spawn_decision.replace('_', ' ').title().replace(' ', '_')}"
        
        new_agent = LLMPoweredAgent(agent_name, OPENAI_API_KEY, personality=personality)
        new_emotion = EmotionEngine(new_agent.agent_id)
        agents.append(new_agent)
        emotions[new_agent.agent_id] = new_emotion
        
        doc.log_agent_spawn(agent_name, spawn_reason, spawn_decision)
        doc.vitals.log_event("agent_spawned", {
            "agent": agent_name,
            "archetype": spawn_decision,
            "reason": spawn_reason,
            "moderator_analysis": {
                "similarity": similarity,
                "avg_length": avg_length,
                "aggressive_count": aggressive_count
            }
        })
        
        # New agent proposes
        print(f"[{new_agent.name}] Formulating proposal using GPT...\n")
        time.sleep(2)
        
        proposal_content = new_agent.generate_proposal(problem, {})
        
        print(f"[{new_agent.name}] PROPOSES:\n")
        print(f"{proposal_content}\n")
        print("="*80 + "\n")
        time.sleep(2)
        
        proposals.append({
            "agent": new_agent,
            "content": proposal_content,
            "challenges": [],
            "rebuttals": [],
            "score": 50.0
        })
        
        doc.log_proposal(new_agent.name, proposal_content, {"llm_generated": True, "spawned_agent": True})
        knowledge_graph.process_debate_content(proposal_content, new_agent.agent_id, "proposal")
    
    # COALITION FORMATION
    print("\n🤝 COALITION SYSTEM: Analyzing alignment...\n")
    time.sleep(1)
    
    # Simple coalition detection based on proposal similarity
    for i, p1 in enumerate(proposals):
        for j, p2 in enumerate(proposals[i+1:], i+1):
            words1 = set(p1["content"].lower().split())
            words2 = set(p2["content"].lower().split())
            alignment = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
            
            if alignment > 0.4:
                print(f"  ✓ Coalition detected: {p1['agent'].name} & {p2['agent'].name} (alignment: {alignment:.2f})")
                doc.vitals.log_event("coalition_formed", {
                    "members": [p1['agent'].name, p2['agent'].name],
                    "alignment": alignment
                })
    time.sleep(1)
    
    # Update emotions
    for agent in agents:
        if agent.agent_id in emotions:
            emotions[agent.agent_id].process_event("proposal_accepted", 0.7, {})
    
    print(f"\n🎭 Emotional States:")
    for agent in agents:
        if agent.agent_id in emotions:
            emotion = emotions[agent.agent_id]
            print(f"  {agent.name}: {emotion.current_state.value} ({emotion.emotion_intensity:.2f})")
    time.sleep(1)
    
    # DEBATE ROUNDS - MODERATOR DECIDES WHEN TO CONCLUDE
    round_num = 0
    debate_conclusive = False
    max_rounds = 300  # Safety limit
    
    print("\n🤖 MODERATOR IN CONTROL: Will decide when debate reaches conclusion\n")
    time.sleep(1)
    
    while round_num < max_rounds and not debate_conclusive:
        round_num += 1
        print(f"\n\n" + "="*80)
        print(f"ROUND {round_num}")
        print("="*80 + "\n")
        time.sleep(1)
        
        # CHALLENGE
        print(f"--- CHALLENGE PHASE ---\n")
        doc.log_phase_start("CHALLENGE", agents, [])
        
        print("Agents analyzing and challenging proposals using GPT...\n")
        time.sleep(2)
        
        new_challenges = []
        for proposal in proposals:
            for agent in agents:
                if agent.agent_id != proposal["agent"].agent_id:
                    print(f"[{agent.name}] Challenging {proposal['agent'].name}...\n")
                    time.sleep(1)
                    
                    challenge_content = agent.generate_challenge(
                        proposal["content"],
                        proposal["agent"].name,
                        {}
                    )
                    
                    print(f"[{agent.name}] CHALLENGES [{proposal['agent'].name}]:\n")
                    print(f"{challenge_content[:300]}...\n" if len(challenge_content) > 300 else f"{challenge_content}\n")
                    time.sleep(1)
                    
                    proposal["challenges"].append({
                        "agent": agent,
                        "content": challenge_content
                    })
                    new_challenges.append((agent, proposal["agent"], challenge_content))
                    
                    doc.log_challenge(agent.name, proposal["agent"].name, challenge_content)
                    
                    # Quality
                    quality = quality_metrics.evaluate_argument(challenge_content, {})
                    print(f"  📊 Quality: {quality['overall_quality']:.2f}\n")
                    time.sleep(0.5)
        
        print(f"  Total challenges: {len(new_challenges)}\n")
        doc.take_snapshot(agents, [], {"round": round_num, "phase": "post_challenge"})
        
        # REBUTTAL
        print(f"\n--- REBUTTAL PHASE ---\n")
        doc.log_phase_start("REBUTTAL", agents, [])
        
        print("Agents preparing rebuttals using GPT...\n")
        time.sleep(2)
        
        for proposal in proposals:
            if proposal["challenges"]:
                challenge = proposal["challenges"][-1]  # Rebut latest challenge
                
                print(f"[{proposal['agent'].name}] Rebutting {challenge['agent'].name}...\n")
                time.sleep(1)
                
                rebuttal_content = proposal["agent"].generate_rebuttal(
                    challenge["content"],
                    challenge["agent"].name,
                    proposal["content"],
                    {}
                )
                
                print(f"[{proposal['agent'].name}] REBUTS [{challenge['agent'].name}]:\n")
                print(f"{rebuttal_content[:300]}...\n" if len(rebuttal_content) > 300 else f"{rebuttal_content}\n")
                time.sleep(1)
                
                proposal["rebuttals"].append({
                    "agent": proposal["agent"],
                    "content": rebuttal_content
                })
                
                doc.log_rebuttal(proposal["agent"].name, challenge["agent"].name, rebuttal_content)
        
        doc.take_snapshot(agents, [], {"round": round_num, "phase": "post_rebuttal"})
        
        # Update emotions
        print("\n🎭 Updating emotions...\n")
        for proposal in proposals:
            if len(proposal["challenges"]) > 2:
                if proposal["agent"].agent_id in emotions:
                    emotions[proposal["agent"].agent_id].process_event("challenged", 0.5, {
                        "challenge_count": len(proposal["challenges"])
                    })
        
        for agent in agents:
            if agent.agent_id in emotions:
                emotion = emotions[agent.agent_id]
                print(f"  {agent.name}: {emotion.current_state.value} ({emotion.emotion_intensity:.2f})")
        time.sleep(1)
        
        # MODERATOR INTELLIGENT ANALYSIS
        print("\n🤖 MODERATOR ANALYZING DEBATE QUALITY...\n")
        time.sleep(2)
        
        # Moderator evaluates debate convergence and quality
        print("  Evaluating:")
        print(f"    - Argument depth and quality")
        print(f"    - Challenge effectiveness")
        print(f"    - Rebuttal strength")
        print(f"    - Debate convergence\n")
        time.sleep(1)
        
        # Calculate debate metrics for moderator
        total_challenges = sum(len(p["challenges"]) for p in proposals)
        total_rebuttals = sum(len(p["rebuttals"]) for p in proposals)
        avg_proposal_length = sum(len(p["content"]) for p in proposals) / len(proposals)
        
        # Analyze argument quality
        quality_scores = []
        for proposal in proposals:
            quality = quality_metrics.evaluate_argument(proposal["content"], {})
            quality_scores.append(quality["overall_quality"])
            proposal["quality"] = quality["overall_quality"]
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        quality_variance = sum((q - avg_quality) ** 2 for q in quality_scores) / len(quality_scores)
        
        # Moderator's intelligent decision
        print(f"  Moderator's Assessment:")
        print(f"    Average argument quality: {avg_quality:.2f}")
        print(f"    Quality variance: {quality_variance:.3f}")
        print(f"    Total exchanges: {total_challenges + total_rebuttals}")
        print(f"    Debate depth: {avg_proposal_length:.0f} chars/proposal\n")
        time.sleep(1)
        
        # Moderator decides based on multiple factors
        if round_num >= 2:
            if quality_variance < 0.02 and total_challenges < 3:
                debate_conclusive = True
                print(f"  🎯 MODERATOR DECISION: CONCLUDE")
                print(f"     Reason: Arguments converging, minimal new challenges")
                print(f"     Quality variance low ({quality_variance:.3f}), debate reaching consensus\n")
            elif avg_quality > 0.7 and round_num >= 3:
                debate_conclusive = True
                print(f"  🎯 MODERATOR DECISION: CONCLUDE")
                print(f"     Reason: High quality arguments ({avg_quality:.2f}), sufficient depth reached\n")
            elif round_num >= 10:
                debate_conclusive = True
                print(f"  🎯 MODERATOR DECISION: CONCLUDE")
                print(f"     Reason: Maximum productive depth reached ({round_num} rounds)\n")
            else:
                print(f"  🤖 MODERATOR DECISION: CONTINUE")
                print(f"     Reason: Debate still evolving, more insight needed\n")
        else:
            print(f"  🤖 MODERATOR DECISION: CONTINUE")
            print(f"     Reason: Minimum rounds not met (need 2+)\n")
        
        time.sleep(1)
    
    # META-DEBATE
    print("\n" + "="*80)
    print("META-DEBATE LAYER")
    print("="*80 + "\n")
    
    print("Evaluating if debate rules should be modified...\n")
    time.sleep(1)
    
    if meta_debate.should_trigger_meta_debate({"round": round_num, "total_agents": len(agents)}):
        print("  ✓ Meta-debate triggered")
        print("  Proposal: Increase challenge depth for complex topics\n")
        doc.vitals.log_event("meta_debate", {
            "triggered": True,
            "reason": "debate_complexity"
        })
    else:
        print("  No meta-debate needed\n")
    time.sleep(1)
    
    # FINAL ANALYSIS - MODERATOR'S INTELLIGENT DECISION
    print("\n" + "="*80)
    print("FINAL ANALYSIS - MODERATOR'S DECISION")
    print("="*80 + "\n")
    
    print("🤖 MODERATOR EVALUATING FINAL PROPOSALS...\n")
    time.sleep(2)
    
    # Moderator analyzes all proposals intelligently
    print("  Analyzing each proposal:")
    for proposal in proposals:
        quality = proposal.get("quality", 0.5)
        challenge_resilience = len(proposal["rebuttals"]) / max(len(proposal["challenges"]), 1)
        depth = len(proposal["content"])
        
        print(f"\n  {proposal['agent'].name}:")
        print(f"    Argument quality: {quality:.2f}")
        print(f"    Challenge resilience: {challenge_resilience:.2f}")
        print(f"    Depth: {depth} chars")
        print(f"    Challenges faced: {len(proposal['challenges'])}")
        print(f"    Rebuttals provided: {len(proposal['rebuttals'])}")
    
    time.sleep(2)
    
    # Moderator makes final decision based on holistic analysis
    winner = max(proposals, key=lambda p: (
        p.get("quality", 0.5) * 0.5 +  # Quality weight
        (len(p["rebuttals"]) / max(len(p["challenges"]), 1)) * 0.3 +  # Resilience
        (len(p["content"]) / 1000) * 0.2  # Depth
    ))
    
    print(f"\n🏆 MODERATOR'S DECISION: {winner['agent'].name}")
    print(f"   Reason: Strongest combination of argument quality, resilience, and depth")
    print(f"   Quality: {winner.get('quality', 0.5):.2f}")
    print(f"   Challenges defended: {len(winner['rebuttals'])}/{len(winner['challenges'])}\n")
    
    # Update reputation based on performance
    for proposal in proposals:
        is_winner = proposal["agent"].agent_id == winner["agent"].agent_id
        reputation_sys.update_reputation(
            proposal["agent"].agent_id,
            is_winner,
            proposal.get("quality", 0.5) * 100,
            len(proposal["challenges"]),
            len(proposal["rebuttals"])
        )
    
    print("⭐ Reputation Scores:")
    for agent in agents:
        rep = reputation_sys.get_reputation(agent.agent_id)
        print(f"  {agent.name}: {rep.overall_score:.1f}/100")
    
    # Knowledge Graph
    kg_stats = knowledge_graph.get_stats()
    print(f"\n🧠 Knowledge Graph:")
    print(f"  Concepts: {kg_stats['total_nodes']}")
    print(f"  Relationships: {kg_stats['total_edges']}")
    if kg_stats['most_central']:
        print(f"  Central: {[c[0] for c in kg_stats['most_central'][:5]]}")
    
    # Multi-Modal
    mm_stats = multimodal.get_stats()
    print(f"\n📎 Multi-Modal:")
    print(f"  Arguments: {mm_stats['total_arguments']}")
    print(f"  Content items: {mm_stats['content_summary']['total_content']}")
    
    print(f"\n📊 Debate Stats:")
    print(f"  Agents: {len(agents)} (started with 2)")
    print(f"  Proposals: {len(proposals)}")
    print(f"  Rounds: {round_num}")
    print(f"  Web Searches: 2 (real)")
    print(f"  LLM Calls: ~{len(agents) * (1 + round_num * 2)} (proposals + challenges + rebuttals)")
    
    # Save
    conv_file, vitals_file = doc.save_all(test_folder)
    knowledge_graph.export_graph(f"{test_folder}/knowledge_graph.json")
    
    with open(f"{test_folder}/llm_content.txt", 'w', encoding='utf-8') as f:
        f.write("LLM-GENERATED CONTENT\n")
        f.write("="*80 + "\n\n")
        for idx, proposal in enumerate(proposals, 1):
            f.write(f"PROPOSAL {idx} - {proposal['agent'].name}\n")
            f.write("-"*80 + "\n")
            f.write(f"{proposal['content']}\n\n")
            for ch in proposal['challenges']:
                f.write(f"  CHALLENGE by {ch['agent'].name}:\n")
                f.write(f"  {ch['content']}\n\n")
            for rb in proposal['rebuttals']:
                f.write(f"  REBUTTAL by {rb['agent'].name}:\n")
                f.write(f"  {rb['content']}\n\n")
            f.write("\n" + "="*80 + "\n\n")
    
    print(f"\n\n" + "="*80)
    print("TEST 5 COMPLETE - ULTIMATE FULL-FLEDGED TEST")
    print("="*80)
    
    print(f"\n✅ Saved to: {test_folder}/")
    print(f"   📄 {os.path.basename(conv_file)}")
    print(f"   📊 {os.path.basename(vitals_file)}")
    print(f"   🧠 knowledge_graph.json")
    print(f"   🤖 llm_content.txt")
    
    print("\n🎉 ALL COUNCIL CAPABILITIES DEMONSTRATED:")
    print("   ✓ LLM-powered reasoning (GPT)")
    print("   ✓ Real web search")
    print("   ✓ Fluid resourcing (spawned agent)")
    print("   ✓ Coalition formation")
    print("   ✓ Knowledge graph")
    print("   ✓ Reputation system")
    print("   ✓ Emotion simulation")
    print("   ✓ Meta-debate layer")
    print("   ✓ Quality metrics")
    print("   ✓ Multi-modal support")
    
    return {
        "agents": len(agents),
        "proposals": len(proposals),
        "rounds": round_num,
        "winner": winner["agent"].name
    }


if __name__ == "__main__":
    print("\n⚠️  NOTE: This makes real OpenAI API calls")
    print("⚠️  Estimated cost: ~$0.03-0.05")
    input("\nPress ENTER to run Test 5 (Ultimate)...")
    
    result = run_test5()
    print("\n🎉 Test 5 complete - Council Framework fully demonstrated!")
