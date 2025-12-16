
# Semantic Compression Engine: From Zero to Deployment

**Project:** Aether / Local LLM Utility
**Goal:** Create a "Shorthand" dialect model that compresses text by 50-70% (removing articles/grammar, retaining facts) to save context tokens.
**Method:** Supervised Fine-Tuning (SFT) using QLoRA on Llama-3, converted to GGUF for use in Ollama.

-----

## 1\. Prerequisites & Environment

We used a split-GPU setup (RTX 3060 + RTX 4060 Ti) and `unsloth` for efficient training.

**Hardware:**

  * **Training GPU:** RTX 4060 Ti (16GB) - Assigned ID `1`
  * **Inference/Data Gen:** Local Ollama instance (CPU or GPU)

**Software Stack:**

  * Linux Mint
  * Python 3.12 (venv)
  * Unsloth (Training)
  * Llama.cpp (Conversion)
  * Ollama (Hosting)

### Setup Command

```bash
mkdir -p ~/projects/shorthand_llm
cd ~/projects/shorthand_llm
python3 -m venv venv
source venv/bin/activate

# Install Unsloth and Training Tools
pip install --upgrade pip
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
```

-----

## 2\. Dataset Generation (Synthetic)

Since no "shorthand" dataset existed, we created one by asking Llama-3 to "compress" raw text.

**Script:** `generate_data_ollama.py`
**Input:** Raw text file (e.g., generic logs or RFC documents).
**Output:** `shorthand_dataset.jsonl` (Training pairs).

```python
# Key System Prompt used for generation:
"""
You are a Semantic Compressor. Rewrite the user's text into a highly dense, lossy shorthand.
Rules:
1. Delete all articles (a, an, the) and copulas (is, are, was).
2. Keep all specific entities (IPs, names, ports, error codes).
3. Use symbols: '->' for causes/implies, '&' for and, '!=' for contrast.
4. output format: Raw dense text only. No intro/outro.
"""
```

**Execution:**

```bash
# We used a generic tech text file (RFC 2616) as source material
curl https://www.ietf.org/rfc/rfc2616.txt > training_data.txt
python3 generate_data_ollama.py training_data.txt
```

-----

## 3\. Training (QLoRA)

We fine-tuned `unsloth/llama-3-8b-Instruct-bnb-4bit` using the generated dataset.

**Script:** `train_shorthand.py`
**Configuration:**

  * **Rank (r):** 16
  * **Target Modules:** All linear layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, etc.)
  * **Max Steps:** 60 (for proof of concept) / 500 (for full convergence)
  * **GPU Isolation:** Forced to GPU 1 to prevent Unsloth multi-gpu crash.

**Execution:**

```bash
CUDA_VISIBLE_DEVICES=1 python3 train_shorthand.py
```

*Result:* A LoRA adapter saved in `./lora_shorthand_adapter`.

-----

## 4\. Merging & GGUF Conversion

To run this in Ollama, we merged the adapter into the base model and quantized it.

### Step A: Merge

We loaded the adapter and saved the full FP16 model to disk.
*Script:* `save_merged.py`

```bash
CUDA_VISIBLE_DEVICES=1 python3 save_merged.py
# Output: ./merged_shorthand_model
```

### Step B: Build Tools (llama.cpp)

We compiled the quantization tools from source.

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release -j8 --target llama-quantize
```

### Step C: Convert & Quantize

1.  **Convert to GGUF (FP16):**
    ```bash
    python3 convert_hf_to_gguf.py ../merged_shorthand_model --outfile ../shorthand_f16.gguf
    ```
2.  **Quantize to Q4\_K\_M (Compact):**
    ```bash
    ./build/bin/llama-quantize ../shorthand_f16.gguf ../shorthand_q4km.gguf Q4_K_M
    ```

-----

## 5\. Deployment (Ollama)

We created a custom Ollama model entry with the system prompt baked in.

**Modelfile:**

```dockerfile
FROM ./shorthand_q4km.gguf
PARAMETER temperature 0.1
PARAMETER stop "Input:"
PARAMETER stop "###"
SYSTEM """
You are a Semantic Compressor. Rewrite the user's text into a highly dense, lossy shorthand.
Rules:
1. Delete all articles (a, an, the) and copulas (is, are, was).
2. Keep all specific entities (IPs, names, ports, error codes).
3. Use symbols: '->' for causes/implies, '&' for and, '!=' for contrast.
4. output format: Raw dense text only. No intro/outro.
"""
```

**Import Command:**

```bash
ollama create shorthand -f Modelfile
```

-----

## 6\. Usage: The `densify` Utility

We created a CLI wrapper to allow piping text directly into the compressor.

**Script:** `~/.local/bin/densify`

```bash
#!/bin/bash
# Usage: echo "text" | densify
if [ -p /dev/stdin ]; then INPUT="$(cat)"; else INPUT="$*"; fi
if [ -z "$INPUT" ]; then echo "Usage: densify 'text'"; exit 1; fi

jq -n --arg p "$INPUT" '{model: "shorthand", prompt: $p, stream: false, options: {temperature: 0.1}}' | \
curl -s -d @- http://localhost:11434/api/generate | jq -r .response
```

**Example Output:**

```bash
$ densify "The server 'virindi' failed to boot because the kernel panic occurred at address 0x0001."
virindi -> boot failed & cause:kernel panic @ 0x0001
```

### **Conclusion**

We successfully built a **Context Compression Engine**.

  * **Reduction:** \~60% token savings on verbose logs.
  * **Latency:** Near-instant via Ollama.
  * **Privacy:** Fully local.

This tool is now ready for integration into the **Aether** OS pipeline for long-term memory ingestion.
