import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class PatternType(Enum):
    ROUTING = "routing"
    CONSENSUS = "consensus"
    AGENT_SELECTION = "agent_selection"
    TASK_DECOMPOSITION = "task_decomposition"
    ERROR_RECOVERY = "error_recovery"
    OPTIMIZATION = "optimization"


@dataclass
class WisdomPattern:
    pattern_id: str
    pattern_type: PatternType
    condition: Dict[str, Any]
    recommendation: Dict[str, Any]
    confidence: float
    evidence_count: int
    success_rate: float
    avg_performance: float
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_from_execution(self, success: bool, performance: float) -> None:
        self.evidence_count += 1
        
        self.success_rate = (
            (self.success_rate * (self.evidence_count - 1) + (1.0 if success else 0.0))
            / self.evidence_count
        )
        
        self.avg_performance = (
            (self.avg_performance * (self.evidence_count - 1) + performance)
            / self.evidence_count
        )
        
        self.confidence = min(1.0, self.evidence_count / 10.0) * self.success_rate
        
        self.last_updated = time.time()
    
    def matches_context(self, context: Dict[str, Any], threshold: float = 0.7) -> float:
        if not self.condition:
            return 0.0
        
        matches = 0
        total = len(self.condition)
        
        for key, expected_value in self.condition.items():
            if key in context:
                if isinstance(expected_value, (list, set)):
                    if context[key] in expected_value:
                        matches += 1
                elif context[key] == expected_value:
                    matches += 1
                elif isinstance(expected_value, str) and isinstance(context[key], str):
                    if expected_value.lower() in context[key].lower():
                        matches += 0.5
        
        match_score = matches / total if total > 0 else 0.0
        return match_score


class WisdomLayer:
    def __init__(
        self,
        min_evidence: int = 3,
        min_confidence: float = 0.6,
        pattern_decay: float = 0.95
    ):
        self.min_evidence = min_evidence
        self.min_confidence = min_confidence
        self.pattern_decay = pattern_decay
        
        self.patterns: Dict[PatternType, List[WisdomPattern]] = {
            pt: [] for pt in PatternType
        }
        
        self.execution_history: List[Dict[str, Any]] = []
        
        self.statistics = {
            "total_patterns": 0,
            "patterns_applied": 0,
            "patterns_created": 0,
            "avg_confidence": 0.0
        }
    
    def record_execution(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any],
        decision: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        execution = {
            "task": task,
            "context": context,
            "decision": decision,
            "result": result,
            "timestamp": time.time(),
            "success": result.get("success", False),
            "performance": result.get("performance_score", 0.0)
        }
        
        self.execution_history.append(execution)
        
        self._update_matching_patterns(execution)
        
        if len(self.execution_history) % 10 == 0:
            self._extract_new_patterns()
    
    def get_recommendation(
        self,
        pattern_type: PatternType,
        context: Dict[str, Any],
        min_match_score: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        patterns = self.patterns[pattern_type]
        
        valid_patterns = [
            p for p in patterns
            if p.confidence >= self.min_confidence
            and p.evidence_count >= self.min_evidence
        ]
        
        scored_patterns = [
            (p, p.matches_context(context, min_match_score))
            for p in valid_patterns
        ]
        
        scored_patterns = [
            (p, score) for p, score in scored_patterns
            if score >= min_match_score
        ]
        
        if not scored_patterns:
            return None
        
        scored_patterns.sort(key=lambda x: (x[1], x[0].confidence), reverse=True)
        
        best_pattern, match_score = scored_patterns[0]
        
        self.statistics["patterns_applied"] += 1
        
        return {
            "recommendation": best_pattern.recommendation,
            "confidence": best_pattern.confidence,
            "match_score": match_score,
            "pattern_id": best_pattern.pattern_id,
            "evidence_count": best_pattern.evidence_count,
            "success_rate": best_pattern.success_rate
        }
    
    def _update_matching_patterns(self, execution: Dict[str, Any]) -> None:
        context = execution["context"]
        decision = execution["decision"]
        success = execution["success"]
        performance = execution["performance"]
        
        for pattern_type in PatternType:
            decision_type = decision.get("type")
            
            if pattern_type.value == decision_type:
                for pattern in self.patterns[pattern_type]:
                    match_score = pattern.matches_context(context)
                    
                    if match_score >= 0.7:
                        if self._decision_matches_recommendation(decision, pattern.recommendation):
                            pattern.update_from_execution(success, performance)
    
    def _extract_new_patterns(self) -> None:
        recent_executions = self.execution_history[-50:]
        
        grouped = defaultdict(list)
        for execution in recent_executions:
            decision_type = execution["decision"].get("type")
            if decision_type:
                grouped[decision_type].append(execution)
        
        for decision_type, executions in grouped.items():
            if len(executions) < self.min_evidence:
                continue
            
            successful = [e for e in executions if e["success"]]
            
            if len(successful) < self.min_evidence:
                continue
            
            common_context = self._find_common_context(successful)
            common_decision = self._find_common_decision(successful)
            
            if not common_context or not common_decision:
                continue
            
            pattern_type = self._decision_type_to_pattern_type(decision_type)
            if not pattern_type:
                continue
            
            existing = self._find_similar_pattern(pattern_type, common_context)
            
            if existing:
                continue
            
            success_rate = len(successful) / len(executions)
            avg_performance = sum(e["performance"] for e in successful) / len(successful)
            
            pattern_id = self._generate_pattern_id(pattern_type, common_context)
            
            new_pattern = WisdomPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                condition=common_context,
                recommendation=common_decision,
                confidence=min(1.0, len(successful) / 10.0) * success_rate,
                evidence_count=len(successful),
                success_rate=success_rate,
                avg_performance=avg_performance
            )
            
            self.patterns[pattern_type].append(new_pattern)
            self.statistics["patterns_created"] += 1
            self.statistics["total_patterns"] += 1
    
    def _find_common_context(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not executions:
            return {}
        
        common = {}
        
        first_context = executions[0]["context"]
        
        for key in first_context.keys():
            values = [e["context"].get(key) for e in executions if key in e["context"]]
            
            if len(values) < len(executions) * 0.8:
                continue
            
            if all(v == values[0] for v in values):
                common[key] = values[0]
            elif isinstance(values[0], str):
                common_words = set(values[0].lower().split())
                for v in values[1:]:
                    if isinstance(v, str):
                        common_words &= set(v.lower().split())
                
                if common_words:
                    common[key] = list(common_words)
        
        return common
    
    def _find_common_decision(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not executions:
            return {}
        
        common = {}
        
        first_decision = executions[0]["decision"]
        
        for key in first_decision.keys():
            values = [e["decision"].get(key) for e in executions if key in e["decision"]]
            
            if len(values) < len(executions) * 0.8:
                continue
            
            if all(v == values[0] for v in values):
                common[key] = values[0]
        
        return common
    
    def _decision_type_to_pattern_type(self, decision_type: str) -> Optional[PatternType]:
        mapping = {
            "routing": PatternType.ROUTING,
            "consensus": PatternType.CONSENSUS,
            "agent_selection": PatternType.AGENT_SELECTION,
            "task_decomposition": PatternType.TASK_DECOMPOSITION,
            "error_recovery": PatternType.ERROR_RECOVERY,
            "optimization": PatternType.OPTIMIZATION
        }
        return mapping.get(decision_type)
    
    def _find_similar_pattern(
        self,
        pattern_type: PatternType,
        context: Dict[str, Any]
    ) -> Optional[WisdomPattern]:
        for pattern in self.patterns[pattern_type]:
            if pattern.condition == context:
                return pattern
        return None
    
    def _decision_matches_recommendation(
        self,
        decision: Dict[str, Any],
        recommendation: Dict[str, Any]
    ) -> bool:
        for key, value in recommendation.items():
            if key not in decision:
                return False
            if decision[key] != value:
                return False
        return True
    
    def _generate_pattern_id(self, pattern_type: PatternType, context: Dict[str, Any]) -> str:
        context_str = str(sorted(context.items()))
        hash_str = hashlib.md5(f"{pattern_type.value}_{context_str}".encode()).hexdigest()
        return f"pattern_{hash_str[:12]}"
    
    def get_wisdom_summary(self) -> Dict[str, Any]:
        pattern_stats = {}
        for pattern_type, patterns in self.patterns.items():
            valid_patterns = [
                p for p in patterns
                if p.confidence >= self.min_confidence
                and p.evidence_count >= self.min_evidence
            ]
            
            pattern_stats[pattern_type.value] = {
                "total": len(patterns),
                "valid": len(valid_patterns),
                "avg_confidence": (
                    sum(p.confidence for p in valid_patterns) / len(valid_patterns)
                    if valid_patterns else 0.0
                ),
                "avg_success_rate": (
                    sum(p.success_rate for p in valid_patterns) / len(valid_patterns)
                    if valid_patterns else 0.0
                )
            }
        
        return {
            "total_patterns": self.statistics["total_patterns"],
            "patterns_applied": self.statistics["patterns_applied"],
            "patterns_created": self.statistics["patterns_created"],
            "execution_history_size": len(self.execution_history),
            "pattern_stats": pattern_stats
        }
    
    def prune_patterns(self, max_age_days: float = 30) -> int:
        pruned = 0
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        for pattern_type in PatternType:
            patterns = self.patterns[pattern_type]
            
            self.patterns[pattern_type] = [
                p for p in patterns
                if (current_time - p.last_updated) < max_age_seconds
                or p.evidence_count >= self.min_evidence * 2
            ]
            
            pruned += len(patterns) - len(self.patterns[pattern_type])
        
        self.statistics["total_patterns"] -= pruned
        return pruned
