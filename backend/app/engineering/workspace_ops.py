from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


class WorkspaceSecurityError(ValueError):
    pass


@dataclass(frozen=True)
class FileChangeProposal:
    change_id: str
    relative_path: str
    summary: str
    old_content: str
    new_content: str
    unified_diff: str
    verification_required: bool = True


class WorkspaceOperator:
    """Read and propose changes inside an explicitly authorized workspace.

    This layer does not execute commands and does not apply changes. A later
    verified write adapter can consume FileChangeProposal objects.
    """

    def safe_path(self, root: str | Path, relative_path: str) -> Path:
        if not relative_path or "\x00" in relative_path:
            raise WorkspaceSecurityError("invalid workspace path")
        candidate = Path(relative_path.replace("\\", "/"))
        if candidate.is_absolute() or candidate.anchor:
            raise WorkspaceSecurityError("absolute paths are not allowed")
        root_path = Path(root).expanduser().resolve()
        if not root_path.is_dir():
            raise WorkspaceSecurityError("workspace root must be an existing directory")
        resolved = (root_path / candidate).resolve()
        try:
            resolved.relative_to(root_path)
        except ValueError as exc:
            raise WorkspaceSecurityError("path escapes the workspace root") from exc
        return resolved

    def list_files(self, root: str | Path, max_files: int = 2000) -> list[str]:
        if not 1 <= max_files <= 10000:
            raise ValueError("max_files must be between 1 and 10000")
        root_path = Path(root).expanduser().resolve()
        if not root_path.is_dir():
            raise WorkspaceSecurityError("workspace root must be an existing directory")
        result: list[str] = []
        for path in sorted(root_path.rglob("*")):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            result.append(path.relative_to(root_path).as_posix())
            if len(result) >= max_files:
                break
        return result

    def read_file(self, root: str | Path, relative_path: str, max_bytes: int = 2_000_000) -> str:
        path = self.safe_path(root, relative_path)
        if not path.is_file():
            raise FileNotFoundError(relative_path)
        if path.stat().st_size > max_bytes:
            raise WorkspaceSecurityError("file exceeds the configured read limit")
        return path.read_text(encoding="utf-8")

    def propose_file_change(self, root: str | Path, relative_path: str, new_content: str, summary: str) -> FileChangeProposal:
        if not summary.strip():
            raise ValueError("summary is required")
        path = self.safe_path(root, relative_path)
        old_content = path.read_text(encoding="utf-8") if path.exists() else ""
        diff = "".join(difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{relative_path}",
            tofile=f"b/{relative_path}",
        ))
        return FileChangeProposal(
            change_id=str(uuid4()),
            relative_path=Path(relative_path.replace("\\", "/")).as_posix(),
            summary=summary.strip(),
            old_content=old_content,
            new_content=new_content,
            unified_diff=diff,
        )
