"""Deterministic task planner used before model-backed planning is added."""

from dataclasses import dataclass
from backend.app.agent.types import AgentTask, RiskLevel

@dataclass(frozen=True)
class PlanStep:
    capability: str
    instruction: str
    risk: RiskLevel = RiskLevel.LOW

class Planner:
    def plan(self, task: AgentTask) -> tuple[PlanStep, ...]:
        return (PlanStep(task.capability, task.instruction, task.risk),)
