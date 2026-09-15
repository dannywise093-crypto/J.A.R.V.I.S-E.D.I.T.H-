from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


SOURCE_TYPES = (
    "web",
    "news",
    "academic",
    "documentation",
    "github",
    "dataset",
    "company",
    "book",
    "pdf",
    "video",
    "image",
)


@dataclass(frozen=True)
class ResearchSource:
    source_id: str
    title: str
    url: str
    source_type: str
    publisher: str | None = None
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ResearchReport:
    research_id: str
    question: str
    sources: list[ResearchSource]
    findings: list[str]
    uncertainty: list[str]
    status: str = "draft"


class ResearchEngine:
    """Evidence-first research orchestration boundary.

    Retrieval providers are intentionally injected later. The engine keeps
    source metadata, findings, and uncertainty separate so reports can expose
    evidence instead of presenting unsupported conclusions as facts.
    """

    def create_research(self, question: str) -> ResearchReport:
        if not question.strip():
            raise ValueError("question is required")
        return ResearchReport(
            research_id=str(uuid4()),
            question=question.strip(),
            sources=[],
            findings=[],
            uncertainty=[],
        )

    def add_source(
        self,
        report: ResearchReport,
        title: str,
        url: str,
        source_type: str = "web",
        publisher: str | None = None,
    ) -> ResearchSource:
        if source_type not in SOURCE_TYPES:
            raise ValueError(f"Unsupported source_type: {source_type}")
        if not title.strip() or not url.strip():
            raise ValueError("title and url are required")
        source = ResearchSource(str(uuid4()), title.strip(), url.strip(), source_type, publisher)
        report.sources.append(source)
        return source

    def add_finding(self, report: ResearchReport, finding: str) -> None:
        if finding.strip():
            report.findings.append(finding.strip())

    def add_uncertainty(self, report: ResearchReport, note: str) -> None:
        if note.strip():
            report.uncertainty.append(note.strip())

    def summarize(self, report: ResearchReport) -> dict[str, Any]:
        return {
            "research_id": report.research_id,
            "question": report.question,
            "status": report.status,
            "source_count": len(report.sources),
            "source_types": sorted({source.source_type for source in report.sources}),
            "findings": report.findings,
            "uncertainty": report.uncertainty,
            "sources": [source.__dict__ for source in report.sources],
        }
