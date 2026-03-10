#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path
from typing import List

# Add the 'src' directory to the path so it can find the 'tinfo' package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tinfo import __version__
from tinfo.cli import analyze_file, get_files_to_analyze


def create_parser_with_exclude() -> argparse.ArgumentParser:
    """Create and return the argument parser for tinfo-parse."""
    parser = argparse.ArgumentParser(
        description=(
            "Analyze text files and directories for token, character, word, "
            "and line counts, with support for excluding paths."
        )
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


def is_excluded(file_path: Path, exclude_paths: List[Path]) -> bool:
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


def main() -> int:
    """Entry point for the tinfo-parse command with exclusion support."""
    parser = create_parser_with_exclude()
    args = parser.parse_args()

    encoding = "cl100k_base"

    # Resolve input and exclusion paths to absolute paths
    paths = [Path(p).resolve() for p in args.paths]
    exclude_paths = [Path(p).resolve() for p in (args.exclude or [])]

    # Collect all files to analyze
    files_to_analyze: List[Path] = []
    for path in paths:
        print(f"Scanning path: {path}")
        new_files = get_files_to_analyze(path)
        if new_files:
            files_to_analyze.extend(new_files)
        else:
            print(f"No analyzable files found in: {path}")

    if not files_to_analyze:
        print("\nNo text files found to analyze.")
        return 1

    # Apply exclusions
    if exclude_paths:
        filtered_files: List[Path] = []
        for file_path in files_to_analyze:
            if is_excluded(file_path, exclude_paths):
                print(f"Skipping excluded file: {file_path}")
            else:
                filtered_files.append(file_path)
    else:
        filtered_files = files_to_analyze

    if not filtered_files:
        print("\nNo text files found to analyze after applying exclusions.")
        return 1

    print(f"\nFound {len(filtered_files)} files to analyze.")

    total_tokens = 0
    total_chars = 0
    total_words = 0
    total_lines = 0
    successful_files = 0

    # Process each file
    for file_path in filtered_files:
        tokens, chars, words, lines = analyze_file(str(file_path), encoding)

        if any([tokens, chars, words, lines]):
            successful_files += 1
            total_tokens += tokens
            total_chars += chars
            total_words += words
            total_lines += lines

            print(f"\nFile: {file_path}")
            print(f"Tokens: {tokens:,}")
            print(f"Characters: {chars:,}")
            print(f"Words: {words:,}")
            print(f"Lines: {lines:,}")

    if len(filtered_files) > 1:
        print(f"\nSummary for {successful_files} of {len(filtered_files)} files:")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"Total Characters: {total_chars:,}")
        print(f"Total Words: {total_words:,}")
        print(f"Total Lines: {total_lines:,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
