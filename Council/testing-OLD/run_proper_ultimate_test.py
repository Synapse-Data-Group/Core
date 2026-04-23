"""
PROPER ULTIMATE INNOVATION TEST
Each test gets its own timestamped folder
Debates take real time with thinking delays
Shows the actual innovation in action
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
from whitepaper_logger import WhitepaperDocumenter
import time
from datetime import datetime


def run_proper_ultimate_test():
    # Create unique folder for this test run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_folder = f"testing/debates/ultimate_test_{timestamp}"
    os.makedirs(test_folder, exist_ok=True)
    
    print("\n" + "🚀"*40)
    print("\n  PROPER ULTIMATE INNOVATION TEST")
    print(f"  Output folder: {test_folder}")
    print("\n" + "🚀"*40 + "\n")
    
    problem = "How should we approach the development of autonomous AI systems that can make critical decisions affecting human lives?"
    
    print("🔧 Initializing innovation systems...\n")
    time.sleep(1)
    
    doc = WhitepaperDocumenter("ultimate_innovation_test")
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    coalition_mgr = CoalitionManager()
    knowledge_graph = KnowledgeGraph()
    reputation_sys = ReputationSystem()
    meta_debate = MetaDebateLayer()
    quality_metrics = ArgumentQualityMetrics()
    
    print("  ✓ Fluid Debate System")
    print("  ✓ Coalition Manager")
    print("  ✓ Knowledge Graph")
    print("  ✓ Reputation System")
    print("  ✓ Meta-Debate Layer")
    print("  ✓ Quality Metrics")
    time.sleep(1)
    
    print("\n👥 Creating initial agents...\n")
    
    agent1 = debate.create_agent("Dr_Ethics", personality={
        "creativity": 0.7,
        "boldness": 0.5,
        "aggressiveness": 0.4,
        "analytical_depth": 0.9,
        "evidence_reliance": 0.9
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    print(f"  ✓ Dr_Ethics (Analytical, Evidence-based)")
    time.sleep(0.5)
    
    agent2 = debate.create_agent("Tech_Innovator", personality={
        "creativity": 0.95,
        "boldness": 0.9,
        "aggressiveness": 0.6,
        "optimism": 0.8
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    print(f"  ✓ Tech_Innovator (Creative, Bold)")
    time.sleep(0.5)
    
    web_tool = WebResearchTool()
    debate.create_tool_for_agent(agent1.agent_id, web_tool)
    print(f"  ✓ Web Research Tool added")
    time.sleep(0.5)
    
    doc.start_debate(problem, 2)
    doc.take_snapshot(list(debate.agents.values()), [], {"phase": "initialization"})
    
    print("\n" + "="*80)
    print("DEBATE STARTING")
    print("="*80 + "\n")
    time.sleep(1)
    
    # Hook spawning
    spawn_count = [0]
    original_spawn = debate.moderator.spawn_agent
    def tracked_spawn(role, debate_sys, reason):
        print(f"\n🌊 MODERATOR SPAWNING AGENT...")
        print(f"   Role: {role}")
        print(f"   Reason: {reason}")
        time.sleep(1)
        
        agent = original_spawn(role, debate_sys, reason)
        if agent:
            spawn_count[0] += 1
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
    
    # PROPOSAL PHASE
    print("\n" + "="*80)
    print("PHASE: PROPOSALS")
    print("="*80 + "\n")
    time.sleep(0.5)
    
    doc.log_phase_start("PROPOSAL", list(debate.agents.values()), [])
    
    print("Agents are formulating their proposals...\n")
    time.sleep(2)
    
    debate._proposal_phase()
    
    for idx, proposal in enumerate(debate.proposals, 1):
        print(f"\n[{proposal.agent_name}] PROPOSES:")
        print(f"  {proposal.content}")
        print()
        time.sleep(1)
        
        doc.log_proposal(proposal.agent_name, proposal.content, {
            "proposal_id": proposal.proposal_id
        })
        
        # Extract knowledge
        knowledge_graph.process_debate_content(proposal.content, proposal.agent_id, "proposal")
        
        # Quality check
        print(f"  📊 Analyzing argument quality...")
        time.sleep(0.5)
        quality = quality_metrics.evaluate_argument(proposal.content, {})
        print(f"     Overall Quality: {quality['overall_quality']:.2f}")
        print(f"     Strengths: {', '.join(quality['strengths']) if quality['strengths'] else 'None identified'}")
        print(f"     Weaknesses: {', '.join(quality['weaknesses']) if quality['weaknesses'] else 'None identified'}")
        doc.vitals.log_event("argument_quality", {
            "agent": proposal.agent_name,
            "quality_score": quality["overall_quality"],
            "scores": quality["scores"]
        })
        time.sleep(1)
    
    doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"phase": "post_proposal"})
    
    # Check for spawning
    print("\n🔍 Moderator analyzing debate needs...")
    time.sleep(1)
    debate._assess_and_spawn_agents("post_proposal")
    
    # Coalition check
    print("\n🤝 Checking for coalition formation...")
    time.sleep(1)
    coalition_mgr.update_coalitions(list(debate.agents.values()), debate.proposals, {})
    
    if coalition_mgr.coalitions:
        for coalition in coalition_mgr.coalitions.values():
            print(f"  ✓ Coalition formed: {len(coalition.members)} members")
            doc.vitals.log_event("coalition_formed", {
                "coalition_id": coalition.coalition_id,
                "members": list(coalition.members)
            })
    else:
        print("  No coalitions formed yet")
    time.sleep(1)
    
    # Update emotions
    emotion1.process_event("proposal_accepted", 0.7, {})
    emotion2.process_event("proposal_accepted", 0.8, {})
    
    print(f"\n🎭 Emotional States:")
    print(f"  {agent1.name}: {emotion1.current_state.value} (intensity: {emotion1.emotion_intensity:.2f})")
    print(f"  {agent2.name}: {emotion2.current_state.value} (intensity: {emotion2.emotion_intensity:.2f})")
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
        
        # CHALLENGE PHASE
        print(f"--- CHALLENGE PHASE ---\n")
        time.sleep(0.5)
        
        doc.log_phase_start("CHALLENGE", list(debate.agents.values()), debate.proposals)
        
        print("Agents are analyzing proposals and formulating challenges...\n")
        time.sleep(2)
        
        debate._challenge_phase()
        
        new_challenges = []
        for proposal in debate.proposals:
            for challenge in proposal.challenges:
                # Check if this is a new challenge
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
                print(f"  {challenge.content}")
                time.sleep(1)
                
                doc.log_challenge(challenge.agent_name, proposal.agent_name, challenge.content)
                
                quality = quality_metrics.evaluate_argument(challenge.content, {})
                print(f"  📊 Challenge Quality: {quality['overall_quality']:.2f}")
                time.sleep(0.5)
        else:
            print("  No new challenges this round.")
        
        print(f"\n  Total challenges this round: {len(new_challenges)}")
        time.sleep(1)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num,
            "phase": "post_challenge"
        })
        
        # Check for spawning
        print("\n🔍 Moderator assessing if more agents needed...")
        time.sleep(1)
        debate._assess_and_spawn_agents("post_challenge")
        
        # REBUTTAL PHASE
        print(f"\n--- REBUTTAL PHASE ---\n")
        time.sleep(0.5)
        
        doc.log_phase_start("REBUTTAL", list(debate.agents.values()), debate.proposals)
        
        print("Agents are preparing rebuttals...\n")
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
                print(f"  {rebuttal.content}")
                time.sleep(1)
                
                doc.log_rebuttal(rebuttal.agent_name, target, rebuttal.content)
        else:
            print("  No new rebuttals this round.")
        
        print(f"\n  Total rebuttals this round: {len(new_rebuttals)}")
        time.sleep(1)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num,
            "phase": "post_rebuttal"
        })
        
        debate._assess_and_spawn_agents("post_rebuttal")
        
        # Update emotions
        print("\n🎭 Updating emotional states...")
        time.sleep(0.5)
        for agent in list(debate.agents.values())[:2]:  # Only track original agents
            challenges_received = sum(1 for p in debate.proposals if p.agent_id == agent.agent_id for c in p.challenges)
            if agent.agent_id == agent1.agent_id and challenges_received > 2:
                emotion1.process_event("challenged", 0.5, {"challenge_count": challenges_received})
                print(f"  {agent.name}: {emotion1.current_state.value} (intensity: {emotion1.emotion_intensity:.2f})")
            elif agent.agent_id == agent2.agent_id and challenges_received > 2:
                emotion2.process_event("challenged", 0.5, {"challenge_count": challenges_received})
                print(f"  {agent.name}: {emotion2.current_state.value} (intensity: {emotion2.emotion_intensity:.2f})")
        time.sleep(1)
        
        # Check conclusion
        print("\n🎯 Moderator evaluating if debate should conclude...")
        time.sleep(1)
        
        scores = [p.score for p in debate.proposals]
        if scores:
            score_range = max(scores) - min(scores)
            
            if round_num >= 3:
                if score_range > 20 and len(new_challenges) < 2:
                    debate_conclusive = True
                    print(f"  ✓ DEBATE CONCLUSIVE: Clear winner (score gap: {score_range:.1f})")
                elif round_num >= 10:
                    debate_conclusive = True
                    print(f"  ✓ DEBATE CONCLUSIVE: Maximum depth reached")
                else:
                    print(f"  → Continuing (score gap: {score_range:.1f}, challenges: {len(new_challenges)})")
            else:
                print(f"  → Continuing (round {round_num}/3 minimum)")
        
        print(f"  Current agents: {len(debate.agents)}")
        print(f"  Total messages: {len(debate.messages)}")
        time.sleep(1)
    
    # SCORING
    print(f"\n\n" + "="*80)
    print("SCORING PHASE")
    print("="*80 + "\n")
    time.sleep(1)
    
    print("Moderator evaluating all proposals...\n")
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
    
    # Update reputation
    for agent in debate.agents.values():
        is_winner = agent.score == max(scores.values())
        reputation_sys.update_reputation(
            agent.agent_id,
            is_winner,
            agent.score,
            len(agent.challenges_made),
            len(agent.rebuttals_made)
        )
    
    print("\n⭐ Reputation Scores:")
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
    print(f"  {debate.final_decision['reasoning']}")
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
    
    fluid_stats = debate.moderator.get_fluid_resourcing_stats()
    print(f"\n🌊 Fluid Resourcing:")
    print(f"  Agents Spawned: {fluid_stats['total_spawned']}")
    print(f"  Final Agent Count: {len(debate.agents)}")
    
    coalition_stats = coalition_mgr.get_stats()
    print(f"\n🤝 Coalitions:")
    print(f"  Total Formed: {coalition_stats['total_coalitions']}")
    
    print(f"\n📊 Debate Metrics:")
    print(f"  Rounds: {round_num}")
    print(f"  Total Messages: {len(debate.messages)}")
    print(f"  Duration: {debate.get_debate_summary()['duration_seconds']:.2f}s")
    
    # Save everything
    conv_file, vitals_file = doc.save_all(test_folder)
    knowledge_graph.export_graph(f"{test_folder}/knowledge_graph.json")
    
    print(f"\n\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    print(f"\n✅ All files saved to: {test_folder}/")
    print(f"   📄 {os.path.basename(conv_file)}")
    print(f"   📊 {os.path.basename(vitals_file)}")
    print(f"   🧠 knowledge_graph.json")
    
    return debate.get_debate_summary()


if __name__ == "__main__":
    result = run_proper_ultimate_test()
    print("\n🎉 Innovation test complete!")
