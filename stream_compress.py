#!/usr/bin/env python3
import sys
import argparse
from shorthand_lib import ShorthandCompressor

def main():
    parser = argparse.ArgumentParser(description="Stream Compressor using Local Shorthand Model")
    parser.add_argument("files", nargs="*", help="Files to compress (reads stdin if empty)")
    parser.add_argument("--chunk", type=int, default=6000, help="Chunk size in characters (Default: 6000)")
    parser.add_argument("--overlap", type=int, default=500, help="Overlap size in characters (Default: 500)")
    args = parser.parse_args()

    # Initialize library
    compressor = ShorthandCompressor()

    # Define input source
    if args.files:
        # Process list of files
        import fileinput
        input_source = fileinput.input(files=args.files)
    else:
        # Process stdin
        if sys.stdin.isatty():
            print("Usage: cat huge_log.txt | python3 stream_compress.py")
            sys.exit(1)
        input_source = sys.stdin

    # Run the stream processor
    try:
        for dense_block in compressor.stream_compress(input_source, args.chunk, args.overlap):
            print(dense_block)
            print("---") # Visual separator between chunks
            sys.stdout.flush() # Ensure immediate output for piping
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
