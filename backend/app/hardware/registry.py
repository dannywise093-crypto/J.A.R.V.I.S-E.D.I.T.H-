from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .adapter import AndroidCompanionAdapter, HardwareAdapter
from .permissions import PermissionManager
from .universal import SUPPORTED_SYSTEM_TYPES, UniversalDevice


@dataclass
class HardwareDevice:
    id: str
    name: str
    platform: str
    authorized: bool = False
    adapter: HardwareAdapter | None = None
    capabilities: set[str] = field(default_factory=set)
    transport: str = "unknown"
    endpoint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class HardwareRegistry:
    def __init__(self, permissions: PermissionManager) -> None:
        self.permissions = permissions
        self._devices: dict[str, HardwareDevice] = {}

    def enroll_android(self, device_id: str, name: str) -> HardwareDevice:
        adapter = AndroidCompanionAdapter()
        device = HardwareDevice(
            device_id, name, "android", True, adapter, set(adapter.capabilities), "companion"
        )
        self._devices[device_id] = device
        return device

    def enroll_system(
        self,
        device_id: str,
        name: str,
        system_type: str,
        transport: str,
        endpoint: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> HardwareDevice:
        system_type = system_type.lower().strip()
        if system_type not in SUPPORTED_SYSTEM_TYPES:
            raise ValueError(f"Unsupported system_type: {system_type}")
        if not device_id.strip() or not name.strip() or not transport.strip():
            raise ValueError("device_id, name and transport are required")
        device = HardwareDevice(
            id=device_id,
            name=name,
            platform=system_type,
            authorized=True,
            adapter=None,
            capabilities=set(),
            transport=transport,
            endpoint=endpoint,
            metadata=metadata or {},
        )
        self._devices[device_id] = device
        return device

    def revoke(self, device_id: str) -> bool:
        device = self._devices.get(device_id)
        if device is None:
            return False
        device.authorized = False
        device.adapter = None
        return True

    def list(self) -> list[dict]:
        return [
            {
                "id": d.id,
                "name": d.name,
                "platform": d.platform,
                "transport": d.transport,
                "endpoint": d.endpoint,
                "authorized": d.authorized,
                "capabilities": sorted(d.capabilities),
                "metadata": d.metadata,
                "adapter_connected": d.adapter is not None,
            }
            for d in self._devices.values()
        ]

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
            raise RuntimeError("No concrete hardware/system adapter is connected")
        result = await device.adapter.execute(capability, action, parameters)
        return {"device_id": device_id, "result": result}
