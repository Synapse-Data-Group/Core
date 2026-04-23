import asyncio
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ReasoningStep:
    step_id: str
    description: str
    executor: Callable
    dependencies: List[str] = field(default_factory=list)
    output: Optional[Any] = None
    executed: bool = False
    execution_time: float = 0.0
    confidence: float = 1.0
    verification_passed: bool = False
    verification_notes: List[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    passed: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]


class SelfVerifyingCoT:
    def __init__(
        self,
        verifier: Optional[Callable] = None,
        min_confidence_threshold: float = 0.7,
        max_retries: int = 2
    ):
        self.verifier = verifier or self._default_verifier
        self.min_confidence_threshold = min_confidence_threshold
        self.max_retries = max_retries
        
        self.steps: List[ReasoningStep] = []
        self.execution_order: List[str] = []
        self.failed_steps: List[str] = []
        
        self.statistics = {
            "total_steps": 0,
            "verified_steps": 0,
            "failed_verifications": 0,
            "retries": 0
        }
    
    def add_step(
        self,
        step_id: str,
        description: str,
        executor: Callable,
        dependencies: Optional[List[str]] = None
    ) -> None:
        step = ReasoningStep(
            step_id=step_id,
            description=description,
            executor=executor,
            dependencies=dependencies or []
        )
        self.steps.append(step)
        self.statistics["total_steps"] += 1
    
    async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        
        self.execution_order = self._topological_sort()
        
        if not self.execution_order:
            return {
                "success": False,
                "error": "Circular dependency detected in reasoning steps"
            }
        
        step_outputs = {}
        
        for step_id in self.execution_order:
            step = self._get_step(step_id)
            
            if not step:
                continue
            
            retry_count = 0
            verification_passed = False
            
            while retry_count <= self.max_retries and not verification_passed:
                start_time = time.time()
                
                step_context = {
                    **context,
                    **step_outputs,
                    "step_description": step.description,
                    "retry_count": retry_count
                }
                
                try:
                    result = step.executor(step_context)
                    if asyncio.iscoroutine(result):
                        result = await result
                    
                    step.output = result
                    step.executed = True
                    step.execution_time = time.time() - start_time
                    
                    verification = await self._verify_step(step, step_context)
                    
                    step.confidence = verification.confidence
                    step.verification_passed = verification.passed
                    step.verification_notes = verification.issues + verification.suggestions
                    
                    if verification.passed and verification.confidence >= self.min_confidence_threshold:
                        verification_passed = True
                        step_outputs[step_id] = result
                        self.statistics["verified_steps"] += 1
                    else:
                        retry_count += 1
                        self.statistics["retries"] += 1
                        
                        if retry_count <= self.max_retries:
                            context["verification_feedback"] = {
                                "issues": verification.issues,
                                "suggestions": verification.suggestions,
                                "previous_attempt": result
                            }
                
                except Exception as e:
                    step.execution_time = time.time() - start_time
                    retry_count += 1
                    self.statistics["retries"] += 1
                    
                    if retry_count > self.max_retries:
                        self.failed_steps.append(step_id)
                        self.statistics["failed_verifications"] += 1
                        return {
                            "success": False,
                            "error": f"Step {step_id} failed: {str(e)}",
                            "failed_step": step_id,
                            "partial_outputs": step_outputs
                        }
            
            if not verification_passed:
                self.failed_steps.append(step_id)
                self.statistics["failed_verifications"] += 1
                return {
                    "success": False,
                    "error": f"Step {step_id} failed verification after {self.max_retries} retries",
                    "failed_step": step_id,
                    "partial_outputs": step_outputs,
                    "verification_notes": step.verification_notes
                }
        
        return {
            "success": True,
            "outputs": step_outputs,
            "execution_order": self.execution_order,
            "statistics": self.get_statistics()
        }
    
    async def _verify_step(
        self,
        step: ReasoningStep,
        context: Dict[str, Any]
    ) -> VerificationResult:
        verification_context = {
            "step_id": step.step_id,
            "description": step.description,
            "output": step.output,
            "context": context
        }
        
        result = self.verifier(verification_context)
        if asyncio.iscoroutine(result):
            result = await result
        
        if isinstance(result, VerificationResult):
            return result
        
        return VerificationResult(
            passed=result.get("passed", True),
            confidence=result.get("confidence", 1.0),
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", [])
        )
    
    def _default_verifier(self, context: Dict[str, Any]) -> VerificationResult:
        output = context.get("output")
        
        if output is None:
            return VerificationResult(
                passed=False,
                confidence=0.0,
                issues=["Output is None"],
                suggestions=["Ensure the step produces a valid output"]
            )
        
        if isinstance(output, dict) and "error" in output:
            return VerificationResult(
                passed=False,
                confidence=0.0,
                issues=[f"Error in output: {output['error']}"],
                suggestions=["Fix the error before proceeding"]
            )
        
        return VerificationResult(
            passed=True,
            confidence=0.8,
            issues=[],
            suggestions=[]
        )
    
    def _topological_sort(self) -> List[str]:
        in_degree = {step.step_id: 0 for step in self.steps}
        graph = {step.step_id: [] for step in self.steps}
        
        for step in self.steps:
            for dep in step.dependencies:
                if dep in graph:
                    graph[dep].append(step.step_id)
                    in_degree[step.step_id] += 1
        
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
    
    def _get_step(self, step_id: str) -> Optional[ReasoningStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "success_rate": (
                self.statistics["verified_steps"] / self.statistics["total_steps"]
                if self.statistics["total_steps"] > 0 else 0.0
            ),
            "avg_retries_per_step": (
                self.statistics["retries"] / self.statistics["total_steps"]
                if self.statistics["total_steps"] > 0 else 0.0
            ),
            "failed_steps": len(self.failed_steps)
        }
    
    def get_reasoning_trace(self) -> List[Dict[str, Any]]:
        trace = []
        
        for step_id in self.execution_order:
            step = self._get_step(step_id)
            if step:
                trace.append({
                    "step_id": step.step_id,
                    "description": step.description,
                    "executed": step.executed,
                    "output": step.output,
                    "confidence": step.confidence,
                    "verification_passed": step.verification_passed,
                    "verification_notes": step.verification_notes,
                    "execution_time": step.execution_time
                })
        
        return trace
