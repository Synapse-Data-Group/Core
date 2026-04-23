import random
import time
from typing import List, Dict, Any, Optional
from learning_engine import ExperienceMemory, QLearningEngine


class SentientModerator:
    def __init__(self, moderator_id: str, name: str, strategy: str = "adaptive"):
        self.moderator_id = moderator_id
        self.name = name
        self.strategy = strategy
        self.evaluation_history: List[Dict[str, Any]] = []
        
        self.memory = ExperienceMemory(capacity=5000)
        self.q_learning = QLearningEngine(
            learning_rate=0.15,
            discount_factor=0.9,
            exploration_rate=0.2,
            exploration_decay=0.99
        )
        
        self.scoring_weights = {
            "content_length": 0.1,
            "challenge_penalty": 0.15,
            "rebuttal_bonus": 0.2,
            "keyword_quality": 0.15,
            "coherence": 0.2,
            "novelty": 0.2
        }
        
        self.debates_moderated = 0
        self.decision_accuracy_history: List[float] = []
    
    def evaluate_proposal(self, proposal: Any, all_proposals: List[Any], context: Dict[str, Any]) -> float:
        state = self._get_evaluation_state(proposal, all_proposals, context)
        
        scoring_strategies = ["strict", "lenient", "balanced", "innovative_focused", "evidence_focused"]
        chosen_strategy = self.q_learning.choose_action(state, scoring_strategies)
        
        base_score = 50.0
        
        content_score = self._evaluate_content_quality(proposal.content)
        base_score += content_score * self.scoring_weights["content_length"]
        
        challenge_impact = self._evaluate_challenge_impact(proposal)
        base_score += challenge_impact * self.scoring_weights["challenge_penalty"]
        
        rebuttal_strength = self._evaluate_rebuttal_strength(proposal)
        base_score += rebuttal_strength * self.scoring_weights["rebuttal_bonus"]
        
        keyword_score = self._evaluate_keywords(proposal.content, chosen_strategy)
        base_score += keyword_score * self.scoring_weights["keyword_quality"]
        
        coherence_score = self._evaluate_coherence(proposal.content)
        base_score += coherence_score * self.scoring_weights["coherence"]
        
        novelty_score = self._evaluate_novelty(proposal, all_proposals)
        base_score += novelty_score * self.scoring_weights["novelty"]
        
        if chosen_strategy == "strict":
            base_score *= 0.9
        elif chosen_strategy == "lenient":
            base_score *= 1.1
        elif chosen_strategy == "innovative_focused":
            if "innovative" in proposal.content.lower() or "novel" in proposal.content.lower():
                base_score *= 1.15
        elif chosen_strategy == "evidence_focused":
            if "evidence" in proposal.content.lower() or "data" in proposal.content.lower():
                base_score *= 1.15
        
        similar_past_evaluations = self.memory.recall_similar(proposal.content, k=5)
        if similar_past_evaluations:
            avg_past_score = sum(exp["outcome"] for exp in similar_past_evaluations) / len(similar_past_evaluations)
            base_score = base_score * 0.7 + (avg_past_score * 100) * 0.3
        
        final_score = max(0.0, min(100.0, base_score))
        
        self.memory.add_experience(
            state=state,
            action=chosen_strategy,
            outcome=final_score / 100,
            context={"proposal_id": proposal.proposal_id, "timestamp": time.time()}
        )
        
        return final_score
    
    def _get_evaluation_state(self, proposal: Any, all_proposals: List[Any], context: Dict[str, Any]) -> str:
        proposal_count = len(all_proposals)
        challenge_count = len(proposal.challenges)
        rebuttal_count = len(proposal.rebuttals)
        
        challenge_level = "high" if challenge_count > 2 else "medium" if challenge_count > 0 else "low"
        
        return f"proposals_{proposal_count}_challenges_{challenge_level}_rebuttals_{rebuttal_count}"
    
    def _evaluate_content_quality(self, content: str) -> float:
        length = len(content)
        
        if length < 50:
            return -20.0
        elif length < 100:
            return 0.0
        elif length < 200:
            return 10.0
        elif length < 400:
            return 15.0
        else:
            return 10.0
    
    def _evaluate_challenge_impact(self, proposal: Any) -> float:
        challenge_count = len(proposal.challenges)
        rebuttal_count = len(proposal.rebuttals)
        
        net_challenges = challenge_count - rebuttal_count
        
        if net_challenges <= 0:
            return 5.0
        elif net_challenges == 1:
            return -5.0
        elif net_challenges == 2:
            return -10.0
        else:
            return -15.0
    
    def _evaluate_rebuttal_strength(self, proposal: Any) -> float:
        rebuttal_count = len(proposal.rebuttals)
        
        if rebuttal_count == 0:
            return 0.0
        
        base_bonus = rebuttal_count * 8.0
        
        rebuttal_quality = 0.0
        for rebuttal in proposal.rebuttals:
            if len(rebuttal.content) > 100:
                rebuttal_quality += 2.0
            if "evidence" in rebuttal.content.lower() or "data" in rebuttal.content.lower():
                rebuttal_quality += 3.0
            if "context" in rebuttal.content.lower():
                rebuttal_quality += 2.0
        
        return base_bonus + rebuttal_quality
    
    def _evaluate_keywords(self, content: str, strategy: str) -> float:
        content_lower = content.lower()
        
        positive_keywords = {
            "comprehensive": 5.0,
            "innovative": 5.0,
            "analytical": 7.0,
            "data-driven": 7.0,
            "evidence": 6.0,
            "systematic": 6.0,
            "phased": 6.0,
            "incremental": 5.0,
            "metrics": 7.0,
            "measurable": 7.0,
            "proven": 5.0,
            "validated": 6.0,
            "research": 5.0,
            "analysis": 5.0,
            "optimize": 5.0,
            "efficient": 4.0,
            "effective": 4.0,
            "robust": 5.0,
            "scalable": 5.0,
            "sustainable": 5.0
        }
        
        negative_keywords = {
            "maybe": -2.0,
            "possibly": -2.0,
            "unclear": -3.0,
            "uncertain": -3.0,
            "vague": -4.0
        }
        
        score = 0.0
        
        for keyword, value in positive_keywords.items():
            if keyword in content_lower:
                score += value
        
        for keyword, value in negative_keywords.items():
            if keyword in content_lower:
                score += value
        
        return score
    
    def _evaluate_coherence(self, content: str) -> float:
        sentences = content.split('.')
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])
        
        if sentence_count < 2:
            return -5.0
        elif sentence_count < 4:
            return 5.0
        elif sentence_count < 7:
            return 10.0
        else:
            return 5.0
    
    def _evaluate_novelty(self, proposal: Any, all_proposals: List[Any]) -> float:
        if len(all_proposals) <= 1:
            return 5.0
        
        proposal_words = set(proposal.content.lower().split())
        
        similarity_scores = []
        for other_proposal in all_proposals:
            if other_proposal.proposal_id == proposal.proposal_id:
                continue
            
            other_words = set(other_proposal.content.lower().split())
            
            if len(proposal_words | other_words) > 0:
                similarity = len(proposal_words & other_words) / len(proposal_words | other_words)
                similarity_scores.append(similarity)
        
        if similarity_scores:
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            novelty_score = (1 - avg_similarity) * 20
            return novelty_score
        
        return 5.0
    
    def score_all_proposals(self, proposals: List[Any], context: Dict[str, Any]) -> Dict[str, float]:
        scores = {}
        for proposal in proposals:
            score = self.evaluate_proposal(proposal, proposals, context)
            proposal.score = score
            scores[proposal.proposal_id] = score
        
        self.evaluation_history.append({
            "timestamp": time.time(),
            "scores": scores.copy(),
            "context": context
        })
        
        return scores
    
    def resolve_debate(self, proposals: List[Any], agents: List[Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if not proposals:
            return {
                "decision": "No proposals submitted",
                "winning_proposal": None,
                "reasoning": "Debate concluded with no proposals to evaluate",
                "confidence": 0.0
            }
        
        scores = self.score_all_proposals(proposals, context)
        
        winning_proposal = max(proposals, key=lambda p: p.score)
        
        score_variance = self._calculate_score_variance(proposals)
        confidence = self._calculate_decision_confidence(winning_proposal, proposals, score_variance)
        
        reasoning = self._generate_adaptive_reasoning(winning_proposal, proposals, agents, confidence)
        
        decision = {
            "decision": f"Accept proposal from {winning_proposal.agent_name}",
            "winning_proposal": winning_proposal.to_dict(),
            "all_scores": scores,
            "reasoning": reasoning,
            "confidence": confidence,
            "score_variance": score_variance,
            "timestamp": time.time()
        }
        
        self.debates_moderated += 1
        
        return decision
    
    def _calculate_score_variance(self, proposals: List[Any]) -> float:
        if len(proposals) <= 1:
            return 0.0
        
        scores = [p.score for p in proposals]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        return variance ** 0.5
    
    def _calculate_decision_confidence(self, winning_proposal: Any, all_proposals: List[Any], variance: float) -> float:
        if len(all_proposals) <= 1:
            return 0.5
        
        sorted_proposals = sorted(all_proposals, key=lambda p: p.score, reverse=True)
        score_gap = sorted_proposals[0].score - sorted_proposals[1].score
        
        gap_confidence = min(score_gap / 30.0, 1.0)
        
        variance_confidence = max(0.0, 1.0 - (variance / 20.0))
        
        rebuttal_confidence = len(winning_proposal.rebuttals) / max(len(winning_proposal.challenges), 1)
        rebuttal_confidence = min(rebuttal_confidence, 1.0)
        
        overall_confidence = (gap_confidence * 0.4 + variance_confidence * 0.3 + rebuttal_confidence * 0.3)
        
        return overall_confidence
    
    def _generate_adaptive_reasoning(self, winning_proposal: Any, all_proposals: List[Any], 
                                    agents: List[Any], confidence: float) -> str:
        reasoning_parts = []
        
        reasoning_parts.append(f"After evaluating {len(all_proposals)} proposals through adaptive scoring,")
        reasoning_parts.append(f"I have determined that {winning_proposal.agent_name}'s proposal is the strongest")
        reasoning_parts.append(f"with a score of {winning_proposal.score:.1f} points.")
        
        if confidence > 0.7:
            reasoning_parts.append("This decision is made with high confidence.")
        elif confidence > 0.4:
            reasoning_parts.append("This decision is made with moderate confidence.")
        else:
            reasoning_parts.append("This decision is made with lower confidence due to close competition.")
        
        if len(winning_proposal.challenges) > 0:
            reasoning_parts.append(f"The proposal faced {len(winning_proposal.challenges)} challenges.")
            if len(winning_proposal.rebuttals) > 0:
                reasoning_parts.append(f"The proposer provided {len(winning_proposal.rebuttals)} rebuttals,")
                reasoning_parts.append("demonstrating strong defensive reasoning.")
            else:
                reasoning_parts.append("However, the core proposal remained sound despite limited rebuttals.")
        
        content_indicators = []
        if "innovative" in winning_proposal.content.lower() or "novel" in winning_proposal.content.lower():
            content_indicators.append("innovation")
        if "evidence" in winning_proposal.content.lower() or "data" in winning_proposal.content.lower():
            content_indicators.append("evidence-based reasoning")
        if "systematic" in winning_proposal.content.lower() or "analytical" in winning_proposal.content.lower():
            content_indicators.append("systematic analysis")
        
        if content_indicators:
            reasoning_parts.append(f"The proposal demonstrates {', '.join(content_indicators)}.")
        
        if self.strategy == "adaptive":
            reasoning_parts.append("This decision adapts to the specific context and learned patterns from previous debates.")
        
        similar_past = self.memory.recall_similar(winning_proposal.content, k=3)
        if similar_past and len(similar_past) > 0:
            avg_past_outcome = sum(exp["outcome"] for exp in similar_past) / len(similar_past)
            if avg_past_outcome > 0.6:
                reasoning_parts.append(f"Historical data supports similar approaches with {avg_past_outcome:.0%} success rate.")
        
        return " ".join(reasoning_parts)
    
    def enact_decision(self, decision: Dict[str, Any]) -> str:
        if decision["winning_proposal"] is None:
            return "No action taken - no valid proposals"
        
        action_log = f"ENACTING DECISION: {decision['decision']}\n"
        action_log += f"Timestamp: {decision['timestamp']}\n"
        action_log += f"Confidence Level: {decision['confidence']:.2%}\n"
        action_log += f"Reasoning: {decision['reasoning']}\n"
        action_log += f"\nImplementation Plan:\n"
        action_log += f"1. Communicate decision to all agents\n"
        action_log += f"2. Execute winning proposal according to specifications\n"
        action_log += f"3. Monitor outcomes for learning and adaptation\n"
        action_log += f"4. Update moderator knowledge base with results\n"
        
        return action_log
    
    def learn_from_debate_outcome(self, decision: Dict[str, Any], actual_outcome: float):
        self.decision_accuracy_history.append(actual_outcome)
        
        if len(self.decision_accuracy_history) > 100:
            self.decision_accuracy_history.pop(0)
        
        winning_score = decision["winning_proposal"]["score"]
        reward = (actual_outcome - 0.5) * 2
        
        for eval_record in self.evaluation_history[-5:]:
            state = f"debate_{len(eval_record['scores'])}_proposals"
            action = "evaluate"
            
            self.q_learning.update(
                state,
                action,
                reward,
                state,
                ["evaluate"]
            )
        
        if actual_outcome > 0.7:
            for weight_key in self.scoring_weights:
                self.scoring_weights[weight_key] *= random.uniform(0.95, 1.05)
        elif actual_outcome < 0.3:
            for weight_key in self.scoring_weights:
                self.scoring_weights[weight_key] *= random.uniform(0.95, 1.05)
        
        total_weight = sum(self.scoring_weights.values())
        for key in self.scoring_weights:
            self.scoring_weights[key] /= total_weight
    
    def get_stats(self) -> Dict[str, Any]:
        avg_accuracy = sum(self.decision_accuracy_history) / len(self.decision_accuracy_history) if self.decision_accuracy_history else 0.5
        
        return {
            "moderator_id": self.moderator_id,
            "name": self.name,
            "strategy": self.strategy,
            "debates_moderated": self.debates_moderated,
            "avg_decision_accuracy": avg_accuracy,
            "total_evaluations": len(self.evaluation_history),
            "scoring_weights": self.scoring_weights.copy(),
            "exploration_rate": self.q_learning.exploration_rate,
            "memory_size": len(self.memory.experiences)
        }
    
    def save_memory(self, filepath: str):
        self.memory.save(filepath)
    
    def load_memory(self, filepath: str):
        self.memory.load(filepath)
