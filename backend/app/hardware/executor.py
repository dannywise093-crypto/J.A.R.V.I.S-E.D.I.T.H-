from __future__ import annotations

from .capabilities import get_capability
from ..core.permissions import PermissionManager


class AuthorizedHardwareExecutor:
    """Single enforcement point before any real hardware transport is invoked."""

    def __init__(self, permissions: PermissionManager) -> None:
        self.permissions = permissions

    async def execute(self, device_id: str, capability: str, action: str, parameters: dict) -> dict:
        spec = get_capability(capability)
        grant = self.permissions.require(device_id, spec.name)
        return {
            "status": "authorized_transport_pending",
            "device_id": device_id,
            "capability": spec.name,
            "action": action,
            "mode": grant.mode.value,
            "parameters": parameters,
        }
