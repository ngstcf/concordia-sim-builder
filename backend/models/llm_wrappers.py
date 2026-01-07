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


class CustomGPTModel:
    """
    Custom GPT model wrapper that handles API compatibility issues.
    Works with OpenAI, DeepSeek, and other OpenAI-compatible endpoints.
    """
    def __init__(self, api_key: str, model_name: str, base_url: str = None, timeout: float = 300.0, verify_ssl: bool = True, disable_ssl_for_https: bool = False):
        from openai import OpenAI
        import httpx

        # Support custom base URLs for OpenAI-compatible APIs like DeepSeek
        # Set longer timeout for local models like Ollama (default: 300 seconds)
        # Local models can be slow, especially larger ones or on limited hardware
        # For Ollama specifically, we use an even longer timeout (600 seconds)
        if base_url and ('ollama' in base_url.lower() or 'myai.unu.edu' in base_url.lower()):
            timeout = max(timeout, 600.0)

        if base_url:
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
        """Sample text from the model with retry logic for transient errors."""
        from openai import APITimeoutError
        from httpcore import ConnectTimeout

        for attempt in range(max_retries):
            try:
                response = self._client.chat.completions.create(
                    model=self._model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    seed=seed
                    # Removed verbosity parameter that causes issues
                )
                return response.choices[0].message.content

            except (APITimeoutError, ConnectTimeout) as e:
                if attempt < max_retries - 1:
                    # Exponential backoff: 5s, 10s, 20s
                    wait_time = 5 * (2 ** attempt)
                    print(f"Timeout on attempt {attempt + 1}/{max_retries}. "
                          f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Error in API call after {max_retries} retries: {e}")
                    raise

            except Exception as e:
                # For non-timeout errors, don't retry
                print(f"Error in API call: {e}")
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

        response = self.sample_text(full_prompt, max_tokens=10, seed=seed)

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
            # Gemini has a minimum token requirement - enforce a minimum of 500 tokens
            # Values below this cause empty responses with finish_reason=MAX_TOKENS
            actual_max_tokens = max(max_tokens, 500)

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
                print(f"Warning: Gemini API returned None response for model {self._model_name}")
                return ""

            # Try to get text using the .text property
            # The .text property exists but might return None if there's no text content
            text = response.text
            if text:
                return text

            # Fallback: debug and try to extract from candidates manually
            print(f"Warning: Gemini API response.text was empty for model {self._model_name}")
            print(f"Response has candidates: {hasattr(response, 'candidates')}")
            if hasattr(response, 'candidates'):
                print(f"Number of candidates: {len(response.candidates) if response.candidates else 0}")

            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                print(f"Candidate finish_reason: {candidate.finish_reason if hasattr(candidate, 'finish_reason') else 'N/A'}")
                print(f"Candidate safety_ratings: {candidate.safety_ratings if hasattr(candidate, 'safety_ratings') else 'N/A'}")

                if hasattr(candidate, 'content'):
                    content = candidate.content
                    print(f"Content: {content}")
                    if hasattr(content, 'parts'):
                        print(f"Parts: {content.parts}")
                        if content.parts:
                            part = content.parts[0]
                            print(f"First part: {part}")
                            if hasattr(part, 'text'):
                                print(f"Part text: {repr(part.text)}")
                                if part.text:
                                    return part.text
                    # Content might have text directly
                    if hasattr(content, 'text'):
                        print(f"Content.text: {repr(content.text)}")

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

        # Use a minimum of 100 tokens for choice selection - 10 is too small for Gemini
        response = self.sample_text(full_prompt, max_tokens=max(10, len(responses) * 10), seed=seed)

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
                    print(f"⚠️  GLM returned None content (raw API response)")
                elif content.strip() == "":
                    print(f"⚠️  GLM returned whitespace-only content (length: {len(content)})")

                # Handle None or empty responses from GLM
                if content is None or content.strip() == "":
                    if attempt < max_retries - 1:
                        print(f"GLM returned empty response on attempt {attempt + 1}/{max_retries}. Retrying...")
                        time.sleep(1)
                        continue
                    else:
                        print(f"GLM returned empty response after {max_retries} attempts. Using fallback.")
                        print(f"Full prompt that failed:\n{prompt[:1000]}...")
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

        response = self.sample_text(full_prompt, max_tokens=10, seed=seed)

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
                        print("Warning: Anthropic API returned no text content")
                        return ""
                else:
                    print("Warning: Anthropic API returned empty content")
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

        response = self.sample_text(full_prompt, max_tokens=10, seed=seed)

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
