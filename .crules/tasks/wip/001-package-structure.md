# Task 001: Package Structure

**Type:** `chore`
**Priority:** High
**Version Bump:** Patch (0.1.0 → 0.1.1)

## Description

Convert the flat script layout into a proper Python package with `pyproject.toml` and a `src/shorthand_llm/` directory structure. This is the foundation for all subsequent tasks (CLI entrypoints, testing, CI).

## Acceptance Criteria

- [ ] `pyproject.toml` exists with project metadata, version `0.1.0`, and dependency declarations
- [ ] `src/shorthand_llm/__init__.py` exists with `__version__ = "0.1.0"`
- [ ] `shorthand_lib.py` moved to `src/shorthand_llm/compressor.py` (or equivalent)
- [ ] All compression/memory scripts either moved into the package or updated to import from it
- [ ] `requirements.txt` remains for backward compat but `pyproject.toml` is the source of truth for deps
- [ ] `python3 -m shorthand_llm` does not crash (even if it just prints usage)
- [ ] Existing functionality is not broken (manual smoke test: `stream_compress.py` still works)

## Notes

- The training scripts (`train_shorthand.py`, `save_merged.py`, `convert_to_gguf.py`, `generate_data_ollama.py`, `generate_dataset.py`) can remain as standalone scripts since they have heavy GPU dependencies not needed at runtime.
- `densify` (bash script) stays in repo root or gets a `scripts/` directory.
