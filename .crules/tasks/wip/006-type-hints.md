# Task 006: Add Type Hints

**Type:** `refactor`
**Priority:** Low
**Version Bump:** Patch
**Depends On:** Task 001

## Description

Add type annotations across all modules in the package for better IDE support and static analysis.

## Acceptance Criteria

- [ ] `shorthand_lib.py` / `compressor.py` — all public methods have type hints
- [ ] `graph_ingest.py` — all functions have type hints
- [ ] `recall.py` — all functions have type hints
- [ ] `memory_tool.py` — all functions have type hints
- [ ] `stream_compress.py` — `main()` and helpers have type hints
- [ ] `openwebui-chat-compression.py` — all functions have type hints
- [ ] `check_memory.py` — all functions have type hints
- [ ] `mypy` or `pyright` passes without errors (or known exclusions documented)

## Notes

- Training scripts can be excluded from type-hint enforcement.
- Use `from __future__ import annotations` for modern syntax.
