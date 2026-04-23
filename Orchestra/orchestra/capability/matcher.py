from typing import Any, Dict, List, Optional, Tuple
from .discovery import CapabilityDiscovery


class CapabilityMatcher:
    def __init__(self, capability_discovery: CapabilityDiscovery):
        self.discovery = capability_discovery
    
    def match_task_to_agents(
        self,
        task: Dict[str, Any],
        available_agents: List[str],
        strategy: str = "best_fit"
    ) -> List[Tuple[str, float]]:
        task_type = task.get("type", "unknown")
        complexity = task.get("complexity", "moderate")
        
        if strategy == "best_fit":
            return self._best_fit_matching(task_type, available_agents)
        
        elif strategy == "load_balanced":
            return self._load_balanced_matching(task_type, available_agents)
        
        elif strategy == "specialist":
            return self._specialist_matching(task_type, available_agents)
        
        elif strategy == "generalist":
            return self._generalist_matching(task_type, available_agents)
        
        else:
            return self._best_fit_matching(task_type, available_agents)
    
    def _best_fit_matching(
        self,
        task_type: str,
        available_agents: List[str]
    ) -> List[Tuple[str, float]]:
        capable_agents = self.discovery.find_capable_agents(task_type, min_confidence=0.5)
        
        available_capable = [
            (agent_id, score)
            for agent_id, score, _ in capable_agents
            if agent_id in available_agents
        ]
        
        if not available_capable:
            return [(agent_id, 0.5) for agent_id in available_agents[:3]]
        
        return available_capable
    
    def _load_balanced_matching(
        self,
        task_type: str,
        available_agents: List[str]
    ) -> List[Tuple[str, float]]:
        agent_loads = {}
        
        for agent_id in available_agents:
            profile = self.discovery.get_agent_capabilities(agent_id)
            if profile:
                agent_loads[agent_id] = profile.total_executions
            else:
                agent_loads[agent_id] = 0
        
        sorted_by_load = sorted(agent_loads.items(), key=lambda x: x[1])
        
        capable_agents = self.discovery.find_capable_agents(task_type, min_confidence=0.5)
        capable_ids = {agent_id for agent_id, _, _ in capable_agents}
        
        result = []
        for agent_id, load in sorted_by_load:
            if agent_id in capable_ids:
                capability_score = next(
                    score for aid, score, _ in capable_agents if aid == agent_id
                )
                load_factor = 1.0 / (1.0 + load / 100.0)
                combined_score = capability_score * 0.7 + load_factor * 0.3
                result.append((agent_id, combined_score))
        
        if not result:
            result = [(agent_id, 0.5) for agent_id, _ in sorted_by_load[:3]]
        
        return result
    
    def _specialist_matching(
        self,
        task_type: str,
        available_agents: List[str]
    ) -> List[Tuple[str, float]]:
        specialists = []
        
        for agent_id in available_agents:
            specialization = self.discovery.get_agent_specialization(agent_id)
            
            if specialization == task_type:
                profile = self.discovery.get_agent_capabilities(agent_id)
                if profile:
                    specialists.append((agent_id, profile.specialization_score))
        
        specialists.sort(key=lambda x: x[1], reverse=True)
        
        if not specialists:
            return self._best_fit_matching(task_type, available_agents)
        
        return specialists
    
    def _generalist_matching(
        self,
        task_type: str,
        available_agents: List[str]
    ) -> List[Tuple[str, float]]:
        generalists = []
        
        for agent_id in available_agents:
            profile = self.discovery.get_agent_capabilities(agent_id)
            
            if profile and len(profile.capabilities) >= 3:
                if task_type in profile.capabilities:
                    capability = profile.capabilities[task_type]
                    score = profile.versatility_score * 0.6 + capability.confidence * 0.4
                    generalists.append((agent_id, score))
        
        generalists.sort(key=lambda x: x[1], reverse=True)
        
        if not generalists:
            return self._best_fit_matching(task_type, available_agents)
        
        return generalists
    
    def recommend_agent_assignment(
        self,
        tasks: List[Dict[str, Any]],
        available_agents: List[str]
    ) -> Dict[str, str]:
        assignments = {}
        agent_workload = {agent_id: 0 for agent_id in available_agents}
        
        task_priorities = sorted(
            enumerate(tasks),
            key=lambda x: x[1].get("priority", 1),
            reverse=True
        )
        
        for task_idx, task in task_priorities:
            task_id = task.get("id", f"task_{task_idx}")
            task_type = task.get("type", "unknown")
            
            candidates = self.match_task_to_agents(
                task,
                [aid for aid in available_agents if agent_workload[aid] < 3],
                strategy="load_balanced"
            )
            
            if candidates:
                best_agent = candidates[0][0]
                assignments[task_id] = best_agent
                agent_workload[best_agent] += 1
        
        return assignments
