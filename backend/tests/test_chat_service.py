import pytest
from backend.app.api.chat import ChatService
from backend.app.llm.mock import MockProvider
from backend.app.orchestration.reasoner import Reasoner

def test_chat_service_returns_model_response():
    result = ChatService(Reasoner(MockProvider())).chat("hello")
    assert result.response == "[mock] hello"
    assert result.model == "mock-v1"

def test_chat_service_rejects_empty_message():
    with pytest.raises(ValueError):
        ChatService(Reasoner(MockProvider())).chat("   ")
