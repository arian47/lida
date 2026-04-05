"""
lida.llm — Built-in multi-provider LLM module.

Drop-in replacement for the deprecated `llmx` package.
Supports OpenAI, Google Gemini, Anthropic Claude, MiniMax, and any OpenAI-compatible endpoint.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (walk up from this file to find it)
_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=False)

from .datamodel import Message, TextGenerationConfig, TextGenerationResponse
from .base_textgen import TextGenerator
from .factory import llm, providers

__all__ = [
    "Message",
    "TextGenerationConfig",
    "TextGenerationResponse",
    "TextGenerator",
    "llm",
    "providers",
]
