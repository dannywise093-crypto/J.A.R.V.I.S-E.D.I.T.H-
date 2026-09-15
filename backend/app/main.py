from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .core.config import settings
from .core.permissions import PermissionManager, PermissionMode
from .core.security import require_api_token
from .hardware.agent_protocol import AgentHello
from .hardware.agent_registry import AgentRegistry
from .hardware.audit import AuditLog
from .hardware.capabilities import CAPABILITIES, get_capability
from .hardware.credentials import AgentCredentialManager
from .hardware.executor import AuthorizedHardwareExecutor
from .hardware.pairing import PairingManager
from .hardware.registry import HardwareRegistry
from .llm.provider import get_llm_provider
from .memory.store import MemoryStore
from .tools.device_registry import DeviceRegistry
from .tools.registry import ToolRegistry
from .tools.system_status import get_system_status
from .vision.openai_adapter import OpenAIVisionAdapter
from .voice.openai_adapter import build_openai_voice_service

app = FastAPI(title=settings.app_name, version="0.6.0")
memory = MemoryStore()
devices = DeviceRegistry()
tools = ToolRegistry()
permissions = PermissionManager()
hardware = AuthorizedHardwareExecutor(permissions)
universal_devices = HardwareRegistry(permissions)
vision = OpenAIVisionAdapter()
pairing = PairingManager()
credentials = AgentCredentialManager()
agents = AgentRegistry()
audit = AuditLog()
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
    session_id: str | None = Field(default=None, max_length=200)


class HardwareActionRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    capability: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    parameters: dict = Field(default_factory=dict)
    session_id: str | None = Field(default=None, max_length=200)


class UniversalEnrollRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=200)
    system_type: str = Field(min_length=1, max_length=50)
    transport: str = Field(min_length=1, max_length=100)
    endpoint: str | None = Field(default=None, max_length=1000)
    metadata: dict = Field(default_factory=dict)


class PairingCreateRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=200)
    ttl_seconds: int = Field(default=300, ge=30, le=900)


class PairingVerifyRequest(BaseModel):
    pairing_id: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=200)
    hello: AgentHello


class AgentTokenHeader(BaseModel):
    token: str


def require_agent_token(device_id: str, authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Agent authentication required")
    token = authorization.removeprefix("Bearer ").strip()
    if not credentials.verify(device_id, token):
        raise HTTPException(status_code=401, detail="Invalid agent credential")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": "0.6.0"}


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
        "agent_count": len(agents.list()),
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
    audit.record("device.enrolled", device_id=device.id, system_type=device.platform)
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
        "next_step": "Create a pairing session and attach a concrete authenticated adapter before executing actions.",
    }


@app.post("/api/v1/hardware/devices/{device_id}/revoke", dependencies=[Depends(require_api_token)])
async def revoke_hardware_device(device_id: str) -> dict:
    revoked = universal_devices.revoke(device_id)
    credentials.revoke(device_id)
    audit.record("device.revoked", device_id=device_id, revoked=revoked)
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
    result = permissions.request(request.device_id, request.capability)
    audit.record("permission.requested", device_id=request.device_id, capability=request.capability)
    return result


@app.post("/api/v1/hardware/permissions/grant", dependencies=[Depends(require_api_token)])
async def grant_hardware_permission(request: PermissionGrantRequest) -> dict:
    capability = get_capability(request.capability)
    try:
        grant = permissions.grant(request.device_id, capability.name, request.mode, request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    audit.record("permission.granted", device_id=request.device_id, capability=capability.name, mode=request.mode.value)
    return {"status": "granted", "grant": {
        "grant_id": grant.grant_id,
        "device_id": grant.device_id,
        "capability": grant.capability,
        "mode": grant.mode.value,
        "granted_at": grant.granted_at,
        "session_id": grant.session_id,
    }}


@app.post("/api/v1/hardware/permissions/revoke", dependencies=[Depends(require_api_token)])
async def revoke_hardware_permission(request: PermissionRequest) -> dict:
    get_capability(request.capability)
    removed = permissions.revoke(request.device_id, request.capability)
    audit.record("permission.revoked", device_id=request.device_id, capability=request.capability, removed=removed)
    return {"status": "revoked" if removed else "not_granted", "device_id": request.device_id, "capability": request.capability}


@app.post("/api/v1/hardware/actions", dependencies=[Depends(require_api_token)])
async def hardware_action(request: HardwareActionRequest) -> dict:
    try:
        spec = get_capability(request.capability)
        grant = permissions.require(request.device_id, spec.name, request.session_id)
        result = await hardware.execute(request.device_id, request.capability, request.action, request.parameters)
        permissions.consume_once(grant)
        audit.record("hardware.action", device_id=request.device_id, capability=request.capability, action=request.action, authorized=True)
        return result
    except PermissionError as exc:
        audit.record("hardware.action.denied", device_id=request.device_id, capability=request.capability, action=request.action, authorized=False)
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.post("/api/v1/hardware/pairing/create", dependencies=[Depends(require_api_token)])
async def create_pairing(request: PairingCreateRequest) -> dict:
    session = pairing.create(request.device_id, request.ttl_seconds)
    audit.record("pairing.created", device_id=request.device_id, pairing_id=session.pairing_id)
    return {
        "pairing_id": session.pairing_id,
        "device_id": session.device_id,
        "code": session.code,
        "expires_at": session.expires_at,
    }


@app.get("/api/v1/hardware/pairing", dependencies=[Depends(require_api_token)])
async def list_pairings() -> dict:
    return {"pairings": pairing.list()}


@app.post("/api/v1/agents/verify")
async def verify_agent(request: PairingVerifyRequest) -> dict:
    if request.hello.device_id != request.hello.device_id:
        raise HTTPException(status_code=400, detail="Invalid device identity")
    try:
        session = pairing.consume(request.pairing_id, request.code)
    except PermissionError as exc:
        audit.record("pairing.failed", pairing_id=request.pairing_id, device_id=request.hello.device_id)
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if session.device_id != request.hello.device_id:
        audit.record("pairing.identity_mismatch", pairing_id=session.pairing_id, device_id=request.hello.device_id)
        raise HTTPException(status_code=403, detail="Pairing identity does not match device")
    token = credentials.issue(request.hello.device_id)
    agents.register(
        request.hello.device_id,
        request.hello.agent_version,
        request.hello.system_type,
        request.hello.platform,
        request.hello.capabilities,
    )
    audit.record("agent.paired", device_id=request.hello.device_id, pairing_id=session.pairing_id)
    return {"status": "paired", "device_id": request.hello.device_id, "agent_token": token}


@app.post("/api/v1/agents/hello")
async def agent_hello(request: AgentHello, authorization: str | None = Header(default=None)) -> dict:
    require_agent_token(request.device_id, authorization)
    record = agents.register(
        request.device_id,
        request.agent_version,
        request.system_type,
        request.platform,
        request.capabilities,
    )
    audit.record("agent.hello", device_id=request.device_id)
    return {"status": "connected", "device_id": record.device_id, "capabilities": sorted(record.capabilities)}


@app.post("/api/v1/agents/{device_id}/heartbeat")
async def agent_heartbeat(device_id: str, authorization: str | None = Header(default=None)) -> dict:
    require_agent_token(device_id, authorization)
    try:
        record = agents.heartbeat(device_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    audit.record("agent.heartbeat", device_id=device_id)
    return {"status": "alive", "device_id": record.device_id, "last_seen": record.last_seen}


@app.get("/api/v1/agents", dependencies=[Depends(require_api_token)])
async def list_agents() -> dict:
    return {"agents": agents.list()}


@app.get("/api/v1/audit", dependencies=[Depends(require_api_token)])
async def list_audit(limit: int = 100) -> dict:
    return {"events": audit.recent(limit)}


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
