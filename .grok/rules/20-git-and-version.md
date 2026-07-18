# Git, versioning, and release

Follow `.crules/modes/GIT_POLICY.md` in full when present.

## Conventional commits

`feat` | `fix` | `docs` | `chore` | `refactor` — imperative subject, ≤72 chars.

## Version sources (must match)

1. `pyproject.toml` — **master** (`[tool.poetry].version` and `[project].version`)
2. `src/tinfo/__init__.py` — runtime `__version__`
3. Git tags on release (`vX.Y.Z`)

Bump from the highest observed value (monotonic). Default: feat→minor,
fix/docs/chore/refactor→patch, breaking→major.

## Pre-commit

- Heuristic secret scan on staged files.
- No credentials or private dumps committed.
- After version edit, verify with:
  `PYTHONPATH=src python3 -m tinfo.cli --version`
  (or `tinfo --version` when installed).

## Shortcuts

User says **commit** / **branch** / **release** → Manager persona + `GIT_POLICY.md`.
