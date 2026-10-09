from abc import ABC, abstractmethod
from typing import Optional


class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""

    pass


class OllamaOfflineError(LLMProviderError):
    """Raised when Ollama server is offline or generation fails."""

    pass


class OpenAIAPIError(LLMProviderError):
    """Raised when OpenAI API request fails or credentials are invalid."""

    pass


class GeminiAPIError(LLMProviderError):
    """Raised when Google Gemini API request fails or credentials are invalid."""

    pass


class LLMAllProvidersFailedError(OllamaOfflineError):
    """Raised when all configured LLM providers fail during generation."""

    def __init__(self, message: str, errors: Optional[dict[str, str]] = None):
        super().__init__(message)
        self.errors = errors or {}


class BaseLLMProvider(ABC):
    """Abstract base class for individual LLM providers."""

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available for execution."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 10.0,
        **kwargs,
    ) -> str:
        """Generate text completion for given prompt.

        Args:
            prompt: User prompt text.
            system_prompt: Optional system instruction prompt.
            timeout: Network request timeout in seconds.
            **kwargs: Extra parameters (e.g. temperature, model).

        Returns:
            Generated text string.
        """
        pass
