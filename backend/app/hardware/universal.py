from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_SYSTEM_TYPES = {
    "windows",
    "macos",
    "linux",
    "android",
    "ios",
    "raspberry_pi",
    "arduino",
    "esp32",
    "iot",
    "server",
    "cloud",
    "network_device",
    "vehicle",
    "web_service",
    "custom",
}


@dataclass(frozen=True)
class UniversalDevice:
    device_id: str
    name: str
    system_type: str
    transport: str
    endpoint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    authorized: bool = True


class UniversalAdapter:
    """Contract for a concrete, authenticated adapter to a real system.

    Concrete adapters should expose a finite action allow-list. They must not
    expose arbitrary command/shell execution through the J.A.R.V.I.S. API.
    """

    def __init__(self, device: UniversalDevice) -> None:
        self.device = device

    async def capabilities(self) -> list[str]:
        return []

    async def actions(self, capability: str) -> list[str]:
        return []

    async def execute(self, capability: str, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Attach a concrete authenticated system adapter")
