from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class CodeChange:
    change_id: str
    workspace_id: str
    summary: str
    files: tuple[str, ...]
    risk: str
    requires_verification: bool = True


@dataclass
class CodeWorkspace:
    workspace_id: str
    name: str
    root: str
    language_hints: list[str] = field(default_factory=list)


class CodeStudio:
    """Provider-neutral planning layer for J.A.R.V.I.S./E.D.I.T.H. coding work.

    This stage prepares structured engineering changes. Applying or executing
    consequential changes remains behind the human verification boundary.
    """

    def create_workspace(self, name: str, root: str, language_hints: list[str] | None = None) -> CodeWorkspace:
        if not name.strip() or not root.strip():
            raise ValueError("name and root are required")
        return CodeWorkspace(str(uuid4()), name.strip(), root.strip(), language_hints or [])

    def propose_change(
        self,
        workspace_id: str,
        summary: str,
        files: list[str],
        risk: str = "medium",
    ) -> CodeChange:
        if not workspace_id or not summary.strip():
            raise ValueError("workspace_id and summary are required")
        if not files:
            raise ValueError("at least one file is required")
        if risk not in {"low", "medium", "high", "critical"}:
            raise ValueError("risk must be low, medium, high, or critical")
        return CodeChange(str(uuid4()), workspace_id, summary.strip(), tuple(files), risk, True)

    def describe(self, workspace: CodeWorkspace) -> dict[str, Any]:
        return {
            "workspace_id": workspace.workspace_id,
            "name": workspace.name,
            "root": workspace.root,
            "language_hints": workspace.language_hints,
            "verification_required": True,
        }
