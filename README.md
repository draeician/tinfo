# Text Information Analyzer (tinfo)

A command-line tool for analyzing text files and directories, providing statistics about tokens, characters, words, and lines.

## Features

- Analyzes text files for:
  - Token count (using OpenAI's tiktoken)
  - Character count
  - Word count
  - Line count
- Supports analyzing:
  - Single files
  - Multiple files
  - Directories (recursive)
- Smart text file detection
- Detailed statistics and summaries

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

### `tinfo-parse` — token column + filename

Compact listing for sorting or piping. Status messages go to stderr; stdout is
only `tokens  path` rows (token counts right-aligned in a left column).

```bash
tinfo-parse --version
tinfo-parse file.txt
tinfo-parse src/ -x src/tinfo/__pycache__
```

Example stdout:

```text
  407  /path/to/README.md
1,540  /path/to/src/tinfo/cli.py
```

## Command-line Options

### `tinfo`

- `--version`: Show the version number and exit
- `paths`: One or more paths to files or directories to analyze

### `tinfo-parse`

- `--version`: Show the version number and exit
- `paths`: One or more paths to files or directories to analyze
- `-x` / `--exclude`: Path to exclude (file or directory); repeatable

## Output

### `tinfo`

For each file analyzed, tinfo will display:
- Token count
- Character count
- Word count
- Line count

When analyzing multiple files, a summary of totals will be displayed at the end.

### `tinfo-parse`

One line per file: token count (left column), filename (right column).

## Requirements

- Python 3.7 or higher
- tiktoken package (installed automatically)

## License

MIT License

Acknowledgments

The Tiktoken library: https://github.com/awslabs/tiktoken

