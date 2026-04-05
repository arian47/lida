import os
from dataclasses import asdict
from typing import Union, List, Dict

from .base_textgen import TextGenerator
from .datamodel import Message, TextGenerationConfig, TextGenerationResponse
from .utils import cache_request, get_models_maxtoken_dict, num_tokens_from_messages


class OpenAITextGenerator(TextGenerator):
    """Text generator using OpenAI or OpenAI-compatible APIs (Azure, MiniMax, vllm, etc.)."""

    def __init__(
        self,
        api_key: str = None,
        provider: str = "openai",
        organization: str = None,
        api_type: str = None,
        api_version: str = None,
        azure_endpoint: str = None,
        api_base: str = None,
        model: str = None,
        models: Dict = None,
        **kwargs,
    ):
        super().__init__(provider=provider)

        try:
            from openai import AzureOpenAI, OpenAI
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for OpenAI provider. "
                "Install it with: pip install openai"
            )

        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or None
        api_base = api_base or os.environ.get("OPENAI_API_BASE") or None
        api_type = api_type or os.environ.get("OPENAI_API_TYPE") or None
        api_version = api_version or os.environ.get("OPENAI_API_VERSION") or None
        organization = organization or os.environ.get("OPENAI_ORGANIZATION") or None
        azure_endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT") or None

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is not set. Set OPENAI_API_KEY in your .env file or environment."
            )

        if api_type and api_type == "azure":
            client_args = {
                "api_key": self.api_key,
                "organization": organization,
                "api_version": api_version,
                "azure_endpoint": azure_endpoint,
            }
            client_args = {k: v for k, v in client_args.items() if v is not None}
            self.client = AzureOpenAI(**client_args)
        else:
            client_args = {
                "api_key": self.api_key,
                "organization": organization,
            }
            if api_base:
                client_args["base_url"] = api_base
            client_args = {k: v for k, v in client_args.items() if v is not None}
            self.client = OpenAI(**client_args)

        self.model_name = model or "gpt-4o-mini"
        self.model_max_token_dict = get_models_maxtoken_dict(models)

    def generate(
        self,
        messages: Union[List[dict], str],
        config: TextGenerationConfig = TextGenerationConfig(),
        **kwargs,
    ) -> TextGenerationResponse:
        use_cache = config.use_cache
        model = config.model or self.model_name
        prompt_tokens = num_tokens_from_messages(messages)
        max_tokens = config.max_tokens or max(
            self.model_max_token_dict.get(model, 4096) - prompt_tokens - 10, 200
        )

        oai_config = {
            "model": model,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
            "n": config.n,
            "messages": messages,
        }

        self.model_name = model
        cache_key_params = dict(oai_config) | {"messages": messages}
        if use_cache:
            response = cache_request(cache=self.cache, params=cache_key_params)
            if response:
                return TextGenerationResponse(**response)

        oai_response = self.client.chat.completions.create(**oai_config)

        response = TextGenerationResponse(
            text=[Message(**x.message.model_dump()) for x in oai_response.choices],
            logprobs=[],
            config=oai_config,
            usage=dict(oai_response.usage) if oai_response.usage else None,
        )

        cache_request(
            cache=self.cache, params=cache_key_params, values=asdict(response)
        )
        return response

    def count_tokens(self, text) -> int:
        return num_tokens_from_messages(text)
