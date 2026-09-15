from __future__ import annotations

from hashlib import sha256
from secrets import token_urlsafe
from threading import Lock


class AgentCredentialManager:
    """Issues revocable per-device bearer credentials without storing raw tokens."""

    def __init__(self) -> None:
        self._hashes: dict[str, str] = {}
        self._lock = Lock()

    def issue(self, device_id: str) -> str:
        token = token_urlsafe(32)
        with self._lock:
            self._hashes[device_id] = self._hash(token)
        return token

    def verify(self, device_id: str, token: str) -> bool:
        if not token:
            return False
        with self._lock:
            expected = self._hashes.get(device_id)
        return expected == self._hash(token)

    def revoke(self, device_id: str) -> bool:
        with self._lock:
            return self._hashes.pop(device_id, None) is not None

    @staticmethod
    def _hash(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()
