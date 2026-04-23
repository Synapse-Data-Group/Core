import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


class TaskType(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    UNKNOWN = "unknown"


class ExecutionMode(Enum):
    LINEAR = "linear"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


class DecisionNode:
    def __init__(
        self,
        node_id: str,
        condition: Callable[[Dict[str, Any]], bool],
        action: Optional[Callable] = None,
        children: Optional[List['DecisionNode']] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.node_id = node_id
        self.condition = condition
        self.action = action
        self.children = children or []
        self.metadata = metadata or {}
        self.execution_count = 0
        self.success_count = 0

    def add_child(self, child: 'DecisionNode') -> None:
        self.children.append(child)

    def evaluate(self, context: Dict[str, Any]) -> bool:
        try:
            return self.condition(context)
        except Exception as e:
            return False

    async def execute(self, context: Dict[str, Any]) -> Any:
        self.execution_count += 1
        if self.action:
            try:
                result = self.action(context)
                if asyncio.iscoroutine(result):
                    result = await result
                self.success_count += 1
                return result
            except Exception as e:
                raise
        return None


class TreeOrchestrator:
    def __init__(self):
        self.root_nodes: List[DecisionNode] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.node_registry: Dict[str, DecisionNode] = {}

    def add_root_node(self, node: DecisionNode) -> None:
        self.root_nodes.append(node)
        self._register_node(node)

    def _register_node(self, node: DecisionNode) -> None:
        self.node_registry[node.node_id] = node
        for child in node.children:
            self._register_node(child)

    def add_decision_node(
        self,
        node_id: str,
        condition: Callable[[Dict[str, Any]], bool],
        action: Optional[Callable] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DecisionNode:
        node = DecisionNode(node_id, condition, action, metadata=metadata)
        
        if parent_id and parent_id in self.node_registry:
            parent = self.node_registry[parent_id]
            parent.add_child(node)
        else:
            self.add_root_node(node)
        
        self._register_node(node)
        return node

    def classify_task(self, task: Dict[str, Any]) -> Tuple[TaskType, float]:
        complexity_score = 0.0
        
        if "complexity" in task:
            return TaskType(task["complexity"]), task.get("complexity_score", 0.5)
        
        task_text = str(task.get("description", "")) + str(task.get("requirements", ""))
        word_count = len(task_text.split())
        
        if word_count < 20:
            complexity_score = 0.2
            task_type = TaskType.SIMPLE
        elif word_count < 100:
            complexity_score = 0.5
            task_type = TaskType.MODERATE
        else:
            complexity_score = 0.8
            task_type = TaskType.COMPLEX
        
        if task.get("requires_parallel", False):
            complexity_score += 0.2
            task_type = TaskType.COMPLEX
        
        if task.get("subtasks") and len(task["subtasks"]) > 3:
            complexity_score += 0.15
            if task_type != TaskType.COMPLEX:
                task_type = TaskType.MODERATE
        
        complexity_score = min(1.0, complexity_score)
        
        return task_type, complexity_score

    def determine_execution_mode(
        self,
        task_type: TaskType,
        complexity_score: float,
        agent_outputs: Optional[List[Dict[str, Any]]] = None
    ) -> ExecutionMode:
        if task_type == TaskType.SIMPLE:
            return ExecutionMode.LINEAR
        elif task_type == TaskType.COMPLEX or complexity_score > 0.7:
            return ExecutionMode.PARALLEL
        else:
            if agent_outputs and len(agent_outputs) > 2:
                return ExecutionMode.PARALLEL
            return ExecutionMode.LINEAR

    async def route_task(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        context["task"] = task
        
        task_type, complexity_score = self.classify_task(task)
        execution_mode = self.determine_execution_mode(task_type, complexity_score)
        
        routing_result = {
            "task_type": task_type.value,
            "complexity_score": complexity_score,
            "execution_mode": execution_mode.value,
            "path": [],
            "actions_taken": [],
            "final_result": None
        }
        
        context["routing_result"] = routing_result
        
        for root_node in self.root_nodes:
            result = await self._traverse_tree(root_node, context, routing_result)
            if result is not None:
                routing_result["final_result"] = result
                break
        
        self.execution_history.append({
            "task": task,
            "routing_result": routing_result,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        return routing_result

    async def _traverse_tree(
        self,
        node: DecisionNode,
        context: Dict[str, Any],
        routing_result: Dict[str, Any]
    ) -> Any:
        if node.evaluate(context):
            routing_result["path"].append(node.node_id)
            
            result = await node.execute(context)
            if result is not None:
                routing_result["actions_taken"].append({
                    "node_id": node.node_id,
                    "result": result
                })
            
            for child in node.children:
                child_result = await self._traverse_tree(child, context, routing_result)
                if child_result is not None:
                    return child_result
            
            return result
        
        return None

    def get_node_statistics(self) -> Dict[str, Dict[str, Any]]:
        stats = {}
        for node_id, node in self.node_registry.items():
            stats[node_id] = {
                "execution_count": node.execution_count,
                "success_count": node.success_count,
                "success_rate": node.success_count / node.execution_count if node.execution_count > 0 else 0.0,
                "metadata": node.metadata
            }
        return stats

    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history

    def clear_history(self) -> None:
        self.execution_history.clear()
