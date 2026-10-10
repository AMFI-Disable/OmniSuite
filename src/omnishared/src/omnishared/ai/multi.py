import logging
from collections.abc import Sequence
from typing import Optional

from omnishared.ai.base import (
    BaseLLMProvider,
    LLMAllProvidersFailedError,
    LLMProviderError,
)
from omnishared.ai.gemini import GeminiProvider
from omnishared.ai.ollama import OllamaProvider
from omnishared.ai.openai import OpenAIProvider

logger = logging.getLogger(__name__)


class MultiLLMProvider:
    """Flexible multi-LLM orchestrator supporting multiple AI providers with automatic fallback capability."""

    def __init__(
        self,
        providers: Optional[Sequence[BaseLLMProvider]] = None,
        default_provider_name: Optional[str] = None,
    ):
        self._providers: dict[str, BaseLLMProvider] = {}
        self._order: list[str] = []
        self.default_provider_name = default_provider_name

        if providers:
            for p in providers:
                self.add_provider(p)

    def add_provider(self, provider: BaseLLMProvider, priority: int = 0) -> None:
        """Register an LLM provider.

        Args:
            provider: BaseLLMProvider instance.
            priority: Higher numbers insert provider earlier in execution order.
        """
        name = provider.name.lower()
        self._providers[name] = provider
        if name not in self._order:
            if priority > 0:
                self._order.insert(0, name)
            else:
                self._order.append(name)

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Retrieve provider by name."""
        return self._providers.get(name.lower())

    @property
    def provider_names(self) -> list[str]:
        """Get ordered list of provider names."""
        return list(self._order)

    def set_fallback_order(self, order: list[str]) -> None:
        """Explicitly set the priority and fallback order of providers."""
        new_order = []
        for name in order:
            name_lower = name.lower()
            if name_lower in self._providers and name_lower not in new_order:
                new_order.append(name_lower)
        for name in self._order:
            if name not in new_order:
                new_order.append(name)
        self._order = new_order

    def check_status(self) -> dict[str, bool]:
        """Return availability map for all registered providers."""
        return {name: p.is_available() for name, p in self._providers.items()}

    def is_available(self) -> bool:
        """Check if at least one registered provider is available."""
        return any(p.is_available() for p in self._providers.values())

    def generate_with_metadata(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 10.0,
        preferred_provider: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Generate completion using available providers in fallback order.

        Returns:
            dict containing keys: 'text', 'provider', 'model', 'errors'
        """
        candidates: list[str] = []

        if preferred_provider and preferred_provider.lower() in self._providers:
            candidates.append(preferred_provider.lower())

        if (
            self.default_provider_name
            and self.default_provider_name.lower() in self._providers
            and self.default_provider_name.lower() not in candidates
        ):
            candidates.append(self.default_provider_name.lower())

        for name in self._order:
            if name not in candidates:
                candidates.append(name)

        errors: dict[str, str] = {}
        for provider_name in candidates:
            provider = self._providers.get(provider_name)
            if not provider:
                continue

            try:
                text = provider.generate(
                    prompt,
                    system_prompt=system_prompt,
                    timeout=timeout,
                    **kwargs,
                )
                return {
                    "text": text,
                    "provider": provider.name,
                    "model": getattr(provider, "model", "unknown"),
                    "errors": errors,
                }
            except (LLMProviderError, Exception) as e:
                logger.warning(f"LLM Provider '{provider_name}' execution failed: {e}")
                errors[provider_name] = str(e)

        err_msg = f"All LLM providers failed to generate completion. Errors: {errors}"
        raise LLMAllProvidersFailedError(err_msg, errors=errors)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 10.0,
        preferred_provider: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate text completion from prompt with automatic provider fallback."""
        meta = self.generate_with_metadata(
            prompt=prompt,
            system_prompt=system_prompt,
            timeout=timeout,
            preferred_provider=preferred_provider,
            **kwargs,
        )
        return meta["text"]

    @classmethod
    def from_config(cls, config: Optional[dict] = None) -> "MultiLLMProvider":
        """Factory method to instantiate MultiLLMProvider from application configuration."""
        if config is None:
            from omnishared.config import load_config

            config = load_config()

        ai_cfg = config.get("ai", {})
        primary_name = ai_cfg.get("provider", "ollama")
        fallbacks = ai_cfg.get("fallbacks", ["gemini", "openai"])
        if isinstance(fallbacks, str):
            fallbacks = [f.strip() for f in fallbacks.split(",") if f.strip()]

        ollama_p = OllamaProvider(
            endpoint=ai_cfg.get("ollama_endpoint"),
            model=ai_cfg.get("ollama_model"),
        )
        openai_p = OpenAIProvider(
            api_key=ai_cfg.get("openai_api_key"),
            model=ai_cfg.get("openai_model"),
            base_url=ai_cfg.get("openai_base_url"),
        )
        gemini_p = GeminiProvider(
            api_key=ai_cfg.get("gemini_api_key"),
            model=ai_cfg.get("gemini_model"),
        )

        multi = cls(
            providers=[ollama_p, gemini_p, openai_p],
            default_provider_name=primary_name,
        )

        order = [primary_name] + [f for f in fallbacks if f != primary_name]
        multi.set_fallback_order(order)
        return multi
