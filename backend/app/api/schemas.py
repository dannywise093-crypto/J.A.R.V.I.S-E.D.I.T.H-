"""API request/response schemas kept independent of any web framework."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ChatRequest:
    message: str

@dataclass(frozen=True)
class ChatResponse:
    response: str
    model: str
