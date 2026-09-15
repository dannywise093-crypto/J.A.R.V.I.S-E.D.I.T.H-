from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class AgentRecord:
    device_id: str
    agent_version: str
    system_type: str
    platform: str
    capabilities: set[str]
    connected: bool = False
    last_seen: str | None = None


class AgentRegistry:
    """Tracks paired agents; transport/authentication is supplied by deployment."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentRecord] = {}
        self._lock = Lock()

    def register(self, device_id: str, agent_version: str, system_type: str, platform: str, capabilities: list[str]) -> AgentRecord:
        record = AgentRecord(device_id, agent_version, system_type, platform, set(capabilities), True, datetime.now(timezone.utc).isoformat())
        with self._lock:
            self._agents[device_id] = record
        return record

    def heartbeat(self, device_id: str) -> AgentRecord:
        with self._lock:
            record = self._agents.get(device_id)
            if record is None:
                raise KeyError(f"Unknown agent '{device_id}'")
            record.connected = True
            record.last_seen = datetime.now(timezone.utc).isoformat()
            return record

    def disconnect(self, device_id: str) -> bool:
        with self._lock:
            record = self._agents.get(device_id)
            if record is None:
                return False
            record.connected = False
            record.last_seen = datetime.now(timezone.utc).isoformat()
            return True

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {
                    "device_id": r.device_id,
                    "agent_version": r.agent_version,
                    "system_type": r.system_type,
                    "platform": r.platform,
                    "capabilities": sorted(r.capabilities),
                    "connected": r.connected,
                    "last_seen": r.last_seen,
                }
                for r in self._agents.values()
            ]
