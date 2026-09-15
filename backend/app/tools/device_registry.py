class DeviceRegistry:
    """Registry for explicitly enrolled, user-authorized devices."""

    def __init__(self) -> None:
        self._devices: dict[str, dict] = {}

    def list(self) -> list[dict]:
        return list(self._devices.values())

    def enroll(self, device_id: str, name: str, kind: str) -> dict:
        device = {"id": device_id, "name": name, "kind": kind, "authorized": True}
        self._devices[device_id] = device
        return device
