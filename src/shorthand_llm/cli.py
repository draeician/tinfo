"""CLI entrypoints for shorthand-llm."""

from __future__ import annotations

import argparse
import sys

from shorthand_llm import __version__


def compress_main():
    """Stream compression via Ollama shorthand model."""
    from shorthand_llm.compressor import ShorthandCompressor

    parser = argparse.ArgumentParser(description="Stream Compressor using Local Shorthand Model")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("files", nargs="*", help="Files to compress (reads stdin if empty)")
    parser.add_argument("--chunk", type=int, default=6000, help="Chunk size in characters (default: 6000)")
    parser.add_argument("--overlap", type=int, default=500, help="Overlap size in characters (default: 500)")
    args = parser.parse_args()

    compressor = ShorthandCompressor()

    if args.files:
        import fileinput

        input_source = fileinput.input(files=args.files)
    else:
        if sys.stdin.isatty():
            parser.print_usage()
            sys.exit(1)
        input_source = sys.stdin

    try:
        for dense_block in compressor.stream_compress(input_source, args.chunk, args.overlap):
            print(dense_block)
            print("---")
            sys.stdout.flush()
    except KeyboardInterrupt:
        sys.exit(0)


def recall_main():
    """Query Neo4j knowledge graph."""
    import os
    import re

    from dotenv import load_dotenv
    from neo4j import GraphDatabase

    load_dotenv()

    parser = argparse.ArgumentParser(description="Query the Shorthand knowledge graph")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("query", help="Natural language query")
    args = parser.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "")

    def extract_keywords(text: str) -> str:
        if re.search(r"\b(i|me|my|myself)\b", text, re.IGNORECASE):
            return "Friday"
        stop_words = {"who", "what", "where", "when", "is", "are", "the", "a", "an", "do", "does", "know", "about"}
        words = text.replace("?", "").replace(".", "").split()
        keywords = [w for w in words if w.lower() not in stop_words]
        return " ".join(keywords) if keywords else text

    search_term = extract_keywords(args.query)
    print(f"   (Searching Memory for: '{search_term}')")

    cypher_query = """
    MATCH (n:Entity)
    WHERE
        toLower(n.id) CONTAINS toLower($term)
        OR any(prop in keys(n) WHERE toLower(n[prop]) CONTAINS toLower($term))
    OPTIONAL MATCH (n)-[r]-(target)
    RETURN n, collect({rel: type(r), target: target.id}) as connections
    LIMIT 5
    """

    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    results = []
    with driver.session() as session:
        records = session.run(cypher_query, term=search_term)
        for record in records:
            node = dict(record["n"])
            connections = record["connections"]
            if "embedding" in node:
                del node["embedding"]
            unique_conns = {c["target"]: c for c in connections if c["rel"] is not None}.values()
            node["__connections__"] = list(unique_conns)
            results.append(node)
    driver.close()

    if results:
        print(f"\n=== MEMORY RETRIEVAL ({len(results)} Results) ===\n")
        for mem in results:
            print(f"[{mem.get('type', 'Entity')}] {mem.get('id')}")
            for k, v in mem.items():
                if k not in ["id", "type", "__connections__"]:
                    print(f"   +-- {k}: {v}")
            if mem.get("__connections__"):
                print("   CONNECTIONS:")
                for c in mem["__connections__"]:
                    print(f"      -> [{c['rel']}] {c['target']}")
            print("")
    else:
        print("\n--- NO MEMORY FOUND ---")


def ingest_main():
    """Ingest compressed text into Neo4j knowledge graph."""
    import json
    import os
    import re

    import requests
    from dotenv import load_dotenv
    from neo4j import GraphDatabase

    load_dotenv()

    parser = argparse.ArgumentParser(description="Ingest compressed text into Neo4j KG")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--input", default="ingest-compressed.md", help="Input file (default: ingest-compressed.md)")
    args = parser.parse_args()

    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    ollama_url = "http://localhost:11434/api/generate"
    model_name = "qwen2.5-coder:latest"

    if not neo4j_password:
        print("ERROR: NEO4J_PASSWORD not found in .env file.")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"File {args.input} not found.")
        sys.exit(1)

    system_prompt = """
You are a Forensic Knowledge Graph Extractor.
Task: Convert the provided DENSE TEXT into a JSON Knowledge Graph.

CRITICAL RULES:
1. **EXTRACT EVERYTHING:** Do not summarize.
2. **Capture All Metrics:** Height, measurements, hair, skin.
3. **Lists:** If an entity has multiple values, you may return them as a list.

Output Schema:
{
  "nodes": [
    {"id": "UniqueName", "type": "Person|Concept|Trait|Protocol", "props": {"prop_name": "Value"}}
  ],
  "edges": [
    {"source": "UniqueName", "target": "UniqueName", "rel": "RELATIONSHIP_TYPE"}
  ]
}
"""

    def clean_json_output(response_text: str) -> str:
        clean = re.sub(r"```json\s*", "", response_text)
        clean = re.sub(r"```\s*$", "", clean)
        return clean.strip()

    def enforce_schema(props: dict | None) -> dict:
        clean = {}
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

    with open(args.input) as f:
        content = f.read()

    print(f"   > Asking {model_name} to extract graph structure...")
    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n\nDENSE TEXT TO PROCESS:\n{content}",
        "stream": False,
        "options": {"temperature": 0.0, "num_ctx": 8192},
    }

    try:
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()
        raw_resp = response.json()["response"]
        data = json.loads(clean_json_output(raw_resp))

        if "nodes" in data:
            for n in data["nodes"]:
                if "props" not in n or n["props"] is None:
                    n["props"] = {}
                n["props"] = enforce_schema(n["props"])
    except Exception as e:
        print(f"   [!] Error: {e}")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        driver.verify_connectivity()
    except Exception as e:
        print(f"   [!] Could not connect to Neo4j: {e}")
        sys.exit(1)

    query_nodes = """
    UNWIND $nodes AS n
    MERGE (e:Entity {id: n.id})
    SET e.type = n.type
    SET e += n.props
    """
    query_edges = """
    UNWIND $edges AS r
    MATCH (s:Entity {id: r.source})
    MATCH (t:Entity {id: r.target})
    MERGE (s)-[rel:RELATIONSHIP {type: r.rel}]->(t)
    """

    with driver.session() as session:
        print(f"   > Merging {len(data.get('nodes', []))} Nodes...")
        session.run(query_nodes, nodes=data.get("nodes", []))
        print(f"   > Merging {len(data.get('edges', []))} Relationships...")
        session.run(query_edges, edges=data.get("edges", []))
    driver.close()
    print("   > Database update complete.")


def memory_main():
    """Dump full Neo4j knowledge graph."""
    import os

    from dotenv import load_dotenv
    from neo4j import GraphDatabase

    load_dotenv()

    parser = argparse.ArgumentParser(description="Dump the full Shorthand knowledge graph")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "")

    driver = GraphDatabase.driver(uri, auth=(user, pwd))

    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    with driver.session() as session:
        result = session.run(query)
        seen_nodes: set[str] = set()

        print("\n=== KNOWLEDGE GRAPH ===\n")

        for record in result:
            node = record["n"]
            rel = record["r"]
            target = record["m"]

            node_id = node.get("id", "Unknown")
            if node_id not in seen_nodes:
                print(f"NODE: [{node.get('type', 'Entity')}] {node_id}")
                for k, v in node.items():
                    if k not in ["id", "type"]:
                        print(f"   +-- {k}: {v}")
                seen_nodes.add(node_id)
                print("")

            if rel:
                print(f"   -> {rel.type} -> {target.get('id')}")

    driver.close()
