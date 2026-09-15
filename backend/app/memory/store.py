from datetime import datetime, timezone


class MemoryStore:
    """Small in-process memory layer for v0.1; replaceable by SQLite/Qdrant later."""

    def __init__(self) -> None:
        self._items: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self._items.append(
            {"role": role, "content": content, "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        self._items = self._items[-100:]

    def recent(self, limit: int = 20) -> list[dict[str, str]]:
        return self._items[-limit:]
