import os
from typing import Optional

import requests

from omnishared.ai.base import BaseLLMProvider, GeminiAPIError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider implementation."""

    name = "gemini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = (
            api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
        )
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    def is_available(self) -> bool:
        """Check if Google Gemini API key is present."""
        return bool(self.api_key and self.api_key.strip())

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 10.0,
        **kwargs,
    ) -> str:
        """Generate text completion using Google Gemini REST API."""
        if not self.is_available():
            raise GeminiAPIError("Google Gemini API key is missing or not configured.")

        target_model = kwargs.get("model", self.model)
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"
            f"?key={self.api_key}"
        )
        headers = {"Content-Type": "application/json"}

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        gen_config = {}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
        if gen_config:
            payload["generationConfig"] = gen_config

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise GeminiAPIError("Gemini API returned no candidates.")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise GeminiAPIError("Gemini API candidate contained no text parts.")
            text = "".join(part.get("text", "") for part in parts)
            return text.strip()
        except Exception as e:
            if isinstance(e, GeminiAPIError):
                raise
            raise GeminiAPIError(f"Gemini generation failed: {e}") from e
