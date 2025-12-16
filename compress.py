import os
import sys
import contextlib

# 1. Silence Stdout/Stderr during heavy imports
# Unsloth is very chatty; this blocks the banner from ruining piped output
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
    import torch
    from unsloth import FastLanguageModel

# 2. Configuration
adapter_path = "lora_shorthand_adapter"

# 3. Load Model (Silently)
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = adapter_path,
        max_seq_length = 2048,
        dtype = None,
        load_in_4bit = True,
    )
    FastLanguageModel.for_inference(model)

# 4. Prompt Template
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
You are a Semantic Compressor. Rewrite the user's text into a highly dense, lossy shorthand.
Rules:
1. Delete all articles (a, an, the) and copulas (is, are, was).
2. Keep all specific entities (IPs, names, ports, error codes).
3. Use symbols: '->' for causes/implies, '&' for and, '!=' for contrast.
4. output format: Raw dense text only. No intro/outro.

### Input:
{}

### Response:
"""

def compress_text(text):
    inputs = tokenizer(
        [alpaca_prompt.format(text)], return_tensors = "pt"
    ).to("cuda")

    outputs = model.generate(
        **inputs, 
        max_new_tokens = 512, 
        use_cache = True,
        pad_token_id = tokenizer.eos_token_id
    )
    
    result = tokenizer.batch_decode(outputs[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return result[0].strip()

if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()
    elif len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_text = f.read()
    else:
        # Fallback if no input provided
        sys.exit(1)

    # Print ONLY the result
    print(compress_text(input_text))
