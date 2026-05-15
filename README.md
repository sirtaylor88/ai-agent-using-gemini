# AI Agent using Gemini

![Python](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?logo=google&logoColor=white)
![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?logo=uv&logoColor=white)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![License](https://img.shields.io/badge/license-MIT-green)

> A terminal AI coding agent powered by **Google Gemini**. Given a natural-language prompt, it autonomously plans and executes file operations inside a sandboxed working directory to read, modify, and run code.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Development](#development)

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| [uv](https://docs.astral.sh/uv/) | latest |
| [Gemini API key](https://aistudio.google.com/app/apikey) | — |

---

## Setup

```bash
uv sync --all-groups
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key_here
```

---

## Usage

```bash
uv run main.py "<prompt>"
uv run main.py "<prompt>" --verbose
```

**Examples:**

```bash
uv run main.py "Fix the failing tests in the calculator project"
uv run main.py "What files are in the pkg directory?" --verbose
```

> `--verbose` prints each tool call with its arguments and reports token usage at the end.

---

## How it works

The agent sends your prompt to `gemini-2.5-flash` and loops — calling tools, appending results to the conversation, and iterating — until the model produces a final text response (up to 20 iterations).

All file operations are **sandboxed to `./calculator`**.

### Available tools

| Tool | Description |
|------|-------------|
| `get_files_info` | List directory contents with file sizes |
| `get_file_content` | Read a file (capped at 10,000 characters) |
| `write_file` | Write or overwrite a file |
| `run_python_file` | Execute a Python script and capture its output |

---

## Development

### Testing

```bash
uv run pytest                                        # run all tests
uv run pytest tests/test_files.py                    # single file
uv run pytest --cov --cov-report=term-missing        # with coverage
```

### Linting & type checking

```bash
uv run ruff check --fix .
uv run ruff format .
uv run pylint main.py utils.py functions/
uv run mypy .
uv run bandit -r . -c pyproject.toml
```

### All checks at once

```bash
pre-commit run --all-files
```
