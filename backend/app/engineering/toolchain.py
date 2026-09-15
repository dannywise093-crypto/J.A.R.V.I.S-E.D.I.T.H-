from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    category: str
    description: str
    requires_verification: bool = True


TOOLCHAIN: tuple[ToolSpec, ...] = (
    ToolSpec("code.read", "editor", "Read authorized project source files", False),
    ToolSpec("code.propose", "editor", "Prepare a structured code change", True),
    ToolSpec("code.diff", "editor", "Generate a reviewable diff", False),
    ToolSpec("tests.plan", "testing", "Plan tests for a proposed change", False),
    ToolSpec("tests.run", "testing", "Run an authorized project test suite", True),
    ToolSpec("build.run", "build", "Run an authorized project build", True),
    ToolSpec("git.diff", "version_control", "Inspect repository changes", False),
    ToolSpec("git.commit", "version_control", "Create an authorized Git commit", True),
    ToolSpec("debug.analyze", "debugging", "Analyze logs, traces, and diagnostics", False),
)


def list_tools() -> list[dict[str, object]]:
    return [
        {
            "name": tool.name,
            "category": tool.category,
            "description": tool.description,
            "requires_verification": tool.requires_verification,
        }
        for tool in TOOLCHAIN
    ]
