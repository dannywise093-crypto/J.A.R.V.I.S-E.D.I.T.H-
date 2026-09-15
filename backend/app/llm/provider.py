from .base import LLMProvider, MockLLMProvider
from ..core.config import settings


def get_llm_provider() -> LLMProvider:
    # External providers are intentionally adapter-based. Credentials stay in
    # environment variables and are never committed to the repository.
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    raise RuntimeError(f"LLM provider '{settings.llm_provider}' is not configured yet")
