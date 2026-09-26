"""Application composition root for the J.A.R.V.I.S chat service."""
from backend.app.api.chat import ChatService
from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.llm.mock import MockProvider
from backend.app.orchestration.reasoner import Reasoner

def build_chat_service() -> ChatService:
    return ChatService(Reasoner(MockProvider()))

def handle_chat(service: ChatService, request: ChatRequest) -> ChatResponse:
    result = service.chat(request.message)
    return ChatResponse(response=result.response, model=result.model)
