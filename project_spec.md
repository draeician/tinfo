# Project Specification

## Status
- [x] Repo evaluation complete (2026-03-04)
- [x] Task pipeline initialized

## Overview

**Project:** Shorthand LLM
**Purpose:** Semantic compression engine that reduces text by ~60% (removing articles, grammar; retaining entities and facts) plus an optional Neo4j knowledge-graph memory pipeline for long-term recall.
**Language:** Python 3.12
**Target OS:** Linux Mint (Debian-based)
**Version:** 0.1.0

## Architecture

### Compression Pipeline

```
Raw Text / Chat Export
        │
        ├── stream_compress.py  (chunked, via Ollama)
        ├── densify              (single-shot bash, via Ollama + jq)
        ├── compress.py          (single-shot, local GPU via Unsloth)
        └── openwebui-chat-compression.py (OpenWebUI JSON → JSONL)
        │
        ▼
   Dense Text (stdout / file)
```

### Memory Pipeline

```
Dense Text
   │
   ▼
graph_ingest.py  (Ollama KG extraction → Neo4j)
   │
   ▼
Neo4j Graph DB
   │
   ├── recall.py         (CLI query)
   ├── check_memory.py   (full graph dump)
   └── memory_tool.py    (Python API wrapper)
```

### Training Pipeline

```
Raw corpus (e.g. RFC docs)
   │
   ▼
generate_data_ollama.py  →  shorthand_dataset.jsonl
   │
   ▼
train_shorthand.py       →  lora_shorthand_adapter/
   │
   ▼
save_merged.py           →  merged_shorthand_model/
   │
   ▼
llama.cpp convert + quantize  →  shorthand_q4km.gguf
   │
   ▼
ollama create shorthand -f Modelfile
```

## File Inventory

### Core Library
| File | Role |
|------|------|
| `shorthand_lib.py` | `ShorthandCompressor` class — entity masking, chunked streaming, Ollama integration |

### Compression Entrypoints
| File | Input | Output |
|------|-------|--------|
| `stream_compress.py` | Stdin or file list | Dense text blocks to stdout |
| `densify` | Stdin or string arg | Single compressed line (bash, needs `jq`) |
| `compress.py` | Stdin or file path | Compressed text (local GPU, Unsloth) |
| `openwebui-chat-compression.py` | OpenWebUI export JSON (stdin) | JSONL (ts, role, compressed) |

### Memory Pipeline
| File | Role |
|------|------|
| `graph_ingest.py` | Extracts KG JSON via Ollama, pushes to Neo4j |
| `recall.py` | CLI query against Neo4j graph |
| `check_memory.py` | Dumps full Neo4j graph to stdout |
| `memory_tool.py` | Python wrapper around `recall.py` for tool use |

### Training / Model Build
| File | Role |
|------|------|
| `generate_data_ollama.py` | Synthetic dataset generation via Ollama |
| `generate_dataset.py` | Dataset generation via local Unsloth model |
| `train_shorthand.py` | QLoRA SFT on Llama-3-8B-Instruct |
| `save_merged.py` | Merge LoRA adapter into base model (FP16) |
| `convert_to_gguf.py` | Export merged model to GGUF via Unsloth |
| `Modelfile` | Ollama model definition (system prompt + GGUF path) |

### Documentation
| File | Role |
|------|------|
| `README.md` | Project overview and quickstart |
| `SOP.md` | Standard operating procedure (all entrypoints, troubleshooting) |
| `README_compression_engine.md` | Full build story (dataset → train → merge → GGUF → Ollama) |

## Dependencies

### Runtime (requirements.txt)
- `requests` — Ollama HTTP API
- `neo4j` — Graph database driver
- `python-dotenv` — `.env` loading

### Training (manual install)
- `unsloth` — Efficient QLoRA fine-tuning
- `torch`, `torchvision`, `torchaudio` — PyTorch (CUDA 12.4)
- `xformers` — Memory-efficient attention
- `trl` — Transformer Reinforcement Learning (SFTTrainer)
- `peft` — Parameter-Efficient Fine-Tuning
- `accelerate` — HuggingFace Accelerate
- `bitsandbytes` — Quantization
- `datasets` — HuggingFace Datasets

### External Services
- **Ollama** at `http://localhost:11434` — hosts the `shorthand` model (compression) and `qwen2.5-coder:latest` (KG extraction)
- **Neo4j** at `bolt://localhost:7687` — knowledge graph storage (configured via `.env`)

## Current State Assessment

### Working
- [x] Compression via Ollama (`stream_compress.py`, `densify`, `shorthand_lib.py`)
- [x] Compression via local GPU (`compress.py`)
- [x] OpenWebUI chat export compression
- [x] Neo4j KG ingest pipeline
- [x] Neo4j recall / memory query
- [x] Training pipeline (dataset gen → QLoRA → merge → GGUF)
- [x] SOP documentation

### Missing / Needs Work
- [ ] No Python package structure (flat scripts, no `pyproject.toml`, no `src/` layout)
- [ ] No `__version__` / `__init__.py`
- [ ] No `--version` flag on any CLI entrypoint
- [ ] No tests
- [ ] No CI/CD (linting, testing)
- [ ] `.gitignore` missing secret-prevention entries per GIT_POLICY (`*.pem`, `*.key`, `credentials.json`)
- [ ] `dense_context.txt`, `graph_dump.json`, `training_data.txt` not gitignored
- [ ] No type hints on most functions
- [ ] `recall.py` and `check_memory.py` have hardcoded fallback password (`password123`)

## Roadmap

| Task | Type | Summary | Status |
|------|------|---------|--------|
| 001 | `chore` | Package structure: `pyproject.toml`, `src/shorthand_llm/` layout, `__init__.py` with `__version__` | wip |
| 002 | `feat` | CLI entrypoints with `--version` flag via `argparse` | wip |
| 003 | `chore` | Harden `.gitignore` and remove hardcoded fallback passwords | wip |
| 004 | `feat` | Add unit tests for `shorthand_lib.py` and pipeline scripts | wip |
| 005 | `chore` | GitHub Actions CI (lint with Ruff, run tests) | wip |
| 006 | `refactor` | Add type hints across all modules | wip |
