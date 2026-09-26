"""Minimal orchestration engine for capability routing and permission checks."""

from backend.app.agent.registry import AgentRegistry
from backend.app.agent.types import AgentResult, AgentTask, RiskLevel
from backend.app.core.permissions import PermissionManager


class OrchestrationEngine:
    def __init__(self, registry: AgentRegistry, permissions: PermissionManager) -> None:
        self.registry = registry
        self.permissions = permissions

    def dispatch(self, task: AgentTask) -> AgentResult:
        candidates = self.registry.find_by_capability(task.capability)
        if not candidates:
            return AgentResult(
                task_id=task.task_id,
                agent_id="",
                status="unavailable",
                error=f"no agent supports capability: {task.capability}",
            )

        agent = candidates[0]
        if task.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return AgentResult(
                task_id=task.task_id,
                agent_id=agent.agent_id,
                status="confirmation_required",
                requires_confirmation=True,
                error="high-impact actions require explicit confirmation",
            )

        try:
            self.permissions.require(task.requested_by, task.capability)
        except PermissionError as exc:
            return AgentResult(
                task_id=task.task_id,
                agent_id=agent.agent_id,
                status="permission_denied",
                error=str(exc),
            )

        try:
            output = agent.handler(task)
        except Exception as exc:  # boundary: agent failures must not crash the orchestrator
            return AgentResult(
                task_id=task.task_id,
                agent_id=agent.agent_id,
                status="failed",
                error=f"agent execution failed: {exc}",
            )

        return AgentResult(
            task_id=task.task_id,
            agent_id=agent.agent_id,
            status="completed",
            output=output,
        )
