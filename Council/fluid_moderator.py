import time
import random
from typing import List, Dict, Any, Optional, Tuple
from sentient_moderator import SentientModerator
from agent_factory import AgentFactory, AgentArchetype
from sentient_agent import SentientAgent


class FluidModerator(SentientModerator):
    """
    Advanced moderator with fluid resourcing capabilities.
    Can dynamically create, activate, and terminate agents during debates.
    """
    
    def __init__(self, moderator_id: str, name: str, strategy: str = "adaptive"):
        super().__init__(moderator_id, name, strategy)
        
        self.agent_factory = AgentFactory()
        self.spawned_agents: List[str] = []
        self.terminated_agents: List[str] = []
        
        self.spawn_threshold = {
            "lack_of_diversity": 0.7,
            "stalemate": 0.6,
            "missing_perspective": 0.8,
            "insufficient_challenge": 0.5,
            "need_mediation": 0.7
        }
        
        self.resource_limits = {
            "max_agents": 10,
            "max_spawns_per_debate": 5,
            "min_agent_lifetime": 2.0
        }
        
        self.spawn_history: List[Dict[str, Any]] = []
    
    def analyze_debate_needs(self, proposals: List[Any], agents: List[SentientAgent], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the debate and determine if new agents are needed"""
        
        needs = {
            "needs_agent": False,
            "reason": None,
            "role": None,
            "urgency": 0.0,
            "analysis": {}
        }
        
        if len(agents) >= self.resource_limits["max_agents"]:
            needs["analysis"]["at_capacity"] = True
            return needs
        
        if len(self.spawned_agents) >= self.resource_limits["max_spawns_per_debate"]:
            needs["analysis"]["spawn_limit_reached"] = True
            return needs
        
        diversity_score = self._assess_diversity(proposals, agents)
        needs["analysis"]["diversity_score"] = diversity_score
        
        if diversity_score < self.spawn_threshold["lack_of_diversity"]:
            needs["needs_agent"] = True
            needs["reason"] = "lack_of_diversity"
            needs["role"] = "innovate"
            needs["urgency"] = 1.0 - diversity_score
            return needs
        
        stalemate_score = self._detect_stalemate(proposals, context)
        needs["analysis"]["stalemate_score"] = stalemate_score
        
        if stalemate_score > self.spawn_threshold["stalemate"]:
            needs["needs_agent"] = True
            needs["reason"] = "stalemate"
            needs["role"] = "mediate"
            needs["urgency"] = stalemate_score
            return needs
        
        challenge_ratio = self._assess_challenge_level(proposals)
        needs["analysis"]["challenge_ratio"] = challenge_ratio
        
        if challenge_ratio < self.spawn_threshold["insufficient_challenge"]:
            needs["needs_agent"] = True
            needs["reason"] = "insufficient_challenge"
            needs["role"] = "challenge"
            needs["urgency"] = 1.0 - challenge_ratio
            return needs
        
        missing_perspective = self._identify_missing_perspective(proposals, agents, context)
        needs["analysis"]["missing_perspective"] = missing_perspective
        
        if missing_perspective["score"] > self.spawn_threshold["missing_perspective"]:
            needs["needs_agent"] = True
            needs["reason"] = "missing_perspective"
            needs["role"] = missing_perspective["type"]
            needs["urgency"] = missing_perspective["score"]
            return needs
        
        conflict_level = self._assess_conflict_level(proposals)
        needs["analysis"]["conflict_level"] = conflict_level
        
        if conflict_level > self.spawn_threshold["need_mediation"]:
            needs["needs_agent"] = True
            needs["reason"] = "high_conflict"
            needs["role"] = "mediate"
            needs["urgency"] = conflict_level
            return needs
        
        return needs
    
    def _assess_diversity(self, proposals: List[Any], agents: List[SentientAgent]) -> float:
        """Measure diversity of proposals and agent perspectives"""
        
        if len(proposals) < 2:
            return 0.5
        
        all_words = set()
        proposal_word_sets = []
        
        for proposal in proposals:
            words = set(proposal.content.lower().split())
            proposal_word_sets.append(words)
            all_words.update(words)
        
        similarities = []
        for i in range(len(proposal_word_sets)):
            for j in range(i + 1, len(proposal_word_sets)):
                intersection = len(proposal_word_sets[i] & proposal_word_sets[j])
                union = len(proposal_word_sets[i] | proposal_word_sets[j])
                similarity = intersection / union if union > 0 else 0
                similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.5
        diversity_score = 1.0 - avg_similarity
        
        personality_variance = 0.0
        if len(agents) > 1:
            creativity_values = [a.personality.get("creativity", 0.5) for a in agents]
            analytical_values = [a.personality.get("analytical_depth", 0.5) for a in agents]
            
            creativity_variance = max(creativity_values) - min(creativity_values)
            analytical_variance = max(analytical_values) - min(analytical_values)
            personality_variance = (creativity_variance + analytical_variance) / 2
        
        combined_diversity = (diversity_score * 0.7 + personality_variance * 0.3)
        
        return combined_diversity
    
    def _detect_stalemate(self, proposals: List[Any], context: Dict[str, Any]) -> float:
        """Detect if debate is in a stalemate"""
        
        if len(proposals) < 2:
            return 0.0
        
        scores = [p.score for p in proposals]
        score_range = max(scores) - min(scores)
        
        if score_range < 10:
            stalemate_indicator = 0.8
        elif score_range < 20:
            stalemate_indicator = 0.5
        else:
            stalemate_indicator = 0.2
        
        total_challenges = sum(len(p.challenges) for p in proposals)
        total_rebuttals = sum(len(p.rebuttals) for p in proposals)
        
        if total_challenges > 0 and total_rebuttals == total_challenges:
            stalemate_indicator += 0.2
        
        return min(1.0, stalemate_indicator)
    
    def _assess_challenge_level(self, proposals: List[Any]) -> float:
        """Assess how much proposals are being challenged"""
        
        if not proposals:
            return 0.5
        
        total_proposals = len(proposals)
        total_challenges = sum(len(p.challenges) for p in proposals)
        
        challenge_ratio = total_challenges / total_proposals if total_proposals > 0 else 0
        
        return min(1.0, challenge_ratio / 2.0)
    
    def _identify_missing_perspective(self, proposals: List[Any], 
                                     agents: List[SentientAgent],
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify what perspective is missing from the debate"""
        
        problem = context.get("problem", "").lower()
        
        perspective_keywords = {
            "analyze": ["data", "evidence", "research", "study", "analysis", "metrics"],
            "ethics": ["ethical", "moral", "right", "wrong", "values", "principles"],
            "innovate": ["innovative", "creative", "novel", "breakthrough", "disruptive"],
            "implement": ["practical", "feasible", "implementation", "execution", "deploy"],
            "expert": ["technical", "specialized", "domain", "expertise", "professional"]
        }
        
        proposal_text = " ".join([p.content.lower() for p in proposals])
        
        missing_scores = {}
        for perspective, keywords in perspective_keywords.items():
            keyword_count = sum(1 for kw in keywords if kw in proposal_text)
            coverage = keyword_count / len(keywords)
            missing_scores[perspective] = 1.0 - coverage
        
        if not agents:
            return {"score": 0.5, "type": "analyze"}
        
        avg_analytical = sum(a.personality.get("analytical_depth", 0.5) for a in agents) / len(agents)
        avg_creativity = sum(a.personality.get("creativity", 0.5) for a in agents) / len(agents)
        
        if avg_analytical < 0.5:
            missing_scores["analyze"] += 0.3
        if avg_creativity < 0.5:
            missing_scores["innovate"] += 0.3
        
        max_missing = max(missing_scores.items(), key=lambda x: x[1])
        
        return {
            "score": min(1.0, max_missing[1]),
            "type": max_missing[0]
        }
    
    def _assess_conflict_level(self, proposals: List[Any]) -> float:
        """Assess the level of conflict in the debate"""
        
        if not proposals:
            return 0.0
        
        total_challenges = sum(len(p.challenges) for p in proposals)
        total_proposals = len(proposals)
        
        challenge_intensity = total_challenges / total_proposals if total_proposals > 0 else 0
        
        unrebuted_challenges = 0
        for proposal in proposals:
            unrebuted = len(proposal.challenges) - len(proposal.rebuttals)
            unrebuted_challenges += max(0, unrebuted)
        
        conflict_score = (challenge_intensity * 0.6 + (unrebuted_challenges / max(total_challenges, 1)) * 0.4)
        
        return min(1.0, conflict_score)
    
    def spawn_agent(self, role: str, debate_system: Any, reason: str) -> Optional[SentientAgent]:
        """Spawn a new agent during the debate"""
        
        agent = self.agent_factory.create_role_specific_agent(role, {})
        
        debate_system.agents[agent.agent_id] = agent
        self.spawned_agents.append(agent.agent_id)
        
        spawn_record = {
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "role": role,
            "reason": reason,
            "timestamp": time.time(),
            "archetype": self.agent_factory.get_agent_info(agent.agent_id)["archetype"]
        }
        
        self.spawn_history.append(spawn_record)
        
        debate_system.log(f"\n[{self.name}] SPAWNING NEW AGENT:")
        debate_system.log(f"  Name: {agent.name}")
        debate_system.log(f"  Role: {role}")
        debate_system.log(f"  Reason: {reason}")
        debate_system.log(f"  Archetype: {spawn_record['archetype']}")
        
        return agent
    
    def terminate_agent(self, agent_id: str, debate_system: Any, reason: str) -> bool:
        """Terminate an agent during the debate"""
        
        if agent_id not in debate_system.agents:
            return False
        
        agent = debate_system.agents[agent_id]
        
        if (time.time() - agent.created_at) < self.resource_limits["min_agent_lifetime"]:
            return False
        
        agent.deactivate()
        self.terminated_agents.append(agent_id)
        
        debate_system.log(f"\n[{self.name}] TERMINATING AGENT:")
        debate_system.log(f"  Name: {agent.name}")
        debate_system.log(f"  Reason: {reason}")
        debate_system.log(f"  Lifetime: {time.time() - agent.created_at:.2f}s")
        
        del debate_system.agents[agent_id]
        
        return True
    
    def optimize_agent_pool(self, debate_system: Any, proposals: List[Any]) -> List[str]:
        """Optimize the agent pool by removing underperforming agents"""
        
        if len(debate_system.agents) <= 3:
            return []
        
        agent_performance = []
        for agent in debate_system.agents.values():
            if agent.agent_id in self.spawned_agents:
                performance = {
                    "agent_id": agent.agent_id,
                    "agent": agent,
                    "score": agent.score,
                    "contributions": len(agent.proposals_made) + len(agent.challenges_made) + len(agent.rebuttals_made),
                    "lifetime": time.time() - agent.created_at
                }
                agent_performance.append(performance)
        
        if not agent_performance:
            return []
        
        agent_performance.sort(key=lambda x: (x["contributions"], x["score"]))
        
        terminated = []
        for perf in agent_performance[:2]:
            if perf["contributions"] == 0 and perf["lifetime"] > 5.0:
                if self.terminate_agent(perf["agent_id"], debate_system, "no_contribution"):
                    terminated.append(perf["agent_id"])
        
        return terminated
    
    def get_fluid_resourcing_stats(self) -> Dict[str, Any]:
        """Get statistics about fluid resourcing"""
        
        return {
            "total_spawned": len(self.spawned_agents),
            "total_terminated": len(self.terminated_agents),
            "currently_active_spawned": len([a for a in self.spawned_agents if a not in self.terminated_agents]),
            "spawn_history": self.spawn_history,
            "spawn_reasons": self._count_spawn_reasons()
        }
    
    def _count_spawn_reasons(self) -> Dict[str, int]:
        """Count spawn reasons"""
        reasons = {}
        for record in self.spawn_history:
            reason = record["reason"]
            reasons[reason] = reasons.get(reason, 0) + 1
        return reasons
