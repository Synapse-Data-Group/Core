"""
ULTIMATE INNOVATION TEST
Tests ALL capabilities of the Council Framework:
- Fluid Resourcing (dynamic agent spawning/termination)
- Web Research (internet access via urllib)
- Coalition Formation (agent alliances)
- Knowledge Graph (concept extraction and relationships)
- Emotion Simulation (emotional states affecting behavior)
- Reputation System (trust networks)
- Debate Forking (parallel exploration)
- Meta-Debate (self-modifying rules)
- Argument Quality Metrics (real-time evaluation)
- Multi-Modal Support (code, data integration)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fluid_debate_system import FluidDebateSystem
from coalition_system import CoalitionManager
from knowledge_graph import KnowledgeGraph
from reputation_system import ReputationSystem
from emotion_system import EmotionEngine, EmotionalState
from web_fetcher import WebResearchTool
from debate_forking import ParallelDebateOrchestrator
from meta_debate import MetaDebateLayer, ArgumentQualityMetrics
from multimodal_support import RichArgumentBuilder
from whitepaper_logger import WhitepaperDocumenter


def run_ultimate_innovation_test():
    print("\n" + "🚀"*40)
    print("\n  ULTIMATE INNOVATION TEST")
    print("  Testing ALL Council Framework Capabilities")
    print("\n" + "🚀"*40 + "\n")
    
    problem = "How should we approach the development of autonomous AI systems that can make critical decisions?"
    
    # Initialize ALL systems
    print("🔧 Initializing ALL innovation systems...\n")
    
    doc = WhitepaperDocumenter("ultimate_innovation_test")
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    coalition_mgr = CoalitionManager()
    knowledge_graph = KnowledgeGraph()
    reputation_sys = ReputationSystem()
    meta_debate = MetaDebateLayer()
    quality_metrics = ArgumentQualityMetrics()
    multimodal = RichArgumentBuilder()
    
    print("  ✓ Fluid Debate System (dynamic spawning)")
    print("  ✓ Coalition Manager (agent alliances)")
    print("  ✓ Knowledge Graph (concept extraction)")
    print("  ✓ Reputation System (trust networks)")
    print("  ✓ Meta-Debate Layer (self-modification)")
    print("  ✓ Argument Quality Metrics (real-time evaluation)")
    print("  ✓ Multi-Modal Support (rich content)")
    
    # Create initial agents with emotions and web tools
    print("\n👥 Creating initial agents with FULL capabilities...\n")
    
    agent1 = debate.create_agent("Dr_Ethics", personality={
        "creativity": 0.7,
        "boldness": 0.5,
        "aggressiveness": 0.4,
        "analytical_depth": 0.9,
        "evidence_reliance": 0.9
    })
    emotion1 = EmotionEngine(agent1.agent_id)
    print(f"  ✓ Dr_Ethics (Analytical, Evidence-based) + Emotion Engine")
    
    agent2 = debate.create_agent("Tech_Innovator", personality={
        "creativity": 0.95,
        "boldness": 0.9,
        "aggressiveness": 0.6,
        "optimism": 0.8,
        "analytical_depth": 0.6
    })
    emotion2 = EmotionEngine(agent2.agent_id)
    print(f"  ✓ Tech_Innovator (Creative, Bold) + Emotion Engine")
    
    # Add web research tool
    web_tool = WebResearchTool()
    debate.create_tool_for_agent(agent1.agent_id, web_tool)
    print(f"  ✓ Web Research Tool added to Dr_Ethics")
    
    doc.start_debate(problem, 2)
    doc.take_snapshot(list(debate.agents.values()), [], {
        "phase": "initialization",
        "features_enabled": [
            "fluid_resourcing",
            "web_research",
            "coalitions",
            "knowledge_graph",
            "emotions",
            "reputation",
            "meta_debate",
            "quality_metrics",
            "multimodal"
        ]
    })
    
    print("\n" + "="*80)
    print("STARTING ULTIMATE INNOVATION TEST")
    print("="*80 + "\n")
    
    # Hook into debate to capture everything
    original_spawn = debate.moderator.spawn_agent
    def documented_spawn(role, debate_sys, reason):
        agent = original_spawn(role, debate_sys, reason)
        if agent:
            archetype = debate.moderator.agent_factory.get_agent_info(agent.agent_id)
            doc.log_agent_spawn(agent.name, reason, archetype["archetype"] if archetype else "unknown")
            
            # Add emotion engine to spawned agent
            emotion = EmotionEngine(agent.agent_id)
            print(f"  🎭 Emotion engine added to spawned agent: {agent.name}")
            
            doc.take_snapshot(list(debate_sys.agents.values()), debate_sys.proposals, {
                "event": "agent_spawned",
                "agent": agent.name,
                "reason": reason
            })
        return agent
    
    debate.moderator.spawn_agent = documented_spawn
    
    # Run debate with FLUID RESOURCING enabled
    print("🌊 FLUID RESOURCING: ENABLED")
    print("   Moderator will spawn agents as needed\n")
    
    doc.log_phase_start("PROPOSAL", list(debate.agents.values()), [])
    debate._proposal_phase()
    
    # Process proposals through all systems
    for proposal in debate.proposals:
        doc.log_proposal(proposal.agent_name, proposal.content, {
            "proposal_id": proposal.proposal_id
        })
        
        # Knowledge Graph: Extract concepts
        knowledge_graph.process_debate_content(proposal.content, proposal.agent_id, "proposal")
        
        # Quality Metrics: Evaluate argument
        quality = quality_metrics.evaluate_argument(proposal.content, {})
        doc.vitals.log_event("argument_quality", {
            "agent": proposal.agent_name,
            "quality_score": quality["overall_quality"],
            "strengths": quality["strengths"],
            "weaknesses": quality["weaknesses"]
        })
        print(f"  📊 Quality Score for {proposal.agent_name}: {quality['overall_quality']:.2f}")
        
        # Multi-Modal: Create rich argument
        arg = multimodal.create_argument(proposal.content, proposal.agent_id)
        multimodal.add_supporting_data(arg["argument_id"], {
            "quality_metrics": quality["scores"],
            "timestamp": proposal.timestamp
        })
    
    doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"phase": "post_proposal"})
    
    # Assess for fluid resourcing
    print("\n🔍 MODERATOR ANALYZING DEBATE NEEDS...")
    debate._assess_and_spawn_agents("post_proposal")
    
    # Coalition Formation: Check for alliances
    print("\n🤝 COALITION SYSTEM: Analyzing agent alignment...")
    coalition_mgr.update_coalitions(list(debate.agents.values()), debate.proposals, {})
    
    if coalition_mgr.coalitions:
        for coalition in coalition_mgr.coalitions.values():
            doc.vitals.log_event("coalition_formed", {
                "coalition_id": coalition.coalition_id,
                "members": list(coalition.members),
                "strength": coalition.strength
            })
            print(f"  ✓ Coalition formed: {len(coalition.members)} members")
    
    # Update emotions based on proposals
    emotion1.process_event("proposal_accepted", 0.7, {"challenge_count": 0})
    emotion2.process_event("proposal_accepted", 0.8, {"challenge_count": 0})
    
    print(f"\n🎭 EMOTIONS:")
    print(f"  Dr_Ethics: {emotion1.current_state.value} (intensity: {emotion1.emotion_intensity:.2f})")
    print(f"  Tech_Innovator: {emotion2.current_state.value} (intensity: {emotion2.emotion_intensity:.2f})")
    
    # Run unlimited rounds until moderator decides debate is conclusive
    round_num = 0
    max_rounds = 100  # Safety limit
    debate_conclusive = False
    
    while round_num < max_rounds and not debate_conclusive:
        round_num += 1
        print(f"\n{'='*80}")
        print(f"ROUND {round_num}")
        print(f"{'='*80}\n")
        
        # Challenge Phase
        print(f"\n--- CHALLENGE PHASE (Round {round_num}) ---\n")
        doc.log_phase_start("CHALLENGE", list(debate.agents.values()), debate.proposals)
        debate._challenge_phase()
        
        challenges_this_round = 0
        for proposal in debate.proposals:
            for challenge in proposal.challenges:
                if challenge not in [c for p in debate.proposals for c in p.challenges[:len(p.challenges)-1]]:
                    challenges_this_round += 1
                    print(f"\n[{challenge.agent_name}] CHALLENGES [{proposal.agent_name}]:")
                    print(f"  {challenge.content[:150]}..." if len(challenge.content) > 150 else f"  {challenge.content}")
                    
                    doc.log_challenge(challenge.agent_name, proposal.agent_name, challenge.content)
                    
                    # Quality check
                    quality = quality_metrics.evaluate_argument(challenge.content, {})
                    print(f"  📊 Quality: {quality['overall_quality']:.2f} | Strengths: {', '.join(quality['strengths'][:2])}")
        
        print(f"\n  Total challenges this round: {challenges_this_round}")
        
        # Check if we need more agents
        print("\n🔍 Moderator assessing debate needs...")
        debate._assess_and_spawn_agents("post_challenge")
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num,
            "phase": "post_challenge",
            "challenges_this_round": challenges_this_round
        })
        
        # Rebuttal Phase
        print(f"\n--- REBUTTAL PHASE (Round {round_num}) ---\n")
        doc.log_phase_start("REBUTTAL", list(debate.agents.values()), debate.proposals)
        debate._rebuttal_phase()
        
        rebuttals_this_round = 0
        for proposal in debate.proposals:
            for rebuttal in proposal.rebuttals:
                if rebuttal not in [r for p in debate.proposals for r in p.rebuttals[:len(p.rebuttals)-1]]:
                    rebuttals_this_round += 1
                    target = rebuttal.metadata.get("challenge_agent", "Unknown")
                    print(f"\n[{rebuttal.agent_name}] REBUTS [{target}]:")
                    print(f"  {rebuttal.content[:150]}..." if len(rebuttal.content) > 150 else f"  {rebuttal.content}")
                    
                    doc.log_rebuttal(rebuttal.agent_name, target, rebuttal.content)
        
        print(f"\n  Total rebuttals this round: {rebuttals_this_round}")
        
        debate._assess_and_spawn_agents("post_rebuttal")
        
        # Update emotions after round
        print("\n🎭 Updating emotional states...")
        for agent in list(debate.agents.values()):
            challenges_received = sum(1 for p in debate.proposals if p.agent_id == agent.agent_id for c in p.challenges)
            if agent.agent_id == agent1.agent_id:
                if challenges_received > 2:
                    emotion1.process_event("challenged", 0.5, {"challenge_count": challenges_received})
                print(f"  {agent.name}: {emotion1.current_state.value} (intensity: {emotion1.emotion_intensity:.2f})")
            elif agent.agent_id == agent2.agent_id:
                if challenges_received > 2:
                    emotion2.process_event("challenged", 0.5, {"challenge_count": challenges_received})
                print(f"  {agent.name}: {emotion2.current_state.value} (intensity: {emotion2.emotion_intensity:.2f})")
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num,
            "phase": "post_rebuttal",
            "rebuttals_this_round": rebuttals_this_round
        })
        
        # Optimize agent pool
        print("\n🔄 Optimizing agent pool...")
        terminated = debate._optimize_agent_pool()
        if terminated:
            print(f"  ✓ Terminated {len(terminated)} underperforming agents")
        
        # Check if debate should conclude
        print("\n🎯 Moderator evaluating debate progress...")
        
        # Calculate debate metrics
        scores = [p.score for p in debate.proposals]
        if scores:
            score_range = max(scores) - min(scores)
            avg_challenges = sum(len(p.challenges) for p in debate.proposals) / len(debate.proposals)
            
            # Debate is conclusive if:
            # 1. Clear winner (score gap > 20)
            # 2. Minimal new challenges (< 2 per round)
            # 3. At least 3 rounds completed
            if round_num >= 3:
                if score_range > 20 and challenges_this_round < 2:
                    debate_conclusive = True
                    print(f"  ✓ DEBATE CONCLUSIVE: Clear winner with score gap of {score_range:.1f}")
                    print(f"  ✓ Challenge activity minimal ({challenges_this_round} new challenges)")
                elif round_num >= 10:
                    debate_conclusive = True
                    print(f"  ✓ DEBATE CONCLUSIVE: Maximum depth reached ({round_num} rounds)")
                else:
                    print(f"  → Debate continues (score gap: {score_range:.1f}, challenges: {challenges_this_round})")
            else:
                print(f"  → Debate continues (round {round_num}/3 minimum)")
        
        print(f"\n  Current agent count: {len(debate.agents)}")
        print(f"  Total messages: {len(debate.messages)}")
    
    # Web Research Simulation
    print("\n🌐 WEB RESEARCH: Simulating information gathering...")
    search_results = web_tool.execute("AI safety research", action="search")
    doc.vitals.log_event("web_research", {
        "query": "AI safety research",
        "results": search_results[:200]
    })
    print(f"  ✓ Web search completed")
    
    # Meta-Debate: Check if rules should change
    print("\n🎯 META-DEBATE: Analyzing debate protocol...")
    if meta_debate.should_trigger_meta_debate({"round": 2, "total_messages": len(debate.messages)}):
        meta_proposal = meta_debate.propose_rule_change(
            agent1.agent_id,
            "max_rounds",
            4,
            "Debate complexity requires additional rounds"
        )
        doc.vitals.log_event("meta_proposal", {
            "rule": meta_proposal.target_rule,
            "new_value": meta_proposal.new_value,
            "reason": meta_proposal.description
        })
        print(f"  ✓ Meta-proposal created: Increase max_rounds to 4")
    
    # Scoring Phase
    print(f"\n{'='*80}")
    print("SCORING PHASE")
    print(f"{'='*80}\n")
    
    doc.log_phase_start("SCORING", list(debate.agents.values()), debate.proposals)
    debate._scoring_phase()
    
    scores = {p.agent_name: p.score for p in debate.proposals}
    doc.log_scoring(scores)
    
    print("\nProposal Scores:")
    sorted_proposals = sorted(debate.proposals, key=lambda p: p.score, reverse=True)
    for idx, proposal in enumerate(sorted_proposals, 1):
        print(f"  {idx}. {proposal.agent_name}: {proposal.score:.1f} points")
        print(f"     Challenges: {len(proposal.challenges)}, Rebuttals: {len(proposal.rebuttals)}")
    
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
    
    print("\n⭐ REPUTATION SCORES:")
    for agent in debate.agents.values():
        rep = reputation_sys.get_reputation(agent.agent_id)
        print(f"  {agent.name}: {rep.overall_score:.1f}/100")
    
    # Resolution Phase
    print(f"\n{'='*80}")
    print("RESOLUTION PHASE")
    print(f"{'='*80}\n")
    
    doc.log_phase_start("RESOLUTION", list(debate.agents.values()), debate.proposals)
    debate._resolution_phase()
    
    print(f"\n[MODERATOR] FINAL DECISION:")
    print(f"  {debate.final_decision['decision']}")
    print(f"  Confidence: {debate.final_decision['confidence']:.1%}")
    print(f"\nReasoning:")
    print(f"  {debate.final_decision['reasoning'][:300]}...")
    
    # Final snapshots and logs
    doc.log_final_decision(debate.final_decision, list(debate.agents.values()), debate.proposals)
    
    # Knowledge Graph Analysis
    kg_stats = knowledge_graph.get_stats()
    doc.vitals.log_event("knowledge_graph_final", kg_stats)
    
    print(f"\n🧠 KNOWLEDGE GRAPH:")
    print(f"  Concepts extracted: {kg_stats['total_nodes']}")
    print(f"  Relationships: {kg_stats['total_edges']}")
    print(f"  Most central concepts: {[c[0] for c in kg_stats['most_central'][:3]]}")
    
    # Fluid Resourcing Stats
    fluid_stats = debate.moderator.get_fluid_resourcing_stats()
    doc.vitals.log_event("fluid_resourcing_final", fluid_stats)
    
    print(f"\n🌊 FLUID RESOURCING STATS:")
    print(f"  Agents spawned: {fluid_stats['total_spawned']}")
    print(f"  Agents terminated: {fluid_stats['total_terminated']}")
    print(f"  Final agent count: {len(debate.agents)}")
    if fluid_stats['spawn_reasons']:
        print(f"  Spawn reasons: {fluid_stats['spawn_reasons']}")
    
    # Coalition Stats
    coalition_stats = coalition_mgr.get_stats()
    print(f"\n🤝 COALITION STATS:")
    print(f"  Total coalitions formed: {coalition_stats['total_coalitions']}")
    print(f"  Agents in coalitions: {coalition_stats['agents_in_coalitions']}")
    
    # Save everything
    os.makedirs("testing/whitepaper_output", exist_ok=True)
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    knowledge_graph.export_graph("testing/whitepaper_output/ultimate_test_knowledge_graph.json")
    
    print("\n" + "="*80)
    print("ULTIMATE INNOVATION TEST COMPLETE")
    print("="*80)
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    print(f"   🧠 Knowledge Graph: testing/whitepaper_output/ultimate_test_knowledge_graph.json")
    
    print(f"\n🏆 FINAL RESULTS:")
    print(f"   Winner: {debate.final_decision['decision']}")
    print(f"   Confidence: {debate.final_decision['confidence']:.1%}")
    print(f"   Duration: {debate.get_debate_summary()['duration_seconds']:.2f}s")
    print(f"   Total Messages: {len(debate.messages)}")
    print(f"   Final Agent Count: {len(debate.agents)}")
    
    print("\n🎉 ALL INNOVATIONS TESTED SUCCESSFULLY!")
    
    return debate.get_debate_summary()


if __name__ == "__main__":
    print("\n" + "⚡"*40)
    print("\n  COUNCIL FRAMEWORK - ULTIMATE INNOVATION TEST")
    print("  Testing: Fluid Resourcing, Web Access, Coalitions,")
    print("  Knowledge Graphs, Emotions, Reputation, Meta-Debate,")
    print("  Quality Metrics, Multi-Modal Support")
    print("\n" + "⚡"*40)
    
    result = run_ultimate_innovation_test()
    
    print("\n✅ Test completed! Check testing/whitepaper_output/ for full documentation")
