import asyncio
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ReasoningStep:
    step_id: str
    description: str
    executor: Callable[[Dict[str, Any]], Any]
    dependencies: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None
    cognitive_load: float = 0.0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_execute(self, completed_steps: set) -> bool:
        return all(dep in completed_steps for dep in self.dependencies)


class ChainOfThought:
    def __init__(self, chain_id: str, clm_integration: Optional[Any] = None):
        self.chain_id = chain_id
        self.steps: List[ReasoningStep] = []
        self.step_registry: Dict[str, ReasoningStep] = {}
        self.completed_steps: set = set()
        self.clm_integration = clm_integration
        self.total_cognitive_load = 0.0
        self.execution_log: List[Dict[str, Any]] = []

    def add_step(
        self,
        step_id: str,
        description: str,
        executor: Callable[[Dict[str, Any]], Any],
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReasoningStep:
        if step_id in self.step_registry:
            raise ValueError(f"Step with id '{step_id}' already exists")
        
        step = ReasoningStep(
            step_id=step_id,
            description=description,
            executor=executor,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self.steps.append(step)
        self.step_registry[step_id] = step
        return step

    def add_steps(self, steps: List[ReasoningStep]) -> None:
        for step in steps:
            if step.step_id not in self.step_registry:
                self.steps.append(step)
                self.step_registry[step.step_id] = step

    async def execute(
        self,
        initial_context: Optional[Dict[str, Any]] = None,
        monitor_load: bool = True
    ) -> Dict[str, Any]:
        context = initial_context or {}
        context["chain_id"] = self.chain_id
        context["step_outputs"] = {}
        
        self.completed_steps.clear()
        self.execution_log.clear()
        self.total_cognitive_load = 0.0
        
        execution_order = self._topological_sort()
        
        for step in execution_order:
            if not step.can_execute(self.completed_steps):
                step.status = StepStatus.SKIPPED
                continue
            
            step.status = StepStatus.IN_PROGRESS
            step.input_data = self._prepare_step_input(step, context)
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                if monitor_load and self.clm_integration:
                    step.cognitive_load = await self._measure_cognitive_load(step)
                    self.total_cognitive_load += step.cognitive_load
                
                result = step.executor(step.input_data)
                if asyncio.iscoroutine(result):
                    result = await result
                
                step.output_data = result
                step.status = StepStatus.COMPLETED
                context["step_outputs"][step.step_id] = result
                self.completed_steps.add(step.step_id)
                
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                
                self._log_step_execution(step, start_time, success=False)
                
                raise RuntimeError(f"Step '{step.step_id}' failed: {str(e)}")
            
            step.execution_time = asyncio.get_event_loop().time() - start_time
            self._log_step_execution(step, start_time, success=True)
        
        return {
            "chain_id": self.chain_id,
            "completed_steps": len(self.completed_steps),
            "total_steps": len(self.steps),
            "total_cognitive_load": self.total_cognitive_load,
            "outputs": context["step_outputs"],
            "execution_log": self.execution_log
        }

    def _topological_sort(self) -> List[ReasoningStep]:
        in_degree = {step.step_id: len(step.dependencies) for step in self.steps}
        queue = [step for step in self.steps if in_degree[step.step_id] == 0]
        sorted_steps = []
        
        while queue:
            current = queue.pop(0)
            sorted_steps.append(current)
            
            for step in self.steps:
                if current.step_id in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step)
        
        if len(sorted_steps) != len(self.steps):
            raise ValueError("Circular dependency detected in reasoning steps")
        
        return sorted_steps

    def _prepare_step_input(
        self,
        step: ReasoningStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        step_input = {"context": context}
        
        for dep_id in step.dependencies:
            if dep_id in context["step_outputs"]:
                step_input[dep_id] = context["step_outputs"][dep_id]
        
        return step_input

    async def _measure_cognitive_load(self, step: ReasoningStep) -> float:
        if not self.clm_integration:
            return 0.0
        
        try:
            load = await self.clm_integration.measure_step_load(
                step_id=step.step_id,
                description=step.description,
                dependencies=len(step.dependencies)
            )
            return load
        except Exception:
            return 0.0

    def _log_step_execution(
        self,
        step: ReasoningStep,
        start_time: float,
        success: bool
    ) -> None:
        log_entry = {
            "step_id": step.step_id,
            "description": step.description,
            "status": step.status.value,
            "execution_time": step.execution_time,
            "cognitive_load": step.cognitive_load,
            "success": success,
            "timestamp": start_time
        }
        
        if not success and step.error:
            log_entry["error"] = step.error
        
        self.execution_log.append(log_entry)

    def get_step_output(self, step_id: str) -> Optional[Any]:
        if step_id in self.step_registry:
            return self.step_registry[step_id].output_data
        return None

    def get_intermediate_outputs(self) -> Dict[str, Any]:
        return {
            step_id: step.output_data
            for step_id, step in self.step_registry.items()
            if step.output_data is not None
        }

    def get_cognitive_load_report(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "total_load": self.total_cognitive_load,
            "step_loads": {
                step.step_id: step.cognitive_load
                for step in self.steps
            },
            "average_load": self.total_cognitive_load / len(self.steps) if self.steps else 0.0
        }

    def reset(self) -> None:
        for step in self.steps:
            step.status = StepStatus.PENDING
            step.output_data = None
            step.error = None
            step.cognitive_load = 0.0
            step.execution_time = 0.0
        
        self.completed_steps.clear()
        self.execution_log.clear()
        self.total_cognitive_load = 0.0
