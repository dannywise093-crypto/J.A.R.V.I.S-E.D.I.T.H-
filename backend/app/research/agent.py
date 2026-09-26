"""Research agent boundary; external retrieval is injected as a dependency."""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class ResearchResult:
    query: str
    findings: str
    sources: tuple[str, ...] = ()

class ResearchAgent:
    capability = "research"

    def __init__(self, search: Callable[[str], ResearchResult]) -> None:
        self._search = search

    def run(self, query: str) -> ResearchResult:
        if not query.strip():
            raise ValueError("research query cannot be empty")
        return self._search(query.strip())
