#!/usr/bin/env python3
import sys
import tiktoken

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

def main():
    encoding = "cl100k_base"
    if len(sys.argv) != 2:
        print("Usage: tinfo.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        file_content = read_file(file_path)
        token_count = count_tokens(file_content, encoding)
        char_count = count_characters(file_content)
        word_count = count_words(file_content)
        line_count = count_lines(file_content)

        print(f'The file {file_path} contains:')
        print(f'{token_count} tokens.')
        print(f'{char_count} characters.')
        print(f'{word_count} words.')
        print(f'{line_count} lines.')

    except FileNotFoundError:
        print(f'File not found: {file_path}')
        sys.exit(1)

if __name__ == "__main__":
    main()

