from datetime import datetime, timezone
from threading import RLock
from typing import Any


class MemoryStore:
    """Thread-safe in-process memory layer for v0.1; replaceable by a durable store later."""

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []
        self._kv: dict[str, Any] = {}
        self._lock = RLock()

    def add(self, role: str, content: str) -> None:
        with self._lock:
            self._items.append({"role": role, "content": content, "timestamp": datetime.now(timezone.utc).isoformat()})
            self._items = self._items[-100:]

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._items[-limit:])

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            self._kv[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._kv.get(key, default)

    def delete(self, key: str) -> None:
        with self._lock:
            self._kv.pop(key, None)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._kv)
