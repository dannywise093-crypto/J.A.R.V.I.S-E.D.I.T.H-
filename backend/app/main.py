from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .core.config import settings
from .core.permissions import PermissionManager, PermissionMode
from .core.security import require_api_token
from .hardware.capabilities import CAPABILITIES, get_capability
from .hardware.executor import AuthorizedHardwareExecutor
from .hardware.registry import HardwareRegistry
from .llm.provider import get_llm_provider
from .memory.store import MemoryStore
from .tools.device_registry import DeviceRegistry
from .tools.registry import ToolRegistry
from .tools.system_status import get_system_status
from .vision.openai_adapter import OpenAIVisionAdapter
from .voice.openai_adapter import build_openai_voice_service

app = FastAPI(title=settings.app_name, version="0.5.0")
memory = MemoryStore()
devices = DeviceRegistry()
tools = ToolRegistry()
permissions = PermissionManager()
hardware = AuthorizedHardwareExecutor(permissions)
universal_devices = HardwareRegistry(permissions)
vision = OpenAIVisionAdapter()
tools.register("system.status", get_system_status)
tools.register("devices.list", devices.list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ToolRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    voice: str | None = Field(default=None, max_length=50)


class PermissionRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    capability: str = Field(min_length=1, max_length=100)


class PermissionGrantRequest(PermissionRequest):
    mode: PermissionMode


class HardwareActionRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    capability: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    parameters: dict = Field(default_factory=dict)


class UniversalEnrollRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=200)
    system_type: str = Field(min_length=1, max_length=50)
    transport: str = Field(min_length=1, max_length=100)
    endpoint: str | None = Field(default=None, max_length=1000)
    metadata: dict = Field(default_factory=dict)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": "0.5.0"}


@app.get("/status", dependencies=[Depends(require_api_token)])
async def status() -> dict:
    return {
        "service": settings.app_name,
        "environment": settings.app_env,
        "memory_items": len(memory.recent(100)),
        "voice": settings.llm_provider == "openai" and bool(settings.openai_api_key),
        "edith_vision": bool(settings.openai_api_key),
        "hardware_permission_count": len(permissions.list_grants()),
        "universal_device_count": len(universal_devices.list()),
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


@app.get("/api/v1/hardware/devices", dependencies=[Depends(require_api_token)])
async def list_hardware_devices() -> dict[str, list[dict]]:
    return {"devices": universal_devices.list()}


@app.post("/api/v1/hardware/devices/enroll", dependencies=[Depends(require_api_token)])
async def enroll_hardware_device(request: UniversalEnrollRequest) -> dict:
    try:
        device = universal_devices.enroll_system(
            request.device_id,
            request.name,
            request.system_type,
            request.transport,
            request.endpoint,
            request.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "status": "enrolled_and_authorized",
        "device": {
            "id": device.id,
            "name": device.name,
            "platform": device.platform,
            "transport": device.transport,
            "endpoint": device.endpoint,
            "authorized": device.authorized,
            "adapter_connected": device.adapter is not None,
        },
        "next_step": "Attach a concrete authenticated adapter before executing actions.",
    }


@app.post("/api/v1/hardware/devices/{device_id}/revoke", dependencies=[Depends(require_api_token)])
async def revoke_hardware_device(device_id: str) -> dict:
    revoked = universal_devices.revoke(device_id)
    return {"status": "revoked" if revoked else "not_found", "device_id": device_id}


@app.get("/api/v1/hardware/capabilities", dependencies=[Depends(require_api_token)])
async def list_hardware_capabilities() -> dict[str, list[dict]]:
    return {"capabilities": [
        {"name": c.name, "description": c.description, "sensitive": c.sensitive}
        for c in CAPABILITIES.values()
    ]}


@app.get("/api/v1/hardware/permissions", dependencies=[Depends(require_api_token)])
async def list_hardware_permissions() -> dict[str, list[dict]]:
    return {"grants": permissions.list_grants()}


@app.post("/api/v1/hardware/permissions/request", dependencies=[Depends(require_api_token)])
async def request_hardware_permission(request: PermissionRequest) -> dict:
    get_capability(request.capability)
    return permissions.request(request.device_id, request.capability)


@app.post("/api/v1/hardware/permissions/grant", dependencies=[Depends(require_api_token)])
async def grant_hardware_permission(request: PermissionGrantRequest) -> dict:
    capability = get_capability(request.capability)
    grant = permissions.grant(request.device_id, capability.name, request.mode)
    return {"status": "granted", "grant": {
        "grant_id": grant.grant_id,
        "device_id": grant.device_id,
        "capability": grant.capability,
        "mode": grant.mode.value,
        "granted_at": grant.granted_at,
    }}


@app.post("/api/v1/hardware/permissions/revoke", dependencies=[Depends(require_api_token)])
async def revoke_hardware_permission(request: PermissionRequest) -> dict:
    get_capability(request.capability)
    return {"status": "revoked" if permissions.revoke(request.device_id, request.capability) else "not_granted", "device_id": request.device_id, "capability": request.capability}


@app.post("/api/v1/hardware/actions", dependencies=[Depends(require_api_token)])
async def hardware_action(request: HardwareActionRequest) -> dict:
    try:
        return await hardware.execute(request.device_id, request.capability, request.action, request.parameters)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.post("/api/v1/edith/analyze", dependencies=[Depends(require_api_token)])
async def edith_analyze(file: UploadFile = File(...), prompt: str = "Analyze this scene for E.D.I.T.H.") -> dict:
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    image = await file.read()
    if not image:
        raise HTTPException(status_code=400, detail="Image is empty")
    if len(image) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image is too large")
    media_type = file.content_type or "image/jpeg"
    try:
        return await vision.analyze(image, media_type, prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"E.D.I.T.H. vision analysis failed: {exc}") from exc


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
