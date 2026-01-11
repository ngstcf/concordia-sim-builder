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
from utils.logger import debug_print


class CustomGPTModel:
    """
    Custom GPT model wrapper that handles API compatibility issues.
    Works with OpenAI, Azure OpenAI, DeepSeek, and other OpenAI-compatible endpoints.
    """
    def __init__(self, api_key: str, model_name: str, base_url: str = None, timeout: float = 300.0, verify_ssl: bool = True, disable_ssl_for_https: bool = False, api_version: str = None):
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
            debug_print("AzureOpenAI client initialization:", "DEBUG")
            debug_print(f"  azure_endpoint: {base_url}", "DEBUG")
            debug_print(f"  api_version: {api_version}", "DEBUG")
            debug_print(f"  api_key: {api_key[:20]}..." if api_key else "  api_key: None", "DEBUG")
            debug_print(f"  timeout: {timeout}", "DEBUG")
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
        max_retries: int = 2  # Retry attempts (can be overridden via LLM_MAX_RETRIES env var)
    ) -> str:
        """Sample text from the model with retry logic for transient errors and enforced timeout.

        Timeout Behavior:
        - Waits the FULL timeout duration before flagging an error
        - Does NOT prematurely interrupt long-running requests
        - If request completes at 179s (of 180s timeout) → SUCCESS
        - If request completes at 181s (of 180s timeout) → RETRY
        """
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
                debug_print(f"Using timeout from LLM_TIMEOUT env var: {timeout}s", "LLM")
            except ValueError:
                debug_print(f"Warning: Invalid LLM_TIMEOUT value '{env_timeout}', using default {timeout}s", "LLM")

        # Allow environment variable override for retry count
        env_retries = os.getenv('LLM_MAX_RETRIES')
        if env_retries:
            try:
                max_retries = max(1, int(env_retries))  # At least 1 retry
                debug_print(f"Using max_retries from LLM_MAX_RETRIES env var: {max_retries}", "LLM")
            except ValueError:
                debug_print(f"Warning: Invalid LLM_MAX_RETRIES value '{env_retries}', using default {max_retries}", "LLM")

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
                    debug_print(f"Using LLM_REASONING_TIMEOUT for reasoning model: {timeout}s", "LLM")
                except ValueError:
                    debug_print(f"Warning: Invalid LLM_REASONING_TIMEOUT, using {timeout}s", "LLM")
            elif timeout < 300.0:
                # Ensure minimum timeout for reasoning models
                timeout = 300.0  # Default: 5 minutes for reasoning models

        debug_print(f"Calling {self._model_name} with timeout={timeout}s, max_tokens={max_tokens}", "LLM")

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
                print(f"[LLM] Response received in {elapsed:.1f}s")

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
                    print(f"[LLM] Timeout after {elapsed:.1f}s on attempt {attempt + 1}/{max_retries}. "
                          f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[LLM] Error: Timeout after {elapsed:.1f}s and {max_retries} retries")
                    print(f"[LLM] Hint: Consider using a faster model or reducing simulation complexity")
                    raise TimeoutError(f"LLM request timed out after {elapsed:.1f}s") from e

            except RateLimitError as e:
                elapsed = time.time() - attempt_start
                if attempt < max_retries - 1:
                    # Longer backoff for rate limits: 10s, 20s
                    wait_time = 10 * (2 ** attempt)
                    print(f"[LLM] Rate limited after {elapsed:.1f}s. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[LLM] Error: Rate limited after {elapsed:.1f}s and {max_retries} retries")
                    print(f"[LLM] Hint: Consider using a different provider or reducing request frequency")
                    raise

            except (AuthenticationError, APIError) as e:
                elapsed = time.time() - attempt_start
                print(f"[LLM] Error: {type(e).__name__} after {elapsed:.1f}s: {e}")
                # Don't retry auth/config errors - these won't fix themselves
                raise

            except Exception as e:
                elapsed = time.time() - attempt_start
                print(f"[LLM] Unexpected error after {elapsed:.1f}s: {type(e).__name__}: {e}")
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
    def __init__(self, api_key: str, model_name: str):
        import google.genai as genai
        # The new API doesn't use configure(), pass api_key directly to Client
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 2000,  # Match Concordia's DEFAULT_MAX_TOKENS
        temperature: float = 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
        terminators: list[str] | None = None,  # Accept but ignore for compatibility
        timeout: float = 60.0,  # Accept but ignore for compatibility
        seed: int | None = None
    ) -> str:
        """Sample text from Gemini using the new google.genai package."""
        try:
            # Gemini models have large context windows (1M tokens for Gemini 2.0)
            # Be generous with max_tokens to ensure complete responses
            # Minimum 2000 tokens for all Gemini models (higher than old 500 minimum)
            actual_max_tokens = max(max_tokens, 2000)

            # Use the new google.genai API
            # Generation parameters must be passed as a config dict
            config = {
                'max_output_tokens': actual_max_tokens,
                'temperature': temperature,
            }
            # Debug: log the config and prompt size
            prompt_preview = prompt[:100] if len(prompt) > 100 else prompt
            print(f"Gemini API call: model={self._model_name}, max_tokens={actual_max_tokens}, temp={temperature}")
            print(f"Prompt preview: {prompt_preview}...")

            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=config,
            )

            # The response object is a GenerateContentResponse with a .text property
            if response is None:
                print(f"⚠️  Warning: Model {self._model_name} returned None response")
                print(f"    Max tokens: {actual_max_tokens}")
                print(f"    Hint: Check API key and model name")
                return ""

            # Try to get text using the .text property
            # The .text property exists but might return None if there's no text content
            text = response.text
            if text:
                return text

            # Fallback: debug and try to extract from candidates manually
            print(f"⚠️  Warning: Model {self._model_name} returned empty response")
            print(f"    Max tokens requested: {actual_max_tokens}")

            finish_reason = "N/A"
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason if hasattr(candidate, 'finish_reason') else 'N/A'

            print(f"    Finish reason: {finish_reason}")

            if finish_reason == "MAX_TOKENS":
                print(f"    Hint: Try increasing max_tokens for this model")
            else:
                print(f"    Hint: Check prompt format and safety filters")

            # Detailed debugging
            print(f"    Response has candidates: {hasattr(response, 'candidates')}")
            if hasattr(response, 'candidates'):
                print(f"    Number of candidates: {len(response.candidates) if response.candidates else 0}")

            return ""

        except Exception as e:
            print(f"Error in Gemini API call: {e}")
            import traceback
            traceback.print_exc()
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
    def __init__(self, api_key: str, model_name: str = "glm-4-flash"):
        from openai import OpenAI
        # GLM uses OpenAI-compatible API
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
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
        timeout: float = 60.0,  # Accept for compatibility with Concordia API; timeout is set at client level
        max_retries: int = 3
    ) -> str:
        """Sample text from GLM model with retry logic."""
        from openai import APITimeoutError
        from httpcore import ConnectTimeout

        # GLM models have large context windows (128k-1M tokens depending on model)
        # Be generous with max_tokens to ensure complete responses
        # Minimum 2000 tokens for all GLM models
        max_tokens = max(max_tokens, 2000)

        for attempt in range(max_retries):
            try:
                # Debug: Log prompt details for empty response investigation
                if attempt == 0:
                    print(f"\n{'='*60}")
                    print(f"GLM API Call:")
                    print(f"  Model: {self._model_name}")
                    print(f"  Max tokens: {max_tokens}")
                    print(f"  Temperature: {temperature}")
                    print(f"  Prompt length: {len(prompt)} chars")
                    print(f"  Prompt preview: {prompt[:300]}...")
                    print(f"{'='*60}\n")

                response = self._client.chat.completions.create(
                    model=self._model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Debug: Log response details
                if hasattr(response, 'usage'):
                    print(f"GLM API Response: tokens_used={response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 'N/A'}")

                content = response.choices[0].message.content

                # Debug: Log if content is None/empty
                if content is None:
                    print(f"⚠️  Warning: Model {self._model_name} returned None content")
                    print(f"    Max tokens: {max_tokens}")
                    print(f"    Hint: Check API key and quota")
                elif content.strip() == "":
                    print(f"⚠️  Warning: Model {self._model_name} returned empty response")
                    print(f"    Max tokens: {max_tokens}")
                    print(f"    Hint: Try increasing max_tokens or check prompt format")

                # Handle None or empty responses from GLM
                if content is None or content.strip() == "":
                    if attempt < max_retries - 1:
                        print(f"    Retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(1)
                        continue
                    else:
                        print(f"    Using fallback after {max_retries} attempts")
                        return "(No response generated)"
                return content

            except (APITimeoutError, ConnectTimeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    print(f"GLM timeout on attempt {attempt + 1}/{max_retries}. "
                          f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"GLM API error after {max_retries} retries: {e}")
                    raise

            except Exception as e:
                print(f"GLM API error: {e}")
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
    def __init__(self, api_key: str, model_name: str = "claude-haiku-4-5"):
        from anthropic import Anthropic
        self._client = Anthropic(api_key=api_key)
        self._model_name = model_name

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 2000,  # Match Concordia's DEFAULT_MAX_TOKENS
        temperature: float = 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
        seed: int | None = None,
        terminators: Sequence[str] | None = None,
        timeout: float = 60.0,  # Accept for compatibility with Concordia API
        max_retries: int = 3
    ) -> str:
        """Sample text from Anthropic Claude with retry logic."""
        # Claude models have large context windows (200k tokens)
        # Be generous with max_tokens to ensure complete responses
        # Minimum 2000 tokens for all Claude models
        max_tokens = max(max_tokens, 2000)

        for attempt in range(max_retries):
            try:
                # Build the message creation parameters
                params = {
                    "model": self._model_name,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}]
                }

                # Anthropic supports the seed parameter for deterministic responses
                if seed is not None:
                    params["seed"] = seed

                # Note: Anthropic doesn't support stop sequences (terminators) in Messages API
                # in the same way as OpenAI, so we ignore them for compatibility

                response = self._client.messages.create(**params)

                # Extract text from response
                # Response format: {'content': [block1, block2, ...], ...}
                # Blocks can be: TextBlock, ThinkingBlock, etc.
                # We need to filter and concatenate only text blocks
                if response.content and len(response.content) > 0:
                    text_parts = []
                    for block in response.content:
                        # Handle different content block types
                        if hasattr(block, 'text'):
                            # This is a TextBlock
                            text_parts.append(block.text)
                        elif hasattr(block, 'thinking'):
                            # This is a ThinkingBlock - skip it
                            continue
                        else:
                            # Unknown block type, try to get string representation
                            text_parts.append(str(block))

                    result = ''.join(text_parts)
                    if result:
                        return result
                    else:
                        print(f"⚠️  Warning: Model {self._model_name} returned empty response")
                        print(f"    Max tokens: {max_tokens}")
                        print(f"    Hint: Check if prompt format is compatible with Claude API")
                        return ""
                else:
                    print(f"⚠️  Warning: Model {self._model_name} returned empty content")
                    print(f"    Max tokens: {max_tokens}")
                    print(f"    Hint: Try increasing max_tokens or check API usage limits")
                    return ""

            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 5 * (2 ** attempt)
                    print(f"Anthropic API error on attempt {attempt + 1}/{max_retries}. "
                          f"Retrying in {wait_time} seconds... Error: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"Anthropic API error after {max_retries} retries: {e}")
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
