import pytest

from app.core.permissions import PermissionManager, PermissionMode


def test_hardware_permissions_default_to_deny() -> None:
    manager = PermissionManager()

    with pytest.raises(PermissionError):
        manager.require("android-phone", "camera.read")


def test_user_grant_allows_authorized_capability() -> None:
    manager = PermissionManager()
    grant = manager.grant("android-phone", "microphone.record", PermissionMode.ONCE)

    assert grant.device_id == "android-phone"
    assert manager.require("android-phone", "microphone.record") == grant


def test_revoke_removes_access() -> None:
    manager = PermissionManager()
    manager.grant("pc", "keyboard.input", PermissionMode.SESSION)

    assert manager.revoke("pc", "keyboard.input") is True
    with pytest.raises(PermissionError):
        manager.require("pc", "keyboard.input")
