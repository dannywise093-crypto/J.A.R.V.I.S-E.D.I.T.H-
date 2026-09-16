from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GateStage(str, Enum):
    SYNTAX = "syntax"
    STATIC = "static"
    TESTS = "tests"
    BUILD = "build"
    DIAGNOSTICS = "diagnostics"


@dataclass(frozen=True)
class ValidationIssue:
    stage: GateStage
    message: str
    file: str | None = None
    line: int | None = None
    severity: str = "error"


@dataclass(frozen=True)
class ValidationResult:
    stage: GateStage
    passed: bool
    issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True)
class RepairAttempt:
    attempt: int
    issue_count: int
    summary: str


@dataclass
class EngineeringRun:
    run_id: str
    status: str = "pending"
    stages: list[ValidationResult] = field(default_factory=list)
    repairs: list[RepairAttempt] = field(default_factory=list)
    ready_for_human_verification: bool = False


class PythonSyntaxValidator:
    """Validate Python source without executing it."""

    def validate(self, filename: str, source: str) -> ValidationResult:
        try:
            ast.parse(source, filename=filename)
        except SyntaxError as exc:
            issue = ValidationIssue(
                stage=GateStage.SYNTAX,
                message=exc.msg,
                file=filename,
                line=exc.lineno,
            )
            return ValidationResult(GateStage.SYNTAX, False, (issue,))
        return ValidationResult(GateStage.SYNTAX, True)


class SelfReviewEngine:
    """Bounded preflight/review loop for J.A.R.V.I.S. and E.D.I.T.H.

    The engine validates known inputs and produces a review state. It never
    executes arbitrary code and never auto-applies a consequential repair.
    """

    def __init__(self, max_repair_attempts: int = 3) -> None:
        if not 1 <= max_repair_attempts <= 10:
            raise ValueError("max_repair_attempts must be between 1 and 10")
        self.max_repair_attempts = max_repair_attempts
        self.python = PythonSyntaxValidator()

    def validate_python_files(self, files: dict[str, str]) -> list[ValidationResult]:
        return [self.python.validate(name, source) for name, source in files.items()]

    def review_python_files(self, files: dict[str, str], run_id: str) -> EngineeringRun:
        run = EngineeringRun(run_id=run_id)
        results = self.validate_python_files(files)
        run.stages.extend(results)

        failures = [r for r in results if not r.passed]
        if failures:
            run.status = "blocked"
            run.repairs.append(
                RepairAttempt(
                    attempt=1,
                    issue_count=sum(len(r.issues) for r in failures),
                    summary="Syntax issues detected; repair must be proposed and revalidated.",
                )
            )
            run.ready_for_human_verification = False
            return run

        run.status = "ready_for_human_verification"
        run.ready_for_human_verification = True
        return run

    def summarize(self, run: EngineeringRun) -> dict[str, Any]:
        return {
            "run_id": run.run_id,
            "status": run.status,
            "ready_for_human_verification": run.ready_for_human_verification,
            "stages": [
                {
                    "stage": result.stage.value,
                    "passed": result.passed,
                    "issues": [issue.__dict__ for issue in result.issues],
                }
                for result in run.stages
            ],
            "repairs": [repair.__dict__ for repair in run.repairs],
            "max_repair_attempts": self.max_repair_attempts,
        }
