import time
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class TaskPattern:
    pattern_id: str
    task_features: Dict[str, Any]
    success_indicators: List[str]
    failure_indicators: List[str]
    optimal_approach: Dict[str, Any]
    sample_count: int
    success_rate: float
    avg_execution_time: float
    created_at: float = field(default_factory=time.time)


class PatternExtractor:
    def __init__(self, min_samples: int = 5):
        self.min_samples = min_samples
        self.patterns: List[TaskPattern] = []
    
    def extract_patterns(
        self,
        executions: List[Dict[str, Any]]
    ) -> List[TaskPattern]:
        if len(executions) < self.min_samples:
            return []
        
        feature_groups = self._group_by_features(executions)
        
        new_patterns = []
        
        for features, group_executions in feature_groups.items():
            if len(group_executions) < self.min_samples:
                continue
            
            pattern = self._create_pattern(features, group_executions)
            if pattern:
                new_patterns.append(pattern)
                self.patterns.append(pattern)
        
        return new_patterns
    
    def _group_by_features(
        self,
        executions: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        groups = {}
        
        for execution in executions:
            features = self._extract_features(execution)
            feature_key = self._features_to_key(features)
            
            if feature_key not in groups:
                groups[feature_key] = []
            groups[feature_key].append(execution)
        
        return groups
    
    def _extract_features(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        task = execution.get("task", {})
        
        features = {
            "task_type": task.get("type", "unknown"),
            "complexity": task.get("complexity", "unknown"),
            "domain": task.get("domain", "general")
        }
        
        context = execution.get("context", {})
        if "agent_count" in context:
            features["agent_count"] = context["agent_count"]
        
        return features
    
    def _features_to_key(self, features: Dict[str, Any]) -> str:
        return "_".join(f"{k}:{v}" for k, v in sorted(features.items()))
    
    def _create_pattern(
        self,
        feature_key: str,
        executions: List[Dict[str, Any]]
    ) -> Optional[TaskPattern]:
        successful = [e for e in executions if e.get("success", False)]
        failed = [e for e in executions if not e.get("success", False)]
        
        if not successful:
            return None
        
        success_rate = len(successful) / len(executions)
        
        success_indicators = self._find_indicators(successful, "success")
        failure_indicators = self._find_indicators(failed, "failure")
        
        optimal_approach = self._find_optimal_approach(successful)
        
        avg_time = sum(e.get("execution_time", 0.0) for e in successful) / len(successful)
        
        features = dict(item.split(":") for item in feature_key.split("_"))
        
        pattern = TaskPattern(
            pattern_id=f"pattern_{feature_key}_{int(time.time())}",
            task_features=features,
            success_indicators=success_indicators,
            failure_indicators=failure_indicators,
            optimal_approach=optimal_approach,
            sample_count=len(executions),
            success_rate=success_rate,
            avg_execution_time=avg_time
        )
        
        return pattern
    
    def _find_indicators(
        self,
        executions: List[Dict[str, Any]],
        indicator_type: str
    ) -> List[str]:
        if not executions:
            return []
        
        indicators = []
        
        all_decisions = [e.get("decision", {}) for e in executions]
        
        decision_keys = set()
        for decision in all_decisions:
            decision_keys.update(decision.keys())
        
        for key in decision_keys:
            values = [d.get(key) for d in all_decisions if key in d]
            
            if len(values) < len(executions) * 0.7:
                continue
            
            value_counts = Counter(values)
            most_common = value_counts.most_common(1)
            
            if most_common and most_common[0][1] >= len(values) * 0.7:
                indicators.append(f"{key}={most_common[0][0]}")
        
        return indicators[:5]
    
    def _find_optimal_approach(
        self,
        successful_executions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not successful_executions:
            return {}
        
        top_performers = sorted(
            successful_executions,
            key=lambda e: e.get("performance", 0.0),
            reverse=True
        )[:3]
        
        optimal = {}
        
        for execution in top_performers:
            decision = execution.get("decision", {})
            for key, value in decision.items():
                if key not in optimal:
                    optimal[key] = []
                optimal[key].append(value)
        
        for key in optimal:
            value_counts = Counter(optimal[key])
            most_common = value_counts.most_common(1)
            if most_common:
                optimal[key] = most_common[0][0]
        
        return optimal
    
    def find_matching_pattern(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[TaskPattern]:
        features = {
            "task_type": task.get("type", "unknown"),
            "complexity": task.get("complexity", "unknown"),
            "domain": task.get("domain", "general")
        }
        
        if "agent_count" in context:
            features["agent_count"] = context["agent_count"]
        
        matching_patterns = []
        
        for pattern in self.patterns:
            match_score = self._calculate_match_score(features, pattern.task_features)
            
            if match_score >= 0.8:
                matching_patterns.append((pattern, match_score))
        
        if not matching_patterns:
            return None
        
        matching_patterns.sort(key=lambda x: (x[1], x[0].success_rate), reverse=True)
        
        return matching_patterns[0][0]
    
    def _calculate_match_score(
        self,
        features: Dict[str, Any],
        pattern_features: Dict[str, Any]
    ) -> float:
        if not pattern_features:
            return 0.0
        
        matches = 0
        total = len(pattern_features)
        
        for key, value in pattern_features.items():
            if key in features and features[key] == value:
                matches += 1
        
        return matches / total
    
    def get_statistics(self) -> Dict[str, Any]:
        if not self.patterns:
            return {
                "total_patterns": 0,
                "avg_success_rate": 0.0,
                "avg_sample_count": 0.0
            }
        
        return {
            "total_patterns": len(self.patterns),
            "avg_success_rate": sum(p.success_rate for p in self.patterns) / len(self.patterns),
            "avg_sample_count": sum(p.sample_count for p in self.patterns) / len(self.patterns),
            "avg_execution_time": sum(p.avg_execution_time for p in self.patterns) / len(self.patterns)
        }
