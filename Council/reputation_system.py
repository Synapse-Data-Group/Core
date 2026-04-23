import time
from typing import Dict, List, Optional, Any
from collections import defaultdict


class ReputationScore:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.overall_score = 50.0
        self.proposal_success_rate = 0.5
        self.challenge_accuracy = 0.5
        self.rebuttal_effectiveness = 0.5
        self.consistency_score = 0.5
        self.trust_network: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []
        
    def update_from_debate(self, is_winner: bool, proposal_score: float, 
                          challenges_made: int, rebuttals_made: int):
        """Update reputation based on debate performance"""
        
        if is_winner:
            self.overall_score = min(100.0, self.overall_score + 10.0)
            self.proposal_success_rate = min(1.0, self.proposal_success_rate + 0.1)
        else:
            self.overall_score = max(0.0, self.overall_score - 5.0)
            self.proposal_success_rate = max(0.0, self.proposal_success_rate - 0.05)
        
        if proposal_score > 70:
            self.overall_score += 5.0
        elif proposal_score < 30:
            self.overall_score -= 3.0
        
        if challenges_made > 0:
            self.challenge_accuracy = min(1.0, self.challenge_accuracy + 0.05)
        
        if rebuttals_made > 0:
            self.rebuttal_effectiveness = min(1.0, self.rebuttal_effectiveness + 0.05)
        
        self.overall_score = max(0.0, min(100.0, self.overall_score))
        
        self.history.append({
            "timestamp": time.time(),
            "is_winner": is_winner,
            "proposal_score": proposal_score,
            "overall_score": self.overall_score
        })
    
    def add_trust(self, other_agent_id: str, trust_value: float):
        """Add or update trust relationship with another agent"""
        
        if other_agent_id not in self.trust_network:
            self.trust_network[other_agent_id] = trust_value
        else:
            current = self.trust_network[other_agent_id]
            self.trust_network[other_agent_id] = (current + trust_value) / 2
    
    def get_trust(self, other_agent_id: str) -> float:
        """Get trust level for another agent"""
        return self.trust_network.get(other_agent_id, 0.5)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "overall_score": self.overall_score,
            "proposal_success_rate": self.proposal_success_rate,
            "challenge_accuracy": self.challenge_accuracy,
            "rebuttal_effectiveness": self.rebuttal_effectiveness,
            "consistency_score": self.consistency_score,
            "trust_network_size": len(self.trust_network),
            "debates_participated": len(self.history)
        }


class ReputationSystem:
    def __init__(self):
        self.reputations: Dict[str, ReputationScore] = {}
        self.global_rankings: List[str] = []
        self.reputation_history: List[Dict[str, Any]] = []
        
    def get_reputation(self, agent_id: str) -> ReputationScore:
        """Get or create reputation for an agent"""
        
        if agent_id not in self.reputations:
            self.reputations[agent_id] = ReputationScore(agent_id)
        
        return self.reputations[agent_id]
    
    def update_reputation(self, agent_id: str, is_winner: bool, proposal_score: float,
                         challenges_made: int, rebuttals_made: int):
        """Update agent reputation after debate"""
        
        reputation = self.get_reputation(agent_id)
        reputation.update_from_debate(is_winner, proposal_score, challenges_made, rebuttals_made)
        
        self.reputation_history.append({
            "agent_id": agent_id,
            "is_winner": is_winner,
            "new_score": reputation.overall_score,
            "timestamp": time.time()
        })
        
        self._update_rankings()
    
    def build_trust_network(self, agents: List[Any], proposals: List[Any]):
        """Build trust network based on agent interactions"""
        
        for proposal in proposals:
            proposer_id = proposal.agent_id
            proposer_rep = self.get_reputation(proposer_id)
            
            for challenge in proposal.challenges:
                challenger_id = challenge.agent_id
                
                if proposal.score > 60:
                    proposer_rep.add_trust(challenger_id, 0.3)
                else:
                    proposer_rep.add_trust(challenger_id, 0.7)
            
            for rebuttal in proposal.rebuttals:
                if rebuttal.agent_id == proposer_id:
                    for challenge in proposal.challenges:
                        if len(proposal.rebuttals) >= len(proposal.challenges):
                            proposer_rep.add_trust(challenge.agent_id, 0.6)
    
    def get_influence_weight(self, agent_id: str) -> float:
        """Get influence weight for an agent based on reputation"""
        
        reputation = self.get_reputation(agent_id)
        
        weight = reputation.overall_score / 100.0
        
        weight *= (1.0 + reputation.proposal_success_rate) / 2.0
        
        return weight
    
    def should_defer_to_expert(self, agent_id: str, expert_id: str, topic: str) -> bool:
        """Determine if agent should defer to expert on a topic"""
        
        agent_rep = self.get_reputation(agent_id)
        expert_rep = self.get_reputation(expert_id)
        
        if expert_rep.overall_score > agent_rep.overall_score + 20:
            trust = agent_rep.get_trust(expert_id)
            if trust > 0.6:
                return True
        
        return False
    
    def _update_rankings(self):
        """Update global reputation rankings"""
        
        ranked = sorted(
            self.reputations.items(),
            key=lambda x: x[1].overall_score,
            reverse=True
        )
        
        self.global_rankings = [agent_id for agent_id, _ in ranked]
    
    def get_top_agents(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top N agents by reputation"""
        
        if not self.global_rankings:
            self._update_rankings()
        
        top_agents = []
        for agent_id in self.global_rankings[:n]:
            reputation = self.reputations[agent_id]
            top_agents.append({
                "agent_id": agent_id,
                "rank": self.global_rankings.index(agent_id) + 1,
                "score": reputation.overall_score,
                "success_rate": reputation.proposal_success_rate
            })
        
        return top_agents
    
    def get_reputation_distribution(self) -> Dict[str, int]:
        """Get distribution of reputation scores"""
        
        distribution = {
            "expert": 0,
            "advanced": 0,
            "intermediate": 0,
            "novice": 0
        }
        
        for reputation in self.reputations.values():
            score = reputation.overall_score
            if score >= 80:
                distribution["expert"] += 1
            elif score >= 60:
                distribution["advanced"] += 1
            elif score >= 40:
                distribution["intermediate"] += 1
            else:
                distribution["novice"] += 1
        
        return distribution
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reputation system statistics"""
        
        return {
            "total_agents": len(self.reputations),
            "top_agents": self.get_top_agents(5),
            "distribution": self.get_reputation_distribution(),
            "total_updates": len(self.reputation_history),
            "avg_reputation": sum(r.overall_score for r in self.reputations.values()) / len(self.reputations) if self.reputations else 0
        }
