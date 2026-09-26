import pytest
from backend.app.agent.tooling import ToolCall, ToolRegistry, ToolSpec
from backend.app.core.permissions import PermissionManager
from backend.app.orchestration.tool_runtime import ToolRuntime

def test_tool_runtime_requires_permission():
    registry = ToolRegistry()
    registry.register(ToolSpec("search", "Search", "research"), lambda query: query)
    runtime = ToolRuntime(registry, PermissionManager())
    with pytest.raises(PermissionError):
        runtime.execute(ToolCall("search", {"query": "hello"}), "user")

def test_tool_runtime_executes_after_permission():
    registry = ToolRegistry()
    registry.register(ToolSpec("search", "Search", "research"), lambda query: query.upper())
    permissions = PermissionManager()
    permissions.grant("user", "research")
    assert ToolRuntime(registry, permissions).execute(ToolCall("search", {"query": "hello"}), "user") == "HELLO"
