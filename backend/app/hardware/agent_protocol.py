from __future__ import annotations

from pydantic import BaseModel, Field


class AgentHello(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    agent_version: str = Field(min_length=1, max_length=50)
    system_type: str = Field(min_length=1, max_length=50)
    platform: str = Field(min_length=1, max_length=100)
    capabilities: list[str] = Field(default_factory=list, max_length=100)


class AgentAction(BaseModel):
    capability: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    parameters: dict = Field(default_factory=dict)


class AgentResult(BaseModel):
    ok: bool
    device_id: str
    result: dict = Field(default_factory=dict)
    error: str | None = None
