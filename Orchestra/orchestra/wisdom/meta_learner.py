import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MetaKnowledge:
    knowledge_id: str
    category: str
    insight: str
    supporting_evidence: List[str]
    confidence: float
    generality_score: float
    created_at: float = field(default_factory=time.time)
    applications: int = 0
    
    def apply(self) -> None:
        self.applications += 1


class MetaLearner:
    def __init__(self, min_pattern_count: int = 5):
        self.min_pattern_count = min_pattern_count
        self.meta_knowledge: List[MetaKnowledge] = []
        self.cross_task_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        self.statistics = {
            "total_insights": 0,
            "insights_applied": 0,
            "cross_task_patterns_found": 0
        }
    
    def analyze_cross_task_patterns(
        self,
        executions: List[Dict[str, Any]]
    ) -> List[MetaKnowledge]:
        task_groups = defaultdict(list)
        
        for execution in executions:
            task_type = execution.get("task", {}).get("type", "unknown")
            task_groups[task_type].append(execution)
        
        new_insights = []
        
        successful_strategies = self._find_successful_strategies(task_groups)
        if successful_strategies:
            new_insights.extend(successful_strategies)
        
        failure_patterns = self._find_failure_patterns(task_groups)
        if failure_patterns:
            new_insights.extend(failure_patterns)
        
        optimization_insights = self._find_optimization_insights(task_groups)
        if optimization_insights:
            new_insights.extend(optimization_insights)
        
        for insight in new_insights:
            self.meta_knowledge.append(insight)
            self.statistics["total_insights"] += 1
        
        return new_insights
    
    def _find_successful_strategies(
        self,
        task_groups: Dict[str, List[Dict[str, Any]]]
    ) -> List[MetaKnowledge]:
        insights = []
        
        strategy_success = defaultdict(lambda: {"success": 0, "total": 0, "tasks": []})
        
        for task_type, executions in task_groups.items():
            for execution in executions:
                strategy = execution.get("decision", {}).get("strategy", "unknown")
                success = execution.get("success", False)
                
                strategy_success[strategy]["total"] += 1
                if success:
                    strategy_success[strategy]["success"] += 1
                strategy_success[strategy]["tasks"].append(task_type)
        
        for strategy, stats in strategy_success.items():
            if stats["total"] < self.min_pattern_count:
                continue
            
            success_rate = stats["success"] / stats["total"]
            
            if success_rate >= 0.8:
                task_types = set(stats["tasks"])
                generality = len(task_types) / len(task_groups)
                
                insight = MetaKnowledge(
                    knowledge_id=f"strategy_{strategy}_{int(time.time())}",
                    category="successful_strategy",
                    insight=f"Strategy '{strategy}' has {success_rate:.1%} success rate across {len(task_types)} task types",
                    supporting_evidence=[
                        f"Applied {stats['total']} times",
                        f"Successful {stats['success']} times",
                        f"Works for: {', '.join(list(task_types)[:3])}"
                    ],
                    confidence=min(1.0, stats["total"] / 20.0) * success_rate,
                    generality_score=generality
                )
                insights.append(insight)
        
        return insights
    
    def _find_failure_patterns(
        self,
        task_groups: Dict[str, List[Dict[str, Any]]]
    ) -> List[MetaKnowledge]:
        insights = []
        
        failure_contexts = defaultdict(lambda: {"count": 0, "tasks": []})
        
        for task_type, executions in task_groups.items():
            failures = [e for e in executions if not e.get("success", False)]
            
            for failure in failures:
                context = failure.get("context", {})
                
                for key, value in context.items():
                    context_key = f"{key}={value}"
                    failure_contexts[context_key]["count"] += 1
                    failure_contexts[context_key]["tasks"].append(task_type)
        
        for context_key, stats in failure_contexts.items():
            if stats["count"] < self.min_pattern_count:
                continue
            
            task_types = set(stats["tasks"])
            
            insight = MetaKnowledge(
                knowledge_id=f"failure_{context_key}_{int(time.time())}",
                category="failure_pattern",
                insight=f"Context '{context_key}' is associated with {stats['count']} failures",
                supporting_evidence=[
                    f"Failed {stats['count']} times",
                    f"Affects: {', '.join(list(task_types)[:3])}"
                ],
                confidence=min(1.0, stats["count"] / 10.0),
                generality_score=len(task_types) / len(task_groups)
            )
            insights.append(insight)
        
        return insights
    
    def _find_optimization_insights(
        self,
        task_groups: Dict[str, List[Dict[str, Any]]]
    ) -> List[MetaKnowledge]:
        insights = []
        
        for task_type, executions in task_groups.items():
            if len(executions) < self.min_pattern_count:
                continue
            
            successful = [e for e in executions if e.get("success", False)]
            
            if not successful:
                continue
            
            performances = [e.get("performance", 0.0) for e in successful]
            avg_performance = sum(performances) / len(performances)
            
            top_performers = sorted(successful, key=lambda e: e.get("performance", 0.0), reverse=True)[:3]
            
            common_factors = self._find_common_factors(top_performers)
            
            if common_factors:
                insight = MetaKnowledge(
                    knowledge_id=f"optimization_{task_type}_{int(time.time())}",
                    category="optimization",
                    insight=f"For '{task_type}' tasks, top performers share: {', '.join(common_factors.keys())}",
                    supporting_evidence=[
                        f"Avg performance: {avg_performance:.3f}",
                        f"Top 3 performers analyzed",
                        f"Common factors: {common_factors}"
                    ],
                    confidence=min(1.0, len(successful) / 10.0),
                    generality_score=0.5
                )
                insights.append(insight)
        
        return insights
    
    def _find_common_factors(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not executions:
            return {}
        
        common = {}
        
        first_decision = executions[0].get("decision", {})
        
        for key in first_decision.keys():
            values = [e.get("decision", {}).get(key) for e in executions]
            
            if all(v == values[0] for v in values if v is not None):
                common[key] = values[0]
        
        return common
    
    def get_applicable_insights(
        self,
        context: Dict[str, Any],
        min_confidence: float = 0.6
    ) -> List[MetaKnowledge]:
        applicable = []
        
        for knowledge in self.meta_knowledge:
            if knowledge.confidence < min_confidence:
                continue
            
            if self._is_applicable(knowledge, context):
                applicable.append(knowledge)
        
        applicable.sort(key=lambda k: (k.confidence, k.generality_score), reverse=True)
        
        return applicable
    
    def _is_applicable(self, knowledge: MetaKnowledge, context: Dict[str, Any]) -> bool:
        if knowledge.category == "successful_strategy":
            return True
        
        if knowledge.category == "failure_pattern":
            for evidence in knowledge.supporting_evidence:
                if any(str(v) in evidence for v in context.values()):
                    return True
        
        if knowledge.category == "optimization":
            task_type = context.get("task_type", "")
            if task_type in knowledge.insight:
                return True
        
        return False
    
    def apply_insight(self, knowledge_id: str) -> bool:
        for knowledge in self.meta_knowledge:
            if knowledge.knowledge_id == knowledge_id:
                knowledge.apply()
                self.statistics["insights_applied"] += 1
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "total_meta_knowledge": len(self.meta_knowledge),
            "avg_confidence": (
                sum(k.confidence for k in self.meta_knowledge) / len(self.meta_knowledge)
                if self.meta_knowledge else 0.0
            ),
            "avg_generality": (
                sum(k.generality_score for k in self.meta_knowledge) / len(self.meta_knowledge)
                if self.meta_knowledge else 0.0
            ),
            "by_category": self._get_category_stats()
        }
    
    def _get_category_stats(self) -> Dict[str, int]:
        stats = defaultdict(int)
        for knowledge in self.meta_knowledge:
            stats[knowledge.category] += 1
        return dict(stats)
