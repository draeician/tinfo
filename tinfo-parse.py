#!/usr/bin/env python3
import argparse
import sys
import re

def parse_line(line):
    """Extract filename, path, and token count from a line, handling quoted input."""
    # Strip surrounding quotes and whitespace
    cleaned_line = line.strip().strip("'")
    match = re.match(r"###---\s+(.+?)\s+(\d+)\s+tokens\s+---###", cleaned_line)
    if match:
        path, tokens = match.groups()
        filename = path.split("/")[-1]
        return {"path": path, "filename": filename, "tokens": int(tokens)}
    return None

def filter_files(data, token_limit, sort_type, ascending):
    """Filter files with token count above the specified limit and sort results."""
    filtered = []
    for line in data:
        parsed = parse_line(line)
        if parsed and parsed["tokens"] > token_limit:
            filtered.append(parsed)
    
    if sort_type:
        key_map = {
            "tokens": lambda x: x["tokens"],
            "filename": lambda x: x["filename"].lower(),
            "path": lambda x: x["path"].lower()
        }
        filtered = sorted(filtered, key=key_map[sort_type], reverse=not ascending)
    
    return filtered

def print_results(filtered_files, show_summary):
    """Print filtered files and optional summary in a clean format."""
    for file in filtered_files:
        print(f"{file['path']}: {file['tokens']} tokens")
    
    if show_summary and filtered_files:
        file_count = len(filtered_files)
        total_tokens = sum(file["tokens"] for file in filtered_files)
        print(f"\nSummary: {file_count} file{'s' if file_count != 1 else ''}, {total_tokens} total tokens")

def read_files(file_list):
    """Read data from a list of files or stdin if file_list is empty."""
    data = []
    if file_list:
        for file_path in file_list:
            try:
                with open(file_path, "r") as f:
                    data.extend(f.readlines())
            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
                sys.exit(1)
    else:
        data = sys.stdin.readlines()
    return data

def main():
    parser = argparse.ArgumentParser(description="Filter files by token count.")
    parser.add_argument(
        "files",
        nargs="*",
        help="Input files with token data (default: stdin if no files provided)"
    )
    parser.add_argument(
        "-f", "--file", type=str, help="Single input file with token data (overrides positional files)"
    )
    parser.add_argument(
        "-t",
        "--token-limit",
        type=int,
        default=0,
        help="Minimum token count to include (default: 0)"
    )
    parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Show summary of filtered files (count and total tokens)"
    )
    parser.add_argument(
        "--sort",
        nargs="?",
        const="tokens",
        choices=["tokens", "filename", "path"],
        help="Sort results by specified field (default: tokens)"
    )
    sort_group = parser.add_mutually_exclusive_group()
    sort_group.add_argument(
        "--ascend",
        action="store_true",
        help="Sort in ascending order (default if --sort is used)"
    )
    sort_group.add_argument(
        "--descend",
        action="store_true",
        help="Sort in descending order"
    )
    args = parser.parse_args()

    # Set sort type and order
    sort_type = args.sort
    ascending = not args.descend if (args.ascend or args.sort) else True

    data = []
    if args.file:
        try:
            with open(args.file, "r") as f:
                data = f.readlines()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        data = read_files(args.files)

    if not data:
        print("Error: No input data provided.", file=sys.stderr)
        sys.exit(1)

    filtered_files = filter_files(data, args.token_limit, sort_type, ascending)
    if not filtered_files:
        print(f"No files found with token count above {args.token_limit}.")
    else:
        print_results(filtered_files, args.summary)

if __name__ == "__main__":
    main()

