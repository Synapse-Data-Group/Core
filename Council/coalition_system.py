import time
import random
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Coalition:
    coalition_id: str
    name: str
    members: Set[str] = field(default_factory=set)
    leader_id: Optional[str] = None
    formed_at: float = field(default_factory=time.time)
    shared_goals: List[str] = field(default_factory=list)
    strength: float = 0.0
    
    def add_member(self, agent_id: str):
        self.members.add(agent_id)
        self._update_strength()
    
    def remove_member(self, agent_id: str):
        if agent_id in self.members:
            self.members.remove(agent_id)
            if agent_id == self.leader_id:
                self.leader_id = None
            self._update_strength()
    
    def _update_strength(self):
        self.strength = len(self.members) * 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coalition_id": self.coalition_id,
            "name": self.name,
            "members": list(self.members),
            "leader_id": self.leader_id,
            "member_count": len(self.members),
            "strength": self.strength,
            "formed_at": self.formed_at,
            "shared_goals": self.shared_goals
        }


class CoalitionManager:
    def __init__(self):
        self.coalitions: Dict[str, Coalition] = {}
        self.agent_coalitions: Dict[str, str] = {}
        self.coalition_counter = 0
        self.formation_history: List[Dict[str, Any]] = []
        
    def detect_potential_coalitions(self, agents: List[Any], proposals: List[Any]) -> List[Dict[str, Any]]:
        """Detect which agents should form coalitions based on alignment"""
        
        potential_coalitions = []
        
        agent_positions = {}
        for proposal in proposals:
            agent_id = proposal.agent_id
            agent_positions[agent_id] = {
                "proposal_content": proposal.content,
                "score": proposal.score,
                "keywords": set(proposal.content.lower().split())
            }
        
        agents_list = list(agent_positions.keys())
        
        for i in range(len(agents_list)):
            for j in range(i + 1, len(agents_list)):
                agent1_id = agents_list[i]
                agent2_id = agents_list[j]
                
                if agent1_id in self.agent_coalitions or agent2_id in self.agent_coalitions:
                    continue
                
                alignment = self._calculate_alignment(
                    agent_positions[agent1_id],
                    agent_positions[agent2_id]
                )
                
                if alignment > 0.6:
                    potential_coalitions.append({
                        "agents": [agent1_id, agent2_id],
                        "alignment": alignment,
                        "reason": "high_proposal_similarity"
                    })
        
        return potential_coalitions
    
    def _calculate_alignment(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate alignment between two agent positions"""
        
        keywords1 = pos1["keywords"]
        keywords2 = pos2["keywords"]
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        keyword_similarity = intersection / union if union > 0 else 0
        
        score_diff = abs(pos1["score"] - pos2["score"])
        score_similarity = 1.0 - (score_diff / 100.0)
        
        alignment = (keyword_similarity * 0.7 + score_similarity * 0.3)
        
        return alignment
    
    def form_coalition(self, agent_ids: List[str], agents_dict: Dict[str, Any], 
                      reason: str = "alignment") -> Coalition:
        """Form a new coalition"""
        
        self.coalition_counter += 1
        coalition_id = f"coalition_{self.coalition_counter}"
        
        coalition_name = f"Coalition_{self.coalition_counter}"
        
        coalition = Coalition(
            coalition_id=coalition_id,
            name=coalition_name,
            members=set(agent_ids)
        )
        
        if agent_ids:
            coalition.leader_id = agent_ids[0]
        
        for agent_id in agent_ids:
            self.agent_coalitions[agent_id] = coalition_id
        
        self.coalitions[coalition_id] = coalition
        
        self.formation_history.append({
            "coalition_id": coalition_id,
            "members": agent_ids,
            "reason": reason,
            "timestamp": time.time()
        })
        
        return coalition
    
    def dissolve_coalition(self, coalition_id: str, reason: str = "natural"):
        """Dissolve a coalition"""
        
        if coalition_id not in self.coalitions:
            return
        
        coalition = self.coalitions[coalition_id]
        
        for agent_id in list(coalition.members):
            if agent_id in self.agent_coalitions:
                del self.agent_coalitions[agent_id]
        
        del self.coalitions[coalition_id]
        
        self.formation_history.append({
            "coalition_id": coalition_id,
            "action": "dissolved",
            "reason": reason,
            "timestamp": time.time()
        })
    
    def get_coalition_for_agent(self, agent_id: str) -> Optional[Coalition]:
        """Get the coalition an agent belongs to"""
        
        coalition_id = self.agent_coalitions.get(agent_id)
        if coalition_id:
            return self.coalitions.get(coalition_id)
        return None
    
    def are_in_same_coalition(self, agent1_id: str, agent2_id: str) -> bool:
        """Check if two agents are in the same coalition"""
        
        coalition1 = self.get_coalition_for_agent(agent1_id)
        coalition2 = self.get_coalition_for_agent(agent2_id)
        
        if coalition1 and coalition2:
            return coalition1.coalition_id == coalition2.coalition_id
        
        return False
    
    def get_coalition_members(self, agent_id: str) -> List[str]:
        """Get all members of an agent's coalition"""
        
        coalition = self.get_coalition_for_agent(agent_id)
        if coalition:
            return list(coalition.members)
        return []
    
    def should_support_proposal(self, agent_id: str, proposal_agent_id: str) -> bool:
        """Determine if agent should support proposal based on coalition"""
        
        if agent_id == proposal_agent_id:
            return False
        
        return self.are_in_same_coalition(agent_id, proposal_agent_id)
    
    def get_coalition_voting_power(self, coalition_id: str) -> float:
        """Calculate voting power of a coalition"""
        
        coalition = self.coalitions.get(coalition_id)
        if not coalition:
            return 0.0
        
        return coalition.strength
    
    def update_coalitions(self, agents: List[Any], proposals: List[Any], 
                         debate_context: Dict[str, Any]):
        """Update coalitions based on current debate state"""
        
        for coalition_id in list(self.coalitions.keys()):
            coalition = self.coalitions[coalition_id]
            
            if len(coalition.members) < 2:
                self.dissolve_coalition(coalition_id, "insufficient_members")
                continue
            
            inactive_members = []
            for member_id in coalition.members:
                agent = next((a for a in agents if a.agent_id == member_id), None)
                if not agent or not agent.is_active:
                    inactive_members.append(member_id)
            
            for member_id in inactive_members:
                coalition.remove_member(member_id)
                if member_id in self.agent_coalitions:
                    del self.agent_coalitions[member_id]
        
        potential = self.detect_potential_coalitions(agents, proposals)
        
        for pot_coalition in potential[:2]:
            if random.random() < 0.5:
                self.form_coalition(
                    pot_coalition["agents"],
                    {a.agent_id: a for a in agents},
                    pot_coalition["reason"]
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coalition statistics"""
        
        return {
            "total_coalitions": len(self.coalitions),
            "active_coalitions": [c.to_dict() for c in self.coalitions.values()],
            "total_formations": len([h for h in self.formation_history if "action" not in h]),
            "total_dissolutions": len([h for h in self.formation_history if h.get("action") == "dissolved"]),
            "agents_in_coalitions": len(self.agent_coalitions),
            "formation_history": self.formation_history
        }
