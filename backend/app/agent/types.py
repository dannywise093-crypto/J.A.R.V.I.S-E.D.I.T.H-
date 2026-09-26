"""Stable data contracts shared by J.A.R.V.I.S agents and orchestration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    capability: str
    instruction: str
    requested_by: str
    risk: RiskLevel = RiskLevel.LOW
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    task_id: str
    agent_id: str
    status: str
    output: Any = None
    error: str | None = None
    requires_confirmation: bool = False
