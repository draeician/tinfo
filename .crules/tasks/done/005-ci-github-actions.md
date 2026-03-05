# Task 005: GitHub Actions CI

**Type:** `chore`
**Priority:** Medium
**Version Bump:** Patch
**Depends On:** Task 001, Task 004

## Description

Set up GitHub Actions to run linting (Ruff) and tests (pytest) on every push and PR.

## Acceptance Criteria

- [x] `.github/workflows/ci.yml` exists
- [x] CI runs `ruff check` on Python files
- [x] CI runs `pytest` (unit tests only, not integration)
- [x] CI uses Python 3.12
- [x] CI installs only runtime dependencies (not training stack)
- [x] Badge in `README.md` shows CI status
- [x] `ruff` is declared as a dev dependency in `pyproject.toml`

## Coder Notes

- Two separate jobs: `lint` (ruff only) and `test` (install + pytest -m "not integration").
- README.md cleaned up — removed old conversational content, added badge, install/usage/test sections.
- Badge URL uses current remote (draeician/tinfo); update if remote changes.
