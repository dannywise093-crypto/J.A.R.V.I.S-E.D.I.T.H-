from __future__ import annotations

import base64

import httpx

from ..core.config import settings


class OpenAIVisionAdapter:
    """E.D.I.T.H. image understanding adapter using the Responses API."""

    async def analyze(self, image: bytes, media_type: str = "image/jpeg", prompt: str = "Analyze this scene for E.D.I.T.H.") -> dict:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        encoded = base64.b64encode(image).decode("ascii")
        payload = {
            "model": settings.vision_model,
            "input": [{"role": "user", "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:{media_type};base64,{encoded}"},
            ]}],
        }
        headers = {"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        text = data.get("output_text", "").strip()
        if not text:
            for item in data.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"}:
                        text = str(content.get("text", "")).strip()
                        if text:
                            break
                if text:
                    break
        return {"analysis": text, "model": settings.vision_model}
