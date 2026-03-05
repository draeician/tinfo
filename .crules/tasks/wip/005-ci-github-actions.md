# Task 005: GitHub Actions CI

**Type:** `chore`
**Priority:** Medium
**Version Bump:** Patch
**Depends On:** Task 001, Task 004

## Description

Set up GitHub Actions to run linting (Ruff) and tests (pytest) on every push and PR.

## Acceptance Criteria

- [ ] `.github/workflows/ci.yml` exists
- [ ] CI runs `ruff check` on Python files
- [ ] CI runs `pytest` (unit tests only, not integration)
- [ ] CI uses Python 3.12
- [ ] CI installs only runtime dependencies (not training stack)
- [ ] Badge in `README.md` shows CI status
- [ ] `ruff` is declared as a dev dependency in `pyproject.toml`

## Notes

- Integration tests (requiring Ollama/Neo4j) should be excluded from CI via pytest marker.
- Training scripts may have linting issues — consider excluding them from Ruff or fixing inline.
