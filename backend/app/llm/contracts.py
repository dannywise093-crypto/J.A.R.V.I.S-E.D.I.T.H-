"""Provider-neutral contracts for model-backed reasoning."""

from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str

@dataclass(frozen=True)
class ModelRequest:
    messages: tuple[ChatMessage, ...]
    model: str | None = None
    temperature: float = 0.2
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ModelResponse:
    content: str
    model: str
    finish_reason: str | None = None
    usage: dict[str, int] = field(default_factory=dict)

class LLMProvider(Protocol):
    def complete(self, request: ModelRequest) -> ModelResponse: ...
