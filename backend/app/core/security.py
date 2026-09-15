from fastapi import Header, HTTPException, status

from .config import settings


def require_api_token(authorization: str | None = Header(default=None)) -> None:
    """Require a bearer token for protected endpoints."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
