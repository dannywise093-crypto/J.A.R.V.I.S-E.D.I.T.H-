from __future__ import annotations

from abc import ABC, abstractmethod


class HardwareAdapter(ABC):
    capabilities: set[str] = set()

    @abstractmethod
    async def execute(self, capability: str, action: str, parameters: dict) -> dict:
        raise NotImplementedError


class AndroidCompanionAdapter(HardwareAdapter):
    """Transport boundary for the future Android/Termux companion.

    The server never directly reaches into phone hardware. The companion
    authenticates, checks Android permissions, then performs an allowlisted
    action and returns a result.
    """

    capabilities = {
        "camera.read", "microphone.record", "location.read", "sensors.read",
        "bluetooth.control", "usb.access", "screen.capture", "speaker.output",
    }

    async def execute(self, capability: str, action: str, parameters: dict) -> dict:
        if capability not in self.capabilities:
            raise PermissionError(f"Unsupported Android capability: {capability}")
        return {"status": "transport_pending", "capability": capability, "action": action, "parameters": parameters}
