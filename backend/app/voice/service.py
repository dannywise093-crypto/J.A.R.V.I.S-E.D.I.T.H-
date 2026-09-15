class VoiceService:
    """Voice adapter boundary. STT/TTS engines plug in without changing the API."""

    async def transcribe(self, audio: bytes) -> str:
        raise NotImplementedError("Configure a Faster-Whisper adapter for speech-to-text")

    async def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("Configure a Piper or other TTS adapter for speech output")
