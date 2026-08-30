"""
LLM factory for creating language model and embedder instances.
Uses the wrapper classes from backend.models.llm_wrappers.
"""
import os
import time
import threading
from typing import Tuple, Optional, Collection
from enum import Enum
from concordia.language_model import language_model
from backend.models.schemas import LLMSettings, LLMProvider

# Shared LLM activity tracker — updated on every call, read by watchdog
_llm_activity = {
    'last_call_start': 0.0,
    'last_call_end': 0.0,
    'calls_in_flight': 0,
    'total_calls': 0,
}
_llm_activity_lock = threading.Lock()

_active_task_id: Optional[str] = None


def set_active_task_id(task_id: Optional[str]):
    global _active_task_id
    _active_task_id = task_id


def get_llm_activity() -> dict:
    with _llm_activity_lock:
        return dict(_llm_activity)


# Import wrapper classes from backend.models.llm_wrappers
from backend.models.llm_wrappers import (
    CustomGPTModel,
    GeminiModel,
    GLMModel,
    AnthropicModel,
    SentenceTransformerEmbedder
)


class TemperatureConfiguredModel(language_model.LanguageModel):
    """
    Wrapper that configures a model with a specific temperature.
    This allows the user's temperature setting from the web app to be used.
    """

    def __init__(self, base_model: language_model.LanguageModel, temperature: float, request_timeout: float = 120.0, max_tokens: int = 3500):
        self._model = base_model
        self._temperature = temperature
        self._request_timeout = request_timeout
        self._max_tokens = max_tokens

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
        terminators: Collection[str] = language_model.DEFAULT_TERMINATORS,
        temperature: Optional[float] = None,
        timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
        seed: int | None = None,
        top_p: float = 0.95,
        top_k: int = 64,
        **kwargs,
    ) -> str:
        """
        Sample text from the model, using configured temperature if not provided.
        """
        if temperature is None:
            temperature = self._temperature

        max_tokens = max(max_tokens, self._max_tokens)

        timeout = self._request_timeout

        env_timeout = os.getenv('LLM_TIMEOUT')
        if env_timeout:
            try:
                timeout = float(env_timeout)
            except ValueError:
                pass

        if _active_task_id:
            from backend.services.simulation_state import simulation_state
            if simulation_state.should_cancel(_active_task_id):
                from backend.services.simulation_runner import SimulationCancelled
                raise SimulationCancelled(f"Cancelled during LLM call (task {_active_task_id})")

        with _llm_activity_lock:
            _llm_activity['last_call_start'] = time.time()
            _llm_activity['calls_in_flight'] += 1
            _llm_activity['total_calls'] += 1
        try:
            return self._model.sample_text(
                prompt,
                max_tokens=max_tokens,
                terminators=terminators,
                temperature=temperature,
                timeout=timeout,
                seed=seed,
                top_p=top_p,
                top_k=top_k,
                **kwargs,
            )
        finally:
            with _llm_activity_lock:
                _llm_activity['last_call_end'] = time.time()
                _llm_activity['calls_in_flight'] -= 1

    def sample_choice(
        self,
        prompt: str,
        responses: list[str],
        seed: int | None = None,
    ) -> tuple[int, str, dict]:
        """
        Sample a choice from responses, using configured temperature.
        This method doesn't use temperature directly but passes through to the model.
        """
        return self._model.sample_choice(prompt, responses, seed)


def get_model_and_embedder(settings: LLMSettings) -> Tuple[language_model.LanguageModel, SentenceTransformerEmbedder]:
    """
    Get language model and embedder based on settings.

    Args:
        settings: LLMSettings containing provider, model, etc.

    Returns:
        Tuple of (language_model, embedder)

    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    # Get provider value - handle both Enum and string
    provider = settings.provider.value if isinstance(settings.provider, Enum) else str(settings.provider)
    provider = provider.lower()
    model_name = settings.model_name
    api_key = settings.api_key
    base_url = settings.base_url

    # Resolve timeout once — used for all providers below
    request_timeout = float(getattr(settings, 'request_timeout', 300))

    # Try to get API key from settings or environment
    if provider == LLMProvider.OPENAI.value:
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in settings or environment")
        model = CustomGPTModel(api_key=api_key, model_name=model_name, base_url=base_url, extra_body=settings.extra_body)

    elif provider == LLMProvider.AZURE.value:
        # Azure OpenAI Service
        # Parameters from .env: AZURE_OAI_KEY, AZURE_OAI_ENDPOINT, AZURE_OAI_VERSION
        # User provides only: model_name (deployment name)
        api_key = api_key or os.getenv('AZURE_OAI_KEY')
        azure_endpoint = base_url or os.getenv('AZURE_OAI_ENDPOINT')
        api_version = settings.api_version or os.getenv('AZURE_OAI_VERSION', '2024-12-01-preview')  # Default API version

        if not api_key:
            raise ValueError("AZURE_OAI_KEY not found in environment. Please add it to your .env file.")
        if not azure_endpoint:
            raise ValueError("AZURE_OAI_ENDPOINT not found in environment. Please add it to your .env file.")

        model = CustomGPTModel(
            api_key=api_key,
            model_name=model_name,
            base_url=azure_endpoint,
            api_version=api_version,
            extra_body=settings.extra_body,
        )

    elif provider == LLMProvider.AZURE2.value:
        # Secondary Azure OpenAI endpoint (e.g. a Kimi-K2.5 deployment).
        # Parameters from .env: AZURE_OAI_KEY2, AZURE_OAI_ENDPOINT2, and
        # optionally AZURE_OAI_VERSION2 (falls back to AZURE_OAI_VERSION).
        # User provides only: model_name (the endpoint-2 deployment name).
        api_key = api_key or os.getenv('AZURE_OAI_KEY2')
        azure_endpoint = base_url or os.getenv('AZURE_OAI_ENDPOINT2')
        api_version = (settings.api_version or os.getenv('AZURE_OAI_VERSION2')
                       or os.getenv('AZURE_OAI_VERSION', '2024-12-01-preview'))

        if not api_key:
            raise ValueError("AZURE_OAI_KEY2 not found in environment. Please add it to your .env file.")
        if not azure_endpoint:
            raise ValueError("AZURE_OAI_ENDPOINT2 not found in environment. Please add it to your .env file.")

        model = CustomGPTModel(
            api_key=api_key,
            model_name=model_name,
            base_url=azure_endpoint,
            api_version=api_version,
            extra_body=settings.extra_body,
        )

    elif provider == LLMProvider.DEEPSEEK.value:
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set in settings or environment")
        model = CustomGPTModel(
            api_key=api_key,
            model_name=model_name,
            base_url='https://api.deepseek.com',
            extra_body=settings.extra_body,
        )

    elif provider == LLMProvider.GEMINI.value:
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in settings or environment")
        model = GeminiModel(api_key=api_key, model_name=model_name, timeout=request_timeout)

    elif provider == LLMProvider.ANTHROPIC.value:
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in settings or environment")
        model = AnthropicModel(api_key=api_key, model_name=model_name, timeout=request_timeout)

    elif provider == LLMProvider.OLLAMA.value:
        # Ollama local — always uses localhost, no auth needed
        ollama_base_url = 'http://localhost:11434/v1'
        model = CustomGPTModel(
            api_key='ollama',
            model_name=model_name,
            base_url=ollama_base_url,
            extra_body=settings.extra_body,
        )

    elif provider == LLMProvider.OLLAMA_REMOTE.value:
        # Ollama remote — uses .env configured endpoint and API key
        ollama_base_url = base_url or os.getenv('OLLAMA_BASE_URL')
        if not ollama_base_url:
            raise ValueError("OLLAMA_BASE_URL not set for remote Ollama. Set it in .env or provide base_url.")
        ollama_api_key = api_key or os.getenv('OLLAMA_API_KEY', '')
        model = CustomGPTModel(
            api_key=ollama_api_key,
            model_name=model_name,
            base_url=ollama_base_url,
            extra_body=settings.extra_body,
        )

    elif provider == LLMProvider.GLM.value:
        # GLM (Zhipu AI) - fast, reliable Chinese and English models
        if not api_key:
            api_key = os.getenv('GLM_API_KEY')
        if not api_key:
            raise ValueError("GLM_API_KEY not set in settings or environment")
        model = GLMModel(api_key=api_key, model_name=model_name, timeout=request_timeout)

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
    model = TemperatureConfiguredModel(model, settings.temperature, request_timeout, settings.max_tokens)

    # Create embedder
    embedder = SentenceTransformerEmbedder(settings.embedder_model)

    return model, embedder


def get_available_providers() -> list[dict]:
    """Get list of available LLM providers with their models."""
    return [
        {
            "provider": LLMProvider.OPENAI,
            "name": "OpenAI",
            "models": ["gpt-4o", "gpt-3.5-turbo"],
            "requires_api_key": True
        },
        {
            "provider": LLMProvider.AZURE,
            "name": "Azure OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini", "o3-mini"],  # Example deployment names
            "requires_api_key": False,  # Loaded from AZURE_OAI_KEY env var
            "requires_api_version": False,  # Loaded from AZURE_OAI_API_VERSION env var (with default)
            "requires_base_url": False,  # Loaded from AZURE_OAI_ENDPOINT env var
            "note": "Configure in .env: AZURE_OAI_KEY, AZURE_OAI_ENDPOINT. Enter your deployment name manually."
        },
        {
            "provider": LLMProvider.DEEPSEEK,
            "name": "DeepSeek",
            "models": ["deepseek-v4-flash", "deepseek-v4-pro"],
            "requires_api_key": True
        },
        {
            "provider": LLMProvider.GEMINI,
            "name": "Google Gemini",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "requires_api_key": True
        },
        {
            "provider": LLMProvider.ANTHROPIC,
            "name": "Anthropic",
            "models": [
                "claude-sonnet-4-5-20250929",
                "claude-haiku-4-5",
                "claude-opus-4-5"
            ],
            "requires_api_key": True
        },
        {
            "provider": LLMProvider.GLM,
            "name": "GLM (Zhipu AI)",
            "models": [
                "GLM-5.1",
                "GLM-5",
                "GLM-4.7",
                "GLM-4.7-Flash",
                "GLM-4.6",
                "GLM-4.5-Air"
            ],
            "requires_api_key": True,
            "note": "Fast, reliable Chinese and English language models."
        },
        {
            "provider": LLMProvider.OLLAMA,
            "name": "Ollama (Local)",
            "models": ["llama3", "llama3:2", "mistral", "codellama", "phi3", "gemma2", "qwen2"],
            "requires_api_key": False,
            "note": "Requires Ollama to be installed and running locally. Optional API key for services like OpenWebUI."
        }
    ]
