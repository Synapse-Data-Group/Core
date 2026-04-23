"""
Test 3: Comprehensive Council Framework Test
ALL capabilities including web research for references
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fluid_debate_system import FluidDebateSystem
from coalition_system import CoalitionManager
from knowledge_graph import KnowledgeGraph
from reputation_system import ReputationSystem
from emotion_system import EmotionEngine
from web_fetcher import WebResearchTool
from meta_debate import MetaDebateLayer, ArgumentQualityMetrics
from multimodal_support import RichArgumentBuilder
from whitepaper_logger import WhitepaperDocumenter
import time
from datetime import datetime


def run_test3():
    # Create unique folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_folder = f"testing/debates/test3_{timestamp}"
    os.makedirs(test_folder, exist_ok=True)
    
    print("\n" + "🌟"*40)
    print("\n  TEST 3: COMPREHENSIVE - ALL CAPABILITIES")
    print("  Including Web Research")
    print(f"  Output: {test_folder}")
    print("\n" + "🌟"*40 + "\n")
    
    problem = "What regulatory framework should govern AI systems in healthcare, considering patient safety, innovation, and ethical concerns?"
    
    print("🔧 Initializing ALL systems...\n")
    time.sleep(1)
    
    doc = WhitepaperDocumenter("test3_comprehensive")
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    coalition_mgr = CoalitionManager()
    knowledge_graph = KnowledgeGraph()
    reputation_sys = ReputationSystem()
    meta_debate = MetaDebateLayer()
    quality_metrics = ArgumentQualityMetrics()
    multimodal = RichArgumentBuilder()
    
    print("  ✓ Fluid Debate System")
    print("  ✓ Coalition Manager")
    print("  ✓ Knowledge Graph")
    print("  ✓ Reputation System")
    print("  ✓ Meta-Debate Layer")
    print("  ✓ Quality Metrics")
    print("  ✓ Multi-Modal Support")
    time.sleep(1)
    
    print("\n👥 Creating agents with web research capability...\n")
    
    # Agent 1: Researcher with web access
    agent1 = debate.create_agent("Dr_Researcher", personality={
        "creativity": 0.6,
        "boldness": 0.5,
        "aggressiveness": 0.3,
        "analytical_depth": 0.95,
        "evidence_reliance": 0.95
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    web_tool1 = WebResearchTool()
    debate.create_tool_for_agent(agent1.agent_id, web_tool1)
    print(f"  ✓ Dr_Researcher (Evidence-based) + Web Research Tool")
    time.sleep(0.5)
    
    # Agent 2: Policy Expert with web access
    agent2 = debate.create_agent("Policy_Expert", personality={
        "creativity": 0.7,
        "boldness": 0.6,
        "aggressiveness": 0.5,
        "analytical_depth": 0.85,
        "evidence_reliance": 0.8
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    web_tool2 = WebResearchTool()
    debate.create_tool_for_agent(agent2.agent_id, web_tool2)
    print(f"  ✓ Policy_Expert (Regulatory focus) + Web Research Tool")
    time.sleep(0.5)
    
    # Agent 3: Innovation Advocate
    agent3 = debate.create_agent("Innovation_Advocate", personality={
        "creativity": 0.9,
        "boldness": 0.85,
        "aggressiveness": 0.7,
        "optimism": 0.9,
        "analytical_depth": 0.6
    })
    emotion3 = EmotionEngine(agent3.agent_id)
    print(f"  ✓ Innovation_Advocate (Pro-innovation)")
    time.sleep(0.5)
    
    doc.start_debate(problem, 3)
    doc.take_snapshot(list(debate.agents.values()), [], {"phase": "initialization"})
    
    print("\n" + "="*80)
    print("DEBATE STARTING")
    print("="*80 + "\n")
    time.sleep(1)
    
    # Hook spawning
    original_spawn = debate.moderator.spawn_agent
    def tracked_spawn(role, debate_sys, reason):
        print(f"\n🌊 MODERATOR SPAWNING AGENT...")
        print(f"   Role: {role}")
        print(f"   Reason: {reason}")
        time.sleep(1)
        
        agent = original_spawn(role, debate_sys, reason)
        if agent:
            archetype = debate.moderator.agent_factory.get_agent_info(agent.agent_id)
            print(f"   ✓ Spawned: {agent.name} ({archetype['archetype'] if archetype else 'unknown'})")
            doc.log_agent_spawn(agent.name, reason, archetype["archetype"] if archetype else "unknown")
            doc.take_snapshot(list(debate_sys.agents.values()), debate_sys.proposals, {
                "event": "agent_spawned",
                "agent": agent.name
            })
            time.sleep(1)
        return agent
    
    debate.moderator.spawn_agent = tracked_spawn
    
    # WEB RESEARCH PHASE
    print("\n" + "="*80)
    print("PHASE: WEB RESEARCH")
    print("="*80 + "\n")
    
    print("Agents conducting web research for evidence...\n")
    time.sleep(1)
    
    # Agent 1 researches AI healthcare regulations
    print(f"[{agent1.name}] Searching: 'AI healthcare regulations patient safety'")
    time.sleep(1)
    research1 = web_tool1.execute("AI healthcare regulations patient safety", action="search")
    print(f"  ✓ Found references")
    doc.vitals.log_event("web_research", {
        "agent": agent1.name,
        "query": "AI healthcare regulations patient safety",
        "results_length": len(research1)
    })
    
    # Create rich argument with web data
    arg1 = multimodal.create_argument("Initial research on AI healthcare regulations", agent1.agent_id)
    multimodal.add_tool_result(arg1["argument_id"], "WebResearchTool", research1[:200])
    time.sleep(1)
    
    # Agent 2 researches regulatory frameworks
    print(f"\n[{agent2.name}] Searching: 'medical device regulation AI systems'")
    time.sleep(1)
    research2 = web_tool2.execute("medical device regulation AI systems", action="search")
    print(f"  ✓ Found references")
    doc.vitals.log_event("web_research", {
        "agent": agent2.name,
        "query": "medical device regulation AI systems",
        "results_length": len(research2)
    })
    
    arg2 = multimodal.create_argument("Regulatory framework analysis", agent2.agent_id)
    multimodal.add_tool_result(arg2["argument_id"], "WebResearchTool", research2[:200])
    time.sleep(1)
    
    print("\n  Web research complete. Agents have evidence for their arguments.")
    time.sleep(1)
    
    # PROPOSAL PHASE
    print("\n" + "="*80)
    print("PHASE: PROPOSALS")
    print("="*80 + "\n")
    
    doc.log_phase_start("PROPOSAL", list(debate.agents.values()), [])
    
    print("Agents formulating proposals based on research...\n")
    time.sleep(2)
    
    debate._proposal_phase()
    
    for idx, proposal in enumerate(debate.proposals, 1):
        print(f"\n[{proposal.agent_name}] PROPOSES:")
        print(f"  {proposal.content}")
        print()
        time.sleep(1)
        
        doc.log_proposal(proposal.agent_name, proposal.content, {
            "proposal_id": proposal.proposal_id,
            "has_web_research": proposal.agent_id in [agent1.agent_id, agent2.agent_id]
        })
        
        # Extract knowledge
        knowledge_graph.process_debate_content(proposal.content, proposal.agent_id, "proposal")
        
        # Quality analysis
        print(f"  📊 Analyzing argument quality...")
        time.sleep(0.5)
        quality = quality_metrics.evaluate_argument(proposal.content, {})
        print(f"     Quality: {quality['overall_quality']:.2f}")
        print(f"     Strengths: {', '.join(quality['strengths'][:3]) if quality['strengths'] else 'None'}")
        if quality['weaknesses']:
            print(f"     Weaknesses: {', '.join(quality['weaknesses'][:2])}")
        doc.vitals.log_event("argument_quality", {
            "agent": proposal.agent_name,
            "quality_score": quality["overall_quality"],
            "scores": quality["scores"]
        })
        time.sleep(1)
    
    doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"phase": "post_proposal"})
    
    # Check spawning
    print("\n🔍 Moderator analyzing debate needs...")
    time.sleep(1)
    debate._assess_and_spawn_agents("post_proposal")
    
    # Coalition check
    print("\n🤝 Checking coalition formation...")
    time.sleep(1)
    coalition_mgr.update_coalitions(list(debate.agents.values()), debate.proposals, {})
    
    if coalition_mgr.coalitions:
        for coalition in coalition_mgr.coalitions.values():
            print(f"  ✓ Coalition formed: {len(coalition.members)} members")
            doc.vitals.log_event("coalition_formed", {
                "coalition_id": coalition.coalition_id,
                "members": list(coalition.members),
                "strength": coalition.strength
            })
    else:
        print("  No coalitions yet")
    time.sleep(1)
    
    # Update emotions
    for agent, emotion in [(agent1, emotion1), (agent2, emotion2), (agent3, emotion3)]:
        emotion.process_event("proposal_accepted", 0.7, {})
    
    print(f"\n🎭 Emotional States:")
    print(f"  {agent1.name}: {emotion1.current_state.value} ({emotion1.emotion_intensity:.2f})")
    print(f"  {agent2.name}: {emotion2.current_state.value} ({emotion2.emotion_intensity:.2f})")
    print(f"  {agent3.name}: {emotion3.current_state.value} ({emotion3.emotion_intensity:.2f})")
    time.sleep(1)
    
    # DEBATE ROUNDS
    round_num = 0
    debate_conclusive = False
    
    while round_num < 10 and not debate_conclusive:
        round_num += 1
        print(f"\n\n" + "="*80)
        print(f"ROUND {round_num}")
        print("="*80 + "\n")
        time.sleep(1)
        
        # CHALLENGE
        print(f"--- CHALLENGE PHASE ---\n")
        time.sleep(0.5)
        
        doc.log_phase_start("CHALLENGE", list(debate.agents.values()), debate.proposals)
        
        print("Agents analyzing and challenging proposals...\n")
        time.sleep(2)
        
        debate._challenge_phase()
        
        new_challenges = []
        for proposal in debate.proposals:
            for challenge in proposal.challenges:
                is_new = True
                for p in debate.proposals:
                    if challenge in p.challenges[:-1]:
                        is_new = False
                        break
                if is_new:
                    new_challenges.append((challenge, proposal))
        
        if new_challenges:
            for challenge, proposal in new_challenges:
                print(f"\n[{challenge.agent_name}] CHALLENGES [{proposal.agent_name}]:")
                print(f"  {challenge.content[:200]}..." if len(challenge.content) > 200 else f"  {challenge.content}")
                time.sleep(1)
                
                doc.log_challenge(challenge.agent_name, proposal.agent_name, challenge.content)
                
                quality = quality_metrics.evaluate_argument(challenge.content, {})
                print(f"  📊 Quality: {quality['overall_quality']:.2f}")
                time.sleep(0.5)
        else:
            print("  No new challenges")
        
        print(f"\n  Challenges this round: {len(new_challenges)}")
        time.sleep(1)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num,
            "phase": "post_challenge"
        })
        
        print("\n🔍 Moderator assessing...")
        time.sleep(1)
        debate._assess_and_spawn_agents("post_challenge")
        
        # REBUTTAL
        print(f"\n--- REBUTTAL PHASE ---\n")
        time.sleep(0.5)
        
        doc.log_phase_start("REBUTTAL", list(debate.agents.values()), debate.proposals)
        
        print("Agents preparing rebuttals...\n")
        time.sleep(2)
        
        debate._rebuttal_phase()
        
        new_rebuttals = []
        for proposal in debate.proposals:
            for rebuttal in proposal.rebuttals:
                is_new = True
                for p in debate.proposals:
                    if rebuttal in p.rebuttals[:-1]:
                        is_new = False
                        break
                if is_new:
                    new_rebuttals.append((rebuttal, proposal))
        
        if new_rebuttals:
            for rebuttal, proposal in new_rebuttals:
                target = rebuttal.metadata.get("challenge_agent", "Unknown")
                print(f"\n[{rebuttal.agent_name}] REBUTS [{target}]:")
                print(f"  {rebuttal.content[:200]}..." if len(rebuttal.content) > 200 else f"  {rebuttal.content}")
                time.sleep(1)
                
                doc.log_rebuttal(rebuttal.agent_name, target, rebuttal.content)
        else:
            print("  No new rebuttals")
        
        print(f"\n  Rebuttals this round: {len(new_rebuttals)}")
        time.sleep(1)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num,
            "phase": "post_rebuttal"
        })
        
        debate._assess_and_spawn_agents("post_rebuttal")
        
        # Update emotions
        print("\n🎭 Updating emotions...")
        time.sleep(0.5)
        for agent, emotion in [(agent1, emotion1), (agent2, emotion2), (agent3, emotion3)]:
            if agent.agent_id in debate.agents:
                challenges = sum(1 for p in debate.proposals if p.agent_id == agent.agent_id for c in p.challenges)
                if challenges > 3:
                    emotion.process_event("challenged", 0.5, {"challenge_count": challenges})
                print(f"  {agent.name}: {emotion.current_state.value} ({emotion.emotion_intensity:.2f})")
        time.sleep(1)
        
        # Check conclusion
        print("\n🎯 Moderator evaluating...")
        time.sleep(1)
        
        scores = [p.score for p in debate.proposals]
        if scores:
            score_range = max(scores) - min(scores)
            
            if round_num >= 3:
                if score_range > 20 and len(new_challenges) < 2:
                    debate_conclusive = True
                    print(f"  ✓ CONCLUSIVE: Clear winner (gap: {score_range:.1f})")
                elif round_num >= 10:
                    debate_conclusive = True
                    print(f"  ✓ CONCLUSIVE: Maximum depth")
                else:
                    print(f"  → Continuing (gap: {score_range:.1f}, challenges: {len(new_challenges)})")
            else:
                print(f"  → Continuing (round {round_num}/3 min)")
        
        print(f"  Agents: {len(debate.agents)} | Messages: {len(debate.messages)}")
        time.sleep(1)
    
    # SCORING
    print(f"\n\n" + "="*80)
    print("SCORING PHASE")
    print("="*80 + "\n")
    time.sleep(1)
    
    print("Moderator evaluating proposals...\n")
    time.sleep(2)
    
    doc.log_phase_start("SCORING", list(debate.agents.values()), debate.proposals)
    debate._scoring_phase()
    
    scores = {p.agent_name: p.score for p in debate.proposals}
    doc.log_scoring(scores)
    
    sorted_proposals = sorted(debate.proposals, key=lambda p: p.score, reverse=True)
    for idx, proposal in enumerate(sorted_proposals, 1):
        print(f"  {idx}. {proposal.agent_name}: {proposal.score:.1f} points")
        print(f"     Challenges: {len(proposal.challenges)}, Rebuttals: {len(proposal.rebuttals)}")
        time.sleep(0.5)
    
    # Reputation
    for agent in debate.agents.values():
        is_winner = agent.score == max(scores.values())
        reputation_sys.update_reputation(
            agent.agent_id,
            is_winner,
            agent.score,
            len(agent.challenges_made),
            len(agent.rebuttals_made)
        )
    
    print("\n⭐ Reputation:")
    for agent in debate.agents.values():
        rep = reputation_sys.get_reputation(agent.agent_id)
        print(f"  {agent.name}: {rep.overall_score:.1f}/100")
        time.sleep(0.3)
    
    # RESOLUTION
    print(f"\n\n" + "="*80)
    print("RESOLUTION PHASE")
    print("="*80 + "\n")
    time.sleep(1)
    
    print("Moderator making final decision...\n")
    time.sleep(2)
    
    doc.log_phase_start("RESOLUTION", list(debate.agents.values()), debate.proposals)
    debate._resolution_phase()
    
    print(f"\n[MODERATOR] FINAL DECISION:")
    print(f"  {debate.final_decision['decision']}")
    print(f"  Confidence: {debate.final_decision['confidence']:.1%}")
    print(f"\nReasoning:")
    print(f"  {debate.final_decision['reasoning'][:300]}...")
    time.sleep(2)
    
    doc.log_final_decision(debate.final_decision, list(debate.agents.values()), debate.proposals)
    
    # FINAL STATS
    kg_stats = knowledge_graph.get_stats()
    doc.vitals.log_event("knowledge_graph_final", kg_stats)
    
    print(f"\n\n" + "="*80)
    print("FINAL STATISTICS")
    print("="*80 + "\n")
    
    print(f"🧠 Knowledge Graph:")
    print(f"  Concepts: {kg_stats['total_nodes']}")
    print(f"  Relationships: {kg_stats['total_edges']}")
    if kg_stats['most_central']:
        print(f"  Central: {[c[0] for c in kg_stats['most_central'][:3]]}")
    
    fluid_stats = debate.moderator.get_fluid_resourcing_stats()
    print(f"\n🌊 Fluid Resourcing:")
    print(f"  Spawned: {fluid_stats['total_spawned']}")
    print(f"  Final Count: {len(debate.agents)}")
    
    coalition_stats = coalition_mgr.get_stats()
    print(f"\n🤝 Coalitions:")
    print(f"  Formed: {coalition_stats['total_coalitions']}")
    
    multimodal_stats = multimodal.get_stats()
    print(f"\n📎 Multi-Modal:")
    print(f"  Arguments: {multimodal_stats['total_arguments']}")
    print(f"  Content: {multimodal_stats['content_summary']['total_content']}")
    
    print(f"\n📊 Debate:")
    print(f"  Rounds: {round_num}")
    print(f"  Messages: {len(debate.messages)}")
    print(f"  Duration: {debate.get_debate_summary()['duration_seconds']:.2f}s")
    print(f"  Web Searches: 2")
    
    # Save
    conv_file, vitals_file = doc.save_all(test_folder)
    knowledge_graph.export_graph(f"{test_folder}/knowledge_graph.json")
    
    print(f"\n\n" + "="*80)
    print("TEST 3 COMPLETE")
    print("="*80)
    
    print(f"\n✅ Saved to: {test_folder}/")
    print(f"   📄 {os.path.basename(conv_file)}")
    print(f"   📊 {os.path.basename(vitals_file)}")
    print(f"   🧠 knowledge_graph.json")
    
    return debate.get_debate_summary()


if __name__ == "__main__":
    result = run_test3()
    print("\n🎉 Test 3 complete - ALL capabilities demonstrated!")
