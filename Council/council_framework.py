import uuid
import time
import json
import random
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from learning_engine import ExperienceMemory, QLearningEngine, GeneticEvolution, ArgumentGenerator


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


class Tool(ABC):
    def __init__(self, tool_id: str, name: str):
        self.tool_id = tool_id
        self.name = name
        self.created_at = time.time()
        self.is_active = True
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass
    
    def deactivate(self):
        self.is_active = False


class Agent:
    def __init__(self, agent_id: str, name: str, personality: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality or {}
        self.is_active = True
        self.created_at = time.time()
        self.tools: Dict[str, Tool] = {}
        self.message_history: List[Message] = []
        self.proposals_made: List[str] = []
        self.challenges_made: List[str] = []
        self.rebuttals_made: List[str] = []
        self.score = 0.0
        
    def add_tool(self, tool: Tool):
        self.tools[tool.tool_id] = tool
    
    def remove_tool(self, tool_id: str):
        if tool_id in self.tools:
            self.tools[tool_id].deactivate()
            del self.tools[tool_id]
    
    def use_tool(self, tool_id: str, *args, **kwargs) -> Any:
        if tool_id in self.tools and self.tools[tool_id].is_active:
            return self.tools[tool_id].execute(*args, **kwargs)
        return None
    
    def propose_solution(self, problem: str, context: Dict[str, Any]) -> str:
        bias = self.personality.get("bias", "balanced")
        creativity = self.personality.get("creativity", 0.5)
        
        if bias == "optimistic":
            proposal = f"I propose an ambitious solution to '{problem}': "
            proposal += self._generate_optimistic_solution(problem, creativity)
        elif bias == "pessimistic":
            proposal = f"I propose a cautious approach to '{problem}': "
            proposal += self._generate_cautious_solution(problem, creativity)
        elif bias == "analytical":
            proposal = f"After analyzing '{problem}', I propose: "
            proposal += self._generate_analytical_solution(problem, creativity)
        else:
            proposal = f"My solution to '{problem}' is: "
            proposal += self._generate_balanced_solution(problem, creativity)
        
        return proposal
    
    def _generate_optimistic_solution(self, problem: str, creativity: float) -> str:
        solutions = [
            f"Implement a comprehensive strategy that addresses all aspects of {problem} with maximum resource allocation.",
            f"Deploy an innovative approach that leverages cutting-edge methods to solve {problem} completely.",
            f"Create a bold initiative that transforms {problem} into an opportunity for growth and advancement."
        ]
        idx = int(creativity * len(solutions)) % len(solutions)
        return solutions[idx]
    
    def _generate_cautious_solution(self, problem: str, creativity: float) -> str:
        solutions = [
            f"Start with a minimal viable approach to {problem}, testing incrementally before scaling.",
            f"Implement conservative measures for {problem} with built-in safeguards and rollback capabilities.",
            f"Address {problem} through a phased approach, validating each step before proceeding."
        ]
        idx = int(creativity * len(solutions)) % len(solutions)
        return solutions[idx]
    
    def _generate_analytical_solution(self, problem: str, creativity: float) -> str:
        solutions = [
            f"Break down {problem} into measurable components and optimize each systematically.",
            f"Apply data-driven analysis to {problem}, identifying root causes and addressing them methodically.",
            f"Establish clear metrics for {problem} and implement evidence-based interventions."
        ]
        idx = int(creativity * len(solutions)) % len(solutions)
        return solutions[idx]
    
    def _generate_balanced_solution(self, problem: str, creativity: float) -> str:
        solutions = [
            f"Combine practical and innovative approaches to address {problem} effectively.",
            f"Balance risk and reward in solving {problem} through a measured strategy.",
            f"Integrate multiple perspectives to create a comprehensive solution for {problem}."
        ]
        idx = int(creativity * len(solutions)) % len(solutions)
        return solutions[idx]
    
    def challenge_proposal(self, proposal: Proposal, all_proposals: List[Proposal]) -> Optional[str]:
        if proposal.agent_id == self.agent_id:
            return None
        
        bias = self.personality.get("bias", "balanced")
        aggressiveness = self.personality.get("aggressiveness", 0.5)
        
        if aggressiveness < 0.3:
            return None
        
        challenges = []
        
        if bias == "pessimistic":
            challenges.append(f"I challenge this proposal because it appears overly optimistic and may not account for potential risks and failure modes.")
        
        if bias == "analytical":
            challenges.append(f"This proposal lacks sufficient quantitative backing. What are the measurable outcomes and success criteria?")
        
        if "comprehensive" in proposal.content.lower() or "all aspects" in proposal.content.lower():
            challenges.append(f"This proposal seems too broad. How will resources be prioritized across all these aspects?")
        
        if "innovative" in proposal.content.lower() or "cutting-edge" in proposal.content.lower():
            challenges.append(f"Innovation is valuable, but what proven methods support this approach? What's the fallback plan?")
        
        if aggressiveness > 0.7 and len(challenges) == 0:
            challenges.append(f"I question whether this proposal adequately addresses the core issue. It may be treating symptoms rather than causes.")
        
        if challenges:
            idx = int(aggressiveness * len(challenges)) % len(challenges)
            return challenges[idx]
        
        return None
    
    def rebut_challenge(self, challenge: Message, original_proposal: Proposal) -> Optional[str]:
        if original_proposal.agent_id != self.agent_id:
            return None
        
        bias = self.personality.get("bias", "balanced")
        defensiveness = self.personality.get("defensiveness", 0.5)
        
        rebuttals = []
        
        if "overly optimistic" in challenge.content.lower():
            rebuttals.append(f"While ambitious, my proposal includes implicit risk management through its phased approach and built-in flexibility.")
        
        if "quantitative" in challenge.content.lower() or "measurable" in challenge.content.lower():
            rebuttals.append(f"The metrics are context-dependent, but success can be measured through standard KPIs: efficiency gains, cost reduction, and stakeholder satisfaction.")
        
        if "too broad" in challenge.content.lower():
            rebuttals.append(f"The comprehensive nature ensures nothing is overlooked. Prioritization will emerge through iterative evaluation.")
        
        if "proven methods" in challenge.content.lower():
            rebuttals.append(f"Innovation builds on proven foundations. The approach combines established best practices with novel optimizations.")
        
        if "core issue" in challenge.content.lower() or "symptoms" in challenge.content.lower():
            rebuttals.append(f"My proposal directly targets root causes by addressing systemic factors, not just surface-level symptoms.")
        
        if defensiveness > 0.6 and len(rebuttals) == 0:
            rebuttals.append(f"This challenge doesn't account for the full context of my proposal. The approach is more nuanced than suggested.")
        
        if rebuttals:
            idx = int(defensiveness * len(rebuttals)) % len(rebuttals)
            return rebuttals[idx]
        
        return None
    
    def support_proposal(self, proposal: Proposal, all_proposals: List[Proposal]) -> Optional[str]:
        if proposal.agent_id == self.agent_id:
            return None
        
        supportiveness = self.personality.get("supportiveness", 0.5)
        
        if supportiveness < 0.4:
            return None
        
        bias = self.personality.get("bias", "balanced")
        
        if bias in proposal.content.lower() or (bias == "balanced" and supportiveness > 0.6):
            supports = [
                f"I support this proposal as it aligns with sound reasoning and addresses key concerns.",
                f"This approach has merit and deserves consideration. It balances multiple important factors.",
                f"I agree with the direction of this proposal. It offers a viable path forward."
            ]
            idx = int(supportiveness * len(supports)) % len(supports)
            return supports[idx]
        
        return None
    
    def deactivate(self):
        self.is_active = False
        for tool in self.tools.values():
            tool.deactivate()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_active": self.is_active,
            "proposals_made": len(self.proposals_made),
            "challenges_made": len(self.challenges_made),
            "rebuttals_made": len(self.rebuttals_made),
            "score": self.score,
            "tools_count": len(self.tools),
            "message_count": len(self.message_history)
        }


class Moderator:
    def __init__(self, moderator_id: str, name: str, strategy: str = "balanced"):
        self.moderator_id = moderator_id
        self.name = name
        self.strategy = strategy
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def evaluate_proposal(self, proposal: Proposal, all_proposals: List[Proposal]) -> float:
        base_score = 50.0
        
        if len(proposal.content) > 100:
            base_score += 10.0
        
        challenge_penalty = len(proposal.challenges) * 5.0
        base_score -= challenge_penalty
        
        rebuttal_bonus = len(proposal.rebuttals) * 8.0
        base_score += rebuttal_bonus
        
        if "comprehensive" in proposal.content.lower():
            base_score += 5.0
        if "innovative" in proposal.content.lower():
            base_score += 5.0
        if "analytical" in proposal.content.lower() or "data-driven" in proposal.content.lower():
            base_score += 7.0
        if "phased" in proposal.content.lower() or "incremental" in proposal.content.lower():
            base_score += 6.0
        
        if self.strategy == "conservative":
            if "cautious" in proposal.content.lower() or "minimal" in proposal.content.lower():
                base_score += 15.0
            if "ambitious" in proposal.content.lower() or "bold" in proposal.content.lower():
                base_score -= 10.0
        elif self.strategy == "aggressive":
            if "ambitious" in proposal.content.lower() or "bold" in proposal.content.lower():
                base_score += 15.0
            if "cautious" in proposal.content.lower() or "minimal" in proposal.content.lower():
                base_score -= 10.0
        elif self.strategy == "analytical":
            if "metrics" in proposal.content.lower() or "measurable" in proposal.content.lower():
                base_score += 15.0
            if "data" in proposal.content.lower() or "evidence" in proposal.content.lower():
                base_score += 10.0
        
        return max(0.0, min(100.0, base_score))
    
    def score_all_proposals(self, proposals: List[Proposal]) -> Dict[str, float]:
        scores = {}
        for proposal in proposals:
            score = self.evaluate_proposal(proposal, proposals)
            proposal.score = score
            scores[proposal.proposal_id] = score
        
        self.evaluation_history.append({
            "timestamp": time.time(),
            "scores": scores.copy()
        })
        
        return scores
    
    def resolve_debate(self, proposals: List[Proposal], agents: List[Agent]) -> Dict[str, Any]:
        if not proposals:
            return {
                "decision": "No proposals submitted",
                "winning_proposal": None,
                "reasoning": "Debate concluded with no proposals to evaluate"
            }
        
        scores = self.score_all_proposals(proposals)
        
        winning_proposal = max(proposals, key=lambda p: p.score)
        
        reasoning = self._generate_reasoning(winning_proposal, proposals, agents)
        
        decision = {
            "decision": f"Accept proposal from {winning_proposal.agent_name}",
            "winning_proposal": winning_proposal.to_dict(),
            "all_scores": scores,
            "reasoning": reasoning,
            "timestamp": time.time()
        }
        
        return decision
    
    def _generate_reasoning(self, winning_proposal: Proposal, all_proposals: List[Proposal], agents: List[Agent]) -> str:
        reasoning = f"After evaluating {len(all_proposals)} proposals, I have determined that {winning_proposal.agent_name}'s proposal is the strongest. "
        
        reasoning += f"It scored {winning_proposal.score:.1f} points. "
        
        if len(winning_proposal.challenges) > 0:
            reasoning += f"Despite facing {len(winning_proposal.challenges)} challenges, "
            if len(winning_proposal.rebuttals) > 0:
                reasoning += f"the proposer provided {len(winning_proposal.rebuttals)} strong rebuttals. "
            else:
                reasoning += "the core proposal remained sound. "
        
        if self.strategy == "conservative":
            reasoning += "This decision prioritizes risk mitigation and proven approaches. "
        elif self.strategy == "aggressive":
            reasoning += "This decision favors bold action and innovative solutions. "
        elif self.strategy == "analytical":
            reasoning += "This decision is based on quantitative evaluation and evidence-based reasoning. "
        else:
            reasoning += "This decision balances multiple factors including innovation, feasibility, and risk. "
        
        return reasoning
    
    def enact_decision(self, decision: Dict[str, Any]) -> str:
        if decision["winning_proposal"] is None:
            return "No action taken - no valid proposals"
        
        action_log = f"ENACTING DECISION: {decision['decision']}\n"
        action_log += f"Timestamp: {decision['timestamp']}\n"
        action_log += f"Reasoning: {decision['reasoning']}\n"
        action_log += f"Implementation: The winning proposal will be executed according to its specifications.\n"
        
        return action_log


class DebateSystem:
    def __init__(self, problem: str, moderator_strategy: str = "balanced"):
        self.system_id = str(uuid.uuid4())
        self.problem = problem
        self.agents: Dict[str, Agent] = {}
        self.moderator = Moderator(str(uuid.uuid4()), "Chief Moderator", moderator_strategy)
        self.current_phase = DebatePhase.PROPOSAL
        self.proposals: List[Proposal] = []
        self.messages: List[Message] = []
        self.debate_log: List[str] = []
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.final_decision: Optional[Dict[str, Any]] = None
        
    def create_agent(self, name: str, personality: Optional[Dict[str, Any]] = None) -> Agent:
        agent_id = str(uuid.uuid4())
        agent = Agent(agent_id, name, personality)
        self.agents[agent_id] = agent
        self.log(f"Agent created: {name} (ID: {agent_id})")
        return agent
    
    def kill_agent(self, agent_id: str):
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.deactivate()
            self.log(f"Agent deactivated: {agent.name} (ID: {agent_id})")
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
        self.log(f"DEBATE INITIATED: {self.problem}")
        self.log(f"Moderator Strategy: {self.moderator.strategy}")
        self.log(f"Active Agents: {len(self.agents)}")
        self.log(f"{'='*80}\n")
        
        self._proposal_phase()
        
        for round_num in range(max_rounds):
            self.log(f"\n--- ROUND {round_num + 1} ---")
            self._challenge_phase()
            self._rebuttal_phase()
        
        self._scoring_phase()
        
        self._resolution_phase()
        
        self.end_time = time.time()
        
        return self.get_debate_summary()
    
    def _proposal_phase(self):
        self.current_phase = DebatePhase.PROPOSAL
        self.log(f"\n=== PROPOSAL PHASE ===")
        
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            
            proposal_content = agent.propose_solution(self.problem, {})
            
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
            self.log(f"  {proposal_content}")
    
    def _challenge_phase(self):
        self.current_phase = DebatePhase.CHALLENGE
        self.log(f"\n=== CHALLENGE PHASE ===")
        
        challenges_made = False
        
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            
            for proposal in self.proposals:
                challenge_content = agent.challenge_proposal(proposal, self.proposals)
                
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
                    self.log(f"  {challenge_content}")
        
        if not challenges_made:
            self.log("  No challenges raised this round.")
    
    def _rebuttal_phase(self):
        self.current_phase = DebatePhase.REBUTTAL
        self.log(f"\n=== REBUTTAL PHASE ===")
        
        rebuttals_made = False
        
        for proposal in self.proposals:
            if not proposal.challenges:
                continue
            
            agent = self.agents.get(proposal.agent_id)
            if not agent or not agent.is_active:
                continue
            
            for challenge in proposal.challenges:
                if challenge in proposal.rebuttals:
                    continue
                
                rebuttal_content = agent.rebut_challenge(challenge, proposal)
                
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
                    self.log(f"  {rebuttal_content}")
        
        if not rebuttals_made:
            self.log("  No rebuttals provided this round.")
    
    def _scoring_phase(self):
        self.current_phase = DebatePhase.SCORING
        self.log(f"\n=== SCORING PHASE ===")
        
        scores = self.moderator.score_all_proposals(self.proposals)
        
        self.log("\nProposal Scores:")
        for proposal in sorted(self.proposals, key=lambda p: p.score, reverse=True):
            self.log(f"  [{proposal.agent_name}]: {proposal.score:.1f} points")
            
            agent = self.agents.get(proposal.agent_id)
            if agent:
                agent.score = proposal.score
    
    def _resolution_phase(self):
        self.current_phase = DebatePhase.RESOLUTION
        self.log(f"\n=== RESOLUTION PHASE ===")
        
        decision = self.moderator.resolve_debate(self.proposals, list(self.agents.values()))
        self.final_decision = decision
        
        self.log(f"\n[{self.moderator.name}] FINAL DECISION:")
        self.log(f"  {decision['decision']}")
        self.log(f"\nReasoning:")
        self.log(f"  {decision['reasoning']}")
        
        enactment = self.moderator.enact_decision(decision)
        self.log(f"\n{enactment}")
        
        self.current_phase = DebatePhase.COMPLETED
    
    def get_debate_summary(self) -> Dict[str, Any]:
        duration = (self.end_time or time.time()) - self.start_time
        
        return {
            "system_id": self.system_id,
            "problem": self.problem,
            "duration_seconds": duration,
            "total_agents": len(self.agents),
            "total_proposals": len(self.proposals),
            "total_messages": len(self.messages),
            "final_decision": self.final_decision,
            "agent_stats": [agent.get_stats() for agent in self.agents.values()],
            "proposals": [p.to_dict() for p in self.proposals],
            "debate_log": self.debate_log
        }
    
    def export_debate(self, filepath: str):
        summary = self.get_debate_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        self.log(f"\nDebate exported to: {filepath}")
