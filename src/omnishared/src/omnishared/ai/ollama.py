import os
from typing import Optional

import requests

from omnishared.ai.base import BaseLLMProvider, OllamaOfflineError


class OllamaProvider(BaseLLMProvider):
    """Local Ollama LLM provider implementation."""

    name = "ollama"

    def __init__(self, endpoint: Optional[str] = None, model: Optional[str] = None):
        raw_endpoint = endpoint or os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")
        self.endpoint = raw_endpoint.rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3")

    def is_available(self) -> bool:
        """Check if local Ollama instance is online and responding."""
        try:
            resp = requests.get(f"{self.endpoint}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 10.0,
        **kwargs,
    ) -> str:
        """Generate text completion using local Ollama endpoint."""
        target_model = kwargs.get("model", self.model)
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": kwargs.get("temperature", 0.3)},
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(f"{self.endpoint}/api/generate", json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except Exception as e:
            raise OllamaOfflineError(f"Ollama generation failed ({self.endpoint}): {e}") from e
