import uuid
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from sentient_agent import SentientAgent
from fluid_moderator import FluidModerator
from sentient_debate_system import DebatePhase, Message, Proposal, Tool


class FluidDebateSystem:
    """
    Advanced debate system with fluid resourcing.
    Moderator can dynamically spawn and terminate agents during debates.
    """
    
    def __init__(self, problem: str, moderator_strategy: str = "adaptive"):
        self.system_id = str(uuid.uuid4())
        self.problem = problem
        self.agents: Dict[str, SentientAgent] = {}
        self.moderator = FluidModerator(str(uuid.uuid4()), "Fluid Moderator", moderator_strategy)
        self.current_phase = DebatePhase.PROPOSAL
        self.proposals: List[Proposal] = []
        self.messages: List[Message] = []
        self.debate_log: List[str] = []
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.final_decision: Optional[Dict[str, Any]] = None
        self.round_number = 0
        
        self.fluid_events: List[Dict[str, Any]] = []
        
    def create_agent(self, name: str, personality: Optional[Dict[str, float]] = None, 
                     memory_path: Optional[str] = None) -> SentientAgent:
        agent_id = str(uuid.uuid4())
        agent = SentientAgent(agent_id, name, personality, memory_path)
        self.agents[agent_id] = agent
        self.log(f"Agent created: {name} (ID: {agent_id})")
        return agent
    
    def kill_agent(self, agent_id: str):
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.deactivate()
            self.log(f"Agent terminated: {agent.name} (ID: {agent_id})")
            del self.agents[agent_id]
    
    def create_tool_for_agent(self, agent_id: str, tool: Tool):
        if agent_id in self.agents:
            self.agents[agent_id].add_tool(tool)
            self.log(f"Tool '{tool.name}' added to agent {self.agents[agent_id].name}")
    
    def remove_tool_from_agent(self, agent_id: str, tool_id: str):
        if agent_id in self.agents:
            self.agents[agent_id].remove_tool(tool_id)
            self.log(f"Tool removed from agent {self.agents[agent_id].name}")
    
    def log(self, message: str):
        timestamp = time.time() - self.start_time
        log_entry = f"[{timestamp:.2f}s] {message}"
        self.debate_log.append(log_entry)
        print(log_entry)
    
    def run_debate(self, max_rounds: int = 3, enable_fluid_resourcing: bool = True) -> Dict[str, Any]:
        self.log(f"\n{'='*80}")
        self.log(f"FLUID DEBATE SYSTEM INITIATED")
        self.log(f"Problem: {self.problem}")
        self.log(f"Moderator: {self.moderator.name} (Strategy: {self.moderator.strategy})")
        self.log(f"Initial Agents: {len(self.agents)}")
        self.log(f"Fluid Resourcing: {'ENABLED' if enable_fluid_resourcing else 'DISABLED'}")
        self.log(f"{'='*80}\n")
        
        self._proposal_phase()
        
        if enable_fluid_resourcing:
            self._assess_and_spawn_agents("post_proposal")
        
        for round_num in range(max_rounds):
            self.round_number = round_num + 1
            self.log(f"\n{'='*60}")
            self.log(f"ROUND {self.round_number}")
            self.log(f"{'='*60}")
            
            self._challenge_phase()
            
            if enable_fluid_resourcing:
                self._assess_and_spawn_agents("post_challenge")
            
            self._rebuttal_phase()
            
            if enable_fluid_resourcing:
                self._assess_and_spawn_agents("post_rebuttal")
                self._optimize_agent_pool()
        
        self._scoring_phase()
        self._resolution_phase()
        self._learning_phase()
        
        self.end_time = time.time()
        
        return self.get_debate_summary()
    
    def _assess_and_spawn_agents(self, phase: str):
        """Assess debate needs and spawn agents if necessary"""
        
        context = {
            "phase": phase,
            "problem": self.problem,
            "round": self.round_number,
            "timestamp": time.time()
        }
        
        needs = self.moderator.analyze_debate_needs(
            self.proposals,
            list(self.agents.values()),
            context
        )
        
        if needs["needs_agent"]:
            self.log(f"\n[{self.moderator.name}] FLUID RESOURCING TRIGGERED:")
            self.log(f"  Reason: {needs['reason']}")
            self.log(f"  Urgency: {needs['urgency']:.2f}")
            self.log(f"  Analysis: {needs['analysis']}")
            
            new_agent = self.moderator.spawn_agent(
                needs["role"],
                self,
                needs["reason"]
            )
            
            if new_agent:
                self.fluid_events.append({
                    "type": "spawn",
                    "phase": phase,
                    "round": self.round_number,
                    "agent_id": new_agent.agent_id,
                    "agent_name": new_agent.name,
                    "reason": needs["reason"],
                    "urgency": needs["urgency"],
                    "timestamp": time.time()
                })
                
                if phase == "post_proposal":
                    self._generate_late_proposal(new_agent)
                elif phase == "post_challenge":
                    self._generate_late_challenges(new_agent)
    
    def _generate_late_proposal(self, agent: SentientAgent):
        """Generate a proposal from a newly spawned agent"""
        
        context = {
            "phase": "proposal",
            "problem": self.problem,
            "proposal_count": len(self.proposals),
            "challenge_count": 0,
            "my_score": 0,
            "timestamp": time.time()
        }
        
        proposal_content = agent.propose_solution(self.problem, context)
        
        proposal = Proposal(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            content=proposal_content,
            timestamp=time.time()
        )
        
        self.proposals.append(proposal)
        agent.proposals_made.append(proposal.proposal_id)
        
        message = Message(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            content=proposal_content,
            message_type="proposal",
            timestamp=time.time(),
            phase=DebatePhase.PROPOSAL,
            metadata={"proposal_id": proposal.proposal_id, "late_entry": True}
        )
        
        self.messages.append(message)
        agent.message_history.append(message)
        
        self.log(f"\n[{agent.name}] LATE PROPOSAL:")
        self.log(f"  {proposal_content[:200]}{'...' if len(proposal_content) > 200 else ''}")
    
    def _generate_late_challenges(self, agent: SentientAgent):
        """Generate challenges from a newly spawned agent"""
        
        context = {
            "phase": "challenge",
            "problem": self.problem,
            "proposal_count": len(self.proposals),
            "round": self.round_number,
            "timestamp": time.time()
        }
        
        for proposal in self.proposals:
            context["my_score"] = agent.score
            context["challenge_count"] = len(proposal.challenges)
            
            challenge_content = agent.challenge_proposal(proposal, self.proposals, context)
            
            if challenge_content:
                message = Message(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    content=challenge_content,
                    message_type="challenge",
                    timestamp=time.time(),
                    phase=DebatePhase.CHALLENGE,
                    target_agent_id=proposal.agent_id,
                    metadata={"proposal_id": proposal.proposal_id, "late_entry": True}
                )
                
                proposal.challenges.append(message)
                self.messages.append(message)
                agent.message_history.append(message)
                agent.challenges_made.append(proposal.proposal_id)
                
                self.log(f"\n[{agent.name}] LATE CHALLENGE [{proposal.agent_name}]:")
                self.log(f"  {challenge_content[:200]}{'...' if len(challenge_content) > 200 else ''}")
    
    def _optimize_agent_pool(self):
        """Optimize agent pool by removing underperforming agents"""
        
        terminated = self.moderator.optimize_agent_pool(self, self.proposals)
        
        if terminated:
            for agent_id in terminated:
                self.fluid_events.append({
                    "type": "terminate",
                    "phase": "optimization",
                    "round": self.round_number,
                    "agent_id": agent_id,
                    "reason": "underperformance",
                    "timestamp": time.time()
                })
    
    def _proposal_phase(self):
        self.current_phase = DebatePhase.PROPOSAL
        self.log(f"\n=== PROPOSAL PHASE ===")
        
        context = {
            "phase": "proposal",
            "problem": self.problem,
            "proposal_count": 0,
            "challenge_count": 0,
            "my_score": 0,
            "timestamp": time.time()
        }
        
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            
            proposal_content = agent.propose_solution(self.problem, context)
            
            proposal = Proposal(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                content=proposal_content,
                timestamp=time.time()
            )
            
            self.proposals.append(proposal)
            agent.proposals_made.append(proposal.proposal_id)
            
            message = Message(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                content=proposal_content,
                message_type="proposal",
                timestamp=time.time(),
                phase=self.current_phase,
                metadata={"proposal_id": proposal.proposal_id}
            )
            
            self.messages.append(message)
            agent.message_history.append(message)
            
            self.log(f"\n[{agent.name}] PROPOSES:")
            self.log(f"  {proposal_content[:200]}{'...' if len(proposal_content) > 200 else ''}")
            
            context["proposal_count"] += 1
    
    def _challenge_phase(self):
        self.current_phase = DebatePhase.CHALLENGE
        self.log(f"\n=== CHALLENGE PHASE ===")
        
        challenges_made = False
        
        context = {
            "phase": "challenge",
            "problem": self.problem,
            "proposal_count": len(self.proposals),
            "round": self.round_number,
            "timestamp": time.time()
        }
        
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            
            for proposal in self.proposals:
                context["my_score"] = agent.score
                context["challenge_count"] = len(proposal.challenges)
                
                challenge_content = agent.challenge_proposal(proposal, self.proposals, context)
                
                if challenge_content:
                    challenges_made = True
                    
                    message = Message(
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        content=challenge_content,
                        message_type="challenge",
                        timestamp=time.time(),
                        phase=self.current_phase,
                        target_agent_id=proposal.agent_id,
                        metadata={"proposal_id": proposal.proposal_id}
                    )
                    
                    proposal.challenges.append(message)
                    self.messages.append(message)
                    agent.message_history.append(message)
                    agent.challenges_made.append(proposal.proposal_id)
                    
                    self.log(f"\n[{agent.name}] CHALLENGES [{proposal.agent_name}]:")
                    self.log(f"  {challenge_content[:200]}{'...' if len(challenge_content) > 200 else ''}")
        
        if not challenges_made:
            self.log("  No challenges raised this round.")
    
    def _rebuttal_phase(self):
        self.current_phase = DebatePhase.REBUTTAL
        self.log(f"\n=== REBUTTAL PHASE ===")
        
        rebuttals_made = False
        
        context = {
            "phase": "rebuttal",
            "problem": self.problem,
            "proposal_count": len(self.proposals),
            "round": self.round_number,
            "timestamp": time.time()
        }
        
        for proposal in self.proposals:
            if not proposal.challenges:
                continue
            
            agent = self.agents.get(proposal.agent_id)
            if not agent or not agent.is_active:
                continue
            
            context["my_score"] = agent.score
            context["challenge_count"] = len(proposal.challenges)
            
            for challenge in proposal.challenges:
                rebutted = any(r.metadata.get("challenge_agent") == challenge.agent_name 
                             for r in proposal.rebuttals)
                if rebutted:
                    continue
                
                rebuttal_content = agent.rebut_challenge(challenge, proposal, context)
                
                if rebuttal_content:
                    rebuttals_made = True
                    
                    message = Message(
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        content=rebuttal_content,
                        message_type="rebuttal",
                        timestamp=time.time(),
                        phase=self.current_phase,
                        target_agent_id=challenge.agent_id,
                        metadata={
                            "proposal_id": proposal.proposal_id,
                            "challenge_agent": challenge.agent_name
                        }
                    )
                    
                    proposal.rebuttals.append(message)
                    self.messages.append(message)
                    agent.message_history.append(message)
                    agent.rebuttals_made.append(proposal.proposal_id)
                    
                    self.log(f"\n[{agent.name}] REBUTS [{challenge.agent_name}]:")
                    self.log(f"  {rebuttal_content[:200]}{'...' if len(rebuttal_content) > 200 else ''}")
        
        if not rebuttals_made:
            self.log("  No rebuttals provided this round.")
    
    def _scoring_phase(self):
        self.current_phase = DebatePhase.SCORING
        self.log(f"\n=== SCORING PHASE ===")
        
        context = {
            "phase": "scoring",
            "problem": self.problem,
            "total_proposals": len(self.proposals),
            "total_messages": len(self.messages),
            "timestamp": time.time()
        }
        
        scores = self.moderator.score_all_proposals(self.proposals, context)
        
        self.log("\nProposal Scores (Adaptive Evaluation):")
        sorted_proposals = sorted(self.proposals, key=lambda p: p.score, reverse=True)
        for idx, proposal in enumerate(sorted_proposals, 1):
            self.log(f"  {idx}. [{proposal.agent_name}]: {proposal.score:.1f} points")
            self.log(f"     Challenges: {len(proposal.challenges)}, Rebuttals: {len(proposal.rebuttals)}")
            
            agent = self.agents.get(proposal.agent_id)
            if agent:
                agent.score = proposal.score
    
    def _resolution_phase(self):
        self.current_phase = DebatePhase.RESOLUTION
        self.log(f"\n=== RESOLUTION PHASE ===")
        
        context = {
            "phase": "resolution",
            "problem": self.problem,
            "timestamp": time.time()
        }
        
        decision = self.moderator.resolve_debate(self.proposals, list(self.agents.values()), context)
        self.final_decision = decision
        
        self.log(f"\n[{self.moderator.name}] FINAL DECISION:")
        self.log(f"  {decision['decision']}")
        self.log(f"  Confidence: {decision['confidence']:.1%}")
        self.log(f"\nReasoning:")
        self.log(f"  {decision['reasoning']}")
        
        enactment = self.moderator.enact_decision(decision)
        self.log(f"\n{enactment}")
        
        self.current_phase = DebatePhase.COMPLETED
    
    def _learning_phase(self):
        self.log(f"\n=== LEARNING PHASE ===")
        
        if not self.final_decision or not self.final_decision.get("winning_proposal"):
            return
        
        winning_agent_id = self.final_decision["winning_proposal"]["agent_id"]
        
        for agent in self.agents.values():
            is_winner = (agent.agent_id == winning_agent_id)
            agent.update_score(agent.score, is_winner)
            
            if is_winner:
                self.log(f"[{agent.name}] WINS - Learning from success (score: {agent.score:.1f})")
            else:
                self.log(f"[{agent.name}] Learning from outcome (score: {agent.score:.1f})")
            
            insights = agent.get_learning_insights()
            self.log(f"  Exploration rate: {insights['exploration_rate']:.3f}")
            self.log(f"  Learned strategies: {insights['total_learned_strategies']}")
        
        outcome_quality = self.final_decision["confidence"]
        self.moderator.learn_from_debate_outcome(self.final_decision, outcome_quality)
        
        self.log(f"\n[{self.moderator.name}] Moderator learning complete")
        
        fluid_stats = self.moderator.get_fluid_resourcing_stats()
        self.log(f"\n=== FLUID RESOURCING STATISTICS ===")
        self.log(f"  Agents Spawned: {fluid_stats['total_spawned']}")
        self.log(f"  Agents Terminated: {fluid_stats['total_terminated']}")
        self.log(f"  Currently Active (Spawned): {fluid_stats['currently_active_spawned']}")
        if fluid_stats['spawn_reasons']:
            self.log(f"  Spawn Reasons: {fluid_stats['spawn_reasons']}")
    
    def get_debate_summary(self) -> Dict[str, Any]:
        duration = (self.end_time or time.time()) - self.start_time
        
        return {
            "system_id": self.system_id,
            "problem": self.problem,
            "duration_seconds": duration,
            "total_agents": len(self.agents),
            "total_proposals": len(self.proposals),
            "total_messages": len(self.messages),
            "rounds_completed": self.round_number,
            "final_decision": self.final_decision,
            "agent_stats": [agent.get_stats() for agent in self.agents.values()],
            "moderator_stats": self.moderator.get_stats(),
            "fluid_resourcing_stats": self.moderator.get_fluid_resourcing_stats(),
            "fluid_events": self.fluid_events,
            "proposals": [p.to_dict() for p in self.proposals],
            "debate_log": self.debate_log,
            "learning_insights": {
                agent.name: agent.get_learning_insights() 
                for agent in self.agents.values()
            }
        }
    
    def export_debate(self, filepath: str):
        summary = self.get_debate_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        self.log(f"\nDebate exported to: {filepath}")
    
    def save_agent_memories(self, directory: str = "."):
        import os
        os.makedirs(directory, exist_ok=True)
        
        for agent in self.agents.values():
            filepath = os.path.join(directory, f"agent_{agent.agent_id}_memory.pkl")
            agent.save_memory(filepath)
            self.log(f"Saved memory for {agent.name} to {filepath}")
        
        moderator_path = os.path.join(directory, "moderator_memory.pkl")
        self.moderator.save_memory(moderator_path)
        self.log(f"Saved moderator memory to {moderator_path}")
