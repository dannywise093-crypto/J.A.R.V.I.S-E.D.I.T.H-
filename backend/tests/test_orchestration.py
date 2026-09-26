from backend.app.agent.registry import AgentRegistry, AgentSpec
from backend.app.agent.types import AgentTask, RiskLevel
from backend.app.core.permissions import PermissionManager
from backend.app.orchestration.engine import OrchestrationEngine


def make_engine():
    registry = AgentRegistry()
    registry.register(
        AgentSpec(
            agent_id="research-agent",
            capabilities=frozenset({"research"}),
            handler=lambda task: {"instruction": task.instruction},
        )
    )
    return registry, PermissionManager()


def test_dispatch_requires_explicit_permission():
    registry, permissions = make_engine()
    engine = OrchestrationEngine(registry, permissions)

    result = engine.dispatch(
        AgentTask("t1", "research", "find facts", "user-1")
    )

    assert result.status == "permission_denied"


def test_dispatch_after_grant():
    registry, permissions = make_engine()
    permissions.grant("user-1", "research")
    engine = OrchestrationEngine(registry, permissions)

    result = engine.dispatch(
        AgentTask("t2", "research", "find facts", "user-1")
    )

    assert result.status == "completed"
    assert result.output == {"instruction": "find facts"}


def test_high_risk_requires_confirmation_before_execution():
    registry, permissions = make_engine()
    permissions.grant("user-1", "research")
    engine = OrchestrationEngine(registry, permissions)

    result = engine.dispatch(
        AgentTask("t3", "research", "perform action", "user-1", RiskLevel.HIGH)
    )

    assert result.status == "confirmation_required"
    assert result.requires_confirmation is True
