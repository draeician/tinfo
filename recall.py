import sys
import os
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PASSWORD", "")

def extract_keywords(text):
    if re.search(r'\b(i|me|my|myself)\b', text, re.IGNORECASE):
        return "Friday"
    stop_words = {'who', 'what', 'where', 'when', 'is', 'are', 'the', 'a', 'an', 'do', 'does', 'know', 'about'}
    words = text.replace('?', '').replace('.', '').split()
    keywords = [w for w in words if w.lower() not in stop_words]
    if keywords:
        return " ".join(keywords) 
    return text 

def recall(query_text):
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    search_term = extract_keywords(query_text)
    print(f"   (Searching Memory for: '{search_term}')")

    # STRICT SCHEMA QUERY:
    # We now know for a fact that ALL properties are Strings.
    # We can safely use toLower() on everything.
    cypher_query = """
    MATCH (n:Entity)
    WHERE 
        toLower(n.id) CONTAINS toLower($term) 
        OR any(prop in keys(n) WHERE toLower(n[prop]) CONTAINS toLower($term))
    
    OPTIONAL MATCH (n)-[r]-(target)
    
    RETURN n, collect({rel: type(r), target: target.id}) as connections
    LIMIT 5
    """
    
    results = []
    with driver.session() as session:
        records = session.run(cypher_query, term=search_term)
        for record in records:
            node = dict(record['n'])
            connections = record['connections']
            if 'embedding' in node: del node['embedding']
            unique_conns = {c['target']: c for c in connections if c['rel'] is not None}.values()
            node['__connections__'] = list(unique_conns)
            results.append(node)

    driver.close()
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 recall.py 'Who is Draeician?'")
        sys.exit(1)
    
    query = sys.argv[1]
    memories = recall(query)
    
    if memories:
        print(f"\n=== 🧠 MEMORY RETRIEVAL ({len(memories)} Results) ===\n")
        for mem in memories:
            print(f"🟢 [{mem.get('type','Entity')}] {mem.get('id')}")
            for k, v in mem.items():
                if k not in ['id', 'type', '__connections__']:
                    print(f"   └── {k}: {v}")
            if mem.get('__connections__'):
                print("   🔗 CONNECTIONS:")
                for c in mem['__connections__']:
                    print(f"      -> [{c['rel']}] {c['target']}")
            print("")
    else:
        print("\n--- NO MEMORY FOUND ---")
