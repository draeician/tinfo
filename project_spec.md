# Project Specification

Scaffolded and filled by Grok `/init` (Skeleton Swarm) from README and package metadata.

## Overview

- **Name**: tinfo (Text Information Analyzer)
- **Summary**: CLI that analyzes text files and directories for token, character, word, and line counts (tokens via OpenAI’s tiktoken / `cl100k_base`).
- **Package / module**: `tinfo` under `src/tinfo/`

## Tech stack

- **Primary language(s)**: Python
- **Framework / runtime**: stdlib `argparse` CLI; `tiktoken` for tokenization
- **Packaging**: Poetry + PEP 621 dual metadata in `pyproject.toml`; `src/` layout
- **Runtime version source**: `src/tinfo/__init__.py` → `__version__` (must match `pyproject.toml`)
- **Python**: `>=3.7` (`requires-python` / Poetry `^3.7`)
- **Dependencies**: `tiktoken` (also listed in `requirements.txt`)

## Commands

- **Smoke**: `PYTHONPATH=src python3 -m tinfo.cli --version`
  - Installed: `tinfo --version` (pipx / `pip install -e .` / Poetry script entry)
- **Analyze (`tinfo`)**: `PYTHONPATH=src python3 -m tinfo.cli <path> [path…]`
- **Parse (`tinfo-parse`)**: filter/sort `###--- path N tokens ---###` lines from files/stdin
  - `./tinfo-parse [files…]` or `PYTHONPATH=src python3 -m tinfo.parse …`
  - Flags: `-f`, `-t/--token-limit`, `-s/--summary`, `--sort`, `--ascend`/`--descend`
- **Tests**: none yet — introduce `pytest` under `tests/` when adding a suite
- **Install**:
  - Local venv: `pip install -e .` (from repo root)
  - pipx: `pipx install .` or `pipx install git+https://github.com/draeician/tinfo`
- **Lint / CI**: not configured yet

## Architecture and conventions

- **Layout**:
  - `src/tinfo/__init__.py` — package metadata / `__version__`
  - `src/tinfo/cli.py` — CLI, file discovery, analysis, reporting
  - `src/tinfo/parse.py` — `tinfo-parse` CLI (filter/sort token-report lines; no tiktoken)
  - `tinfo-parse` — repo-root launcher for local use without install
  - `pyproject.toml` — build, deps, console scripts `tinfo` and `tinfo-parse`
- **Module boundaries**:
  - `tinfo` / `cli.py`: analyze source files (tiktoken, discovery, detailed stats)
  - `tinfo-parse` / `parse.py`: parse existing report lines only — do not conflate with analysis
- **Behavior notes**:
  - `tinfo`: skips known binary extensions and non-UTF-8 / null-byte content; recursive `rglob`; multi-file summary
  - `tinfo-parse`: keeps rows with tokens **strictly greater than** `-t`; optional sort by tokens/filename/path
- **Forbidden patterns**:
  - `pip install --break-system-packages`
  - `subprocess` with `shell=True`
  - Secrets or private data dumps in git
  - Speculative CLI flags or features outside the active task / user request

## Hard rules

- No `pip install --break-system-packages`
- No secrets in git
- No `shell=True` in subprocess calls
- Keep public CLI surface stable unless user requests a breaking change
- Version strings in `pyproject.toml` and `src/tinfo/__init__.py` must always match
- Do not commit `venv/`

## Status

- [x] Repo identity, stack, version sources, and smoke command filled from real files
- [ ] Automated tests (optional follow-up)
- [ ] Lint/CI configuration (optional follow-up)
