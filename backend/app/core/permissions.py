"""Explicit user permission boundary for device and tool actions."""

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class PermissionGrant:
    principal: str
    capability: str


class PermissionManager:
    """In-memory permission gate; persistence can be added behind this interface."""

    def __init__(self) -> None:
        self._grants: set[PermissionGrant] = set()
        self._lock = RLock()

    def grant(self, principal: str, capability: str) -> None:
        with self._lock:
            self._grants.add(PermissionGrant(principal, capability))

    def revoke(self, principal: str, capability: str) -> None:
        with self._lock:
            self._grants.discard(PermissionGrant(principal, capability))

    def is_granted(self, principal: str, capability: str) -> bool:
        with self._lock:
            return PermissionGrant(principal, capability) in self._grants

    def require(self, principal: str, capability: str) -> None:
        if not self.is_granted(principal, capability):
            raise PermissionError(
                f"permission required: principal={principal!r}, capability={capability!r}"
            )
