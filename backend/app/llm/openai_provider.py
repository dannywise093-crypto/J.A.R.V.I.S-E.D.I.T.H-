import httpx

from .base import LLMProvider
from ..core.config import settings


class OpenAIProvider(LLMProvider):
    """OpenAI Responses API adapter. The API key is read only from the environment."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def chat(self, message: str, context: list[dict[str, str]] | None = None) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        history = context or []
        input_items = [
            {"role": item["role"], "content": item["content"]}
            for item in history
            if item.get("role") in {"user", "assistant"}
        ]
        input_items.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "input": input_items,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        output_text = data.get("output_text")
        if output_text:
            return output_text

        for item in data.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if text:
                    return text
        raise RuntimeError("OpenAI returned no text output")
