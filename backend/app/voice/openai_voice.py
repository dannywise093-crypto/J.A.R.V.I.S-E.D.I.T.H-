from __future__ import annotations

import io

import httpx


class OpenAIVoiceService:
    """OpenAI-backed speech-to-text and text-to-speech adapter."""

    def __init__(self, api_key: str, transcription_model: str = "gpt-4o-transcribe", tts_model: str = "gpt-4o-mini-tts") -> None:
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI voice")
        self.api_key = api_key
        self.transcription_model = transcription_model
        self.tts_model = tts_model

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        files = {"file": (filename, io.BytesIO(audio), "application/octet-stream")}
        data = {"model": self.transcription_model}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=self.headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            payload = response.json()
        return str(payload.get("text", "")).strip()

    async def synthesize(self, text: str, voice: str = "alloy", response_format: str = "mp3") -> bytes:
        payload = {
            "model": self.tts_model,
            "voice": voice,
            "input": text,
            "response_format": response_format,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return response.content
