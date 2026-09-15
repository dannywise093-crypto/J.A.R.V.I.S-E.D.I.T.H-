from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core.config import settings
from .core.security import require_api_token
from .llm.provider import get_llm_provider
from .memory.store import MemoryStore
from .tools.device_registry import DeviceRegistry
from .tools.registry import ToolRegistry
from .tools.system_status import get_system_status

app = FastAPI(title=settings.app_name, version="0.1.0")
memory = MemoryStore()
devices = DeviceRegistry()
tools = ToolRegistry()
tools.register("system.status", get_system_status)
tools.register("devices.list", devices.list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ToolRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}


@app.get("/status", dependencies=[Depends(require_api_token)])
async def status() -> dict:
    return {"service": settings.app_name, "environment": settings.app_env, "memory_items": len(memory.recent(100))}


@app.post("/api/v1/chat", dependencies=[Depends(require_api_token)])
async def chat(request: ChatRequest) -> dict[str, str]:
    provider = get_llm_provider()
    context = memory.recent()
    memory.add("user", request.message)
    response = await provider.chat(request.message, context)
    memory.add("assistant", response)
    return {"response": response}


@app.post("/api/v1/tools/execute", dependencies=[Depends(require_api_token)])
async def execute_tool(request: ToolRequest) -> dict:
    try:
        return {"tool": request.name, "result": tools.execute(request.name)}
    except (PermissionError, KeyError) as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.get("/api/v1/devices", dependencies=[Depends(require_api_token)])
async def list_devices() -> dict[str, list[dict]]:
    return {"devices": devices.list()}
