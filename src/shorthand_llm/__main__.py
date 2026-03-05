"""Allow running as `python3 -m shorthand_llm`."""

import argparse
import sys

from shorthand_llm import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="shorthand_llm",
        description="Shorthand LLM — semantic compression engine and Neo4j memory pipeline",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("compress", help="Stream-compress text via Ollama")
    sub.add_parser("recall", help="Query the Neo4j knowledge graph")
    sub.add_parser("ingest", help="Ingest compressed text into Neo4j")
    sub.add_parser("memory", help="Dump the full knowledge graph")

    args, remaining = parser.parse_known_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    sys.argv = [f"shorthand_llm {args.command}"] + remaining

    from shorthand_llm import cli

    commands = {
        "compress": cli.compress_main,
        "recall": cli.recall_main,
        "ingest": cli.ingest_main,
        "memory": cli.memory_main,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
