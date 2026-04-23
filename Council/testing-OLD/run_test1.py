"""
Run Test 1: Basic Three-Agent Debate with Full Documentation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentient_debate_system import SentientDebateSystem
from whitepaper_logger import WhitepaperDocumenter


def run_test1():
    print("\n" + "="*80)
    print("TEST 1: BASIC THREE-AGENT DEBATE (DOCUMENTED)")
    print("="*80 + "\n")
    
    problem = "Should companies implement a 4-day work week?"
    doc = WhitepaperDocumenter("test1_basic_debate")
    
    print(f"Problem: {problem}\n")
    print("Creating debate system...")
    
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    print("Creating agents with distinct personalities...\n")
    
    alice = debate.create_agent("Alice_Optimist", personality={
        "creativity": 0.8, "boldness": 0.7, "aggressiveness": 0.4,
        "optimism": 0.9, "analytical_depth": 0.6
    })
    print("  ✓ Alice (Optimistic, Creative)")
    
    bob = debate.create_agent("Bob_Skeptic", personality={
        "creativity": 0.4, "boldness": 0.6, "aggressiveness": 0.8,
        "optimism": 0.2, "analytical_depth": 0.9
    })
    print("  ✓ Bob (Skeptical, Analytical)")
    
    carol = debate.create_agent("Carol_Balanced", personality={
        "creativity": 0.6, "boldness": 0.5, "aggressiveness": 0.5,
        "optimism": 0.5, "analytical_depth": 0.7
    })
    print("  ✓ Carol (Balanced, Pragmatic)")
    
    doc.start_debate(problem, 3)
    doc.take_snapshot(list(debate.agents.values()), [], {"phase": "initialization"})
    
    print("\n🚀 Running debate with full documentation...\n")
    print("="*80)
    
    # Proposal Phase
    doc.log_phase_start("PROPOSAL", list(debate.agents.values()), [])
    debate._proposal_phase()
    
    for proposal in debate.proposals:
        doc.log_proposal(proposal.agent_name, proposal.content, {
            "proposal_id": proposal.proposal_id,
            "timestamp": proposal.timestamp
        })
    
    doc.take_snapshot(list(debate.agents.values()), debate.proposals, {"phase": "post_proposal"})
    
    # 2 Rounds of Challenge/Rebuttal
    for round_num in range(2):
        print(f"\n--- Round {round_num + 1} ---\n")
        
        # Challenge Phase
        doc.log_phase_start("CHALLENGE", list(debate.agents.values()), debate.proposals)
        debate._challenge_phase()
        
        for proposal in debate.proposals:
            for challenge in proposal.challenges:
                doc.log_challenge(challenge.agent_name, proposal.agent_name, challenge.content)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num + 1, 
            "phase": "post_challenge"
        })
        
        # Rebuttal Phase
        doc.log_phase_start("REBUTTAL", list(debate.agents.values()), debate.proposals)
        debate._rebuttal_phase()
        
        for proposal in debate.proposals:
            for rebuttal in proposal.rebuttals:
                target = rebuttal.metadata.get("challenge_agent", "Unknown")
                doc.log_rebuttal(rebuttal.agent_name, target, rebuttal.content)
        
        doc.take_snapshot(list(debate.agents.values()), debate.proposals, {
            "round": round_num + 1, 
            "phase": "post_rebuttal"
        })
    
    # Scoring Phase
    doc.log_phase_start("SCORING", list(debate.agents.values()), debate.proposals)
    debate._scoring_phase()
    
    scores = {p.agent_name: p.score for p in debate.proposals}
    doc.log_scoring(scores)
    
    # Resolution Phase
    doc.log_phase_start("RESOLUTION", list(debate.agents.values()), debate.proposals)
    debate._resolution_phase()
    
    doc.log_final_decision(debate.final_decision, list(debate.agents.values()), debate.proposals)
    
    # Save documentation
    os.makedirs("testing/whitepaper_output", exist_ok=True)
    conv_file, vitals_file = doc.save_all("testing/whitepaper_output")
    
    print("\n" + "="*80)
    print("TEST 1 COMPLETE")
    print("="*80)
    
    print(f"\n✅ Documentation saved:")
    print(f"   📄 Conversation: {conv_file}")
    print(f"   📊 Vitals: {vitals_file}")
    
    print(f"\n🏆 Winner: {debate.final_decision['decision']}")
    print(f"📊 Confidence: {debate.final_decision['confidence']:.1%}")
    print(f"⏱️  Duration: {debate.get_debate_summary()['duration_seconds']:.2f}s")
    
    print("\n📈 Agent Performance:")
    for agent in debate.agents.values():
        print(f"  {agent.name}: {agent.score:.1f} points")
    
    return debate.get_debate_summary()


if __name__ == "__main__":
    print("\n🚀 Starting Test 1...")
    result = run_test1()
    print("\n✅ Test 1 completed successfully!")
