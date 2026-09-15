from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from uuid import uuid4


class VerificationDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class VerificationRequest:
    request_id: str
    actor: str
    action: str
    target: str
    impact: str
    risk: str
    summary: str
    created_at: str
    decision: VerificationDecision = VerificationDecision.PENDING
    decided_at: str | None = None
    decided_by: str | None = None
    reason: str | None = None


class VerificationManager:
    """Human-in-the-loop gate for consequential J.A.R.V.I.S./E.D.I.T.H. actions.

    AI agents may create requests and provide analysis, but they cannot approve
    their own requests. A caller must explicitly record the human decision.
    """

    def __init__(self, max_items: int = 1000) -> None:
        self._requests: dict[str, VerificationRequest] = {}
        self._order: list[str] = []
        self._max_items = max_items
        self._lock = Lock()

    def create(self, actor: str, action: str, target: str, impact: str, risk: str, summary: str) -> VerificationRequest:
        request = VerificationRequest(
            request_id=str(uuid4()),
            actor=actor,
            action=action,
            target=target,
            impact=impact,
            risk=risk,
            summary=summary,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._requests[request.request_id] = request
            self._order.append(request.request_id)
            while len(self._order) > self._max_items:
                old = self._order.pop(0)
                self._requests.pop(old, None)
        return request

    def decide(self, request_id: str, approved: bool, decided_by: str, reason: str | None = None) -> VerificationRequest:
        if not decided_by.strip():
            raise ValueError("decided_by is required")
        with self._lock:
            current = self._requests.get(request_id)
            if current is None:
                raise KeyError(f"Unknown verification request '{request_id}'")
            if current.decision != VerificationDecision.PENDING:
                raise ValueError("Verification request has already been decided")
            updated = VerificationRequest(
                request_id=current.request_id,
                actor=current.actor,
                action=current.action,
                target=current.target,
                impact=current.impact,
                risk=current.risk,
                summary=current.summary,
                created_at=current.created_at,
                decision=VerificationDecision.APPROVED if approved else VerificationDecision.REJECTED,
                decided_at=datetime.now(timezone.utc).isoformat(),
                decided_by=decided_by,
                reason=reason,
            )
            self._requests[request_id] = updated
            return updated

    def require_approved(self, request_id: str) -> VerificationRequest:
        with self._lock:
            request = self._requests.get(request_id)
            if request is None:
                raise KeyError(f"Unknown verification request '{request_id}'")
            if request.decision != VerificationDecision.APPROVED:
                raise PermissionError("Human verification has not approved this action")
            return request

    def list(self, limit: int = 100) -> list[dict]:
        with self._lock:
            ids = self._order[-max(1, min(limit, len(self._order))):]
            return [self._to_dict(self._requests[item]) for item in ids if item in self._requests]

    @staticmethod
    def _to_dict(request: VerificationRequest) -> dict:
        return {
            "request_id": request.request_id,
            "actor": request.actor,
            "action": request.action,
            "target": request.target,
            "impact": request.impact,
            "risk": request.risk,
            "summary": request.summary,
            "created_at": request.created_at,
            "decision": request.decision.value,
            "decided_at": request.decided_at,
            "decided_by": request.decided_by,
            "reason": request.reason,
        }
