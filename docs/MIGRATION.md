# Migration: Replacing `llmx` with Built-in LLM Module

## Background

LIDA previously depended on [`llmx`](https://github.com/victordibia/llmx), a unified API for chat-based LLMs. This package is **no longer maintained** and has compatibility issues with modern Python versions and LLM provider APIs. To ensure continued functionality and support for current LLM providers, `llmx` has been replaced with a built-in `lida.llm` module.

---

## What Changed

### 1. New `lida/llm/` Package

A drop-in replacement module was created at `lida/llm/` with the following files:

| File | Purpose |
|------|---------|
| `__init__.py` | Public API exports |
| `datamodel.py` | `Message`, `TextGenerationConfig`, `TextGenerationResponse` — identical interfaces to `llmx` |
| `utils.py` | Disk caching (`diskcache`), token counting (`tiktoken`), platform-aware cache directories |
| `base_textgen.py` | `TextGenerator` abstract base class |
| `openai_textgen.py` | OpenAI, Azure OpenAI, and OpenAI-compatible endpoints |
| `gemini_textgen.py` | Google Gemini via `google-genai` SDK |
| `anthropic_textgen.py` | Anthropic Claude |
| `minimax_textgen.py` | MiniMax M2.5 via Anthropic-compatible (using `httpx` directly) or OpenAI-compatible API |
| `factory.py` | `llm()` factory function and `providers` dictionary |

### 2. Import Migration (14 Files)

All imports were changed from `from llmx import ...` to `from lida.llm import ...`:

- `lida/__init__.py`
- `lida/datamodel.py`
- `lida/cli.py`
- `lida/web/app.py`
- `lida/components/manager.py`
- `lida/components/summarizer.py`
- `lida/components/goal.py`
- `lida/components/persona.py`
- `lida/components/viz/vizgenerator.py`
- `lida/components/viz/vizeditor.py`
- `lida/components/viz/vizexplainer.py`
- `lida/components/viz/vizrepairer.py`
- `lida/components/viz/vizrecommender.py`
- `lida/components/viz/vizevaluator.py`
- `tests/test_components.py`

### 3. Dependency Changes (`pyproject.toml`)

**Removed:**
```
llmx>=0.0.21a
```

**Added (core):**
```
openai>=1.0
tiktoken
diskcache
```

**Updated optional dependencies:**
```
# Before
transformers = ["llmx[transformers]"]

# After
gemini = ["google-genai"]
anthropic = ["anthropic"]
```

---

## Supported Providers

| Provider | Environment Variable | Usage | Models |
|----------|---------------------|-------|--------|
| **OpenAI** | `OPENAI_API_KEY` | `llm("openai")` | GPT-4o, GPT-4o-mini, GPT-4, GPT-3.5-turbo |
| **Google Gemini** | `GOOGLE_API_KEY` | `llm("gemini")` | Gemini 2.0 Flash, 1.5 Pro, 1.5 Flash |
| **Anthropic Claude** | `ANTHROPIC_API_KEY` | `llm("anthropic")` | Claude Sonnet 4, Haiku 3.5, Opus 3 |
| **MiniMax** | `MINIMAX_API_KEY` | `llm("minimax")` | MiniMax-M2.5, M2.5-highspeed, M2.1, M2 |
| **OpenAI-compatible** | `OPENAI_API_KEY` | `llm("openai", api_base="https://...")` | vllm, any compatible endpoint |

### Installing Optional Providers

```bash
# Core (OpenAI) — installed by default
pip install lida

# Google Gemini support
pip install lida[gemini]

# Anthropic Claude support (also required for MiniMax default mode)
pip install lida[anthropic]

# All optional providers
pip install lida[gemini,anthropic]
```

### Configuration via `.env`

All API keys and base URLs are loaded from a `.env` file in the project root. Copy the template and fill in your keys:

```bash
cp .env.example .env
```

The `.env` file supports these variables:

| Variable | Provider | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | OpenAI | API key |
| `OPENAI_API_BASE` | OpenAI | Custom base URL (for compatible endpoints) |
| `OPENAI_API_TYPE` | OpenAI | Set to `azure` for Azure OpenAI |
| `OPENAI_API_VERSION` | OpenAI | Azure API version |
| `OPENAI_ORGANIZATION` | OpenAI | Organization ID |
| `GOOGLE_API_KEY` | Gemini | API key |
| `ANTHROPIC_API_KEY` | Anthropic | API key |
| `MINIMAX_API_KEY` | MiniMax | API key |
| `MINIMAX_API_MODE` | MiniMax | `anthropic` (default) or `openai` |
| `MINIMAX_ANTHROPIC_BASE_URL` | MiniMax | Override Anthropic endpoint (MUST include `/anthropic`, e.g. `https://api.minimax.io/anthropic`) |
| `MINIMAX_OPENAI_BASE_URL` | MiniMax | Override OpenAI endpoint (MUST include `/v1`, e.g. `https://api.minimax.io/v1`) |

> **Note:** Environment variables set in your shell always take priority over `.env` values (loaded with `override=False`).

---

## Usage Examples

For a complete, interactive guide, see the **[updated tutorial notebook](notebooks/tutorial_updated.ipynb)**.

### Basic Usage (unchanged API)

```python
from lida import Manager, TextGenerationConfig, llm

# Default (OpenAI)
lida = Manager(text_gen=llm("openai"))

# With Gemini
lida = Manager(text_gen=llm("gemini"))

# With Claude
lida = Manager(text_gen=llm("anthropic"))

# With MiniMax M2.5 (uses Anthropic-compatible API by default)
lida = Manager(text_gen=llm("minimax"))

# With MiniMax via OpenAI-compatible API
lida = Manager(text_gen=llm("minimax", api_mode="openai"))

# With MiniMax using a specific model
lida = Manager(text_gen=llm("minimax", model="MiniMax-M2.5-highspeed"))
```

### Specifying Models via Config

```python
config = TextGenerationConfig(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_tokens=4096,
    provider="gemini"
)

summary = lida.summarize(data, textgen_config=config)
```

---

## Breaking Changes

- **External code importing from `llmx` directly** (e.g., notebooks, user scripts) must update imports:
  ```python
  # Before
  from llmx import llm, TextGenerationConfig

  # After
  from lida.llm import llm, TextGenerationConfig
  ```

- The `transformers` optional dependency group (`pip install lida[transformers]`) has been removed. For local HuggingFace models, use an OpenAI-compatible server like [vllm](https://vllm.readthedocs.io/) and connect via `llm("openai", api_base="http://localhost:8000")`.

- The old `palm` and `cohere` providers from `llmx` are no longer directly supported. Use `gemini` for Google models. For Cohere, use an OpenAI-compatible endpoint if available.
