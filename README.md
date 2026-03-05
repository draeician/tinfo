[![CI](https://github.com/draeician/tinfo/actions/workflows/ci.yml/badge.svg)](https://github.com/draeician/tinfo/actions/workflows/ci.yml)

# Shorthand LLM

Semantic compression (dense, lossy text) and an optional Neo4j memory pipeline (compress → extract KG → ingest → recall).

## Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
# Compress text via Ollama
cat logs.txt | shorthand-compress

# Query the knowledge graph
shorthand-recall "Who is Draeician?"

# Ingest compressed text into Neo4j
shorthand-ingest --input ingest-compressed.md

# Dump the full graph
shorthand-memory

# Version
python3 -m shorthand_llm --version
```

## Docs

- **[SOP.md](SOP.md)** — Quickstarts, entrypoints, and troubleshooting.
- **[README_compression_engine.md](README_compression_engine.md)** — Dataset, training, merge, GGUF, Ollama.

## Training Stack (GPU only)

```bash
pip install torch torchvision torchaudio
pip install xformers
pip install unsloth
```

See [README_compression_engine.md](README_compression_engine.md) for full training instructions.

## Tests

```bash
pytest                          # unit tests only
pytest -m integration           # include Ollama/Neo4j tests
ruff check src/ tests/          # lint
```
