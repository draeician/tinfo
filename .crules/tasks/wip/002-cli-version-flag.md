# Task 002: CLI Entrypoints with --version

**Type:** `feat`
**Priority:** High
**Version Bump:** Minor (0.1.x → 0.2.0)
**Depends On:** Task 001

## Description

Add proper CLI entrypoints via `pyproject.toml [project.scripts]` and ensure every CLI tool supports `--version` per the CODER standard.

## Acceptance Criteria

- [ ] `stream_compress.py` has `--version` flag reporting `shorthand_llm.__version__`
- [ ] `openwebui-chat-compression.py` has `--version` flag
- [ ] `graph_ingest.py` has `--version` flag
- [ ] `recall.py` has `--version` flag
- [ ] `check_memory.py` has `--version` flag
- [ ] `pyproject.toml` declares `[project.scripts]` entrypoints (e.g., `shorthand-compress`, `shorthand-recall`)
- [ ] `python3 -m shorthand_llm --version` prints the version string
- [ ] All `--version` outputs match the version in `pyproject.toml`

## Notes

- `compress.py` can be excluded since it requires the full GPU stack and isn't a general-use CLI.
- `densify` is bash and outside scope — document its version in `--help` output if desired.
