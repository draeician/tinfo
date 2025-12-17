import subprocess
import json
import os

# Path to the recall script we just perfected
RECALL_SCRIPT = os.path.join(os.path.dirname(__file__), "recall.py")

def query_friday_memory(question: str) -> str:
    """
    TOOL: Searches Friday's long-term Knowledge Graph (Neo4j).
    USE WHEN: The user asks about past events, specific details about Friday's identity, 
              relationship history, or complex concepts (e.g. "What is the Living Log Doctrine?").
    """
    try:
        # Run the existing robust script
        result = subprocess.run(
            ["python3", RECALL_SCRIPT, question],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"[MEMORY ERROR]: {result.stderr}"
            
        # If the script prints "--- NO MEMORY FOUND ---", we tell the LLM that.
        output = result.stdout.strip()
        if "--- NO MEMORY FOUND ---" in output:
            return "Memory Search: No relevant records found."
            
        return f"Memory Search Results:\n{output}"
        
    except Exception as e:
        return f"[SYSTEM ERROR]: {str(e)}"

# Example Test
if __name__ == "__main__":
    print(query_friday_memory("Who is Draeician?"))
