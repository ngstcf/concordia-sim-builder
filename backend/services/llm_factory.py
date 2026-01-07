"""
LLM factory for creating language model and embedder instances.
Uses the wrapper classes from backend.models.llm_wrappers.
"""
import os
from typing import Tuple, Optional, Collection
from enum import Enum
from concordia.language_model import language_model
from backend.models.schemas import LLMSettings, LLMProvider


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

    def __init__(self, base_model: language_model.LanguageModel, temperature: float):
        self._model = base_model
        self._temperature = temperature

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
        terminators: Collection[str] = language_model.DEFAULT_TERMINATORS,
        temperature: Optional[float] = None,
        timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
        seed: int | None = None,
    ) -> str:
        """
        Sample text from the model, using configured temperature if not provided.
        """
        # Use our configured temperature if caller doesn't specify one
        if temperature is None:
            temperature = self._temperature

        # Call the underlying model's sample_text with the temperature
        return self._model.sample_text(
            prompt,
            max_tokens=max_tokens,
            terminators=terminators,
            temperature=temperature,
            timeout=timeout,
            seed=seed
        )

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

    # Try to get API key from settings or environment
    if provider == LLMProvider.OPENAI.value:
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in settings or environment")
        model = CustomGPTModel(api_key=api_key, model_name=model_name, base_url=base_url)

    elif provider == LLMProvider.DEEPSEEK.value:
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set in settings or environment")
        model = CustomGPTModel(
            api_key=api_key,
            model_name=model_name,
            base_url='https://api.deepseek.com'
        )

    elif provider == LLMProvider.GEMINI.value:
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in settings or environment")
        model = GeminiModel(api_key=api_key, model_name=model_name)

    elif provider == LLMProvider.ANTHROPIC.value:
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in settings or environment")
        model = AnthropicModel(api_key=api_key, model_name=model_name)

    elif provider == LLMProvider.OLLAMA.value:
        # Ollama uses OpenAI-compatible API running on localhost or remote server
        # Default base URL for Ollama is http://localhost:11434/v1
        # Can also use services like OpenWebUI which may require an API key
        ollama_base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')

        # Use provided API key, or check environment, or use dummy key for local Ollama
        # Some Ollama hosting services (like OpenWebUI) require an API key
        ollama_api_key = api_key or os.getenv('OLLAMA_API_KEY', 'ollama')

        model = CustomGPTModel(
            api_key=ollama_api_key,
            model_name=model_name,
            base_url=ollama_base_url
        )

    elif provider == LLMProvider.GLM.value:
        # GLM (Zhipu AI) - fast, reliable Chinese and English models
        if not api_key:
            api_key = os.getenv('GLM_API_KEY')
        if not api_key:
            raise ValueError("GLM_API_KEY not set in settings or environment")
        model = GLMModel(api_key=api_key, model_name=model_name)

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    # Wrap model with temperature configuration from settings
    # This ensures the user's temperature setting from the web app is actually used
    model = TemperatureConfiguredModel(model, settings.temperature)

    # Create embedder
    embedder = SentenceTransformerEmbedder(settings.embedder_model)

    return model, embedder


def get_available_providers() -> list[dict]:
    """Get list of available LLM providers with their models."""
    return [
        {
            "provider": LLMProvider.OPENAI,
            "name": "OpenAI",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"],
            "requires_api_key": True
        },
        {
            "provider": LLMProvider.DEEPSEEK,
            "name": "DeepSeek",
            "models": ["deepseek-chat", "deepseek-coder"],
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
                "glm-4.7",
                "glm-4.6",
                "glm-4.5",
                "glm-4.5-air",
                "glm-4.5-flash",
                "glm-4-plus"
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
