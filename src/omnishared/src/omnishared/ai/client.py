import requests
from omnishared.config import load_config


class OllamaOfflineError(Exception):
    """Raised when the Ollama server is offline or doesn't respond."""

    pass


def check_ollama_status() -> bool:
    """Check if the local Ollama instance is online."""
    config = load_config()
    ai_config = config.get("ai", {})
    endpoint = ai_config.get("ollama_endpoint", "http://localhost:11434")
    try:
        resp = requests.get(f"{endpoint}/api/tags", timeout=1.5)
        return resp.status_code == 200
    except Exception:
        return False


def generate_completion(
    prompt: str, system_prompt: str = None, timeout: float = 10.0
) -> str:
    """Generate a text completion using the local Ollama instance."""
    config = load_config()
    ai_config = config.get("ai", {})
    endpoint = ai_config.get("ollama_endpoint", "http://localhost:11434")
    model = ai_config.get("ollama_model", "llama3")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        resp = requests.post(f"{endpoint}/api/generate", json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        raise OllamaOfflineError(f"Ollama generation failed: {e}") from e
