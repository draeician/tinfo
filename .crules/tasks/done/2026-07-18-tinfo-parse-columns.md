# tinfo-parse rename + columnar output

## Acceptance criteria

- [x] `tinfo-parse.py` renamed/replaced by `tinfo-parse` (package module + root launcher + console script)
- [x] Per-file stdout is token count (left column) + filename (right column)
- [x] Diagnostics (scan/skip) do not pollute stdout (stderr)

## Coder notes

- Logic lives in `src/tinfo/parse.py`; entry points: `tinfo-parse` script, `python3 -m tinfo.parse`, Poetry/`[project.scripts]` `tinfo-parse = tinfo.parse:cli`
- Root `tinfo-parse` inserts `src/` for repo-local runs without install
- Shared discovery/analysis diagnostics in `cli.py` now print to stderr so both tools stay pipe-friendly
