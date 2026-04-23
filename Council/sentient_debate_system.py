import uuid
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from sentient_agent import SentientAgent
from sentient_moderator import SentientModerator


class DebatePhase(Enum):
    PROPOSAL = "proposal"
    CHALLENGE = "challenge"
    REBUTTAL = "rebuttal"
    SCORING = "scoring"
    RESOLUTION = "resolution"
    COMPLETED = "completed"


@dataclass
class Message:
    agent_id: str
    agent_name: str
    content: str
    message_type: str
    timestamp: float
    phase: DebatePhase
    target_agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "phase": self.phase.value,
            "target_agent_id": self.target_agent_id,
            "metadata": self.metadata
        }


@dataclass
class Proposal:
    agent_id: str
    agent_name: str
    content: str
    timestamp: float
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    score: float = 0.0
    challenges: List[Message] = field(default_factory=list)
    rebuttals: List[Message] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": self.content,
            "timestamp": self.timestamp,
            "score": self.score,
            "challenges": [c.to_dict() for c in self.challenges],
            "rebuttals": [r.to_dict() for r in self.rebuttals]
        }


class Tool:
    def __init__(self, tool_id: str, name: str):
        self.tool_id = tool_id
        self.name = name
        self.created_at = time.time()
        self.is_active = True
    
    def execute(self, *args, **kwargs) -> Any:
        return None
    
    def deactivate(self):
        self.is_active = False


class SentientDebateSystem:
    def __init__(self, problem: str, moderator_strategy: str = "adaptive"):
        self.system_id = str(uuid.uuid4())
        self.problem = problem
        self.agents: Dict[str, SentientAgent] = {}
        self.moderator = SentientModerator(str(uuid.uuid4()), "Adaptive Moderator", moderator_strategy)
        self.current_phase = DebatePhase.PROPOSAL
        self.proposals: List[Proposal] = []
        self.messages: List[Message] = []
        self.debate_log: List[str] = []
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.final_decision: Optional[Dict[str, Any]] = None
        self.round_number = 0
        
    def create_agent(self, name: str, personality: Optional[Dict[str, float]] = None, 
                     memory_path: Optional[str] = None) -> SentientAgent:
        agent_id = str(uuid.uuid4())
        agent = SentientAgent(agent_id, name, personality, memory_path)
        self.agents[agent_id] = agent
        self.log(f"Sentient agent created: {name} (ID: {agent_id})")
        self.log(f"  Initial personality: creativity={agent.personality.get('creativity', 0):.2f}, "
                f"boldness={agent.personality.get('boldness', 0):.2f}, "
                f"aggressiveness={agent.personality.get('aggressiveness', 0):.2f}")
        return agent
    
    def kill_agent(self, agent_id: str):
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.deactivate()
            self.log(f"Agent terminated: {agent.name} (ID: {agent_id})")
            self.log(f"  Final stats: {agent.wins}W-{agent.losses}L, "
                    f"avg_score={agent.lifetime_score / max(agent.debates_participated, 1):.1f}")
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
    
    def run_debate(self, max_rounds: int = 3) -> Dict[str, Any]:
        self.log(f"\n{'='*80}")
        self.log(f"SENTIENT DEBATE SYSTEM INITIATED")
        self.log(f"Problem: {self.problem}")
        self.log(f"Moderator: {self.moderator.name} (Strategy: {self.moderator.strategy})")
        self.log(f"Active Agents: {len(self.agents)}")
        self.log(f"{'='*80}\n")
        
        self._proposal_phase()
        
        for round_num in range(max_rounds):
            self.round_number = round_num + 1
            self.log(f"\n{'='*60}")
            self.log(f"ROUND {self.round_number}")
            self.log(f"{'='*60}")
            self._challenge_phase()
            self._rebuttal_phase()
        
        self._scoring_phase()
        self._resolution_phase()
        
        self._learning_phase()
        
        self.end_time = time.time()
        
        return self.get_debate_summary()
    
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
            "challenge_count": 0,
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
            if insights['recent_performance']:
                avg_recent = sum(insights['recent_performance']) / len(insights['recent_performance'])
                self.log(f"  Recent performance trend: {avg_recent:.2%}")
        
        outcome_quality = self.final_decision["confidence"]
        self.moderator.learn_from_debate_outcome(self.final_decision, outcome_quality)
        
        self.log(f"\n[{self.moderator.name}] Moderator learning complete")
        self.log(f"  Debates moderated: {self.moderator.debates_moderated}")
        self.log(f"  Exploration rate: {self.moderator.q_learning.exploration_rate:.3f}")
    
    def evolve_agents(self):
        self.log(f"\n=== GENETIC EVOLUTION PHASE ===")
        
        if len(self.agents) < 2:
            self.log("Not enough agents for evolution")
            return
        
        agents_list = list(self.agents.values())
        agents_data = []
        
        for agent in agents_list:
            fitness = agent.score / 100.0 if agent.debates_participated > 0 else 0.5
            agents_data.append({
                "agent": agent,
                "personality": agent.personality,
                "fitness": fitness
            })
        
        evolved_population = agents_list[0].genetic_evolution.evolve_population(agents_data)
        
        for agent, evolved_data in zip(agents_list, evolved_population):
            old_personality = agent.personality.copy()
            agent.personality = evolved_data["personality"]
            
            self.log(f"[{agent.name}] Personality evolved:")
            for trait in ["creativity", "boldness", "aggressiveness"]:
                old_val = old_personality.get(trait, 0.5)
                new_val = agent.personality.get(trait, 0.5)
                change = new_val - old_val
                self.log(f"  {trait}: {old_val:.2f} -> {new_val:.2f} ({change:+.2f})")
    
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
