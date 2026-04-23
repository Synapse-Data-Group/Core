import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class AgentCapability:
    capability_name: str
    confidence: float
    success_rate: float
    avg_performance: float
    sample_count: int
    last_updated: float = field(default_factory=time.time)


@dataclass
class CapabilityProfile:
    agent_id: str
    capabilities: Dict[str, AgentCapability]
    total_executions: int = 0
    specialization_score: float = 0.0
    versatility_score: float = 0.0
    created_at: float = field(default_factory=time.time)


class CapabilityDiscovery:
    def __init__(
        self,
        min_samples: int = 3,
        confidence_threshold: float = 0.6,
        discovery_window: int = 50
    ):
        self.min_samples = min_samples
        self.confidence_threshold = confidence_threshold
        self.discovery_window = discovery_window
        
        self.agent_profiles: Dict[str, CapabilityProfile] = {}
        self.execution_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        self.statistics = {
            "total_agents": 0,
            "total_capabilities_discovered": 0,
            "avg_capabilities_per_agent": 0.0
        }
    
    def record_execution(
        self,
        agent_id: str,
        task_type: str,
        success: bool,
        performance: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        execution = {
            "task_type": task_type,
            "success": success,
            "performance": performance,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self.execution_history[agent_id].append(execution)
        
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = CapabilityProfile(
                agent_id=agent_id,
                capabilities={}
            )
            self.statistics["total_agents"] += 1
        
        profile = self.agent_profiles[agent_id]
        profile.total_executions += 1
        
        if len(self.execution_history[agent_id]) % 10 == 0:
            self._update_capabilities(agent_id)
    
    def _update_capabilities(self, agent_id: str) -> None:
        executions = self.execution_history[agent_id][-self.discovery_window:]
        
        task_type_stats = defaultdict(lambda: {
            "successes": 0,
            "total": 0,
            "performances": []
        })
        
        for execution in executions:
            task_type = execution["task_type"]
            task_type_stats[task_type]["total"] += 1
            
            if execution["success"]:
                task_type_stats[task_type]["successes"] += 1
            
            task_type_stats[task_type]["performances"].append(execution["performance"])
        
        profile = self.agent_profiles[agent_id]
        
        for task_type, stats in task_type_stats.items():
            if stats["total"] < self.min_samples:
                continue
            
            success_rate = stats["successes"] / stats["total"]
            avg_performance = sum(stats["performances"]) / len(stats["performances"])
            
            confidence = min(1.0, stats["total"] / (self.min_samples * 3)) * success_rate
            
            if confidence >= self.confidence_threshold:
                if task_type not in profile.capabilities:
                    self.statistics["total_capabilities_discovered"] += 1
                
                profile.capabilities[task_type] = AgentCapability(
                    capability_name=task_type,
                    confidence=confidence,
                    success_rate=success_rate,
                    avg_performance=avg_performance,
                    sample_count=stats["total"]
                )
        
        self._update_profile_scores(agent_id)
    
    def _update_profile_scores(self, agent_id: str) -> None:
        profile = self.agent_profiles[agent_id]
        
        if not profile.capabilities:
            profile.specialization_score = 0.0
            profile.versatility_score = 0.0
            return
        
        capabilities = list(profile.capabilities.values())
        
        performances = [cap.avg_performance for cap in capabilities]
        avg_performance = sum(performances) / len(performances)
        max_performance = max(performances)
        
        profile.specialization_score = max_performance
        
        profile.versatility_score = len(capabilities) / 10.0
        
        self.statistics["avg_capabilities_per_agent"] = (
            sum(len(p.capabilities) for p in self.agent_profiles.values()) /
            len(self.agent_profiles)
        )
    
    def get_agent_capabilities(self, agent_id: str) -> Optional[CapabilityProfile]:
        return self.agent_profiles.get(agent_id)
    
    def find_capable_agents(
        self,
        task_type: str,
        min_confidence: float = 0.6,
        top_k: int = 5
    ) -> List[tuple]:
        capable_agents = []
        
        for agent_id, profile in self.agent_profiles.items():
            if task_type in profile.capabilities:
                capability = profile.capabilities[task_type]
                
                if capability.confidence >= min_confidence:
                    score = (
                        capability.confidence * 0.4 +
                        capability.success_rate * 0.3 +
                        capability.avg_performance * 0.3
                    )
                    
                    capable_agents.append((agent_id, score, capability))
        
        capable_agents.sort(key=lambda x: x[1], reverse=True)
        
        return capable_agents[:top_k]
    
    def get_best_agent_for_task(
        self,
        task_type: str,
        min_confidence: float = 0.6
    ) -> Optional[str]:
        capable = self.find_capable_agents(task_type, min_confidence, top_k=1)
        
        if capable:
            return capable[0][0]
        
        return None
    
    def get_agent_specialization(self, agent_id: str) -> Optional[str]:
        if agent_id not in self.agent_profiles:
            return None
        
        profile = self.agent_profiles[agent_id]
        
        if not profile.capabilities:
            return None
        
        best_capability = max(
            profile.capabilities.values(),
            key=lambda c: c.confidence * c.avg_performance
        )
        
        return best_capability.capability_name
    
    def get_versatile_agents(self, min_capabilities: int = 3) -> List[tuple]:
        versatile = []
        
        for agent_id, profile in self.agent_profiles.items():
            if len(profile.capabilities) >= min_capabilities:
                versatile.append((agent_id, profile.versatility_score, len(profile.capabilities)))
        
        versatile.sort(key=lambda x: x[1], reverse=True)
        
        return versatile
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "agents_with_capabilities": sum(
                1 for p in self.agent_profiles.values()
                if p.capabilities
            ),
            "total_executions": sum(
                p.total_executions for p in self.agent_profiles.values()
            )
        }
    
    def export_capabilities(self) -> Dict[str, Any]:
        return {
            agent_id: {
                "capabilities": {
                    cap_name: {
                        "confidence": cap.confidence,
                        "success_rate": cap.success_rate,
                        "avg_performance": cap.avg_performance,
                        "sample_count": cap.sample_count
                    }
                    for cap_name, cap in profile.capabilities.items()
                },
                "specialization_score": profile.specialization_score,
                "versatility_score": profile.versatility_score,
                "total_executions": profile.total_executions
            }
            for agent_id, profile in self.agent_profiles.items()
        }
