from backend.app.agent.registry import AgentRegistry, AgentSpec
from backend.app.agent.types import AgentTask
from backend.app.core.permissions import PermissionManager
from backend.app.memory.store import MemoryStore
from backend.app.orchestration.runtime import JarvisRuntime

def test_runtime_plans_dispatches_and_remembers():
    registry = AgentRegistry()
    registry.register(AgentSpec("research-agent", frozenset({"research"}), lambda task: "research-complete"))
    permissions = PermissionManager()
    permissions.grant("user-1", "research")
    memory = MemoryStore()
    result = JarvisRuntime(registry, permissions, memory).run(AgentTask("t1", "research", "find facts", "user-1"))
    assert result.steps[0].status == "completed"
    assert result.steps[0].output == "research-complete"
    assert memory.get("task:t1").status == "completed"
