from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, message: str, context: list[dict[str, str]] | None = None) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    async def chat(self, message: str, context: list[dict[str, str]] | None = None) -> str:
        return f"J.A.R.V.I.S. core received: {message}"
