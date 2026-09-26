"""Provider-neutral structured tool-call parsing."""
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ParsedToolCall:
    name: str
    arguments: dict[str, Any]

def parse_tool_call(payload: dict[str, Any]) -> ParsedToolCall:
    name = payload.get("name")
    arguments = payload.get("arguments", {})
    if not isinstance(name, str) or not name.strip():
        raise ValueError("tool call name is required")
    if not isinstance(arguments, dict):
        raise ValueError("tool call arguments must be an object")
    return ParsedToolCall(name=name.strip(), arguments=arguments)
