import json
import requests
import os
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv() 

# 2. Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") 
INPUT_FILE = "ingest-compressed.md"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:latest" 

if not NEO4J_PASSWORD:
    print("ERROR: NEO4J_PASSWORD not found in .env file.")
    exit(1)

# 3. System Prompt (The "Exhaustive" Version)
SYSTEM_PROMPT = """
You are a Forensic Knowledge Graph Extractor. 
Task: Convert the provided DENSE TEXT into a JSON Knowledge Graph.

CRITICAL RULES:
1. **EXTRACT EVERYTHING:** Do not summarize. If the text says "34-26-35, B Cup, athletic", the property MUST be "34-26-35, B Cup, athletic".
2. **Lists are allowed:** If an entity has multiple values, store them as a JSON list.
3. **Capture All Metrics:** Height, measurements, hair, skin, specific rules, and file versions.

Output Schema (Strict JSON):
{
  "nodes": [
    {"id": "UniqueName", "type": "Person|Concept|Trait|Protocol", "props": {"prop_name": "Exact Text Value"}}
  ],
  "edges": [
    {"source": "UniqueName", "target": "UniqueName", "rel": "RELATIONSHIP_TYPE"}
  ]
}
"""

def clean_json_output(response_text):
    # Remove markdown code fences
    clean = re.sub(r'```json\s*', '', response_text)
    clean = re.sub(r'```\s*$', '', clean)
    return clean.strip()

def sanitize_props(props):
    """
    Neo4j fails if you try to store a nested Dictionary as a property.
    This function converts any Dicts or Lists-of-Dicts into JSON Strings.
    """
    clean = {}
    if not props:
        return clean

    for k, v in props.items():
        if isinstance(v, dict):
            # Nested Object -> Stringify
            clean[k] = json.dumps(v)
        elif isinstance(v, list):
            # List of Objects -> Stringify
            if any(isinstance(i, dict) for i in v):
                clean[k] = json.dumps(v)
            else:
                # List of Strings/Ints -> Safe
                clean[k] = v
        else:
            # Primitives -> Safe
            clean[k] = v
    return clean

def extract_graph_json(text_chunk):
    print(f"   > Asking {MODEL_NAME} to extract graph structure...")
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nDENSE TEXT TO PROCESS:\n{text_chunk}",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_ctx": 8192
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_resp = response.json()['response']
        cleaned_resp = clean_json_output(raw_resp)
        data = json.loads(cleaned_resp)
        
        # SAFETY FIX: Ensure props exist and are SANITIZED
        if 'nodes' in data:
            for n in data['nodes']:
                if 'props' not in n or n['props'] is None:
                    n['props'] = {}
                # Apply sanitization
                n['props'] = sanitize_props(n['props'])
                    
        return data
    except Exception as e:
        print(f"   [!] Error querying Ollama/Parsing JSON: {e}")
        return None

def push_to_neo4j(data):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"   [!] Could not connect to Neo4j: {e}")
        return

    # Simple Query (APOC Optional)
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

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        content = f.read()

    graph_data = extract_graph_json(content)
    
    if graph_data:
        push_to_neo4j(graph_data)
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    main()
