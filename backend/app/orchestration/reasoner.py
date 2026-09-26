"""Model-backed reasoning seam for J.A.R.V.I.S."""

from backend.app.llm.contracts import ChatMessage, LLMProvider, ModelRequest, ModelResponse

class Reasoner:
    def __init__(self, provider: LLMProvider, system_prompt: str = "You are J.A.R.V.I.S, a careful AI assistant.") -> None:
        self.provider = provider
        self.system_prompt = system_prompt

    def answer(self, user_text: str, model: str | None = None) -> ModelResponse:
        request = ModelRequest(
            messages=(ChatMessage("system", self.system_prompt), ChatMessage("user", user_text)),
            model=model,
        )
        return self.provider.complete(request)
