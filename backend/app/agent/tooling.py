"""Safe tool contracts for agent function calling."""
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    capability: str
    risk: str = "low"
    input_schema: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, Callable[..., Any]]] = {}

    def register(self, spec: ToolSpec, handler: Callable[..., Any]) -> None:
        if spec.name in self._tools:
            raise ValueError(f"tool already registered: {spec.name}")
        self._tools[spec.name] = (spec, handler)

    def get(self, name: str) -> tuple[ToolSpec, Callable[..., Any]] | None:
        return self._tools.get(name)

    def specs(self) -> list[ToolSpec]:
        return [item[0] for item in self._tools.values()]

    def execute(self, call: ToolCall) -> Any:
        item = self._tools.get(call.name)
        if item is None:
            raise KeyError(f"unknown tool: {call.name}")
        _, handler = item
        return handler(**call.arguments)
