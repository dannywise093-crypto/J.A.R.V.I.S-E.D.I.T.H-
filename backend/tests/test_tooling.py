import pytest
from backend.app.agent.tooling import ToolRegistry, ToolSpec, ToolCall

def test_tool_registry_executes_registered_tool():
    registry = ToolRegistry()
    registry.register(ToolSpec("add", "Add numbers", "calculator"), lambda a, b: a + b)
    assert registry.execute(ToolCall("add", {"a": 2, "b": 3})) == 5

def test_tool_registry_rejects_unknown_tool():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.execute(ToolCall("missing", {}))
