from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class GrantMode(str, Enum):
    ONCE = "once"
    SESSION = "session"
    PERSISTENT = "persistent"


SENSITIVE = {"camera.read", "microphone.record", "location.read", "screen.capture"}


@dataclass
class Grant:
    id: str
    device_id: str
    capability: str
    mode: GrantMode
    granted_at: str
    expires_at: str | None = None


class PermissionManager:
    def __init__(self) -> None:
        self._grants: dict[str, Grant] = {}
        self._audit: list[dict] = []

    def request(self, device_id: str, capability: str) -> dict:
        event = {"event": "permission.requested", "device_id": device_id, "capability": capability, "at": self._now()}
        self._audit.append(event)
        return {**event, "requires_user_grant": True, "sensitive": capability in SENSITIVE}

    def grant(self, device_id: str, capability: str, mode: GrantMode) -> Grant:
        grant = Grant(str(uuid4()), device_id, capability, mode, self._now())
        self._grants[f"{device_id}:{capability}"] = grant
        self._audit.append({"event": "permission.granted", "grant_id": grant.id, "device_id": device_id, "capability": capability, "mode": mode.value, "at": grant.granted_at})
        return grant

    def revoke(self, device_id: str, capability: str) -> bool:
        removed = self._grants.pop(f"{device_id}:{capability}", None) is not None
        self._audit.append({"event": "permission.revoked", "device_id": device_id, "capability": capability, "at": self._now(), "removed": removed})
        return removed

    def check(self, device_id: str, capability: str) -> bool:
        return f"{device_id}:{capability}" in self._grants

    def list_grants(self) -> list[dict]:
        return [{"id": g.id, "device_id": g.device_id, "capability": g.capability, "mode": g.mode.value, "granted_at": g.granted_at} for g in self._grants.values()]

    def audit(self) -> list[dict]:
        return list(self._audit)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
