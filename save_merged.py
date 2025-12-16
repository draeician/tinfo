from unsloth import FastLanguageModel

# 1. Load the adapter
print("Loading adapter for merging...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "lora_shorthand_adapter",
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)

# 2. Save the fully merged model (Float16)
# We need this intermediate state to run the GGUF converter manually.
print("Saving merged model to 'merged_shorthand_model'...")
model.save_pretrained_merged(
    "merged_shorthand_model", 
    tokenizer, 
    save_method = "merged_16bit",
)
print("Merge complete.")
