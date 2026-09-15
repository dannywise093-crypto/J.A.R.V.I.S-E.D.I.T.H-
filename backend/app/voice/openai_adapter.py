from __future__ import annotations

import io

import httpx

from ..core.config import settings
from .service import SpeechToText, TextToSpeech


class OpenAISpeechToText(SpeechToText):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def transcribe(self, audio: bytes, filename: str = "audio.wav") -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": (filename, io.BytesIO(audio), "application/octet-stream")}
        data = {"model": self.model}
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            payload = response.json()
        return str(payload.get("text", "")).strip()


class OpenAITextToSpeech(TextToSpeech):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        payload = {
            "model": self.model,
            "voice": voice or "alloy",
            "input": text,
            "response_format": "mp3",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.content


def build_openai_voice_service():
    from .service import VoiceService

    return VoiceService(
        stt=OpenAISpeechToText(settings.openai_api_key, settings.openai_transcription_model),
        tts=OpenAITextToSpeech(settings.openai_api_key, settings.openai_tts_model),
    )
