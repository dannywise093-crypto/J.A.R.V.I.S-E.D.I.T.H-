from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareCapability:
    name: str
    description: str
    sensitive: bool = False


CAPABILITIES: dict[str, HardwareCapability] = {
    "camera.read": HardwareCapability("camera.read", "Read camera frames", True),
    "microphone.record": HardwareCapability("microphone.record", "Record microphone audio", True),
    "location.read": HardwareCapability("location.read", "Read device location", True),
    "screen.capture": HardwareCapability("screen.capture", "Capture the device display", True),
    "speaker.output": HardwareCapability("speaker.output", "Play audio through the device", False),
    "sensor.read": HardwareCapability("sensor.read", "Read supported device sensors", False),
    "bluetooth.control": HardwareCapability("bluetooth.control", "Control authorized Bluetooth peripherals", False),
    "usb.access": HardwareCapability("usb.access", "Access an authorized USB peripheral", False),
    "display.control": HardwareCapability("display.control", "Control an authorized display", False),
    "keyboard.input": HardwareCapability("keyboard.input", "Send input to an authorized computer", True),
    "mouse.input": HardwareCapability("mouse.input", "Send pointer input to an authorized computer", True),
    "iot.control": HardwareCapability("iot.control", "Control an authorized smart-home device", True),
}


def get_capability(name: str) -> HardwareCapability:
    try:
        return CAPABILITIES[name]
    except KeyError as exc:
        raise PermissionError(f"Unknown hardware capability: {name}") from exc
