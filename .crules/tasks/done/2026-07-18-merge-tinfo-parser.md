# Merge pappas_bag tinfo-parser into tinfo-parse

## Acceptance criteria

- [x] `tinfo` remains the file analyzer (detailed stats)
- [x] `tinfo-parse` implements standalone `tinfo-parser.py` behavior (report filter/sort)
- [x] Console name is `tinfo-parse` (no `.py`)
- [x] README / project_spec document the split

## Coder notes

- Replaced analyze/columnar `parse.py` with report-line parser from `~/pappas_bag/tinfo-parser.py`
- Preserved CLI flags: files, `-f`, `-t`, `-s`, `--sort`, `--ascend`, `--descend`; added `--version`
- Strictly greater than token-limit (same as original)
