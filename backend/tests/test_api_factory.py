from backend.app.api.factory import build_chat_service, handle_chat
from backend.app.api.schemas import ChatRequest

def test_chat_composition_root():
    result = handle_chat(build_chat_service(), ChatRequest("hello"))
    assert result.response == "[mock] hello"
    assert result.model == "mock-v1"
