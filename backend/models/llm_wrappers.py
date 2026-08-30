"""
LLM Model Wrappers for Concordia

This module provides wrapper classes for various LLM providers that implement
Concordia's language model interface. These wrappers handle API compatibility
issues and provide a consistent interface across different providers.

Supported providers:
- OpenAI (GPT models)
- DeepSeek (OpenAI-compatible)
- Google Gemini
- Anthropic (Claude)
- GLM (Zhipu AI)
- Ollama (local models)
"""

from typing import Sequence
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.debug_print import debug_print, llm_print


class CustomGPTModel:
    """
    Custom GPT model wrapper that handles API compatibility issues.
    Works with OpenAI, Azure OpenAI, DeepSeek, and other OpenAI-compatible endpoints.
    """
    def __init__(self, api_key: str, model_name: str, base_url: str = None, timeout: float = 300.0, verify_ssl: bool = True, disable_ssl_for_https: bool = False, api_version: str = None, extra_body: dict = None):
        from openai import OpenAI, AzureOpenAI
        import httpx

        # Support custom base URLs for OpenAI-compatible APIs like DeepSeek
        # Set longer timeout for local models like Ollama (default: 300 seconds)
        # Local models can be slow, especially larger ones or on limited hardware
        # For Ollama specifically, we use an even longer timeout (600 seconds)
        if base_url and ('ollama' in base_url.lower() or 'myai.unu.edu' in base_url.lower()):
            timeout = max(timeout, 600.0)

        # Detect if this is Azure OpenAI (has api_version parameter)
        is_azure = api_version is not None

        if is_azure:
            # Azure OpenAI requires specific parameters
            if not base_url:
                raise ValueError("Azure OpenAI requires base_url (azure_endpoint)")
            debug_print(f"[DEBUG] AzureOpenAI client initialization:")
            debug_print(f"[DEBUG]   azure_endpoint: {base_url}")
            debug_print(f"[DEBUG]   api_version: {api_version}")
            debug_print(f"[DEBUG]   api_key: {api_key[:20]}..." if api_key else "[DEBUG]   api_key: None")
            debug_print(f"[DEBUG]   timeout: {timeout}")
            self._client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=base_url,
                api_version=api_version,
                timeout=timeout
            )
        elif base_url:
            # For HTTPS endpoints with SSL certificate issues, allow disabling verification
            # This is needed for self-hosted Ollama instances with custom certificates
            # disable_ssl_for_https flag or detection of known problematic endpoints triggers SSL bypass
            needs_ssl_bypass = (
                not verify_ssl or
                disable_ssl_for_https or
                'myai.unu.edu' in base_url.lower() or
                (base_url.startswith('https://') and 'ollama' in base_url.lower())
            )

            if needs_ssl_bypass:
                # Create a custom httpx client with SSL verification disabled
                http_client = httpx.Client(verify=False)
                self._client = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    timeout=timeout,
                    http_client=http_client
                )
            else:
                self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        else:
            self._client = OpenAI(api_key=api_key, timeout=timeout)
        self._model_name = model_name
        self._extra_body = extra_body or {}
        self._timeout = timeout

    def _use_max_completion_tokens(self) -> bool:
        """Check if model requires max_completion_tokens instead of max_tokens.

        Newer models (GPT-5*, O3-*) require max_completion_tokens parameter.
        """
        model_lower = self._model_name.lower()
        # O3 series models
        if model_lower.startswith('o3-'):
            return True
        # GPT-5 series models
        if model_lower.startswith('gpt-5'):
            return True
        # Future models can be added here
        return False

    def _is_reasoning_model(self) -> bool:
        """Check if model is a reasoning model that doesn't support temperature.

        Reasoning models (O1*, O3*, GPT-5*) use deterministic reasoning and don't
        support sampling parameters like temperature, top_p, presence_penalty, etc.
        """
        model_lower = self._model_name.lower()
        # O1 series models (original reasoning models)
        if model_lower.startswith('o1-'):
            return True
        # O3 series models (new reasoning models)
        if model_lower.startswith('o3-'):
            return True
        # GPT-5 series models
        if model_lower.startswith('gpt-5'):
            return True
        # Future reasoning models can be added here
        return False

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 2000,  # Match Concordia's DEFAULT_MAX_TOKENS
        temperature: float = 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
        seed: int | None = None,
        terminators: Sequence[str] | None = None,
        timeout: float = 180.0,  # Per-request timeout (can be overridden via LLM_TIMEOUT env var)
        top_p: float = 0.95,
        top_k: int = 64,
        max_retries: int = 2,  # Retry attempts (can be overridden via LLM_MAX_RETRIES env var)
        **kwargs,
    ) -> str:
        """Sample text from the model with retry logic for transient errors and enforced timeout."""
        import os
        from openai import APITimeoutError, AuthenticationError, RateLimitError, APIError
        from httpcore import ConnectTimeout, ConnectError

        # Allow environment variable overrides for timeout configuration
        # This lets users adjust timeouts without changing code
        # Environment variable takes precedence over passed timeout value
        env_timeout = os.getenv('LLM_TIMEOUT')
        if env_timeout:
            try:
                timeout = float(env_timeout)
                llm_print(f"[LLM] Using timeout from LLM_TIMEOUT env var: {timeout}s")
            except ValueError:
                llm_print(f"[LLM] Warning: Invalid LLM_TIMEOUT value '{env_timeout}', using default {timeout}s")

        # Allow environment variable override for retry count
        env_retries = os.getenv('LLM_MAX_RETRIES')
        if env_retries:
            try:
                max_retries = max(1, int(env_retries))  # At least 1 retry
                llm_print(f"[LLM] Using max_retries from LLM_MAX_RETRIES env var: {max_retries}")
            except ValueError:
                llm_print(f"[LLM] Warning: Invalid LLM_MAX_RETRIES value '{env_retries}', using default {max_retries}")

        # Determine appropriate timeout based on model type
        # Reasoning models (O1, O3, GPT-5) can take much longer
        # These models perform internal reasoning before responding
        if self._is_reasoning_model():
            # Reasoning models: Use LLM_REASONING_TIMEOUT or default to 5 minutes
            # These can take 60-300 seconds depending on complexity
            reasoning_timeout = os.getenv('LLM_REASONING_TIMEOUT')
            if reasoning_timeout:
                try:
                    timeout = float(reasoning_timeout)
                    llm_print(f"[LLM] Using LLM_REASONING_TIMEOUT for reasoning model: {timeout}s")
                except ValueError:
                    llm_print(f"[LLM] Warning: Invalid LLM_REASONING_TIMEOUT, using {timeout}s")
            elif timeout < 300.0:
                # Ensure minimum timeout for reasoning models
                timeout = 300.0  # Default: 5 minutes for reasoning models

        llm_print(f"[LLM] Calling {self._model_name} with timeout={timeout}s, max_tokens={max_tokens}")

        # Newer models (o3-*, gpt-5*) require max_completion_tokens instead of max_tokens
        use_max_completion_tokens = self._use_max_completion_tokens()
        # Reasoning models (o1-*, o3-*, gpt-5*) don't support temperature parameter
        is_reasoning_model = self._is_reasoning_model()

        # Modern models have large context windows - be generous with token limits
        # O3/GPT-5 models: Use max_completion_tokens with high limits (100k+ context windows)
        # GPT-4/4O/3.5: Use max_tokens with reasonable limits
        if use_max_completion_tokens:
            # Reasoning models (O3, GPT-5) - use very generous limits
            # These models have 100k+ token context windows, so we can be generous
            max_tokens = max(max_tokens, 10000)  # Ensure at least 10k for reasoning models
        elif max_tokens < 2000:
            # For older models, ensure at least 2000 tokens for complex prompts
            max_tokens = max(max_tokens, 2000)

        for attempt in range(max_retries):
            attempt_start = time.time()
            try:
                # Build request parameters
                request_params = {
                    "model": self._model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "seed": seed,
                    "timeout": timeout  # Enforce timeout at request level
                }

                # Provider-specific passthrough fields (e.g. reasoning_effort,
                # speed on reasoning deployments); sent verbatim in the body.
                if self._extra_body:
                    request_params["extra_body"] = dict(self._extra_body)

                # Only add temperature for non-reasoning models
                if not is_reasoning_model:
                    request_params["temperature"] = temperature

                # Use appropriate parameter based on model type
                if use_max_completion_tokens:
                    request_params["max_completion_tokens"] = max_tokens
                else:
                    request_params["max_tokens"] = max_tokens

                response = self._client.chat.completions.create(**request_params)

                elapsed = time.time() - attempt_start
                llm_print(f"[LLM] Response received in {elapsed:.1f}s")

                # Check for empty response and log warning
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    print(f"⚠️  Warning: Model {self._model_name} returned empty response")
                    print(f"    Finish reason: {response.choices[0].finish_reason}")
                    print(f"    Max tokens requested: {max_tokens}")
                    if response.choices[0].finish_reason == "length":
                        print(f"    Hint: Try increasing max_tokens for this model")

                return content

            except (APITimeoutError, ConnectTimeout, ConnectError) as e:
                elapsed = time.time() - attempt_start
                if attempt < max_retries - 1:
                    # Reduced backoff: 3s, 6s (faster recovery)
                    wait_time = 3 * (2 ** attempt)
                    llm_print(f"[LLM] Timeout after {elapsed:.1f}s on attempt {attempt + 1}/{max_retries}. "
                          f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    llm_print(f"[LLM] Error: Timeout after {elapsed:.1f}s and {max_retries} retries")
                    llm_print(f"[LLM] Hint: Consider using a faster model or reducing simulation complexity")
                    raise TimeoutError(f"LLM request timed out after {elapsed:.1f}s") from e

            except RateLimitError as e:
                elapsed = time.time() - attempt_start
                if attempt < max_retries - 1:
                    # Longer backoff for rate limits: 10s, 20s
                    wait_time = 10 * (2 ** attempt)
                    llm_print(f"[LLM] Rate limited after {elapsed:.1f}s. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    llm_print(f"[LLM] Error: Rate limited after {elapsed:.1f}s and {max_retries} retries")
                    llm_print(f"[LLM] Hint: Consider using a different provider or reducing request frequency")
                    raise

            except (AuthenticationError, APIError) as e:
                elapsed = time.time() - attempt_start
                llm_print(f"[LLM] Error: {type(e).__name__} after {elapsed:.1f}s: {e}")
                # Don't retry auth/config errors - these won't fix themselves
                raise

            except Exception as e:
                elapsed = time.time() - attempt_start
                llm_print(f"[LLM] Unexpected error after {elapsed:.1f}s: {type(e).__name__}: {e}")
                raise

    def sample_choice(
        self,
        prompt: str,
        responses: list[str],
        seed: int | None = None
    ) -> tuple[int, str, dict[str, float]]:
        """Sample a choice from a list of responses."""
        # Format prompt with choices
        choice_text = "\n".join([f"{i}. {r}" for i, r in enumerate(responses)])
        full_prompt = f"{prompt}\n\nChoices:\n{choice_text}\n\nRespond with only the number of your choice (0-{len(responses)-1})."

        # Use generous max_tokens for modern models with large context windows
        # Reasoning models (O3, GPT-5): 10000 tokens minimum (100k+ context windows)
        # Standard models: 1000 tokens (more than enough for number response)
        max_tokens_for_choice = 10000 if self._use_max_completion_tokens() else 1000
        response = self.sample_text(full_prompt, max_tokens=max_tokens_for_choice, seed=seed)

        # Parse response
        try:
            choice_idx = int(response.strip())
            if 0 <= choice_idx < len(responses):
                return choice_idx, responses[choice_idx], {}
        except ValueError:
            pass

        # Fallback to first choice if parsing fails
        return 0, responses[0], {}


class GeminiModel:
    """
    Gemini model wrapper using Google's genai library.
    """
    def __init__(self, api_key: str, model_name: str, timeout: float = 300.0):
        import google.genai as genai
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._default_timeout = timeout

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 2000,  # Match Concordia's DEFAULT_MAX_TOKENS
        temperature: float = 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
        terminators: list[str] | None = None,
        timeout: float = 300.0,
        seed: int | None = None,
        top_p: float = 0.95,
        top_k: int = 64,
        **kwargs,
    ) -> str:
        """Sample text from Gemini using the new google.genai package."""
        import concurrent.futures as _cf
        try:
            actual_max_tokens = max(max_tokens, 2000)
            config = {
                'max_output_tokens': actual_max_tokens,
                'temperature': temperature,
            }
            llm_print(f"[LLM] Calling {self._model_name} with max_tokens={actual_max_tokens}, temp={temperature}, timeout={timeout}s")
            call_start = time.time()

            # Enforce timeout at the Python level — google.genai's HttpOptions
            # deadline is version-sensitive and can misfire; a thread+Future is reliable.
            def _call():
                return self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                )

            with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
                _fut = _ex.submit(_call)
                try:
                    response = _fut.result(timeout=timeout)
                except _cf.TimeoutError:
                    raise TimeoutError(f"Gemini call timed out after {timeout:.0f}s")

            elapsed = time.time() - call_start

            if response is None:
                llm_print(f"[LLM] Warning: {self._model_name} returned None after {elapsed:.1f}s")
                return ""

            text = response.text
            if text:
                llm_print(f"[LLM] Response received in {elapsed:.1f}s ({len(text)} chars)")
                return text

            llm_print(f"[LLM] Warning: {self._model_name} returned empty response after {elapsed:.1f}s")
            return ""

        except Exception as e:
            llm_print(f"[LLM] Gemini error: {type(e).__name__}: {e}")
            raise

    def sample_choice(
        self,
        prompt: str,
        responses: list[str],
        seed: int | None = None
    ) -> tuple[int, str, dict[str, float]]:
        """Sample a choice from a list of responses."""
        choice_text = "\n".join([f"{i}. {r}" for i, r in enumerate(responses)])
        full_prompt = f"{prompt}\n\nChoices:\n{choice_text}\n\nRespond with only the number of your choice (0-{len(responses)-1})."

        # Use generous max_tokens for Gemini models (1M context windows)
        # 1000 tokens is more than enough for choice selection
        response = self.sample_text(full_prompt, max_tokens=1000, seed=seed)

        # Handle None response
        if response is None:
            print("Warning: Gemini API returned None response in sample_choice, using fallback")
            return 0, responses[0], {}

        try:
            choice_idx = int(response.strip())
            if 0 <= choice_idx < len(responses):
                return choice_idx, responses[choice_idx], {}
        except (ValueError, AttributeError):
            pass

        return 0, responses[0], {}


class GLMModel:
    """
    GLM (Zhipu AI) model wrapper using OpenAI-compatible API.
    GLM provides fast, reliable Chinese and English language models.
    """
    def __init__(self, api_key: str, model_name: str = "glm-4-flash", timeout: float = 300.0):
        from openai import OpenAI
        # GLM uses OpenAI-compatible API
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            timeout=timeout,
        )
        self._model_name = model_name

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 2000,  # Match Concordia's DEFAULT_MAX_TOKENS
        temperature: float = 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
        seed: int | None = None,
        terminators: Sequence[str] | None = None,
        timeout: float = 60.0,
        top_p: float = 0.95,
        top_k: int = 64,
        max_retries: int = 3,
        **kwargs,
    ) -> str:
        """Sample text from GLM model with retry logic."""
        from openai import APITimeoutError
        from httpcore import ConnectTimeout

        # GLM models have large context windows (128k-1M tokens depending on model)
        # Be generous with max_tokens to ensure complete responses
        # Minimum 2000 tokens for all GLM models
        max_tokens = max(max_tokens, 2000)

        for attempt in range(max_retries):
            attempt_start = time.time()
            try:
                llm_print(f"[LLM] Calling {self._model_name} with max_tokens={max_tokens}, temp={temperature}")

                response = self._client.chat.completions.create(
                    model=self._model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                elapsed = time.time() - attempt_start
                content = response.choices[0].message.content

                if content is None or content.strip() == "":
                    if attempt < max_retries - 1:
                        llm_print(f"[LLM] Warning: {self._model_name} returned empty response after {elapsed:.1f}s, retrying...")
                        time.sleep(1)
                        continue
                    else:
                        llm_print(f"[LLM] Warning: {self._model_name} returned empty after {max_retries} attempts")
                        return "(No response generated)"

                llm_print(f"[LLM] Response received in {elapsed:.1f}s ({len(content)} chars)")
                return content

            except (APITimeoutError, ConnectTimeout) as e:
                elapsed = time.time() - attempt_start
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    llm_print(f"[LLM] GLM timeout after {elapsed:.1f}s on attempt {attempt + 1}/{max_retries}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    llm_print(f"[LLM] GLM error after {elapsed:.1f}s and {max_retries} retries: {e}")
                    raise

            except Exception as e:
                llm_print(f"[LLM] GLM error: {type(e).__name__}: {e}")
                raise

    def sample_choice(
        self,
        prompt: str,
        responses: list[str],
        seed: int | None = None
    ) -> tuple[int, str, dict[str, float]]:
        """Sample a choice from a list of responses."""
        choice_text = "\n".join([f"{i}. {r}" for i, r in enumerate(responses)])
        full_prompt = f"{prompt}\n\nChoices:\n{choice_text}\n\nRespond with only the number of your choice (0-{len(responses)-1})."

        # Use generous max_tokens for GLM models (large context windows)
        # 1000 tokens is more than enough for choice selection
        response = self.sample_text(full_prompt, max_tokens=1000, seed=seed)

        try:
            choice_idx = int(response.strip())
            if 0 <= choice_idx < len(responses):
                return choice_idx, responses[choice_idx], {}
        except ValueError:
            pass

        return 0, responses[0], {}


class AnthropicModel:
    """
    Anthropic (Claude) model wrapper using the Anthropic API.
    """
    def __init__(self, api_key: str, model_name: str = "claude-haiku-4-5", timeout: float = 300.0):
        from anthropic import Anthropic
        self._client = Anthropic(api_key=api_key, timeout=timeout)
        self._model_name = model_name

    def _supports_temperature(self) -> bool:
        """Opus 4.7+ uses extended thinking and rejects the temperature parameter."""
        m = self._model_name.lower()
        if 'opus-4-7' in m or 'opus-4-8' in m or 'opus-4-9' in m:
            return False
        return True

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 2000,  # Match Concordia's DEFAULT_MAX_TOKENS
        temperature: float = 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
        seed: int | None = None,
        terminators: Sequence[str] | None = None,
        timeout: float = 60.0,
        top_p: float = 0.95,
        top_k: int = 64,
        max_retries: int = 3,
        **kwargs,
    ) -> str:
        """Sample text from Anthropic Claude with retry logic."""
        # Claude models have large context windows (200k tokens)
        # Be generous with max_tokens to ensure complete responses
        # Minimum 2000 tokens for all Claude models
        max_tokens = max(max_tokens, 2000)

        for attempt in range(max_retries):
            attempt_start = time.time()
            try:
                llm_print(f"[LLM] Calling {self._model_name} with max_tokens={max_tokens}, temp={temperature}")

                params = {
                    "model": self._model_name,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                }

                if self._supports_temperature():
                    params["temperature"] = temperature

                if seed is not None:
                    params["seed"] = seed

                response = self._client.messages.create(**params)

                # Extract text from response
                # Response format: {'content': [block1, block2, ...], ...}
                # Blocks can be: TextBlock, ThinkingBlock, etc.
                # We need to filter and concatenate only text blocks
                elapsed = time.time() - attempt_start

                if response.content and len(response.content) > 0:
                    text_parts = []
                    for block in response.content:
                        if hasattr(block, 'text'):
                            text_parts.append(block.text)
                        elif hasattr(block, 'thinking'):
                            continue
                        else:
                            text_parts.append(str(block))

                    result = ''.join(text_parts)
                    if result:
                        llm_print(f"[LLM] Response received in {elapsed:.1f}s ({len(result)} chars)")
                        return result
                    else:
                        llm_print(f"[LLM] Warning: {self._model_name} returned empty response after {elapsed:.1f}s")
                        return ""
                else:
                    llm_print(f"[LLM] Warning: {self._model_name} returned empty content after {elapsed:.1f}s")
                    return ""

            except Exception as e:
                elapsed = time.time() - attempt_start
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    llm_print(f"[LLM] Anthropic error after {elapsed:.1f}s on attempt {attempt + 1}/{max_retries}. "
                          f"Retrying in {wait_time}s... Error: {e}")
                    time.sleep(wait_time)
                else:
                    llm_print(f"[LLM] Anthropic error after {elapsed:.1f}s and {max_retries} retries: {e}")
                    raise

    def sample_choice(
        self,
        prompt: str,
        responses: list[str],
        seed: int | None = None
    ) -> tuple[int, str, dict[str, float]]:
        """Sample a choice from a list of responses."""
        choice_text = "\n".join([f"{i}. {r}" for i, r in enumerate(responses)])
        full_prompt = f"{prompt}\n\nChoices:\n{choice_text}\n\nRespond with only the number of your choice (0-{len(responses)-1})."

        # Use generous max_tokens for Claude models (200k context windows)
        # 1000 tokens is more than enough for choice selection
        response = self.sample_text(full_prompt, max_tokens=1000, seed=seed)

        try:
            choice_idx = int(response.strip())
            if 0 <= choice_idx < len(responses):
                return choice_idx, responses[choice_idx], {}
        except ValueError:
            pass

        return 0, responses[0], {}


class SentenceTransformerEmbedder:
    """
    Wrapper for SentenceTransformer to match Concordia's expected interface.
    Concordia expects embedder to be a callable that takes a list of strings.
    """
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)

    def __call__(self, texts):
        """
        Embed a list of texts.

        Args:
            texts: List of strings or a single string

        Returns:
            numpy array of embeddings - 1D for single text, 2D for list
        """
        if isinstance(texts, str):
            # Return 1D array for single text
            return self._model.encode(texts, convert_to_numpy=True).flatten()
        # Return 2D array for list of texts
        return self._model.encode(texts, convert_to_numpy=True)
