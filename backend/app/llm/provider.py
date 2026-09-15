from .base import LLMProvider, MockLLMProvider
from .openai_provider import OpenAIProvider
from ..core.config import settings


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    if settings.llm_provider == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
        )
    raise RuntimeError(f"LLM provider '{settings.llm_provider}' is not configured yet")
