"""Research retrieval service with bounded result counts."""
from backend.app.research.providers import SearchHit, SearchProvider

class ResearchService:
    def __init__(self, provider: SearchProvider, max_results: int = 5) -> None:
        if max_results < 1:
            raise ValueError("max_results must be positive")
        self.provider = provider
        self.max_results = max_results

    def search(self, query: str, limit: int | None = None) -> list[SearchHit]:
        count = self.max_results if limit is None else min(max(1, limit), self.max_results)
        return self.provider.search(query.strip(), count)
