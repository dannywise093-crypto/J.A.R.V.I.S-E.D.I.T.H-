"""Small application-facing chat service boundary."""
from dataclasses import dataclass
from backend.app.orchestration.reasoner import Reasoner

@dataclass(frozen=True)
class ChatResult:
    response: str
    model: str

class ChatService:
    def __init__(self, reasoner: Reasoner) -> None:
        self.reasoner = reasoner

    def chat(self, user_text: str) -> ChatResult:
        if not user_text.strip():
            raise ValueError("message cannot be empty")
        result = self.reasoner.answer(user_text.strip())
        return ChatResult(response=result.content, model=result.model)
