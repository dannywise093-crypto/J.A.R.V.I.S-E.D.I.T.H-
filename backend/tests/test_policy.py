import pytest

from app.core.policy import get_tool_policy
from app.tools.registry import ToolRegistry


def test_known_tool_is_allowlisted():
    assert get_tool_policy("system.status") is not None


def test_unknown_tool_is_blocked():
    registry = ToolRegistry()
    with pytest.raises(ValueError):
        registry.register("shell.exec", lambda: "dangerous")
