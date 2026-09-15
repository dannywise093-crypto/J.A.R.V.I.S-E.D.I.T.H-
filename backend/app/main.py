from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .core.config import settings
from .core.security import require_api_token
from .llm.provider import get_llm_provider
from .memory.store import MemoryStore
from .tools.device_registry import DeviceRegistry
from .tools.registry import ToolRegistry
from .tools.system_status import get_system_status
from .voice.openai_adapter import build_openai_voice_service

app = FastAPI(title=settings.app_name, version="0.2.0")
memory = MemoryStore()
devices = DeviceRegistry()
tools = ToolRegistry()
tools.register("system.status", get_system_status)
tools.register("devices.list", devices.list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ToolRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    voice: str | None = Field(default=None, max_length=50)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": "0.2.0"}


@app.get("/status", dependencies=[Depends(require_api_token)])
async def status() -> dict:
    return {
        "service": settings.app_name,
        "environment": settings.app_env,
        "memory_items": len(memory.recent(100)),
        "voice": settings.llm_provider == "openai" and bool(settings.openai_api_key),
    }


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


@app.post("/api/v1/voice/transcribe", dependencies=[Depends(require_api_token)])
async def transcribe_voice(file: UploadFile = File(...)) -> dict[str, str]:
    if settings.llm_provider != "openai":
        raise HTTPException(status_code=503, detail="Set LLM_PROVIDER=openai to enable cloud speech")
    audio = await file.read()
    if not audio:
        raise HTTPException(status_code=400, detail="Audio file is empty")
    if len(audio) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file is too large")
    try:
        text = await build_openai_voice_service().transcribe(audio, file.filename or "audio.wav")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Speech transcription failed: {exc}") from exc
    return {"text": text}


@app.post("/api/v1/voice/speak", dependencies=[Depends(require_api_token)])
async def speak_voice(request: SpeakRequest) -> Response:
    if settings.llm_provider != "openai":
        raise HTTPException(status_code=503, detail="Set LLM_PROVIDER=openai to enable cloud speech")
    try:
        audio = await build_openai_voice_service().synthesize(request.text, request.voice)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Speech synthesis failed: {exc}") from exc
    return Response(content=audio, media_type="audio/mpeg")
