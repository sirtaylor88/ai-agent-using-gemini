# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the agent
uv run main.py "<prompt>"
uv run main.py "<prompt>" --verbose

# Tests
uv run pytest
uv run pytest tests/test_files.py          # single file
uv run pytest --cov --cov-report=term-missing

# Lint and format
uv run ruff check --fix .
uv run ruff format .
uv run pylint main.py utils.py functions/
uv run mypy .

# Run pre-commit hooks on all files
pre-commit run --all-files
```

Dependencies are managed with `uv`. Requires `GEMINI_API_KEY` in a `.env` file.

## Architecture

This project is a Gemini-powered coding agent with a **fixed working directory** (`./calculator`). The agent can only read, write, and run files within that directory.

**Agentic loop** (`main.py`): Sends user prompt to `gemini-2.5-flash`, processes function calls in a loop (max 20 iterations), and prints the final text response. Each iteration appends both the model response and tool results to the `messages` list, building conversational history.

**Tool dispatch** (`utils.py`): `call_function` maps Gemini `FunctionCall` objects to Python implementations, always injecting `./calculator` as `working_directory`. All tool functions accept `working_directory` as their first argument for sandboxing.

**Tool implementations** (`functions/files.py`): Four tools available to the model:
- `get_files_info` — lists directory contents with sizes
- `get_file_content` — reads a file (truncated at 10,000 chars)
- `write_file` — writes/overwrites a file, creating parent dirs
- `run_python_file` — runs a `.py` file via subprocess with 30s timeout

All tools validate paths via `check_valid_path` to prevent directory traversal outside the working directory.

**Target project** (`calculator/`): A simple calculator app the agent is designed to modify and debug. It parses arithmetic expressions and renders results.

**Function schemas** are defined inline in `main.py` as `types.FunctionDeclaration` objects and passed to the model via `types.GenerateContentConfig`.
