#!/usr/bin/env python3
"""tinfo-parse: filter/sort token-report lines (not a file analyzer).

Reads lines shaped like::

    ###--- /path/to/file 1234 tokens ---###

from files or stdin, then filters by token threshold and optional sort.
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Dict, Iterable, List, Optional, Sequence

from . import __version__

TOKEN_LINE_RE = re.compile(
    r"###---\s+(.+?)\s+(\d+)\s+tokens\s+---###"
)

# Parsed row: path, basename, token count
FileStat = Dict[str, object]


def parse_line(line: str) -> Optional[FileStat]:
    """Extract path, filename, and token count from one report line.

    Strips surrounding whitespace and optional wrapping single quotes.
    Returns None when the line does not match the expected format.
    """
    cleaned_line = line.strip().strip("'")
    match = TOKEN_LINE_RE.match(cleaned_line)
    if not match:
        return None
    path, tokens = match.groups()
    filename = path.split("/")[-1]
    return {"path": path, "filename": filename, "tokens": int(tokens)}


def filter_files(
    data: Iterable[str],
    token_limit: int,
    sort_type: Optional[str],
    ascending: bool,
) -> List[FileStat]:
    """Keep rows with tokens above token_limit; optionally sort."""
    filtered: List[FileStat] = []
    for line in data:
        parsed = parse_line(line)
        if parsed is not None and int(parsed["tokens"]) > token_limit:
            filtered.append(parsed)

    if sort_type:
        key_map = {
            "tokens": lambda x: int(x["tokens"]),
            "filename": lambda x: str(x["filename"]).lower(),
            "path": lambda x: str(x["path"]).lower(),
        }
        filtered = sorted(
            filtered,
            key=key_map[sort_type],
            reverse=not ascending,
        )

    return filtered


def print_results(filtered_files: Sequence[FileStat], show_summary: bool) -> None:
    """Print filtered rows and an optional count/token summary."""
    for file_stat in filtered_files:
        print(f"{file_stat['path']}: {file_stat['tokens']} tokens")

    if show_summary and filtered_files:
        file_count = len(filtered_files)
        total_tokens = sum(int(f["tokens"]) for f in filtered_files)
        plural = "s" if file_count != 1 else ""
        print(
            f"\nSummary: {file_count} file{plural}, "
            f"{total_tokens} total tokens"
        )


def read_input_lines(file_list: Sequence[str]) -> List[str]:
    """Read lines from the given files, or stdin when file_list is empty.

    Raises:
        FileNotFoundError: if a path is missing.
        OSError: on other I/O failures.
    """
    if not file_list:
        return sys.stdin.readlines()

    data: List[str] = []
    for file_path in file_list:
        with open(file_path, "r", encoding="utf-8") as handle:
            data.extend(handle.readlines())
    return data


def create_parser() -> argparse.ArgumentParser:
    """Build the argparse CLI for tinfo-parse."""
    parser = argparse.ArgumentParser(
        prog="tinfo-parse",
        description=(
            "Filter and sort token-report lines of the form "
            "'###--- <path> <N> tokens ---###' from files or stdin."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Input files with token data (default: stdin if none given)",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Single input file with token data (overrides positional files)",
    )
    parser.add_argument(
        "-t",
        "--token-limit",
        type=int,
        default=0,
        help="Only include rows with token count above this value (default: 0)",
    )
    parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Show summary of filtered files (count and total tokens)",
    )
    parser.add_argument(
        "--sort",
        nargs="?",
        const="tokens",
        choices=["tokens", "filename", "path"],
        help="Sort results by field (default field: tokens)",
    )
    sort_group = parser.add_mutually_exclusive_group()
    sort_group.add_argument(
        "--ascend",
        action="store_true",
        help="Sort ascending (default when --sort is used)",
    )
    sort_group.add_argument(
        "--descend",
        action="store_true",
        help="Sort descending",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry: parse args, read input, filter/print results."""
    parser = create_parser()
    args = parser.parse_args(argv)

    sort_type = args.sort
    # Match original: default ascending; --descend flips when sort is active
    ascending = not args.descend if (args.ascend or args.sort) else True

    try:
        if args.file:
            data = read_input_lines([args.file])
        else:
            data = read_input_lines(args.files)
    except FileNotFoundError as exc:
        missing = getattr(exc, "filename", None) or args.file or "?"
        print(f"Error: File '{missing}' not found.", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error reading input: {exc}", file=sys.stderr)
        return 1

    if not data:
        print("Error: No input data provided.", file=sys.stderr)
        return 1

    filtered_files = filter_files(data, args.token_limit, sort_type, ascending)
    if not filtered_files:
        print(f"No files found with token count above {args.token_limit}.")
    else:
        print_results(filtered_files, args.summary)

    return 0


def cli() -> None:
    """Console-script entry point for tinfo-parse."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
