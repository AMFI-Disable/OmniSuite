import os
from typing import Optional

import requests

from omnishared.ai.base import BaseLLMProvider, OpenAIAPIError


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation."""

    name = "openai"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        raw_base = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.base_url = raw_base.rstrip("/")

    def is_available(self) -> bool:
        """Check if OpenAI API key is present."""
        return bool(self.api_key and self.api_key.strip())

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 10.0,
        **kwargs,
    ) -> str:
        """Generate text completion using OpenAI Chat Completions API."""
        if not self.is_available():
            raise OpenAIAPIError("OpenAI API key is missing or not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.3),
        }
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]

        try:
            url = f"{self.base_url}/chat/completions"
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise OpenAIAPIError("OpenAI API returned no completion choices.")
            return choices[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            if isinstance(e, OpenAIAPIError):
                raise
            raise OpenAIAPIError(f"OpenAI generation failed: {e}") from e
