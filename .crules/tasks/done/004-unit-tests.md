# Task 004: Unit Tests

**Type:** `feat`
**Priority:** Medium
**Version Bump:** Minor
**Depends On:** Task 001

## Description

Add a test suite covering the core library and pipeline scripts. Focus on `shorthand_lib.py` since it has pure-logic methods that can be tested without Ollama.

## Acceptance Criteria

- [x] `tests/` directory exists with `conftest.py`
- [x] `tests/test_compressor.py` covers:
  - [x] `_mask_entities()` — URLs and emails are masked correctly
  - [x] `_unmask_entities()` — masked tokens are restored
  - [x] `_find_safe_boundary()` — boundary detection at sentence/word/hard limits
  - [x] `stream_compress()` — short input yields one chunk; long input yields multiple
- [x] `tests/test_graph_utils.py` covers:
  - [x] `enforce_schema()` — lists, dicts, and primitives are flattened to strings
  - [x] `clean_json_output()` — markdown code fences are stripped
- [x] `pytest` is declared as a dev dependency in `pyproject.toml`
- [x] `pytest` runs green from repo root (31 passed, 0.09s)
- [x] Tests that require Ollama or Neo4j are marked with `@pytest.mark.integration` and skipped by default

## Coder Notes

- Extracted `enforce_schema` and `clean_json_output` into `src/shorthand_llm/graph_utils.py` so they're importable for testing.
- `_query_ollama()` is mocked via `unittest.mock.patch` in stream_compress tests.
- `conftest.py` auto-skips `@pytest.mark.integration` tests unless `-m integration` is passed.
- 31 tests total: 16 compressor, 15 graph utils.
