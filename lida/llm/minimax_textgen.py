import os
import logging
from dataclasses import asdict
from typing import Union, List, Dict

from .base_textgen import TextGenerator
from .datamodel import Message, TextGenerationConfig, TextGenerationResponse
from .utils import cache_request, num_tokens_from_messages

logger = logging.getLogger("lida")

# MiniMax recommends the Anthropic-compatible API
# Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api
DEFAULT_MINIMAX_ANTHROPIC_BASE_URL = "https://api.minimax.io/anthropic"
DEFAULT_MINIMAX_OPENAI_BASE_URL = "https://api.minimax.io/v1"

# Known MiniMax model names — used to ignore foreign model names from config
MINIMAX_MODELS = {
    "MiniMax-M2.5",
    "MiniMax-M2.5-highspeed",
    "MiniMax-M2.1",
    "MiniMax-M2.1-highspeed",
    "MiniMax-M2",
}


class MiniMaxTextGenerator(TextGenerator):
    """Text generator using MiniMax API (via Anthropic-compatible endpoint).

    MiniMax M2.5 supports both Anthropic and OpenAI compatible APIs.
    The Anthropic API is recommended by MiniMax for best performance.

    Usage:
        llm("minimax")                                # uses Anthropic-compatible API (recommended)
        llm("minimax", api_mode="openai")             # uses OpenAI-compatible API
        llm("minimax", api_key="your-key")            # explicit API key
    """

    def __init__(
        self,
        api_key: str = None,
        provider: str = "minimax",
        model: str = None,
        api_mode: str = "anthropic",
        models: Dict = None,
        **kwargs,
    ):
        super().__init__(provider=provider)

        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY") or None
        if not self.api_key:
            raise ValueError(
                "MiniMax API key is not set. Set MINIMAX_API_KEY in your .env file or environment."
            )

        self.model_name = model or "MiniMax-M2.5"
        self.api_mode = (api_mode or os.environ.get("MINIMAX_API_MODE") or "anthropic").lower()

        # Allow base URLs to be overridden via env vars (fall back to defaults if empty)
        self._anthropic_base_url = (
            os.environ.get("MINIMAX_ANTHROPIC_BASE_URL") or DEFAULT_MINIMAX_ANTHROPIC_BASE_URL
        )
        self._openai_base_url = (
            os.environ.get("MINIMAX_OPENAI_BASE_URL") or DEFAULT_MINIMAX_OPENAI_BASE_URL
        )

        if self.api_mode == "openai":
            self._init_openai_client()
        else:
            self._init_anthropic_client()

    def _init_anthropic_client(self):
        """Initialize httpx client for Anthropic-compatible endpoint (recommended).

        Note: We use httpx directly instead of the Anthropic SDK because
        SDK v0.82+ resolves absolute paths (e.g. /v1/messages) against
        the origin, stripping the /anthropic path from the base URL.
        This causes requests to go to /v1/messages instead of
        /anthropic/v1/messages, resulting in 404 errors.
        """
        import httpx
        self._httpx_client = httpx.Client(timeout=httpx.Timeout(600.0, connect=10.0))
        # Ensure base URL ends with /
        base = self._anthropic_base_url.rstrip("/")
        self._anthropic_messages_url = f"{base}/v1/messages"
        self._anthropic_headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _init_openai_client(self):
        """Initialize using OpenAI-compatible endpoint."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for MiniMax (OpenAI mode). "
                "Install it with: pip install openai"
            )
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self._openai_base_url,
        )

    def generate(
        self,
        messages: Union[List[dict], str],
        config: TextGenerationConfig = TextGenerationConfig(),
        **kwargs,
    ) -> TextGenerationResponse:
        if self.api_mode == "openai":
            return self._generate_openai(messages, config)
        else:
            return self._generate_anthropic(messages, config)

    def _generate_anthropic(
        self,
        messages: Union[List[dict], str],
        config: TextGenerationConfig = TextGenerationConfig(),
    ) -> TextGenerationResponse:
        """Generate using Anthropic-compatible API via httpx (recommended by MiniMax)."""
        use_cache = config.use_cache
        # Only use config.model if it's a known MiniMax model; ignore foreign names like "gpt-4o-mini"
        model = config.model if config.model in MINIMAX_MODELS else self.model_name

        # Separate system messages (Anthropic API takes system as separate param)
        system_parts = []
        api_messages = []
        for msg in messages:
            role = msg.get("role", "user") if isinstance(msg, dict) else msg.role
            content = msg.get("content", "") if isinstance(msg, dict) else msg.content

            if role == "system":
                system_parts.append(content)
            else:
                api_messages.append({"role": role, "content": content})

        # Ensure first message is from user and roles alternate
        if api_messages and api_messages[0]["role"] == "assistant":
            api_messages.insert(0, {"role": "user", "content": "Please proceed."})

        merged = []
        for msg in api_messages:
            if merged and merged[-1]["role"] == msg["role"]:
                merged[-1]["content"] += "\n\n" + msg["content"]
            else:
                merged.append(msg)

        system_text = "\n\n".join(system_parts) if system_parts else None

        cache_key_params = {
            "provider": "minimax",
            "model": model,
            "temperature": config.temperature,
            "messages": messages,
        }

        if use_cache:
            cached = cache_request(cache=self.cache, params=cache_key_params)
            if cached:
                return TextGenerationResponse(**cached)

        body = {
            "model": model,
            "messages": merged,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4096,
            "top_p": config.top_p,
        }

        if system_text:
            body["system"] = system_text

        if config.stop:
            body["stop_sequences"] = config.stop if isinstance(config.stop, list) else [config.stop]

        # Use httpx directly to avoid Anthropic SDK URL path-stripping bug
        http_response = self._httpx_client.post(
            self._anthropic_messages_url,
            headers=self._anthropic_headers,
            json=body,
        )

        if http_response.status_code != 200:
            raise RuntimeError(
                f"MiniMax API error {http_response.status_code}: {http_response.text}"
            )

        response_data = http_response.json()

        # Extract text (MiniMax may return thinking blocks too)
        text_content = ""
        for block in response_data.get("content", []):
            if block.get("type") == "text":
                text_content += block.get("text", "")

        result_messages = [Message(role="assistant", content=text_content)]

        usage_info = None
        usage_data = response_data.get("usage")
        if usage_data:
            usage_info = {
                "prompt_tokens": usage_data.get("input_tokens", 0),
                "completion_tokens": usage_data.get("output_tokens", 0),
                "total_tokens": usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
            }

        response = TextGenerationResponse(
            text=result_messages,
            logprobs=[],
            config=cache_key_params,
            usage=usage_info,
        )

        cache_request(cache=self.cache, params=cache_key_params, values=asdict(response))
        return response

    def _generate_openai(
        self,
        messages: Union[List[dict], str],
        config: TextGenerationConfig = TextGenerationConfig(),
    ) -> TextGenerationResponse:
        """Generate using OpenAI-compatible API."""
        use_cache = config.use_cache
        # Only use config.model if it's a known MiniMax model; ignore foreign names like "gpt-4o-mini"
        model = config.model if config.model in MINIMAX_MODELS else self.model_name

        oai_config = {
            "model": model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4096,
            "top_p": config.top_p,
            "n": config.n,
            "messages": messages,
        }

        cache_key_params = {"provider": "minimax-openai", **oai_config}

        if use_cache:
            cached = cache_request(cache=self.cache, params=cache_key_params)
            if cached:
                return TextGenerationResponse(**cached)

        oai_response = self.client.chat.completions.create(**oai_config)

        response = TextGenerationResponse(
            text=[Message(**x.message.model_dump()) for x in oai_response.choices],
            logprobs=[],
            config=oai_config,
            usage=dict(oai_response.usage) if oai_response.usage else None,
        )

        cache_request(cache=self.cache, params=cache_key_params, values=asdict(response))
        return response

    def count_tokens(self, text) -> int:
        return num_tokens_from_messages(text)
