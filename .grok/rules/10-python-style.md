# Python coding style (tinfo)

Apply on any `*.py` edit under this repository.

## Language and packaging

- Match the project’s declared Python version when present (`requires-python`,
  Ruff target, classifiers); otherwise prefer modern 3.9+ habits only if the
  codebase already uses them. This package declares `requires-python = ">=3.7"`.
- Package: `tinfo` (`src/tinfo/` layout).
- Prefer existing production dependencies; do not add new ones without an
  explicit task or user request. Current runtime dep: `tiktoken`.
- Ad-hoc execution: `PYTHONPATH=src python3 -m tinfo.cli …` (or installed `tinfo`).

## Style

1. PEP 8 / Ruff-friendly layout; 4-space indent.
2. Type hints on public functions; return types included.
3. Google-style docstrings for public callables.
4. f-strings for formatting.
5. `snake_case` functions and variables; `PascalCase` classes.
6. Prefer explicit `is None` checks for singletons.
7. Narrow `except` clauses; preserve causes when re-raising.
8. Use `with` for resources; no bare `open` without context managers.

## Subprocess and safety

- Always pass argv **lists** to `subprocess` — never `shell=True`.
- Do not use `pip install --break-system-packages`.
- Install with `pipx` or a project venv; ad-hoc via module execution.

## Structure preference

Keep changes local to existing modules until size or clarity demands a split.
If splitting, preserve public CLI/API surfaces (`tinfo` entry point, `--version`,
`paths` args).

## Tests

- Prefer pure-function unit tests for parsers, helpers, and pure logic
  (e.g. `count_tokens`, `is_probably_text_file`, `get_files_to_analyze`).
- Do not weaken tests to pass a bad change.
- Name tests clearly; one concern per test function.
- Default command: none yet — introduce `pytest` under `tests/` when adding a suite
