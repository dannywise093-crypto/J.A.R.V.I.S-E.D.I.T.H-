from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from uuid import uuid4


class PermissionMode(str, Enum):
    ONCE = "once"
    SESSION = "session"
    PERSISTENT = "persistent"


@dataclass(frozen=True)
class PermissionGrant:
    grant_id: str
    device_id: str
    capability: str
    mode: PermissionMode
    granted_at: str
    expires_at: str | None = None
    session_id: str | None = None


class PermissionManager:
    """Default-deny permission gate for all hardware/device operations."""

    def __init__(self) -> None:
        self._grants: dict[tuple[str, str], PermissionGrant] = {}
        self._lock = Lock()

    def request(self, device_id: str, capability: str) -> dict:
        return {
            "request_id": str(uuid4()),
            "device_id": device_id,
            "capability": capability,
            "status": "awaiting_user_grant",
            "allowed_modes": [mode.value for mode in PermissionMode],
        }

    def grant(
        self,
        device_id: str,
        capability: str,
        mode: PermissionMode,
        session_id: str | None = None,
    ) -> PermissionGrant:
        if mode == PermissionMode.SESSION and not session_id:
            raise ValueError("session_id is required for a session permission")
        now = datetime.now(timezone.utc).isoformat()
        grant = PermissionGrant(
            grant_id=str(uuid4()),
            device_id=device_id,
            capability=capability,
            mode=mode,
            granted_at=now,
            session_id=session_id,
        )
        with self._lock:
            self._grants[(device_id, capability)] = grant
        return grant

    def revoke(self, device_id: str, capability: str) -> bool:
        with self._lock:
            return self._grants.pop((device_id, capability), None) is not None

    def check(self, device_id: str, capability: str, session_id: str | None = None) -> PermissionGrant | None:
        with self._lock:
            grant = self._grants.get((device_id, capability))
            if grant is None:
                return None
            if grant.mode == PermissionMode.SESSION and grant.session_id != session_id:
                return None
            return grant

    def require(self, device_id: str, capability: str, session_id: str | None = None) -> PermissionGrant:
        grant = self.check(device_id, capability, session_id)
        if grant is None:
            raise PermissionError(
                f"Hardware capability '{capability}' is not authorized for device '{device_id}'"
            )
        return grant

    def consume_once(self, grant: PermissionGrant) -> None:
        if grant.mode != PermissionMode.ONCE:
            return
        with self._lock:
            current = self._grants.get((grant.device_id, grant.capability))
            if current and current.grant_id == grant.grant_id:
                self._grants.pop((grant.device_id, grant.capability), None)

    def list_grants(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "grant_id": grant.grant_id,
                    "device_id": grant.device_id,
                    "capability": grant.capability,
                    "mode": grant.mode.value,
                    "granted_at": grant.granted_at,
                    "session_id": grant.session_id,
                }
                for grant in self._grants.values()
            ]
