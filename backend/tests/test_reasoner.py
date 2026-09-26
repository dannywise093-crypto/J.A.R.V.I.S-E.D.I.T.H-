from backend.app.llm.mock import MockProvider
from backend.app.orchestration.reasoner import Reasoner

def test_reasoner_uses_provider():
    response = Reasoner(MockProvider()).answer("hello")
    assert response.content == "[mock] hello"
    assert response.finish_reason == "stop"
