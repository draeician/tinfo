from unsloth import FastLanguageModel

# 1. Config
adapter_path = "lora_shorthand_adapter"

# 2. Load the trained adapter
print("Loading adapter...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = adapter_path,
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)

# 3. Export to GGUF
# This merges the LoRA into the base model and converts it.
# We use q4_k_m which is the standard balanced quantization (small size, high accuracy).
print("Saving as GGUF (this may take a few minutes)...")
model.save_pretrained_gguf(
    "shorthand_gguf", 
    tokenizer, 
    quantization_method = "q4_k_m"
)
print("Conversion complete! File saved in shorthand_gguf/")
