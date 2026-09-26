"""Permission-aware execution boundary for model-selected tools."""
from backend.app.agent.tooling import ToolCall, ToolRegistry
from backend.app.core.permissions import PermissionManager

class ToolRuntime:
    def __init__(self, registry: ToolRegistry, permissions: PermissionManager) -> None:
        self.registry = registry
        self.permissions = permissions

    def execute(self, call: ToolCall, requester: str) -> object:
        item = self.registry.get(call.name)
        if item is None:
            raise KeyError(f"unknown tool: {call.name}")
        spec, _ = item
        self.permissions.require(requester, spec.capability)
        return self.registry.execute(call)
