import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class MetaProposal:
    """Proposal to change debate rules or structure"""
    proposal_id: str
    proposer_id: str
    proposal_type: str
    description: str
    target_rule: str
    new_value: Any
    votes_for: int = 0
    votes_against: int = 0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposer_id": self.proposer_id,
            "proposal_type": self.proposal_type,
            "description": self.description,
            "target_rule": self.target_rule,
            "new_value": self.new_value,
            "votes_for": self.votes_for,
            "votes_against": self.votes_against,
            "timestamp": self.timestamp
        }


class MetaDebateLayer:
    """Layer for agents to debate about the debate itself"""
    
    def __init__(self):
        self.meta_proposals: List[MetaProposal] = []
        self.debate_rules: Dict[str, Any] = {
            "max_rounds": 3,
            "proposal_time_limit": None,
            "challenge_required": False,
            "rebuttal_required": False,
            "min_agents": 2,
            "max_agents": 10,
            "scoring_method": "adaptive",
            "allow_coalitions": True,
            "allow_agent_spawning": True
        }
        self.rule_change_history: List[Dict[str, Any]] = []
        self.meta_debate_active = False
        self.proposal_counter = 0
    
    def should_trigger_meta_debate(self, debate_context: Dict[str, Any]) -> bool:
        """Determine if meta-debate should be triggered"""
        
        round_num = debate_context.get("round", 0)
        
        if round_num > self.debate_rules["max_rounds"]:
            return True
        
        total_messages = debate_context.get("total_messages", 0)
        if total_messages > 50:
            return True
        
        agent_count = debate_context.get("agent_count", 0)
        if agent_count > self.debate_rules["max_agents"]:
            return True
        
        return False
    
    def propose_rule_change(self, proposer_id: str, rule_name: str, 
                           new_value: Any, reason: str) -> MetaProposal:
        """Propose a change to debate rules"""
        
        self.proposal_counter += 1
        proposal_id = f"meta_{self.proposal_counter}"
        
        proposal = MetaProposal(
            proposal_id=proposal_id,
            proposer_id=proposer_id,
            proposal_type="rule_change",
            description=reason,
            target_rule=rule_name,
            new_value=new_value
        )
        
        self.meta_proposals.append(proposal)
        
        return proposal
    
    def vote_on_proposal(self, proposal_id: str, agent_id: str, vote: bool):
        """Vote on a meta-proposal"""
        
        proposal = next((p for p in self.meta_proposals if p.proposal_id == proposal_id), None)
        
        if not proposal:
            return
        
        if vote:
            proposal.votes_for += 1
        else:
            proposal.votes_against += 1
    
    def evaluate_proposals(self, total_agents: int) -> List[MetaProposal]:
        """Evaluate meta-proposals and apply approved changes"""
        
        approved = []
        threshold = total_agents / 2
        
        for proposal in self.meta_proposals:
            if proposal.votes_for > threshold:
                self._apply_rule_change(proposal)
                approved.append(proposal)
        
        self.meta_proposals = [p for p in self.meta_proposals if p not in approved]
        
        return approved
    
    def _apply_rule_change(self, proposal: MetaProposal):
        """Apply an approved rule change"""
        
        old_value = self.debate_rules.get(proposal.target_rule)
        self.debate_rules[proposal.target_rule] = proposal.new_value
        
        self.rule_change_history.append({
            "proposal_id": proposal.proposal_id,
            "rule": proposal.target_rule,
            "old_value": old_value,
            "new_value": proposal.new_value,
            "timestamp": time.time(),
            "votes_for": proposal.votes_for,
            "votes_against": proposal.votes_against
        })
    
    def agent_suggests_meta_change(self, agent_id: str, debate_context: Dict[str, Any]) -> Optional[MetaProposal]:
        """Agent analyzes debate and suggests meta-level changes"""
        
        round_num = debate_context.get("round", 0)
        
        if round_num > 5:
            return self.propose_rule_change(
                agent_id,
                "max_rounds",
                round_num + 2,
                "Debate requires more rounds for thorough exploration"
            )
        
        agent_count = debate_context.get("agent_count", 0)
        if agent_count < 3:
            return self.propose_rule_change(
                agent_id,
                "min_agents",
                3,
                "Need more diverse perspectives"
            )
        
        challenge_ratio = debate_context.get("challenge_ratio", 0)
        if challenge_ratio < 0.3:
            return self.propose_rule_change(
                agent_id,
                "challenge_required",
                True,
                "Insufficient critical analysis - require challenges"
            )
        
        return None
    
    def get_current_rules(self) -> Dict[str, Any]:
        """Get current debate rules"""
        return self.debate_rules.copy()
    
    def get_meta_debate_summary(self) -> Dict[str, Any]:
        """Get summary of meta-debate activity"""
        
        return {
            "active_proposals": len(self.meta_proposals),
            "total_rule_changes": len(self.rule_change_history),
            "current_rules": self.debate_rules.copy(),
            "recent_changes": self.rule_change_history[-5:],
            "pending_proposals": [p.to_dict() for p in self.meta_proposals]
        }


class ArgumentQualityMetrics:
    """Evaluate argument quality in real-time"""
    
    def __init__(self):
        self.quality_history: List[Dict[str, Any]] = []
        
        self.logical_connectors = {
            "therefore", "thus", "hence", "consequently", "because",
            "since", "given", "if", "then", "however", "although",
            "nevertheless", "moreover", "furthermore"
        }
        
        self.evidence_indicators = {
            "data", "research", "study", "evidence", "proof", "shows",
            "demonstrates", "indicates", "suggests", "according to"
        }
        
        self.fallacy_patterns = {
            "ad_hominem": ["you are", "you're just", "coming from you"],
            "strawman": ["you claim", "you say", "your position"],
            "appeal_to_authority": ["expert says", "authority", "everyone knows"],
            "false_dichotomy": ["only two", "either or", "must choose"]
        }
    
    def evaluate_argument(self, argument: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate quality of an argument"""
        
        scores = {
            "logical_structure": self._assess_logical_structure(argument),
            "evidence_strength": self._assess_evidence(argument),
            "coherence": self._assess_coherence(argument),
            "fallacy_score": self._detect_fallacies(argument),
            "clarity": self._assess_clarity(argument)
        }
        
        overall_quality = (
            scores["logical_structure"] * 0.25 +
            scores["evidence_strength"] * 0.25 +
            scores["coherence"] * 0.20 +
            (1.0 - scores["fallacy_score"]) * 0.15 +
            scores["clarity"] * 0.15
        )
        
        evaluation = {
            "overall_quality": overall_quality,
            "scores": scores,
            "strengths": self._identify_strengths(scores),
            "weaknesses": self._identify_weaknesses(scores),
            "timestamp": time.time()
        }
        
        self.quality_history.append(evaluation)
        
        return evaluation
    
    def _assess_logical_structure(self, argument: str) -> float:
        """Assess logical structure of argument"""
        
        argument_lower = argument.lower()
        
        connector_count = sum(1 for conn in self.logical_connectors if conn in argument_lower)
        
        sentences = argument.split('.')
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])
        
        structure_score = min(1.0, (connector_count / max(sentence_count, 1)) * 2)
        
        return structure_score
    
    def _assess_evidence(self, argument: str) -> float:
        """Assess evidence strength"""
        
        argument_lower = argument.lower()
        
        evidence_count = sum(1 for indicator in self.evidence_indicators if indicator in argument_lower)
        
        has_numbers = any(char.isdigit() for char in argument)
        
        evidence_score = min(1.0, evidence_count * 0.2)
        if has_numbers:
            evidence_score += 0.2
        
        return evidence_score
    
    def _assess_coherence(self, argument: str) -> float:
        """Assess coherence and flow"""
        
        sentences = [s.strip() for s in argument.split('.') if len(s.strip()) > 10]
        
        if len(sentences) < 2:
            return 0.5
        
        coherence_score = 0.7
        
        if len(sentences) > 1:
            for i in range(len(sentences) - 1):
                words1 = set(sentences[i].lower().split())
                words2 = set(sentences[i + 1].lower().split())
                
                overlap = len(words1 & words2)
                if overlap > 0:
                    coherence_score += 0.1
        
        return min(1.0, coherence_score)
    
    def _detect_fallacies(self, argument: str) -> float:
        """Detect logical fallacies"""
        
        argument_lower = argument.lower()
        
        fallacy_count = 0
        for fallacy_type, patterns in self.fallacy_patterns.items():
            for pattern in patterns:
                if pattern in argument_lower:
                    fallacy_count += 1
                    break
        
        fallacy_score = min(1.0, fallacy_count * 0.25)
        
        return fallacy_score
    
    def _assess_clarity(self, argument: str) -> float:
        """Assess clarity of expression"""
        
        words = argument.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        sentences = [s for s in argument.split('.') if len(s.strip()) > 10]
        avg_sentence_length = word_count / max(len(sentences), 1)
        
        if 10 <= avg_sentence_length <= 25:
            clarity_score = 0.9
        elif 5 <= avg_sentence_length <= 35:
            clarity_score = 0.7
        else:
            clarity_score = 0.5
        
        return clarity_score
    
    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify argument strengths"""
        
        strengths = []
        
        if scores["logical_structure"] > 0.7:
            strengths.append("Strong logical structure")
        if scores["evidence_strength"] > 0.6:
            strengths.append("Well-supported with evidence")
        if scores["coherence"] > 0.7:
            strengths.append("Highly coherent")
        if scores["fallacy_score"] < 0.2:
            strengths.append("Logically sound")
        if scores["clarity"] > 0.7:
            strengths.append("Clear and concise")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict[str, float]) -> List[str]:
        """Identify argument weaknesses"""
        
        weaknesses = []
        
        if scores["logical_structure"] < 0.4:
            weaknesses.append("Weak logical structure")
        if scores["evidence_strength"] < 0.3:
            weaknesses.append("Lacks evidence")
        if scores["coherence"] < 0.5:
            weaknesses.append("Poor coherence")
        if scores["fallacy_score"] > 0.5:
            weaknesses.append("Contains logical fallacies")
        if scores["clarity"] < 0.5:
            weaknesses.append("Unclear expression")
        
        return weaknesses
    
    def get_stats(self) -> Dict[str, Any]:
        """Get quality metrics statistics"""
        
        if not self.quality_history:
            return {"message": "No evaluations yet"}
        
        avg_quality = sum(e["overall_quality"] for e in self.quality_history) / len(self.quality_history)
        
        return {
            "total_evaluations": len(self.quality_history),
            "average_quality": avg_quality,
            "recent_evaluations": self.quality_history[-5:]
        }
