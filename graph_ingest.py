import json
import requests
import os
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") 
INPUT_FILE = "ingest-compressed.md"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:latest" 

if not NEO4J_PASSWORD:
    print("ERROR: NEO4J_PASSWORD not found in .env file.")
    exit(1)

# Prompt remains the same, but we handle the output strictly in Python
SYSTEM_PROMPT = """
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

def clean_json_output(response_text):
    clean = re.sub(r'```json\s*', '', response_text)
    clean = re.sub(r'```\s*$', '', clean)
    return clean.strip()

def enforce_schema(props):
    """
    CRITICAL: Flattens all data into simple Strings.
    - Dicts -> JSON String
    - Lists -> Comma-separated String
    - Ints/Floats -> String
    This ensures 100% compatibility with Neo4j text search.
    """
    clean = {}
    if not props:
        return clean

    for k, v in props.items():
        if isinstance(v, list):
            # Flatten List: ["A", "B"] -> "A, B"
            clean[k] = ", ".join([str(i) for i in v])
        elif isinstance(v, dict):
            # Flatten Dict: {"a": 1} -> '{"a": 1}'
            clean[k] = json.dumps(v)
        else:
            # Enforce String for everything else
            clean[k] = str(v)
    return clean

def extract_graph_json(text_chunk):
    print(f"   > Asking {MODEL_NAME} to extract graph structure...")
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nDENSE TEXT TO PROCESS:\n{text_chunk}",
        "stream": False,
        "options": {"temperature": 0.0, "num_ctx": 8192}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_resp = response.json()['response']
        data = json.loads(clean_json_output(raw_resp))
        
        # Apply Schema Enforcement
        if 'nodes' in data:
            for n in data['nodes']:
                if 'props' not in n or n['props'] is None:
                    n['props'] = {}
                n['props'] = enforce_schema(n['props'])
                    
        return data
    except Exception as e:
        print(f"   [!] Error: {e}")
        return None

def push_to_neo4j(data):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"   [!] Could not connect to Neo4j: {e}")
        return

    # Simple, safe merge query
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
        session.run(query_nodes, nodes=data.get('nodes', []))
        print(f"   > Merging {len(data.get('edges', []))} Relationships...")
        session.run(query_edges, edges=data.get('edges', []))
    
    driver.close()
    print("   > Database update complete.")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return
    with open(INPUT_FILE, 'r') as f:
        content = f.read()
    graph_data = extract_graph_json(content)
    if graph_data:
        push_to_neo4j(graph_data)

if __name__ == "__main__":
    main()
