from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DeviceDescriptor:
    """Identity and capabilities advertised by an enrolled system/device."""

    device_id: str
    name: str
    system_type: str
    transport: str
    platform: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    authorized: bool = False


class DeviceAdapter(ABC):
    """Provider-neutral boundary for a real, user-enrolled system/device.

    Adapters implement documented APIs/agents for a concrete platform. There is
    deliberately no arbitrary shell-execution method here.
    """

    descriptor: DeviceDescriptor

    @abstractmethod
    async def capabilities(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def actions(self, capability: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, capability: str, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class RegisteredAdapter(DeviceAdapter):
    """Safe generic adapter used until a concrete transport is connected.

    It exposes discovery but refuses execution. This lets J.A.R.V.I.S. enroll
    heterogeneous systems without pretending a transport is already wired.
    """

    def __init__(self, descriptor: DeviceDescriptor, capabilities: list[str] | None = None) -> None:
        self.descriptor = descriptor
        self._capabilities = list(capabilities or [])

    async def capabilities(self) -> list[str]:
        return list(self._capabilities)

    async def actions(self, capability: str) -> list[str]:
        if capability not in self._capabilities:
            return []
        return []

    async def execute(self, capability: str, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError(
            f"No concrete transport adapter is connected for device '{self.descriptor.device_id}'"
        )
