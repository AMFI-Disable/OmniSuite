from typing import Optional

from omnishared.ai.base import (
    GeminiAPIError,
    LLMAllProvidersFailedError,
    LLMProviderError,
    OllamaOfflineError,
    OpenAIAPIError,
)
from omnishared.ai.multi import MultiLLMProvider
from omnishared.ai.ollama import OllamaProvider

__all__ = [
    "LLMProviderError",
    "OllamaOfflineError",
    "OpenAIAPIError",
    "GeminiAPIError",
    "LLMAllProvidersFailedError",
    "get_multi_provider",
    "reset_multi_provider",
    "check_ollama_status",
    "check_ai_status",
    "generate_completion",
]

_default_multi_provider: Optional[MultiLLMProvider] = None


def get_multi_provider() -> MultiLLMProvider:
    """Get or create default MultiLLMProvider singleton instance."""
    global _default_multi_provider
    if _default_multi_provider is None:
        _default_multi_provider = MultiLLMProvider.from_config()
    return _default_multi_provider


def reset_multi_provider() -> None:
    """Reset default MultiLLMProvider singleton instance."""
    global _default_multi_provider
    _default_multi_provider = None


def check_ollama_status() -> bool:
    """Check if the local Ollama instance is online."""
    provider = OllamaProvider()
    return provider.is_available()


def check_ai_status() -> dict[str, bool]:
    """Check availability of all configured AI providers."""
    return get_multi_provider().check_status()


def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    timeout: float = 10.0,
    provider: Optional[str] = None,
) -> str:
    """Generate text completion using MultiLLMProvider fallback mechanism.

    Args:
        prompt: Prompt text for completion.
        system_prompt: Optional system prompt context.
        timeout: Request timeout in seconds.
        provider: Optional name of preferred provider to try first.

    Returns:
        Generated text string.
    """
    multi = get_multi_provider()
    return multi.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        timeout=timeout,
        preferred_provider=provider,
    )
