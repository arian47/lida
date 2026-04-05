# Contributing to LIDA

Thank you for your interest in contributing to LIDA! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
1. Check the [existing issues](https://github.com/microsoft/lida/issues) to avoid duplicates
2. Update to the latest version to see if the issue persists
3. Include your Python version, operating system, and relevant dependency versions

When submitting a bug report, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Code snippets or minimal reproduction examples
- Error messages and stack traces

### Suggesting Features

We welcome feature suggestions! Please:
1. Check existing issues and discussions first
2. Describe the problem you're trying to solve
3. Explain the expected behavior
4. Consider the scope and maintainability of the feature

### Pull Requests

1. **Fork the repository** and create a branch from `main`
2. **Keep your changes focused** - one feature or fix per PR
3. **Follow the coding style** - we use `black` and `isort` for formatting
4. **Write tests** for new features or significant changes
5. **Update documentation** as needed
6. **Ensure all tests pass** before submitting

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip or conda

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/microsoft/lida.git
cd lida

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lida --cov-report=html

# Run specific test file
pytest tests/test_components.py
```

### Code Style

We use automated formatting tools:

```bash
# Format code
black .
isort .

# Check formatting without applying
black --check .
isort --check .
```

## Project Structure

```
lida/
├── __init__.py          # Package exports
├── cli.py               # Command-line interface
├── datamodel.py         # Data models
├── utils.py             # Utility functions
├── version.py           # Version information
├── components/          # Core components
│   ├── manager.py       # Main manager class
│   ├── summarizer.py   # Data summarization
│   ├── goal.py         # Goal generation
│   ├── persona.py      # Persona-based goals
│   ├── executor.py     # Chart execution
│   ├── infographer.py   # Infographic generation
│   └── viz/            # Visualization components
│       ├── vizgenerator.py
│       ├── vizeditor.py
│       ├── vizexplainer.py
│       ├── vizevaluator.py
│       ├── vizrepairer.py
│       └── vizrecommender.py
├── llm/                # LLM provider integrations
│   ├── __init__.py
│   ├── base_textgen.py
│   ├── openai_textgen.py
│   ├── gemini_textgen.py
│   ├── anthropic_textgen.py
│   ├── minimax_textgen.py
│   └── factory.py
└── web/                # Web API and UI
    ├── app.py
    └── ui/
```

## Documentation

We welcome documentation improvements:
- Fix typos or unclear explanations
- Add examples and tutorials
- Improve docstrings
- Translate documentation

## License

By contributing to LIDA, you agree that your contributions will be licensed under the MIT License.
