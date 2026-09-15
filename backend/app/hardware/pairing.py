from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from secrets import token_urlsafe
from threading import Lock
from uuid import uuid4


@dataclass(frozen=True)
class PairingSession:
    pairing_id: str
    device_id: str
    code: str
    created_at: str
    expires_at: str
    status: str = "pending"


class PairingManager:
    """Short-lived pairing challenges for enrolling concrete device agents."""

    def __init__(self) -> None:
        self._sessions: dict[str, PairingSession] = {}
        self._lock = Lock()

    def create(self, device_id: str, ttl_seconds: int = 300) -> PairingSession:
        if not 30 <= ttl_seconds <= 900:
            raise ValueError("ttl_seconds must be between 30 and 900")
        now = datetime.now(timezone.utc)
        expires = now.timestamp() + ttl_seconds
        session = PairingSession(
            pairing_id=str(uuid4()),
            device_id=device_id,
            code=token_urlsafe(24),
            created_at=now.isoformat(),
            expires_at=datetime.fromtimestamp(expires, timezone.utc).isoformat(),
        )
        with self._lock:
            self._sessions[session.pairing_id] = session
        return session

    def consume(self, pairing_id: str, code: str) -> PairingSession:
        now = datetime.now(timezone.utc)
        with self._lock:
            session = self._sessions.get(pairing_id)
            if session is None or session.status != "pending":
                raise PermissionError("Pairing session is invalid or already used")
            if now >= datetime.fromisoformat(session.expires_at):
                self._sessions.pop(pairing_id, None)
                raise PermissionError("Pairing session has expired")
            if code != session.code:
                raise PermissionError("Invalid pairing code")
            verified = PairingSession(
                session.pairing_id,
                session.device_id,
                session.code,
                session.created_at,
                session.expires_at,
                "verified",
            )
            self._sessions[pairing_id] = verified
            return verified

    def list(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        with self._lock:
            active = []
            for session in self._sessions.values():
                if now < datetime.fromisoformat(session.expires_at):
                    active.append({
                        "pairing_id": session.pairing_id,
                        "device_id": session.device_id,
                        "created_at": session.created_at,
                        "expires_at": session.expires_at,
                        "status": session.status,
                    })
            return active
