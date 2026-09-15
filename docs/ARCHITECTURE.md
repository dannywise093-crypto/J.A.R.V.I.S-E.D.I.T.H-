# J.A.R.V.I.S.-E.D.I.T.H. Architecture

## Core
- **J.A.R.V.I.S.**: conversational reasoning, memory, tool orchestration, device policy, and API control plane.
- **E.D.I.T.H.**: visual/context layer for image and scene analysis. It is an adapter boundary in v0.1.
- **Security core**: bearer authentication, explicit tool allowlists, authorized-device registry, and audit-ready boundaries.

## v0.1 flow

Client -> authenticated API -> J.A.R.V.I.S. orchestration -> provider/tool/memory adapters.

E.D.I.T.H. will later attach through a vision adapter and pass structured observations into the orchestration layer.

## Design rule
No arbitrary shell execution, covert microphone/camera activation, credential collection, or unrestricted remote-control endpoint is part of the core. Device actions must be explicitly enrolled and permissioned.

## Planned adapters
- Faster-Whisper STT
- Piper or another TTS engine
- OpenAI/Gemini/Anthropic/local LLM providers
- OpenCV/YOLO/MediaPipe vision
- SQLite then Qdrant/ChromaDB for persistent memory
- Home Assistant/MQTT for explicitly authorized smart-home devices
- User-controlled VPN/zero-trust networking for remote access
