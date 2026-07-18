# Text Information Analyzer (tinfo)

A command-line tool for analyzing text files and directories, providing statistics about tokens, characters, words, and lines.

## Features

**`tinfo`** — analyze source files:

- Token count (OpenAI tiktoken / `cl100k_base`)
- Character, word, and line counts
- Single files, multiple paths, recursive directories
- Smart text-file detection and detailed summaries

**`tinfo-parse`** — filter existing token-report lines:

- Parse `###--- <path> <N> tokens ---###` from files or stdin
- Threshold (`-t`), sort (`--sort`), and summary (`-s`)

## Installation

Install pipx if you haven't already:

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

**From GitHub** (after the repo is pushed):

```bash
pipx install git+https://github.com/draeician/tinfo
```

**Local** (from the project root):

```bash
pipx install .
```

Or in a virtual environment:

```bash
pip install -e .
```

## Usage

### `tinfo` — detailed stats

```bash
# Show version information
tinfo --version

# Analyze a single file
tinfo file.txt

# Analyze multiple files
tinfo file1.txt file2.txt

# Analyze a directory (recursively)
tinfo /path/to/directory

# Analyze mixed paths
tinfo file1.txt /path/to/directory file2.txt
```

### `tinfo-parse` — filter token-report lines

**Not** a file analyzer. Reads lines in this form (from files or stdin):

```text
###--- /path/to/file 1234 tokens ---###
```

Then filters by token threshold and optional sort (merged from the old
standalone `tinfo-parser.py` / `tinfo-parse.py` helper).

```bash
tinfo-parse --version
tinfo-parse report.txt
tinfo-parse -t 500 --sort tokens --descend report.txt
cat report.txt | tinfo-parse -s --sort path
tinfo-parse -f report.txt -t 100 --summary --sort filename --ascend
```

Example stdout:

```text
/path/to/big.py: 1540 tokens
/path/to/README.md: 609 tokens

Summary: 2 files, 2149 total tokens
```

## Command-line Options

### `tinfo`

- `--version`: Show the version number and exit
- `paths`: One or more paths to files or directories to analyze

### `tinfo-parse`

- `--version`: Show the version number and exit
- `files`: Input files with token-report lines (default: stdin)
- `-f` / `--file`: Single input file (overrides positional `files`)
- `-t` / `--token-limit`: Keep rows with tokens **above** this value (default: 0)
- `-s` / `--summary`: Print file count and total tokens
- `--sort [tokens|filename|path]`: Sort results (default field: `tokens`)
- `--ascend` / `--descend`: Sort direction (with `--sort`)

## Output

### `tinfo`

For each file analyzed, tinfo will display:
- Token count
- Character count
- Word count
- Line count

When analyzing multiple files, a summary of totals will be displayed at the end.

### `tinfo-parse`

One line per matching report row: `path: N tokens`, plus optional summary.

## Requirements

- Python 3.7 or higher
- tiktoken package (installed automatically)

## License

MIT License

Acknowledgments

The Tiktoken library: https://github.com/awslabs/tiktoken

