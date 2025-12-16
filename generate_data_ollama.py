import json
import requests
import sys
import os

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:latest" 
OUTPUT_FILE = "shorthand_dataset.jsonl"

SYSTEM_INSTRUCTION = """
You are a Semantic Compressor. Rewrite the user's text into a highly dense, lossy shorthand.
Rules:
1. Delete all articles (a, an, the) and copulas (is, are, was).
2. Keep all specific entities (IPs, names, ports, error codes).
3. Use symbols: '->' for causes/implies, '&' for and, '!=' for contrast.
4. output format: Raw dense text only. No intro/outro.
"""

def query_ollama(text):
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_INSTRUCTION}\n\nTEXT TO COMPRESS:\n{text}",
        "stream": False,
        "options": {
            "temperature": 0.1, 
            "num_predict": 512
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_dataset(input_source):
    raw_texts = []
    
    if isinstance(input_source, list):
        raw_texts = input_source
    elif isinstance(input_source, str) and os.path.exists(input_source):
        print(f"Reading from {input_source}...")
        with open(input_source, 'r') as f:
            content = f.read()
            # Split by double newlines to treat paragraphs as separate samples
            raw_texts = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
    else:
        print(f"File not found or invalid input: {input_source}")
        return

    print(f"Generating {len(raw_texts)} samples using {MODEL_NAME}...")
    
    with open(OUTPUT_FILE, 'a') as f:
        for i, text in enumerate(raw_texts):
            compressed = query_ollama(text)
            if compressed:
                entry = {
                    "instruction": SYSTEM_INSTRUCTION,
                    "input": text,
                    "output": compressed
                }
                f.write(json.dumps(entry) + "\n")
                print(f"[{i+1}/{len(raw_texts)}] Processed.")
            else:
                print(f"[{i+1}/{len(raw_texts)}] Failed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_dataset(sys.argv[1])
    else:
        print("Usage: python3 generate_data_ollama.py <filename>")
