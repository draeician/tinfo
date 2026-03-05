"""Utility functions for knowledge-graph ingest and query."""

from __future__ import annotations

import json
import re


def clean_json_output(response_text: str) -> str:
    """Strip markdown code fences from LLM JSON output."""
    clean = re.sub(r"```json\s*", "", response_text)
    clean = re.sub(r"```\s*$", "", clean)
    return clean.strip()


def enforce_schema(props: dict | None) -> dict[str, str]:
    """Flatten all property values to strings for Neo4j compatibility."""
    clean: dict[str, str] = {}
    if not props:
        return clean
    for k, v in props.items():
        if isinstance(v, list):
            clean[k] = ", ".join([str(i) for i in v])
        elif isinstance(v, dict):
            clean[k] = json.dumps(v)
        else:
            clean[k] = str(v)
    return clean
