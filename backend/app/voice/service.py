from abc import ABC, abstractmethod


class SpeechToText(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes, filename: str = "audio.wav") -> str:
        raise NotImplementedError


class TextToSpeech(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        raise NotImplementedError


class VoiceService:
    """Provider-neutral voice orchestration boundary.

    Concrete STT/TTS adapters are injected later, so the API does not depend
    on a particular speech vendor or local engine.
    """

    def __init__(self, stt: SpeechToText | None = None, tts: TextToSpeech | None = None) -> None:
        self.stt = stt
        self.tts = tts

    async def transcribe(self, audio: bytes, filename: str = "audio.wav") -> str:
        if self.stt is None:
            raise RuntimeError("Speech-to-text adapter is not configured")
        return await self.stt.transcribe(audio, filename)

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        if self.tts is None:
            raise RuntimeError("Text-to-speech adapter is not configured")
        return await self.tts.synthesize(text, voice)
