import logging

from .openai_textgen import OpenAITextGenerator

logger = logging.getLogger("lida")


# Providers dictionary — lists available providers and their models
providers = {
    "openai": {
        "name": "OpenAI",
        "description": "OpenAI and Azure OpenAI GPT models. Also supports OpenAI-compatible endpoints via api_base.",
        "models": [
            {"name": "gpt-4o", "max_tokens": 128000, "model": {"provider": "openai", "parameters": {"model": "gpt-4o"}}},
            {"name": "gpt-4o-mini", "max_tokens": 128000, "model": {"provider": "openai", "parameters": {"model": "gpt-4o-mini"}}},
            {"name": "gpt-4-turbo", "max_tokens": 128000, "model": {"provider": "openai", "parameters": {"model": "gpt-4-turbo"}}},
            {"name": "gpt-4", "max_tokens": 8192, "model": {"provider": "openai", "parameters": {"model": "gpt-4"}}},
            {"name": "gpt-3.5-turbo", "max_tokens": 16384, "model": {"provider": "openai", "parameters": {"model": "gpt-3.5-turbo"}}},
        ],
    },
    "gemini": {
        "name": "Google Gemini",
        "description": "Google Gemini models via the google-genai SDK.",
        "models": [
            {"name": "gemini-2.0-flash", "max_tokens": 1048576, "model": {"provider": "gemini", "parameters": {"model": "gemini-2.0-flash"}}},
            {"name": "gemini-2.0-flash-lite", "max_tokens": 1048576, "model": {"provider": "gemini", "parameters": {"model": "gemini-2.0-flash-lite"}}},
            {"name": "gemini-1.5-pro", "max_tokens": 2097152, "model": {"provider": "gemini", "parameters": {"model": "gemini-1.5-pro"}}},
            {"name": "gemini-1.5-flash", "max_tokens": 1048576, "model": {"provider": "gemini", "parameters": {"model": "gemini-1.5-flash"}}},
        ],
    },
    "anthropic": {
        "name": "Anthropic",
        "description": "Anthropic Claude models.",
        "models": [
            {"name": "claude-sonnet-4-20250514", "max_tokens": 200000, "model": {"provider": "anthropic", "parameters": {"model": "claude-sonnet-4-20250514"}}},
            {"name": "claude-3-5-haiku-20241022", "max_tokens": 200000, "model": {"provider": "anthropic", "parameters": {"model": "claude-3-5-haiku-20241022"}}},
            {"name": "claude-3-opus-20240229", "max_tokens": 200000, "model": {"provider": "anthropic", "parameters": {"model": "claude-3-opus-20240229"}}},
        ],
    },
    "minimax": {
        "name": "MiniMax",
        "description": "MiniMax models via Anthropic-compatible API (recommended) or OpenAI-compatible API.",
        "models": [
            {"name": "MiniMax-M2.5", "max_tokens": 1000000, "model": {"provider": "minimax", "parameters": {"model": "MiniMax-M2.5"}}},
            {"name": "MiniMax-M2.5-highspeed", "max_tokens": 1000000, "model": {"provider": "minimax", "parameters": {"model": "MiniMax-M2.5-highspeed"}}},
            {"name": "MiniMax-M2.1", "max_tokens": 1000000, "model": {"provider": "minimax", "parameters": {"model": "MiniMax-M2.1"}}},
            {"name": "MiniMax-M2", "max_tokens": 1000000, "model": {"provider": "minimax", "parameters": {"model": "MiniMax-M2"}}},
        ],
    },
}


def sanitize_provider(provider: str) -> str:
    """Normalize provider name to a canonical form."""
    p = provider.lower().strip()

    if p in ("openai", "default", "azureopenai", "azureoai"):
        return "openai"
    elif p in ("gemini", "google"):
        return "gemini"
    elif p in ("anthropic", "claude"):
        return "anthropic"
    elif p in ("minimax", "minimax-m2.5", "minimax-m2"):
        return "minimax"
    else:
        raise ValueError(
            f"Invalid provider '{provider}'. "
            f"Supported providers: 'openai', 'gemini', 'anthropic', 'minimax'. "
        )


def llm(provider: str = None, **kwargs):
    """Factory function to create a text generator for the specified provider.

    Args:
        provider: LLM provider name. Supported: 'openai', 'gemini', 'anthropic', 'minimax'.
                  Defaults to 'openai'.
        **kwargs: Additional arguments passed to the provider's constructor.
                  Common kwargs:
                  - api_key: API key (overrides env variable)
                  - model: Default model name
                  - api_base: Base URL for OpenAI-compatible endpoints
                  - api_type: 'azure' for Azure OpenAI
                  - api_mode: 'anthropic' (default) or 'openai' — for MiniMax only

    Returns:
        TextGenerator instance for the specified provider.
    """
    if provider is None:
        provider = "openai"
        logger.info("No provider specified. Defaulting to 'openai'.")

    provider = sanitize_provider(provider)

    if provider == "openai":
        return OpenAITextGenerator(provider=provider, **kwargs)
    elif provider == "gemini":
        from .gemini_textgen import GeminiTextGenerator
        return GeminiTextGenerator(provider=provider, **kwargs)
    elif provider == "anthropic":
        from .anthropic_textgen import AnthropicTextGenerator
        return AnthropicTextGenerator(provider=provider, **kwargs)
    elif provider == "minimax":
        from .minimax_textgen import MiniMaxTextGenerator
        return MiniMaxTextGenerator(provider=provider, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
