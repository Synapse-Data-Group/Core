import uuid
import time
import copy
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DebateFork:
    fork_id: str
    parent_debate_id: str
    fork_point: str
    exploration_focus: str
    agents: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed: bool = False
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fork_id": self.fork_id,
            "parent_debate_id": self.parent_debate_id,
            "fork_point": self.fork_point,
            "exploration_focus": self.exploration_focus,
            "agent_count": len(self.agents),
            "completed": self.completed,
            "created_at": self.created_at,
            "result_summary": self._summarize_result() if self.result else None
        }
    
    def _summarize_result(self) -> Dict[str, Any]:
        if not self.result:
            return {}
        
        return {
            "decision": self.result.get("final_decision", {}).get("decision", "Unknown"),
            "confidence": self.result.get("final_decision", {}).get("confidence", 0),
            "duration": self.result.get("duration_seconds", 0)
        }


class ForkManager:
    def __init__(self):
        self.forks: Dict[str, DebateFork] = {}
        self.fork_counter = 0
        self.synthesis_history: List[Dict[str, Any]] = []
    
    def should_fork_debate(self, proposals: List[Any], context: Dict[str, Any]) -> bool:
        """Determine if debate should be forked"""
        
        if len(proposals) < 2:
            return False
        
        scores = [p.score for p in proposals]
        score_range = max(scores) - min(scores)
        
        if score_range < 10:
            return True
        
        total_challenges = sum(len(p.challenges) for p in proposals)
        total_rebuttals = sum(len(p.rebuttals) for p in proposals)
        
        if total_challenges > 0 and total_rebuttals == total_challenges:
            return True
        
        return False
    
    def create_fork(self, parent_debate_id: str, fork_point: str, 
                   exploration_focus: str, agent_ids: List[str]) -> DebateFork:
        """Create a new debate fork"""
        
        self.fork_counter += 1
        fork_id = f"fork_{self.fork_counter}_{str(uuid.uuid4())[:8]}"
        
        fork = DebateFork(
            fork_id=fork_id,
            parent_debate_id=parent_debate_id,
            fork_point=fork_point,
            exploration_focus=exploration_focus,
            agents=agent_ids.copy()
        )
        
        self.forks[fork_id] = fork
        
        return fork
    
    def execute_fork(self, fork: DebateFork, debate_system_class: Any, 
                    problem: str, agents_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a forked debate"""
        
        forked_debate = debate_system_class(
            problem=f"{problem} (Exploring: {fork.exploration_focus})"
        )
        
        for agent_id in fork.agents:
            if agent_id in agents_dict:
                original_agent = agents_dict[agent_id]
                
                forked_agent = forked_debate.create_agent(
                    f"{original_agent.name}_fork",
                    personality=copy.deepcopy(original_agent.personality)
                )
        
        result = forked_debate.run_debate(max_rounds=2, enable_fluid_resourcing=False)
        
        fork.result = result
        fork.completed = True
        
        return result
    
    def synthesize_forks(self, forks: List[DebateFork]) -> Dict[str, Any]:
        """Synthesize results from multiple forks"""
        
        if not forks:
            return {"synthesis": "No forks to synthesize"}
        
        completed_forks = [f for f in forks if f.completed and f.result]
        
        if not completed_forks:
            return {"synthesis": "No completed forks"}
        
        decisions = []
        for fork in completed_forks:
            if fork.result and "final_decision" in fork.result:
                decisions.append({
                    "fork_id": fork.fork_id,
                    "focus": fork.exploration_focus,
                    "decision": fork.result["final_decision"]["decision"],
                    "confidence": fork.result["final_decision"]["confidence"],
                    "score": fork.result["final_decision"]["winning_proposal"]["score"]
                })
        
        if not decisions:
            return {"synthesis": "No valid decisions from forks"}
        
        best_fork = max(decisions, key=lambda x: x["confidence"] * x["score"])
        
        synthesis = {
            "synthesis_method": "confidence_weighted",
            "forks_analyzed": len(completed_forks),
            "best_fork": best_fork,
            "all_decisions": decisions,
            "consensus_level": self._calculate_consensus(decisions),
            "recommendation": self._generate_recommendation(decisions, best_fork),
            "timestamp": time.time()
        }
        
        self.synthesis_history.append(synthesis)
        
        return synthesis
    
    def _calculate_consensus(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate consensus level across fork decisions"""
        
        if len(decisions) < 2:
            return 1.0
        
        decision_texts = [d["decision"].lower() for d in decisions]
        
        similarities = []
        for i in range(len(decision_texts)):
            for j in range(i + 1, len(decision_texts)):
                words1 = set(decision_texts[i].split())
                words2 = set(decision_texts[j].split())
                
                if words1 and words2:
                    similarity = len(words1 & words2) / len(words1 | words2)
                    similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.5
    
    def _generate_recommendation(self, decisions: List[Dict[str, Any]], 
                                 best_fork: Dict[str, Any]) -> str:
        """Generate synthesis recommendation"""
        
        recommendation = f"Based on parallel exploration of {len(decisions)} solution paths, "
        recommendation += f"the strongest approach is from the '{best_fork['focus']}' exploration. "
        recommendation += f"Decision: {best_fork['decision']} "
        recommendation += f"(Confidence: {best_fork['confidence']:.1%}). "
        
        consensus = self._calculate_consensus(decisions)
        if consensus > 0.7:
            recommendation += "High consensus across all explorations supports this direction."
        elif consensus > 0.4:
            recommendation += "Moderate agreement across explorations, with some divergence in approaches."
        else:
            recommendation += "Significant divergence in explorations suggests multiple valid paths."
        
        return recommendation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get fork statistics"""
        
        completed = sum(1 for f in self.forks.values() if f.completed)
        
        return {
            "total_forks": len(self.forks),
            "completed_forks": completed,
            "pending_forks": len(self.forks) - completed,
            "total_syntheses": len(self.synthesis_history),
            "active_forks": [f.to_dict() for f in self.forks.values() if not f.completed]
        }


class ParallelDebateOrchestrator:
    """Orchestrates parallel debate forks"""
    
    def __init__(self, debate_system_class: Any):
        self.debate_system_class = debate_system_class
        self.fork_manager = ForkManager()
        self.orchestration_log: List[str] = []
    
    def run_parallel_debate(self, problem: str, initial_agents: List[Any], 
                          max_forks: int = 3) -> Dict[str, Any]:
        """Run debate with parallel forking"""
        
        self.log("Starting parallel debate orchestration")
        
        main_debate = self.debate_system_class(problem)
        
        agents_dict = {}
        for agent in initial_agents:
            created_agent = main_debate.create_agent(
                agent.name if hasattr(agent, 'name') else f"Agent_{len(agents_dict)}",
                personality=agent.personality if hasattr(agent, 'personality') else None
            )
            agents_dict[created_agent.agent_id] = created_agent
        
        self.log(f"Running main debate with {len(agents_dict)} agents")
        main_result = main_debate.run_debate(max_rounds=2, enable_fluid_resourcing=False)
        
        if self.fork_manager.should_fork_debate(main_debate.proposals, {}):
            self.log("Stalemate detected - forking debate")
            
            fork_focuses = [
                "conservative_approach",
                "innovative_solution",
                "balanced_compromise"
            ]
            
            forks = []
            for focus in fork_focuses[:max_forks]:
                fork = self.fork_manager.create_fork(
                    main_debate.system_id,
                    "post_initial_debate",
                    focus,
                    list(agents_dict.keys())
                )
                
                self.log(f"Executing fork: {focus}")
                fork_result = self.fork_manager.execute_fork(
                    fork,
                    self.debate_system_class,
                    problem,
                    agents_dict
                )
                
                forks.append(fork)
            
            self.log("Synthesizing fork results")
            synthesis = self.fork_manager.synthesize_forks(forks)
            
            return {
                "main_result": main_result,
                "forks": [f.to_dict() for f in forks],
                "synthesis": synthesis,
                "orchestration_log": self.orchestration_log,
                "forked": True
            }
        
        else:
            self.log("No fork needed - main debate conclusive")
            return {
                "main_result": main_result,
                "forks": [],
                "synthesis": None,
                "orchestration_log": self.orchestration_log,
                "forked": False
            }
    
    def log(self, message: str):
        """Log orchestration event"""
        timestamp = time.time()
        log_entry = f"[{timestamp}] {message}"
        self.orchestration_log.append(log_entry)
        print(log_entry)
