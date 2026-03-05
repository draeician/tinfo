# Task 006: Add Type Hints

**Type:** `refactor`
**Priority:** Low
**Version Bump:** Patch
**Depends On:** Task 001

## Description

Add type annotations across all modules in the package for better IDE support and static analysis.

## Acceptance Criteria

- [x] `compressor.py` — all public methods have type hints
- [x] `graph_utils.py` — all functions have type hints
- [x] `cli.py` — all functions have return types, inner helpers typed
- [x] `__main__.py` — typed
- [ ] `openwebui-chat-compression.py` — standalone script, not ported
- [ ] Standalone legacy scripts (`recall.py`, `check_memory.py`, etc.) — not ported

## Coder Notes

- All modules under `src/shorthand_llm/` now use `from __future__ import annotations`.
- `compressor.py`: full type hints on all methods including `Iterator[str]` for stream_compress.
- `graph_utils.py`: was already typed when extracted.
- Legacy standalone scripts not in the package are excluded from type-hint enforcement.
- Ruff clean, 31 tests pass.
