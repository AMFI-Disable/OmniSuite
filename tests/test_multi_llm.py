from unittest.mock import MagicMock, patch

import pytest
from omnishared.ai import (
    BaseLLMProvider,
    GeminiAPIError,
    GeminiProvider,
    LLMAllProvidersFailedError,
    LLMProviderError,
    MultiLLMProvider,
    OllamaOfflineError,
    OllamaProvider,
    OpenAIAPIError,
    OpenAIProvider,
    check_ai_status,
    generate_completion,
    get_multi_provider,
    reset_multi_provider,
)


def teardown_function():
    reset_multi_provider()


# ─── 1. Ollama Provider Tests ──────────────────────────────────────────────────


@patch("requests.get")
def test_ollama_provider_availability(mock_get):
    provider = OllamaProvider(endpoint="http://localhost:11434")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    assert provider.is_available() is True

    mock_get.side_effect = Exception("Connection refused")
    assert provider.is_available() is False


@patch("requests.post")
def test_ollama_provider_generate(mock_post):
    provider = OllamaProvider(endpoint="http://localhost:11434", model="llama3")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "Ollama response"}
    mock_post.return_value = mock_resp

    res = provider.generate("Hello Ollama", system_prompt="System prompt")
    assert res == "Ollama response"

    # Verify payload
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:11434/api/generate"
    assert kwargs["json"]["prompt"] == "Hello Ollama"
    assert kwargs["json"]["system"] == "System prompt"
    assert kwargs["json"]["model"] == "llama3"


@patch("requests.post")
def test_ollama_provider_failure(mock_post):
    provider = OllamaProvider()
    mock_post.side_effect = Exception("Timeout")
    with pytest.raises(OllamaOfflineError):
        provider.generate("Hello")


# ─── 2. OpenAI Provider Tests ──────────────────────────────────────────────────


def test_openai_provider_availability():
    provider_no_key = OpenAIProvider(api_key="")
    assert provider_no_key.is_available() is False

    provider_with_key = OpenAIProvider(api_key="sk-test-key")
    assert provider_with_key.is_available() is True


@patch("requests.post")
def test_openai_provider_generate(mock_post):
    provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o-mini")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "OpenAI response"}}]}
    mock_post.return_value = mock_resp

    res = provider.generate("Hello OpenAI", system_prompt="Be concise")
    assert res == "OpenAI response"

    args, kwargs = mock_post.call_args
    assert "https://api.openai.com/v1/chat/completions" in args[0]
    assert kwargs["headers"]["Authorization"] == "Bearer sk-test-key"
    assert kwargs["json"]["messages"][0] == {"role": "system", "content": "Be concise"}
    assert kwargs["json"]["messages"][1] == {"role": "user", "content": "Hello OpenAI"}


def test_openai_provider_missing_key():
    provider = OpenAIProvider(api_key="")
    with pytest.raises(OpenAIAPIError):
        provider.generate("Hello")


# ─── 3. Gemini Provider Tests ──────────────────────────────────────────────────


def test_gemini_provider_availability():
    provider_no_key = GeminiProvider(api_key="")
    assert provider_no_key.is_available() is False

    provider_with_key = GeminiProvider(api_key="AIzaSyTestKey")
    assert provider_with_key.is_available() is True


@patch("requests.post")
def test_gemini_provider_generate(mock_post):
    provider = GeminiProvider(api_key="AIzaSyTestKey", model="gemini-2.5-flash")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Gemini response"}]}}]
    }
    mock_post.return_value = mock_resp

    res = provider.generate("Hello Gemini", system_prompt="Instruct system")
    assert res == "Gemini response"

    args, kwargs = mock_post.call_args
    assert "generativelanguage.googleapis.com" in args[0]
    assert "AIzaSyTestKey" in args[0]
    assert kwargs["json"]["contents"][0]["parts"][0]["text"] == "Hello Gemini"
    assert kwargs["json"]["systemInstruction"]["parts"][0]["text"] == "Instruct system"


def test_gemini_provider_missing_key():
    provider = GeminiProvider(api_key="")
    with pytest.raises(GeminiAPIError):
        provider.generate("Hello")


# ─── 4. MultiLLMProvider Fallback & Orchestration Tests ─────────────────────────


class MockFailingProvider(BaseLLMProvider):
    name = "mock_fail"

    def is_available(self) -> bool:
        return True

    def generate(
        self, prompt: str, system_prompt: str = None, timeout: float = 10.0, **kwargs
    ) -> str:
        raise LLMProviderError("Primary provider connection reset")


class MockSuccessProvider(BaseLLMProvider):
    name = "mock_success"

    def is_available(self) -> bool:
        return True

    def generate(
        self, prompt: str, system_prompt: str = None, timeout: float = 10.0, **kwargs
    ) -> str:
        return "Success from fallback provider"


def test_multi_llm_provider_fallback():
    failing = MockFailingProvider()
    succeeding = MockSuccessProvider()

    multi = MultiLLMProvider(providers=[failing, succeeding])
    multi.set_fallback_order(["mock_fail", "mock_success"])

    meta = multi.generate_with_metadata("Test prompt")
    assert meta["text"] == "Success from fallback provider"
    assert meta["provider"] == "mock_success"
    assert "mock_fail" in meta["errors"]


def test_multi_llm_provider_all_failed():
    failing1 = MockFailingProvider()
    failing2 = MockFailingProvider()
    failing2.name = "mock_fail2"

    multi = MultiLLMProvider(providers=[failing1, failing2])
    with pytest.raises(LLMAllProvidersFailedError) as exc_info:
        multi.generate("Test prompt")

    assert "mock_fail" in exc_info.value.errors
    assert "mock_fail2" in exc_info.value.errors


def test_multi_llm_preferred_provider():
    p1 = MockSuccessProvider()
    p1.name = "provider1"
    p2 = MockSuccessProvider()
    p2.name = "provider2"

    multi = MultiLLMProvider(providers=[p1, p2])
    meta = multi.generate_with_metadata("Test prompt", preferred_provider="provider2")
    assert meta["provider"] == "provider2"


def test_multi_llm_from_config():
    custom_config = {
        "ai": {
            "provider": "openai",
            "fallbacks": ["gemini", "ollama"],
            "openai_api_key": "sk-key",
            "gemini_api_key": "gem-key",
            "ollama_endpoint": "http://localhost:11434",
        }
    }
    multi = MultiLLMProvider.from_config(custom_config)
    assert multi.provider_names == ["openai", "gemini", "ollama"]
    status = multi.check_status()
    assert status["openai"] is True
    assert status["gemini"] is True


def test_check_ai_status_and_generate_completion():
    reset_multi_provider()
    status = check_ai_status()
    assert "ollama" in status
    assert "openai" in status
    assert "gemini" in status


@patch("requests.post")
def test_generate_completion_wrapper(mock_post):
    reset_multi_provider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "Wrapped completion text"}
    mock_post.return_value = mock_resp

    res = generate_completion("Wrapper prompt")
    assert res == "Wrapped completion text"
    assert get_multi_provider() is not None
