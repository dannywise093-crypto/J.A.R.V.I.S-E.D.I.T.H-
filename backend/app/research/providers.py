"""Provider-neutral research retrieval contracts."""
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str = ""

class SearchProvider(Protocol):
    def search(self, query: str, limit: int = 5) -> list[SearchHit]: ...

class MockSearchProvider:
    def __init__(self, hits: list[SearchHit] | None = None) -> None:
        self.hits = hits or []

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        if not query.strip():
            raise ValueError("search query cannot be empty")
        return self.hits[: max(0, limit)]
