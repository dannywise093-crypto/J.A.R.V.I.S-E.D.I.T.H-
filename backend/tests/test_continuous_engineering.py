from app.engineering.continuous import ContinuousEngineeringCoordinator


def test_coordinator_routes_two_ai_identities() -> None:
    coordinator = ContinuousEngineeringCoordinator()
    session = coordinator.start("Build the API client")
    assert session.route["primary"] == "J.A.R.V.I.S."
    assert session.route["secondary"] == "E.D.I.T.H."
    assert session.route["collaboration"] is True


def test_coordinator_blocks_bad_source() -> None:
    coordinator = ContinuousEngineeringCoordinator()
    session = coordinator.start("Repair this module")
    coordinator.validate(session, {"broken.py": "def broken(\n"})
    assert session.status == "blocked"
    assert session.review["ready_for_human_verification"] is False
