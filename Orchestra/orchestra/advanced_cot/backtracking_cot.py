import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class ReasoningPath:
    path_id: str
    steps: List[str]
    outputs: Dict[str, Any]
    confidence: float
    success: bool
    total_time: float = 0.0
    backtrack_count: int = 0


class BacktrackingCoT:
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        max_backtracks: int = 3,
        max_alternative_paths: int = 3
    ):
        self.confidence_threshold = confidence_threshold
        self.max_backtracks = max_backtracks
        self.max_alternative_paths = max_alternative_paths
        
        self.steps: Dict[str, Dict[str, Any]] = {}
        self.alternative_executors: Dict[str, List[Callable]] = {}
        self.paths_explored: List[ReasoningPath] = []
        
        self.statistics = {
            "total_backtracks": 0,
            "paths_explored": 0,
            "successful_paths": 0
        }
    
    def add_step(
        self,
        step_id: str,
        description: str,
        executor: Callable,
        alternatives: Optional[List[Callable]] = None,
        dependencies: Optional[List[str]] = None
    ) -> None:
        self.steps[step_id] = {
            "description": description,
            "executor": executor,
            "dependencies": dependencies or []
        }
        
        if alternatives:
            self.alternative_executors[step_id] = alternatives
    
    async def execute(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        
        execution_order = self._topological_sort()
        
        if not execution_order:
            return {
                "success": False,
                "error": "Circular dependency detected"
            }
        
        best_path = await self._explore_with_backtracking(
            execution_order,
            context,
            {},
            0,
            []
        )
        
        if best_path and best_path.success:
            return {
                "success": True,
                "outputs": best_path.outputs,
                "path_taken": best_path.steps,
                "confidence": best_path.confidence,
                "backtracks": best_path.backtrack_count,
                "paths_explored": len(self.paths_explored),
                "statistics": self.get_statistics()
            }
        
        return {
            "success": False,
            "error": "No successful path found",
            "paths_explored": len(self.paths_explored),
            "best_attempt": best_path.outputs if best_path else None
        }
    
    async def _explore_with_backtracking(
        self,
        remaining_steps: List[str],
        context: Dict[str, Any],
        current_outputs: Dict[str, Any],
        backtrack_count: int,
        path_taken: List[str]
    ) -> Optional[ReasoningPath]:
        if not remaining_steps:
            path = ReasoningPath(
                path_id=f"path_{len(self.paths_explored)}",
                steps=path_taken.copy(),
                outputs=deepcopy(current_outputs),
                confidence=1.0,
                success=True
            )
            self.paths_explored.append(path)
            self.statistics["paths_explored"] += 1
            self.statistics["successful_paths"] += 1
            return path
        
        if backtrack_count >= self.max_backtracks:
            return None
        
        current_step_id = remaining_steps[0]
        remaining = remaining_steps[1:]
        
        step_info = self.steps[current_step_id]
        
        executors_to_try = [step_info["executor"]]
        if current_step_id in self.alternative_executors:
            executors_to_try.extend(self.alternative_executors[current_step_id][:self.max_alternative_paths - 1])
        
        best_path = None
        best_confidence = 0.0
        
        for executor_idx, executor in enumerate(executors_to_try):
            start_time = time.time()
            
            step_context = {
                **context,
                **current_outputs,
                "step_description": step_info["description"],
                "executor_variant": executor_idx
            }
            
            try:
                result = executor(step_context)
                if asyncio.iscoroutine(result):
                    result = await result
                
                execution_time = time.time() - start_time
                
                confidence = self._estimate_confidence(result, step_context)
                
                if confidence >= self.confidence_threshold:
                    new_outputs = {**current_outputs, current_step_id: result}
                    new_path = path_taken + [f"{current_step_id}_v{executor_idx}"]
                    
                    path = await self._explore_with_backtracking(
                        remaining,
                        context,
                        new_outputs,
                        backtrack_count,
                        new_path
                    )
                    
                    if path and path.success:
                        path.total_time += execution_time
                        return path
                    
                    if path and path.confidence > best_confidence:
                        best_path = path
                        best_confidence = path.confidence
                
                elif executor_idx < len(executors_to_try) - 1:
                    self.statistics["total_backtracks"] += 1
                    continue
            
            except Exception as e:
                if executor_idx < len(executors_to_try) - 1:
                    self.statistics["total_backtracks"] += 1
                    continue
        
        if best_path:
            return best_path
        
        if backtrack_count < self.max_backtracks:
            self.statistics["total_backtracks"] += 1
            
            return await self._explore_with_backtracking(
                remaining_steps,
                context,
                current_outputs,
                backtrack_count + 1,
                path_taken
            )
        
        failed_path = ReasoningPath(
            path_id=f"path_{len(self.paths_explored)}",
            steps=path_taken.copy(),
            outputs=deepcopy(current_outputs),
            confidence=0.0,
            success=False,
            backtrack_count=backtrack_count
        )
        self.paths_explored.append(failed_path)
        self.statistics["paths_explored"] += 1
        
        return failed_path
    
    def _estimate_confidence(
        self,
        result: Any,
        context: Dict[str, Any]
    ) -> float:
        if result is None:
            return 0.0
        
        if isinstance(result, dict):
            if "error" in result:
                return 0.0
            
            if "confidence" in result:
                return result["confidence"]
            
            if "success" in result and not result["success"]:
                return 0.3
        
        return 0.8
    
    def _topological_sort(self) -> List[str]:
        in_degree = {step_id: 0 for step_id in self.steps.keys()}
        graph = {step_id: [] for step_id in self.steps.keys()}
        
        for step_id, step_info in self.steps.items():
            for dep in step_info["dependencies"]:
                if dep in graph:
                    graph[dep].append(step_id)
                    in_degree[step_id] += 1
        
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.steps):
            return []
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "success_rate": (
                self.statistics["successful_paths"] / self.statistics["paths_explored"]
                if self.statistics["paths_explored"] > 0 else 0.0
            ),
            "avg_backtracks": (
                self.statistics["total_backtracks"] / self.statistics["paths_explored"]
                if self.statistics["paths_explored"] > 0 else 0.0
            )
        }
    
    def get_all_paths(self) -> List[ReasoningPath]:
        return self.paths_explored.copy()
