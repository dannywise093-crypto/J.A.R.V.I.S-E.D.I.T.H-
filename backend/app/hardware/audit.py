from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any


class AuditLog:
    """Small bounded audit trail for permission and hardware events."""

    def __init__(self, max_items: int = 1000) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=max_items)
        self._lock = Lock()

    def record(self, event: str, **details: Any) -> dict[str, Any]:
        item = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **details,
        }
        with self._lock:
            self._items.append(item)
        return item

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._items)[-max(1, min(limit, len(self._items))):]
