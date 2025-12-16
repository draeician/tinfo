import json
import requests
import os
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv() # Reads .env file in current directory

# 2. Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") # Must be in .env
INPUT_FILE = "ingest-compressed.md"

# We use Ministral-3-14b for its high logic capability without the "<think>" parsing overhead
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "ministral-3:14b" 

if not NEO4J_PASSWORD:
    print("ERROR: NEO4J_PASSWORD not found in .env file.")
    exit(1)

# 3. System Prompt
# Explicitly teaching it the Shorthand -> Graph logic
SYSTEM_PROMPT = """
You are a Knowledge Graph Extractor. 
Task: Convert the provided DENSE TEXT into a JSON Knowledge Graph.

Shorthand Rules:
- "A -> B" means A implies, causes, or has property B.
- "A: B" means A has attribute B.
- "F" usually refers to "Friday Vale".
- "Draeician" is the User/Partner.

Output Schema (Strict JSON):
{
  "nodes": [
    {"id": "UniqueName", "type": "Person|Concept|Trait|Protocol", "props": {"prop_name": "value"}}
  ],
  "edges": [
    {"source": "UniqueName", "target": "UniqueName", "rel": "RELATIONSHIP_TYPE"}
  ]
}
Do not include markdown blocks (```json). Just the raw JSON string.
"""

def clean_json_output(response_text):
    """
    sometimes LLMs wrap output in markdown code blocks. This cleans it.
    """
    # Remove markdown code fences
    clean = re.sub(r'```json\s*', '', response_text)
    clean = re.sub(r'```\s*$', '', clean)
    return clean.strip()

def extract_graph_json(text_chunk):
    print(f"   > Asking {MODEL_NAME} to extract graph structure...")
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nDENSE TEXT TO PROCESS:\n{text_chunk}",
        "stream": False,
        "options": {
            "temperature": 0.0, # Deterministic
            "num_ctx": 8192     # Ministral can handle larger context
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_resp = response.json()['response']
        cleaned_resp = clean_json_output(raw_resp)
        return json.loads(cleaned_resp)
    except json.JSONDecodeError:
        print("   [!] Error: Model did not return valid JSON. Saving raw output to debug.log")
        with open("debug_raw.log", "w") as f:
            f.write(raw_resp)
        return None
    except Exception as e:
        print(f"   [!] Error querying Ollama: {e}")
        return None

def push_to_neo4j(data):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"   [!] Could not connect to Neo4j: {e}")
        return

    # Cypher Queries
    query_nodes = """
    UNWIND $nodes AS n
    MERGE (e:Entity {id: n.id})
    SET e.type = n.type
    SET e += n.props
    # Add a secondary label dynamically if possible, strictly we just use Entity + Property for now
    WITH e, n
    CALL apoc.create.addLabels(e, [n.type]) YIELD node
    RETURN count(node)
    """
    
    query_edges = """
    UNWIND $edges AS r
    MATCH (s:Entity {id: r.source})
    MATCH (t:Entity {id: r.target})
    MERGE (s)-[rel:RELATIONSHIP {type: r.rel}]->(t)
    """

    with driver.session() as session:
        print(f"   > Merging {len(data.get('nodes', []))} Nodes...")
        # Note: 'apoc' is a plugin. If you don't have APOC, we can simplify the label logic.
        # Simple fallback query if APOC is missing:
        simple_node_query = """
        UNWIND $nodes AS n
        MERGE (e:Entity {id: n.id})
        SET e.type = n.type
        SET e += n.props
        """
        try:
            session.run(query_nodes, nodes=data.get('nodes', []))
        except Exception:
            print("     (APOC not detected, using simple node merge)")
            session.run(simple_node_query, nodes=data.get('nodes', []))

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

    # Process
    graph_data = extract_graph_json(content)
    
    if graph_data:
        # Backup
        with open("graph_dump.json", "w") as f:
            json.dump(graph_data, f, indent=2)
        
        # Push
        push_to_neo4j(graph_data)
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    main()
