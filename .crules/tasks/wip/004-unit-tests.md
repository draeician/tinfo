# Task 004: Unit Tests

**Type:** `feat`
**Priority:** Medium
**Version Bump:** Minor
**Depends On:** Task 001

## Description

Add a test suite covering the core library and pipeline scripts. Focus on `shorthand_lib.py` since it has pure-logic methods that can be tested without Ollama.

## Acceptance Criteria

- [ ] `tests/` directory exists with `conftest.py`
- [ ] `tests/test_compressor.py` covers:
  - [ ] `_mask_entities()` — URLs and emails are masked correctly
  - [ ] `_unmask_entities()` — masked tokens are restored
  - [ ] `_find_safe_boundary()` — boundary detection at sentence/word/hard limits
  - [ ] `stream_compress()` — short input yields one chunk; long input yields multiple
- [ ] `tests/test_graph_ingest.py` covers:
  - [ ] `enforce_schema()` — lists, dicts, and primitives are flattened to strings
  - [ ] `clean_json_output()` — markdown code fences are stripped
- [ ] `pytest` is declared as a dev dependency in `pyproject.toml`
- [ ] `pytest` runs green from repo root
- [ ] Tests that require Ollama or Neo4j are marked with `@pytest.mark.integration` and skipped by default

## Notes

- Mock `_query_ollama()` in unit tests to avoid requiring a running Ollama instance.
- Training scripts do not need tests at this stage.
