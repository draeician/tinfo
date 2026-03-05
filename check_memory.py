import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PASSWORD", "")

def print_memory():
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    
    query = """
    MATCH (n) 
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    
    with driver.session() as session:
        result = session.run(query)
        seen_nodes = set()
        
        print("\n=== 🧠 FRIDAY'S KNOWLEDGE GRAPH ===\n")
        
        for record in result:
            node = record['n']
            rel = record['r']
            target = record['m']
            
            # Print Node Details (Only once per node)
            node_id = node.get('id', 'Unknown')
            if node_id not in seen_nodes:
                print(f"🟢 NODE: [{node.get('type', 'Entity')}] {node_id}")
                # Print all properties neatly
                for k, v in node.items():
                    if k not in ['id', 'type']:
                        print(f"   └── {k}: {v}")
                seen_nodes.add(node_id)
                print("")

            # Print Relationship
            if rel:
                print(f"   🔗 {rel.type} -> {target.get('id')}")

    driver.close()

if __name__ == "__main__":
    print_memory()
