from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .agents import CollaborationEngine
from .quality_gate import SelfReviewEngine


@dataclass
class EngineeringSession:
    session_id: str
    task: str
    status: str = "planning"
    route: dict[str, Any] = field(default_factory=dict)
    review: dict[str, Any] | None = None


class ContinuousEngineeringCoordinator:
    """Coordinates bounded, repeatable coding/review cycles.

    J.A.R.V.I.S. and E.D.I.T.H. remain separate identities. The coordinator
    can repeatedly inspect and validate proposed source, but it does not
    silently apply consequential changes or execute arbitrary code.
    """

    def __init__(self, max_repair_attempts: int = 3) -> None:
        self.collaboration = CollaborationEngine()
        self.quality = SelfReviewEngine(max_repair_attempts)

    def start(self, task: str, visual_context: bool = False) -> EngineeringSession:
        if not task.strip():
            raise ValueError("task is required")
        return EngineeringSession(
            session_id=str(uuid4()),
            task=task.strip(),
            route=self.collaboration.route(task, visual_context),
        )

    def validate(self, session: EngineeringSession, python_files: dict[str, str]) -> EngineeringSession:
        review = self.quality.review_python_files(python_files, session.session_id)
        session.review = self.quality.summarize(review)
        session.status = "ready_for_human_verification" if review.ready_for_human_verification else "blocked"
        return session

    def summarize(self, session: EngineeringSession) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "task": session.task,
            "status": session.status,
            "route": session.route,
            "review": session.review,
        }
