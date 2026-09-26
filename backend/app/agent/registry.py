"""Registry for capability-based agent discovery."""

from dataclasses import dataclass, field
from typing import Any, Callable


AgentHandler = Callable[[Any], Any]


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    capabilities: frozenset[str]
    handler: AgentHandler
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        if spec.agent_id in self._agents:
            raise ValueError(f"agent already registered: {spec.agent_id}")
        if not spec.capabilities:
            raise ValueError("an agent must expose at least one capability")
        self._agents[spec.agent_id] = spec

    def get(self, agent_id: str) -> AgentSpec | None:
        return self._agents.get(agent_id)

    def find_by_capability(self, capability: str) -> list[AgentSpec]:
        return [
            spec for spec in self._agents.values()
            if capability in spec.capabilities
        ]

    def all(self) -> tuple[AgentSpec, ...]:
        return tuple(self._agents.values())
