from __future__ import annotations

from dataclasses import dataclass, field

from .adapter import AndroidCompanionAdapter, HardwareAdapter
from .permissions import PermissionManager


@dataclass
class HardwareDevice:
    id: str
    name: str
    platform: str
    authorized: bool = False
    adapter: HardwareAdapter | None = None
    capabilities: set[str] = field(default_factory=set)


class HardwareRegistry:
    def __init__(self, permissions: PermissionManager) -> None:
        self.permissions = permissions
        self._devices: dict[str, HardwareDevice] = {}

    def enroll_android(self, device_id: str, name: str) -> HardwareDevice:
        device = HardwareDevice(device_id, name, "android", True, AndroidCompanionAdapter(), set(AndroidCompanionAdapter.capabilities))
        self._devices[device_id] = device
        return device

    def list(self) -> list[dict]:
        return [{"id": d.id, "name": d.name, "platform": d.platform, "authorized": d.authorized, "capabilities": sorted(d.capabilities)} for d in self._devices.values()]

    async def execute(self, device_id: str, capability: str, action: str, parameters: dict) -> dict:
        device = self._devices.get(device_id)
        if device is None or not device.authorized:
            raise PermissionError("Hardware device is not enrolled and authorized")
        if capability not in device.capabilities:
            raise PermissionError("Capability is not supported by this device")
        if not self.permissions.check(device_id, capability):
            self.permissions.request(device_id, capability)
            raise PermissionError("User permission is required for this hardware capability")
        if device.adapter is None:
            raise RuntimeError("No hardware adapter is configured")
        result = await device.adapter.execute(capability, action, parameters)
        return {"device_id": device_id, "result": result}
