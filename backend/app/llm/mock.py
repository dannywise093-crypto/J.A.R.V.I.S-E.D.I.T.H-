"""Deterministic provider for local development and tests."""

from backend.app.llm.contracts import ModelRequest, ModelResponse

class MockProvider:
    def __init__(self, model: str = "mock-v1") -> None:
        self.model = model

    def complete(self, request: ModelRequest) -> ModelResponse:
        last = request.messages[-1].content if request.messages else ""
        return ModelResponse(content=f"[mock] {last}", model=request.model or self.model, finish_reason="stop")
