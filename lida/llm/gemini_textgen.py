import os
import logging
from dataclasses import asdict
from typing import Union, List, Dict

from .base_textgen import TextGenerator
from .datamodel import Message, TextGenerationConfig, TextGenerationResponse
from .utils import cache_request, num_tokens_from_messages

logger = logging.getLogger("lida")


class GeminiTextGenerator(TextGenerator):
    """Text generator using Google's Gemini API via the google-genai SDK."""

    def __init__(
        self,
        api_key: str = None,
        provider: str = "gemini",
        model: str = None,
        models: Dict = None,
        **kwargs,
    ):
        super().__init__(provider=provider)

        try:
            from google import genai
            self._genai = genai
        except ImportError:
            raise ImportError(
                "The 'google-genai' package is required for Gemini provider. "
                "Install it with: pip install google-genai"
            )

        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or None
        if not self.api_key:
            raise ValueError(
                "Google API key is not set. Set GOOGLE_API_KEY in your .env file or environment."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model or "gemini-2.0-flash"

    def _convert_messages(self, messages: List[Dict]) -> tuple:
        """Convert OpenAI-style messages to Gemini format.

        Returns:
            (system_instruction, contents) where system_instruction is a string or None,
            and contents is a list of Gemini Content dicts.
        """
        system_parts = []
        contents = []

        for msg in messages:
            role = msg.get("role", "user") if isinstance(msg, dict) else msg.role
            content = msg.get("content", "") if isinstance(msg, dict) else msg.content

            if role == "system":
                system_parts.append(content)
            else:
                # Gemini uses "user" and "model" roles
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })

        system_instruction = "\n\n".join(system_parts) if system_parts else None

        # Gemini requires alternating roles; merge consecutive same-role messages
        merged = []
        for c in contents:
            if merged and merged[-1]["role"] == c["role"]:
                merged[-1]["parts"].extend(c["parts"])
            else:
                merged.append(c)

        return system_instruction, merged

    def generate(
        self,
        messages: Union[List[dict], str],
        config: TextGenerationConfig = TextGenerationConfig(),
        **kwargs,
    ) -> TextGenerationResponse:
        from google.genai import types

        use_cache = config.use_cache
        model = config.model or self.model_name

        system_instruction, contents = self._convert_messages(messages)

        cache_key_params = {
            "provider": "gemini",
            "model": model,
            "temperature": config.temperature,
            "messages": messages,
        }

        if use_cache:
            cached = cache_request(cache=self.cache, params=cache_key_params)
            if cached:
                return TextGenerationResponse(**cached)

        generate_config = types.GenerateContentConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_tokens or 4096,
            top_p=config.top_p,
            top_k=config.top_k,
            candidate_count=config.n,
        )

        if system_instruction:
            generate_config.system_instruction = system_instruction

        gemini_response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_config,
        )

        # Build response in the same format as OpenAI generator
        result_messages = []
        if gemini_response.candidates:
            for candidate in gemini_response.candidates:
                text_parts = []
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.text:
                            text_parts.append(part.text)
                result_messages.append(
                    Message(role="assistant", content="".join(text_parts))
                )

        usage_info = None
        if gemini_response.usage_metadata:
            usage_info = {
                "prompt_tokens": gemini_response.usage_metadata.prompt_token_count,
                "completion_tokens": gemini_response.usage_metadata.candidates_token_count,
                "total_tokens": gemini_response.usage_metadata.total_token_count,
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
