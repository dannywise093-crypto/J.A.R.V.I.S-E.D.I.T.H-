"""J.A.R.V.I.S execution runtime."""

from dataclasses import dataclass
from backend.app.agent.registry import AgentRegistry
from backend.app.agent.types import AgentResult, AgentTask
from backend.app.core.permissions import PermissionManager
from backend.app.memory.store import MemoryStore
from backend.app.orchestration.engine import OrchestrationEngine
from backend.app.orchestration.planner import Planner

@dataclass(frozen=True)
class RuntimeResult:
    task_id: str
    steps: tuple[AgentResult, ...]

class JarvisRuntime:
    def __init__(self, registry: AgentRegistry, permissions: PermissionManager, memory: MemoryStore) -> None:
        self.planner = Planner()
        self.engine = OrchestrationEngine(registry, permissions)
        self.memory = memory

    def run(self, task: AgentTask) -> RuntimeResult:
        results = []
        for step in self.planner.plan(task):
            result = self.engine.dispatch(AgentTask(task.task_id, step.capability, step.instruction, task.requested_by, step.risk, task.metadata))
            results.append(result)
            self.memory.put(f"task:{task.task_id}", result)
            if result.status != "completed":
                break
        return RuntimeResult(task.task_id, tuple(results))
