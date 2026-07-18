# Agent System Status: [CUSTOMIZED]

Canonical instruction file for Grok Build, Codex, Claude Code, Cursor, and human contributors.

Read this file completely before changing code. When instructions conflict:

`project_spec.md` > `AGENTS.md` > `.crules/modes/*` > tool-specific entrypoints (`GROK.md`, `CLAUDE.md`, `CODEX.md`)

## Project identity

This repository is **tinfo**: a CLI for analyzing text files and directories (token, character, word, and line counts via tiktoken).

- Package / module: `tinfo` (`src/tinfo/`)
- Version master: `pyproject.toml` (`[tool.poetry].version` and `[project].version`)
- Runtime version source: `src/tinfo/__init__.py` → `__version__`
- Current version: `0.2.0`
- CLI entry: `tinfo = tinfo.cli:cli` (Poetry scripts)
- Smoke: `PYTHONPATH=src python3 -m tinfo.cli --version` (or `tinfo --version` when installed)
- Tests: no automated suite yet
- Authoritative scope: `project_spec.md`

## Required reading before implementation

1. `AGENTS.md` (this file)
2. `project_spec.md`
3. Active task under `.crules/tasks/wip/` (if present)
4. Relevant swarm mode under `.crules/modes/` when acting as Manager or Coder
5. `README.md` / `CHANGELOG.md` when changing user-facing behavior

## Swarm SOP (crules)

This repo uses the **Skeleton Swarm** workflow.

| Path | Role |
|------|------|
| `.crules/modes/MANAGER.md` | Orchestrate, version, task pipeline — do not implement product code |
| `.crules/modes/CODER.md` | Implement atomic, tested changes from tasks / user request |
| `.crules/modes/GIT_POLICY.md` | Conventional commits, branching, secret scan, release |
| `.crules/modes/BOOTSTRAPPER.md` | Only when status is `[TEMPLATE]` |
| `.crules/tasks/{wip,review,done}/` | Markdown task files with acceptance criteria |
| `project_spec.md` | Single source of truth for scope and conventions |
| `.grok/rules/` | Always-on Grok project rules (SOP + style) |
| `.grok/agents/` | Optional Grok agent profiles (manager / coder / swarm) |

Default persona for implementation work: **Coder**.  
Default persona for planning, commits, releases, backlog: **Manager**.

Shortcut keywords (act as Manager, then follow `GIT_POLICY.md`):

- **commit** — secret scan, version bump, verify runtime version, conventional commit
- **branch** — create `feat/` / `fix/` / `docs/` / `chore/` / `refactor/` branch
- **release** — verify version, changelog summary, tag, push tags (only if asked)

## Hard boundaries

1. Never use `pip install --break-system-packages`. Prefer `pipx`, project `venv/`, or module execution.
2. Never commit secrets, credentials, or private data dumps.
3. Prefer list-form `subprocess` — never `shell=True`.
4. Do not expand scope beyond `project_spec.md` / the active task without user confirmation.
5. Minimum code that solves the problem. Nothing speculative.
6. Touch only what you must. Clean up only your own mess.
7. Define success criteria. Loop until verified.
8. Keep the public CLI stable: `tinfo [--version] paths…` unless the user requests a breaking change.
9. Do not commit `venv/` or generated IDE rule dumps under `.cursor/rules/*.mdc`.

## Coding style

- Match existing project style before introducing new patterns.
- Type hints on public functions where the language supports them.
- Google-style docstrings for public Python callables.
- Keep CLI / API surfaces stable; document breaking changes explicitly.
- Prefer pure helpers in `tinfo.cli` (or extracted modules) for counting and file discovery so they stay unit-testable.

## Versioning and packaging

- Version strings must agree across `pyproject.toml` and `src/tinfo/__init__.py`.
- Bump rules: `feat` → minor, `fix`/`docs`/`chore`/`refactor` → patch, breaking → major.
- Versions only increase (monotonic). Base = highest of metadata, runtime constant, and git tags.

## Testing discipline

- Prefer the smallest test that proves the change.
- Do not weaken assertions to green a bad implementation.
- When introducing tests, prefer `pytest` under `tests/` and pure-function coverage of counters and text-file detection.

## Git discipline

- Follow `.crules/modes/GIT_POLICY.md` when present.
- Conventional commits; no force-push to shared default branches unless explicitly requested.
- Do not commit as part of unrelated tasks without the user asking.

## Common principles

- Don’t assume. Don’t hide confusion. Surface tradeoffs.
- Prefer short, actionable edits over huge rewrites.
- Track non-trivial work in `.crules/tasks/wip/` with acceptance criteria.
