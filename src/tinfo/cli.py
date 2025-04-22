#!/usr/bin/env python3
"""
Text Information Analyzer CLI

A command-line tool for analyzing text files and directories,
providing statistics about tokens, characters, words, and lines.
"""

import sys
import tiktoken
import argparse
from typing import Dict, List, Tuple, Set
from pathlib import Path

from . import __version__

# Known binary file extensions to skip
BINARY_EXTENSIONS = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz', '.7z'}

def is_probably_text_file(file_path: Path) -> bool:
    """
    Check if a file is likely a text file.
    Files without extensions are considered text files unless proven otherwise.
    Files with known binary extensions are skipped.
    
    Args:
        file_path: Path object representing the file
        
    Returns:
        bool: True if the file is likely a text file, False otherwise
    """
    # Skip files with known binary extensions
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return False
        
    # Try to read the first few bytes to check if it's text
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            # Check for common binary file signatures
            if chunk.startswith(b'\x00') or b'\x00' in chunk[:1000]:
                print(f'Skipping likely binary file: {file_path}')
                return False
            # Try decoding as UTF-8
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                print(f'Skipping file with invalid UTF-8 encoding: {file_path}')
                return False
    except Exception as e:
        print(f'Error checking file type for {file_path}: {str(e)}')
        return False

def read_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()

def count_tokens(file_content, encoding_name):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(file_content)
    return len(tokens)

def count_characters(file_content):
    return len(file_content)

def count_words(file_content):
    # Split the content by whitespace to count words
    words = file_content.split()
    return len(words)

def count_lines(file_content):
    # Split the content by lines to count lines
    lines = file_content.splitlines()
    return len(lines)

def analyze_file(file_path: str, encoding: str) -> Tuple[int, int, int, int]:
    """
    Analyze a single file and return its statistics.
    
    Args:
        file_path: Path to the file to analyze
        encoding: The encoding to use for token counting
        
    Returns:
        Tuple of (token_count, char_count, word_count, line_count)
    """
    try:
        file_content = read_file(file_path)
        return (
            count_tokens(file_content, encoding),
            count_characters(file_content),
            count_words(file_content),
            count_lines(file_content)
        )
    except FileNotFoundError:
        print(f'Error: File not found: {file_path}')
        return (0, 0, 0, 0)
    except Exception as e:
        print(f'Error processing {file_path}: {str(e)}')
        return (0, 0, 0, 0)

def get_files_to_analyze(path: Path) -> List[Path]:
    """
    Get a list of files to analyze from a path.
    If path is a file, returns a list with just that file.
    If path is a directory, recursively finds all text files.
    
    Args:
        path: Path object representing file or directory
        
    Returns:
        List of Path objects to analyze
    """
    if not path.exists():
        print(f'Error: Path does not exist: {path}')
        return []
        
    if path.is_file():
        return [path] if is_probably_text_file(path) else []
        
    files = []
    try:
        for file_path in path.rglob('*'):
            if file_path.is_file():
                if is_probably_text_file(file_path):
                    files.append(file_path)
    except PermissionError as e:
        print(f'Error: Permission denied accessing {path}: {str(e)}')
    except Exception as e:
        print(f'Error traversing directory {path}: {str(e)}')
    
    return files

def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Analyze text files and directories for token, character, word, and line counts."
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='Paths to files or directories to analyze'
    )
    return parser

def main():
    """Entry point for the tinfo command."""
    parser = create_parser()
    args = parser.parse_args()
    
    encoding = "cl100k_base"
    
    # Convert all arguments to Path objects and resolve them to absolute paths
    paths = [Path(p).resolve() for p in args.paths]
    
    # Collect all files to analyze
    files_to_analyze = []
    for path in paths:
        print(f'Scanning path: {path}')
        new_files = get_files_to_analyze(path)
        if new_files:
            files_to_analyze.extend(new_files)
        else:
            print(f'No analyzable files found in: {path}')
    
    if not files_to_analyze:
        print("\nNo text files found to analyze.")
        sys.exit(1)
    
    print(f'\nFound {len(files_to_analyze)} files to analyze.')
    
    total_tokens = 0
    total_chars = 0
    total_words = 0
    total_lines = 0
    successful_files = 0

    # Process each file
    for file_path in files_to_analyze:
        tokens, chars, words, lines = analyze_file(str(file_path), encoding)
        
        if any([tokens, chars, words, lines]):  # If file was processed successfully
            successful_files += 1
            total_tokens += tokens
            total_chars += chars
            total_words += words
            total_lines += lines
            
            # Print individual file statistics
            print(f'\nFile: {file_path}')
            print(f'Tokens: {tokens:,}')
            print(f'Characters: {chars:,}')
            print(f'Words: {words:,}')
            print(f'Lines: {lines:,}')

    # Print summary if multiple files were processed
    if len(files_to_analyze) > 1:
        print(f'\nSummary for {successful_files} of {len(files_to_analyze)} files:')
        print(f'Total Tokens: {total_tokens:,}')
        print(f'Total Characters: {total_chars:,}')
        print(f'Total Words: {total_words:,}')
        print(f'Total Lines: {total_lines:,}')

def cli():
    """CLI entry point for the package."""
    main()

if __name__ == "__main__":
    cli() 