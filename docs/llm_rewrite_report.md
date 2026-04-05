# LIDA LLM Module Rewrite Report

## Overview

The `lida.llm` module was rewritten to replace the deprecated `llmx` package (https://github.com/victordibia/llmx). This report documents the implementation details and changes made for reproducibility.

## Original llmx Package

The original `llmx` package provided a unified interface to several LLM providers:

- **OpenAI** (GPT models)
- **Google PaLM** (MakerSuite and Vertex AI)
- **Cohere**
- **HuggingFace** (local models)

### Key Features of Original llmx

1. **Unified Model Interface** - Single interface to create LLM text generators
2. **Standardized Messaging** - OpenAI ChatML message format
3. **Caching Support** - Built-in caching for faster responses
4. **Configurable Providers** - Support for API keys via environment variables

## Rewritten lida.llm Module

The new implementation in `lida/llm/` provides a drop-in replacement with enhanced features:

### Architecture

```
lida/llm/
├── __init__.py          # Main exports
├── base_textgen.py      # Abstract base class
├── factory.py           # Provider factory function
├── datamodel.py         # Data models (Message, Config, Response)
├── utils.py             # Utility functions
├── openai_textgen.py    # OpenAI provider
├── gemini_textgen.py   # Google Gemini provider
├── anthropic_textgen.py # Anthropic Claude provider
└── minimax_textgen.py   # MiniMax provider
```

### Key Implementation Details

#### 1. Factory Pattern (`factory.py`)

The `llm()` factory function creates provider-specific text generators:

```python
from lida.llm import llm

# Supported providers
gen = llm("openai")    # OpenAI GPT models
gen = llm("gemini")    # Google Gemini
gen = llm("anthropic") # Anthropic Claude
gen = llm("minimax")   # MiniMax models
```

**Provider Registry:**

| Provider | Models | API |
|----------|--------|-----|
| openai | gpt-4o, gpt-4o-mini, gpt-4, gpt-3.5-turbo | OpenAI |
| gemini | gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash | google-genai |
| anthropic | claude-sonnet-4, claude-3-5-haiku, claude-3-opus | anthropic SDK |
| minimax | MiniMax-M2.5, MiniMax-M2.1, MiniMax-M2 | httpx (Anthropic-compatible) |

#### 2. Abstract Base Class (`base_textgen.py`)

All providers inherit from `TextGenerator` ABC:

```python
class TextGenerator(ABC):
    @abstractmethod
    def generate(self, messages, config, **kwargs) -> TextGenerationResponse:
        pass
    
    @abstractmethod
    def count_tokens(self, text) -> int:
        pass
```

**Key Features:**
- Built-in disk caching using `diskcache`
- Configurable cache directory per provider/model
- Token counting utilities

#### 3. Data Models (`datamodel.py`)

Using Pydantic dataclasses for type safety:

```python
@dataclass
class Message:
    role: str
    content: str

@dataclass
class TextGenerationConfig:
    n: int = 1
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    top_k: int = 50
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    model: Optional[str] = None
    use_cache: bool = True

@dataclass
class TextGenerationResponse:
    text: List[Message]
    config: Any
    logprobs: Optional[Any] = None
    usage: Optional[Any] = None
```

#### 4. Provider Implementations

**OpenAI (`openai_textgen.py`):**
- Supports both OpenAI and Azure OpenAI
- OpenAI-compatible endpoints (via `api_base` parameter)
- Automatic token counting
- Caching support

**Gemini (`gemini_textgen.py`):**
- Uses `google-genai` SDK
- Message format conversion (OpenAI → Gemini)
- System instruction handling
- Model-specific configuration

**Anthropic (`anthropic_textgen.py`):**
- Uses official `anthropic` SDK
- System message extraction
- Role alternation enforcement
- Automatic prompt caching

**MiniMax (`minimax_textgen.py`):**
- Dual API mode: `anthropic` (recommended) or `openai`
- Uses `httpx` directly for Anthropic-compatible endpoint
- Environment variable configuration
- Custom token counting

#### 5. Environment Variable Configuration

The module automatically loads `.env` from project root:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Google Gemini
GOOGLE_API_KEY=AIza...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# MiniMax
MINIMAX_API_KEY=sk-cp-...
MINIMAX_API_MODE=anthropic  # or 'openai'
```

### Breaking Changes from llmx

1. **Provider Names**: Changed from `palm` to `gemini`
2. **API Dependencies**: Uses newer SDKs where available
3. **Configuration**: Simplified parameter names
4. **Removed**: Cohere and HuggingFace local model support

### Usage Example

```python
from lida import Manager, TextGenerationConfig, llm

# Create LLM generator
text_gen = llm("minimax", model="MiniMax-M2.5")

# Create LIDA manager
lida = Manager(text_gen=text_gen)

# Configure generation
config = TextGenerationConfig(
    n=1,
    temperature=0.5,
    model="MiniMax-M2.5",
    use_cache=True
)

# Use with LIDA
summary = lida.summarize(data, summary_method="default", textgen_config=config)
goals = lida.goals(summary, n=2, textgen_config=config)
charts = lida.visualize(summary, goals[0], textgen_config=config, library="seaborn")
```

## Dependencies

```
openai>=1.0.0
google-genai
anthropic
httpx
diskcache
pydantic
python-dotenv
```

## Reproducibility Notes

1. **API Keys**: Ensure correct environment variables are set
2. **Model Versions**: Specify exact model names for reproducibility
3. **Caching**: Enable `use_cache=True` for consistent results
4. **Temperature**: Set explicit temperature values (default: 0.1)

## Migration from llmx

```python
# Old llmx code
from llmx import llm
gen = llm(provider="openai", model="gpt-4")

# New lida.llm code
from lida.llm import llm
gen = llm("openai", model="gpt-4")
```

## References

- Original llmx: https://github.com/victordibia/llmx
- LIDA Repository: https://github.com/Microsoft/lida
- MiniMax API: https://platform.minimax.io/docs/api-reference/text-anthropic-api
