from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentProfile:
    name: str
    role: str
    specialties: tuple[str, ...]


JARVIS = AgentProfile(
    name="J.A.R.V.I.S.",
    role="general intelligence and engineering agent",
    specialties=("reasoning", "software engineering", "architecture", "debugging", "automation", "systems", "research", "planning"),
)

EDITH = AgentProfile(
    name="E.D.I.T.H.",
    role="general intelligence, vision, and multimodal engineering agent",
    specialties=("reasoning", "vision", "multimodal analysis", "software engineering", "visual debugging", "research", "situational analysis"),
)


class CollaborationEngine:
    """Coordinates two distinct AI identities while preserving human verification."""

    def route(self, task: str, visual_context: bool = False) -> dict[str, Any]:
        primary = EDITH if visual_context else JARVIS
        secondary = JARVIS if visual_context else EDITH
        return {
            "primary": primary.name,
            "secondary": secondary.name,
            "task": task,
            "collaboration": True,
            "requires_human_verification": True,
        }
