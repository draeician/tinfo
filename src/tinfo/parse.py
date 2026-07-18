#!/usr/bin/env python3
"""tinfo-parse: token counts with exclusion support, columnar output."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

from . import __version__
from .cli import analyze_file, get_files_to_analyze


def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser for tinfo-parse."""
    parser = argparse.ArgumentParser(
        prog="tinfo-parse",
        description=(
            "Analyze text files and directories for token counts, "
            "with support for excluding paths. Prints token count "
            "(left column) and filename (right column)."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Paths to files or directories to analyze",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        action="append",
        default=[],
        help=(
            "Path to a file or directory to exclude from analysis. "
            "May be specified multiple times."
        ),
    )
    return parser


def is_excluded(file_path: Path, exclude_paths: Sequence[Path]) -> bool:
    """Return True if file_path should be excluded based on exclude_paths."""
    for ex in exclude_paths:
        if file_path == ex:
            return True
        try:
            # If this does not raise, file_path is under the excluded directory
            file_path.relative_to(ex)
            return True
        except ValueError:
            continue
    return False


def format_token_rows(rows: Sequence[Tuple[int, Path]]) -> List[str]:
    """Format (token_count, path) rows as left-column tokens, right-column path."""
    if not rows:
        return []
    width = max(len(f"{tokens:,}") for tokens, _ in rows)
    return [f"{tokens:>{width},}  {path}" for tokens, path in rows]


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the tinfo-parse command with exclusion support."""
    parser = create_parser()
    args = parser.parse_args(argv)

    encoding = "cl100k_base"

    paths = [Path(p).resolve() for p in args.paths]
    exclude_paths = [Path(p).resolve() for p in (args.exclude or [])]

    files_to_analyze: List[Path] = []
    for path in paths:
        print(f"Scanning path: {path}", file=sys.stderr)
        new_files = get_files_to_analyze(path)
        if new_files:
            files_to_analyze.extend(new_files)
        else:
            print(f"No analyzable files found in: {path}", file=sys.stderr)

    if not files_to_analyze:
        print("No text files found to analyze.", file=sys.stderr)
        return 1

    if exclude_paths:
        filtered_files: List[Path] = []
        for file_path in files_to_analyze:
            if is_excluded(file_path, exclude_paths):
                print(f"Skipping excluded file: {file_path}", file=sys.stderr)
            else:
                filtered_files.append(file_path)
    else:
        filtered_files = files_to_analyze

    if not filtered_files:
        print(
            "No text files found to analyze after applying exclusions.",
            file=sys.stderr,
        )
        return 1

    print(f"Found {len(filtered_files)} files to analyze.", file=sys.stderr)

    results: List[Tuple[int, Path]] = []
    for file_path in filtered_files:
        tokens, chars, words, lines = analyze_file(str(file_path), encoding)
        if any([tokens, chars, words, lines]):
            results.append((tokens, file_path))

    if not results:
        print("No files were analyzed successfully.", file=sys.stderr)
        return 1

    for line in format_token_rows(results):
        print(line)

    return 0


def cli() -> None:
    """Console-script entry point for tinfo-parse."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
