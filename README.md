# LIDA: Automatic Generation of Visualizations and Infographics using Large Language Models

[![PyPI version](https://badge.fury.io/py/lida.svg)](https://badge.fury.io/py/lida)
[![arXiv](https://img.shields.io/badge/arXiv-2303.02927-<COLOR>.svg)](https://arxiv.org/abs/2303.02927)
![PyPI - Downloads](https://img.shields.io/pypi/dm/lida?label=pypi%20downloads)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<a target="_blank" href="https://colab.research.google.com/github/microsoft/lida/blob/main/notebooks/tutorial.ipynb">
<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

LIDA is a library for generating data visualizations and data-faithful infographics. LIDA is grammar agnostic (will work with any programming language and visualization libraries e.g. matplotlib, seaborn, altair, d3 etc) and works with multiple large language model providers (OpenAI, Azure OpenAI, Google Gemini, Anthropic Claude, MiniMax, and other OpenAI-compatible endpoints). Details on the components of LIDA are described in the [paper](https://arxiv.org/abs/2303.02927) and in this tutorial [notebook](notebooks/tutorial.ipynb).

> **Note on Code Execution:**
> To create visualizations, LIDA _generates_ and _executes_ code.
> Ensure that you run LIDA in a secure environment.

## Features

LIDA treats _**visualizations as code**_ and provides a clean API for generating, executing, editing, explaining, evaluating and repairing visualization code.

- [x] Data Summarization
- [x] Goal Generation
- [x] Goal Exploration with Personas
- [x] Visualization Generation
- [x] Visualization Editing
- [x] Visualization Explanation
- [x] Visualization Evaluation and Repair
- [x] Visualization Recommendation
- [x] Infographic Generation (beta)

```python
from lida import Manager, llm

lida = Manager(text_gen=llm("openai"))
summary = lida.summarize("data/cars.csv")
goals = lida.goals(summary, n=2)
charts = lida.visualize(summary=summary, goal=goals[0])
```

## Installation

### Standard Installation

```bash
pip install lida
```

### Development Installation

```bash
git clone https://github.com/arian47/lida.git
cd lida
pip install -e ".[dev]"
```

### Optional Dependencies

```bash
# For web UI
pip install lida[web]

# For Google Gemini support
pip install lida[gemini]

# For Anthropic Claude support
pip install lida[anthropic]

# For infographic generation
pip install lida[infographics]

# For all optional dependencies
pip install lida[web,gemini,anthropic,infographics]
```

## Supported LLM Providers

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| OpenAI | GPT-4, GPT-3.5 Turbo | `OPENAI_API_KEY` |
| Azure OpenAI | GPT-4, GPT-3.5 Turbo | `AZURE_OPENAI_API_KEY` |
| Google Gemini | Gemini Pro | `GOOGLE_API_KEY` |
| Anthropic | Claude 3 Opus, Claude 3 Sonnet | `ANTHROPIC_API_KEY` |
| MiniMax | MiniMax M2 | `MINIMAX_API_KEY` |
| OpenAI Compatible | Any OpenAI-compatible endpoint | `OPENAI_API_BASE` |

## Supported Visualization Libraries

- matplotlib
- seaborn
- altair
- plotly
- plotnine (ggplot2 port)
- Any other library representable as code

## Quick Start

### Python API

```python
from lida import Manager, llm

# Initialize with OpenAI
lida = Manager(text_gen=llm("openai"))

# Summarize data
summary = lida.summarize("data/cars.csv")

# Generate visualization goals
goals = lida.goals(summary, n=5)

# Generate visualizations
charts = lida.visualize(summary=summary, goal=goals[0], library="matplotlib")
```

### Web API and UI

```bash
lida ui --port=8080 --docs
```

Navigate to http://localhost:8080/ in your browser.

### Docker

```bash
docker compose up
```

## Documentation

### Core Concepts

#### Data Summarization

Given a dataset, generate a compact summary of the data.

```python
summary = lida.summarize("data/cars.json")
```

#### Goal Generation

Generate visualization goals given a data summary.

```python
goals = lida.goals(summary, n=5, persona="data analyst")
```

#### Visualization Generation

Generate, refine, execute and filter visualization code.

```python
charts = lida.visualize(
    summary=summary, 
    goal=goals[0], 
    library="matplotlib"
)
```

#### Visualization Editing

Edit visualizations using natural language.

```python
edited_charts = lida.edit(
    code=code,
    summary=summary,
    instructions=["convert to bar chart", "change color to red"],
    library="matplotlib"
)
```

#### Visualization Explanation

Generate natural language explanations of visualization code.

```python
explanation = lida.explain(code=charts[0].code, summary=summary)
```

#### Visualization Evaluation

Evaluate visualizations and get repair suggestions.

```python
evaluations = lida.evaluate(code=code, goal=goals[i], library="matplotlib")
```

## API Reference

See the full API documentation for detailed information on all methods and parameters.

## Contributing

Contributions are welcome! Please see our contributing guidelines for more information.

## Citation

If you use LIDA in your research, please cite:

```bibtex
@article{dibia2023lida,
    title={LIDA: A Tool for Automatic Generation of Grammar-Agnostic Visualizations and Infographics using Large Language Models},
    author={Victor Dibia},
    year={2023},
    booktitle = {Proceedings of the 61th Annual Meeting of the Association for Computational Linguistics: System Demonstrations},
    publisher = {Association for Computational Linguistics},
    month={March},
    day={6},
    eprint={2303.02927},
    archivePrefix={arXiv},
    primaryClass={cs.AI}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.
