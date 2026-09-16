from app.engineering.quality_gate import GateStage, SelfReviewEngine


def test_valid_python_passes_syntax_gate() -> None:
    engine = SelfReviewEngine()
    run = engine.review_python_files(
        {"example.py": "def add(a, b):\n    return a + b\n"},
        "run-valid",
    )
    assert run.status == "ready_for_human_verification"
    assert run.ready_for_human_verification is True
    assert run.stages[0].stage == GateStage.SYNTAX
    assert run.stages[0].passed is True


def test_invalid_python_is_blocked() -> None:
    engine = SelfReviewEngine()
    run = engine.review_python_files(
        {"broken.py": "def add(a, b)\n    return a + b\n"},
        "run-invalid",
    )
    assert run.status == "blocked"
    assert run.ready_for_human_verification is False
    assert run.stages[0].passed is False
    assert run.stages[0].issues[0].stage == GateStage.SYNTAX


def test_repair_budget_is_bounded() -> None:
    engine = SelfReviewEngine(max_repair_attempts=3)
    assert engine.max_repair_attempts == 3
    run = engine.review_python_files({"broken.py": "def x(\n"}, "run-budget")
    assert len(run.repairs) <= engine.max_repair_attempts
