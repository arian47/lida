# Changelog

All notable changes to LIDA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive pytest test suite with fixtures and integration tests
- Health check endpoint for Docker container orchestration
- Multi-stage Docker build for optimized production images
- Development dependencies in `pyproject.toml` (`[dev]` extra)
- CONTRIBUTING.md guidelines for community contributions

### Changed
- Updated LICENSE to MIT with "LIDA Contributors" as copyright holder
- Updated pyproject.toml with proper classifiers, keywords, and maintainers
- Enhanced Docker configuration with multi-stage builds and health checks
- README.md restructured for better clarity and community focus
- docker-compose.yml updated with proper environment variable handling

### Fixed
- Docker healthcheck configuration
- CORS middleware configuration for broader compatibility

## [0.1.0] - 2023-07-01

### Added
- Data summarization with multiple methods (default, llm)
- Goal generation with persona support
- Visualization generation (matplotlib, seaborn, altair, plotly, plotnine)
- Visualization editing via natural language instructions
- Visualization explanation
- Visualization evaluation and repair
- Visualization recommendation
- Infographic generation (beta)
- Web API and UI
- Docker support
- Multi-LLM provider support (OpenAI, Azure OpenAI, Google Gemini, Anthropic Claude, MiniMax)

### Original Release
- First public release as documented in the ACL 2023 paper
