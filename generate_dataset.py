import json
import os
from unsloth import FastLanguageModel

# 1. Configuration
output_file = "shorthand_dataset.jsonl"
num_samples = 50  # Start small to test, scale to 500+ for real training
model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit"

# 2. The "Shorthand" Prompt Logic
# This prompt teaches the model the behavior we want to bake in.
system_prompt = """
You are a Semantic Compressor. Your goal is to minimize token usage while preserving 100% of the entities, logic, and facts.
Rules:
1. Remove articles (a, an, the) and copulas (is, are, was).
2. Use symbols for logic (-> for implies, & for and, != for distinct).
3. Drop polite fillers.
4. Output Format: DENSE_TEXT
"""

# 3. Sample Inputs (In reality, load these from a file like a book or logs)
raw_texts = [
    "The CPU usage on the server named 'virindi' spiked to 99% at 3:00 PM due to a runaway python process.",
    "Friday Vale is a digital persona who acts as a familiar. She specializes in Python and system administration.",
    # ... You would load a large text file and chunk it here ...
]

# For this script, we'll just mock the generation loop to show structure
print(f"Loading {model_name} for data generation...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    load_in_4bit = True,
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)
FastLanguageModel.for_inference(model)

data_pairs = []

# This loop would normally use the model to generate the 'response'
# relying on the strong system prompt to create the "target" data.
# For the roadmap, we are creating the structure. 
# You will likely use an existing LLM API or this local model to generate these pairs.

# Mock Example of what the model SHOULD produce and save:
example_entry = {
    "instruction": system_prompt,
    "input": "The CPU usage on the server named 'virindi' spiked to 99% at 3:00 PM due to a runaway python process.",
    "output": "CPU usage server:'virindi' -> 99% @ 3:00PM. Cause: runaway python process."
}

# Save to JSONL
with open(output_file, 'w') as f:
    f.write(json.dumps(example_entry) + "\n")

print(f"Dataset structure created at {output_file}")
