import os
import logging
from dataclasses import asdict
from typing import Union, List, Dict

from .base_textgen import TextGenerator
from .datamodel import Message, TextGenerationConfig, TextGenerationResponse
from .utils import cache_request, num_tokens_from_messages

logger = logging.getLogger("lida")


class AnthropicTextGenerator(TextGenerator):
    """Text generator using Anthropic's Claude API."""

    def __init__(
        self,
        api_key: str = None,
        provider: str = "anthropic",
        model: str = None,
        models: Dict = None,
        **kwargs,
    ):
        super().__init__(provider=provider)

        try:
            import anthropic
            self._anthropic = anthropic
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required for Anthropic provider. "
                "Install it with: pip install anthropic"
            )

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY") or None
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is not set. Set ANTHROPIC_API_KEY in your .env file or environment."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model_name = model or "claude-sonnet-4-20250514"

    def _extract_system_and_messages(self, messages: List[Dict]) -> tuple:
        """Separate system messages from user/assistant messages.

        Anthropic API takes system as a separate parameter, not in the messages list.
        Returns: (system_text, filtered_messages)
        """
        system_parts = []
        filtered = []

        for msg in messages:
            role = msg.get("role", "user") if isinstance(msg, dict) else msg.role
            content = msg.get("content", "") if isinstance(msg, dict) else msg.content

            if role == "system":
                system_parts.append(content)
            else:
                filtered.append({"role": role, "content": content})

        # Anthropic requires the first message to be from the user
        # If the first message is assistant, prepend a user message
        if filtered and filtered[0]["role"] == "assistant":
            filtered.insert(0, {"role": "user", "content": "Please proceed."})

        # Merge consecutive same-role messages (Anthropic requires alternating roles)
        merged = []
        for msg in filtered:
            if merged and merged[-1]["role"] == msg["role"]:
                merged[-1]["content"] += "\n\n" + msg["content"]
            else:
                merged.append(msg)

        system_text = "\n\n".join(system_parts) if system_parts else None
        return system_text, merged

    def generate(
        self,
        messages: Union[List[dict], str],
        config: TextGenerationConfig = TextGenerationConfig(),
        **kwargs,
    ) -> TextGenerationResponse:
        use_cache = config.use_cache
        model = config.model or self.model_name

        system_text, api_messages = self._extract_system_and_messages(messages)

        cache_key_params = {
            "provider": "anthropic",
            "model": model,
            "temperature": config.temperature,
            "messages": messages,
        }

        if use_cache:
            cached = cache_request(cache=self.cache, params=cache_key_params)
            if cached:
                return TextGenerationResponse(**cached)

        api_kwargs = {
            "model": model,
            "messages": api_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4096,
            "top_p": config.top_p,
        }

        if system_text:
            api_kwargs["system"] = system_text

        if config.stop:
            api_kwargs["stop_sequences"] = config.stop if isinstance(config.stop, list) else [config.stop]

        claude_response = self.client.messages.create(**api_kwargs)

        # Extract text from response content blocks
        text_content = ""
        for block in claude_response.content:
            if block.type == "text":
                text_content += block.text

        result_messages = [Message(role="assistant", content=text_content)]

        usage_info = None
        if claude_response.usage:
            usage_info = {
                "prompt_tokens": claude_response.usage.input_tokens,
                "completion_tokens": claude_response.usage.output_tokens,
                "total_tokens": claude_response.usage.input_tokens + claude_response.usage.output_tokens,
            }

        response = TextGenerationResponse(
            text=result_messages,
            logprobs=[],
            config=cache_key_params,
            usage=usage_info,
        )

        cache_request(
            cache=self.cache, params=cache_key_params, values=asdict(response)
        )
        return response

    def count_tokens(self, text) -> int:
        return num_tokens_from_messages(text)
