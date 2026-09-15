from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPolicy:
    name: str
    requires_confirmation: bool = False


ALLOWED_TOOLS = {
    "system.status": ToolPolicy("system.status"),
    "devices.list": ToolPolicy("devices.list"),
}


def get_tool_policy(name: str) -> ToolPolicy | None:
    return ALLOWED_TOOLS.get(name)
