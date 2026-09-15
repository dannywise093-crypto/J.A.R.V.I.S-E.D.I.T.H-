from typing import Any, Callable

from ..core.policy import get_tool_policy


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[], Any]] = {}

    def register(self, name: str, handler: Callable[[], Any]) -> None:
        if get_tool_policy(name) is None:
            raise ValueError(f"Tool '{name}' is not permitted by policy")
        self._handlers[name] = handler

    def execute(self, name: str) -> Any:
        if get_tool_policy(name) is None:
            raise PermissionError(f"Tool '{name}' is not allowlisted")
        handler = self._handlers.get(name)
        if handler is None:
            raise KeyError(f"Tool '{name}' is not registered")
        return handler()
