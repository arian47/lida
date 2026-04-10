<div align="center">
  <h1>📊 LIDA</h1>
  <p><b>Automatic Generation of Visualizations and Infographics using Large Language Models</b></p>

  [![PyPI version](https://badge.fury.io/py/lida.svg)](https://badge.fury.io/py/lida)
  [![arXiv](https://img.shields.io/badge/arXiv-2303.02927-b31b1b.svg)](https://arxiv.org/abs/2303.02927)
  ![PyPI - Downloads](https://img.shields.io/pypi/dm/lida?label=downloads&color=green)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

<br/>

LIDA is a grammar-agnostic library for generating data visualizations and data-faithful infographics. It works seamlessly with any programming language and visualization library (e.g., **matplotlib, seaborn, altair, d3, plotly**) and natively supports multiple Large Language Model (LLM) providers.

> **Note on Code Execution:**
> To create visualizations, LIDA _generates_ and _executes_ Python code. Please ensure that you run LIDA in a securely sandboxed or trusted environment.

---

## 🌟 What's New in the Re-Engineered Version?

This enhanced branch of LIDA has been heavily re-engineered for better stability, removing external bloated dependencies and bringing LLM integration securely in-house!

- **Deprecation of `llmx`:** We stripped out the external `llmx` dependency. LIDA now utilizes a powerful, native, drop-in replacement built directly into `lida.llm`.
- **Broader Provider Support:** First-class, built-in support for **OpenAI, Azure OpenAI, Google Gemini, Anthropic Claude, and MiniMax**, as well as any OpenAI-compatible API endpoint.
- **Robust Environment Loading:** Configurations and API Keys are safely and dynamically loaded from your local `.env` files, natively propagating to both the UI and the Python environments.

---

## ✨ Core Features

LIDA treats _**visualizations as code**_ and provides a unified, clean API specifically built to handle the end-to-end pipeline:

- **📦 Data Summarization:** Create compact but rich semantic dataset profiles.
- **🎯 Goal Generation:** Automatically identify analytics targets and data questions.
- **🎭 Persona Exploration:** Tailor analytic goals by user-specific roles (e.g., Executive vs. Data Scientist).
- **📈 Visualization Generation:** Draft perfectly formatted visualization code.
- **⚙️ Visualization Editing:** Morph and tweak charts via natural language commands.
- **💬 Visualization Explanation:** Generate plain-english breakdowns of complex charts.
- **🔧 Evaluation & Repair:** Self-correct bugs or syntax errors in charting libraries.
- **🎨 Infographic Generation:** Transform standard plots into stylized art (*beta*).

---

## 🚀 Installation

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

You can customize your installation based on the providers and tools you intend to use:

```bash
pip install lida[web]            # For the Web GUI (FastAPI & React)
pip install lida[gemini]         # For Google Gemini support
pip install lida[anthropic]      # For Anthropic Claude support
pip install lida[infographics]   # For AI infographic generation (Peacasso)

# Or grab everything:
pip install lida[web,gemini,anthropic,infographics]
```

---

## 🔐 Environment Setup

To use LIDA, you must provide the API keys for the providers you wish to utilize. LIDA loads these automatically from your environment or a `.env` file!

Create a `.env` file in the root of your project:

```env
# Define which provider LIDA UI should default to (e.g., openai, minimax, gemini, anthropic)
LIDA_PROVIDER=minimax

# --- OpenAI / Azure OpenAI ---
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=
OPENAI_API_TYPE=

# --- Google Gemini ---
GOOGLE_API_KEY=your_gemini_key

# --- Anthropic Claude ---
ANTHROPIC_API_KEY=your_anthropic_key

# --- MiniMax ---
MINIMAX_API_KEY=your_minimax_key
MINIMAX_API_MODE=anthropic
```

---

## 🖥️ Using LIDA: The Web GUI

LIDA ships with a beautiful, fully-featured interactive React Single Page Application (SPA). This is the fastest way to get started and allows you to upload datasets, select models dynamically, and generate visualizations entirely visually.

> **Important:** Ensure you have configured `LIDA_PROVIDER` correctly in your `.env` file so the backend boots with your active API key.

Start the User Interface:
```bash
lida ui --port=8080 --docs
```
Navigate to `http://localhost:8080/` in your browser.

---

## 🐍 Using LIDA: Python API (Non-GUI)

If you're building a data-pipeline, integrating LIDA into a Jupyter Notebook, or writing an autonomous data agent, use the Python API. 

The primary entry point is the `Manager` class.

```python
from lida import Manager, llm

# Instantiate the manager. LIDA will automatically pick up API keys from your .env!
# You can swap out "openai" for "gemini", "anthropic", or "minimax"
text_generator = llm("minimax")
lida = Manager(text_gen=text_generator)

# 1. Summarize the dataset
summary = lida.summarize("data/cars.csv")

# 2. Generate insightful visualization goals
goals = lida.goals(summary, n=5)

# 3. Generate a chart addressing the first Goal using Seaborn
charts = lida.visualize(
    summary=summary, 
    goal=goals[0], 
    library="seaborn"
)

# Render the code!
print(charts[0].code)
```

Other useful core modules to play with from the Python side:

```python
# Edit an existing visualization
edited_charts = lida.edit(code=charts[0].code, summary=summary, instructions=["change the bars to red"])

# Explain a complex plot
explanation = lida.explain(code=charts[0].code, summary=summary)

# Repair broken charts (using stack traces or feedback)
repaired = lida.repair(code=broken_code, goal=goals[0], summary=summary, feedback="NameError: name 'sns' is not defined")
```

---

## 🤝 Contributing

Contributions are completely welcome! Please see our contributing guidelines for information on preparing your PR routines and setting up the development framework.

## 📖 Citation

If you use LIDA in your research, please cite the core paper:

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

## ⚖️ License

MIT License - see [LICENSE](LICENSE) for details.
