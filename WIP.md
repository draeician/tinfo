projects/shorthand_llm

# Run this via python or just copy-paste into a temporary script
python -c '
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PWD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(URI, auth=(USER, PWD))
with driver.session() as s:
    s.run("MATCH (n) DETACH DELETE n")
print("💥 Database wiped.")
'

python graph_ingest.py

python check_memory.py

python recall.py "What do I look like?"


# web interface for the neo4j
http://nomnom:7474/browser/

