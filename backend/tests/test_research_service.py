import pytest
from backend.app.research.providers import MockSearchProvider, SearchHit
from backend.app.research.service import ResearchService

def test_research_service_bounds_results():
    provider = MockSearchProvider([SearchHit("a", "https://example.com/a"), SearchHit("b", "https://example.com/b")])
    assert len(ResearchService(provider, max_results=1).search("query", limit=5)) == 1

def test_research_service_rejects_invalid_max_results():
    with pytest.raises(ValueError):
        ResearchService(MockSearchProvider(), max_results=0)
