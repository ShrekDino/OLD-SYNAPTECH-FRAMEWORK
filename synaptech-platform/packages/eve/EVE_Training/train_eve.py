import os
# This tells the GPU to manage memory segments more efficiently
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from unsloth import FastLanguageModel, is_bfloat16_supported
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import torch
import sys
from pathlib import Path

# 1. Configuration for OLMo-3-Think (Squeezed for 8GB VRAM)
sys.path.append(str(Path(__file__).parent.parent))
from config import TRAINING_MODEL_NAME, TRAINING_MAX_SEQ_LENGTH as max_seq_length, TRAINING_LORA_RANK as r, TRAINING_LORA_ALPHA as lora_alpha, TRAINING_OUTPUT_DIR, TRAINING_GGUF_OUTPUT

# Note: TRAINING_MODEL_NAME = "olmo-3:7b-think" (local model)
# Unsloth can load local ollama models directly
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = TRAINING_MODEL_NAME,
    max_seq_length = TRAINING_MAX_SEQ_LENGTH,
    load_in_4bit = True,
    device_map = "auto",
)


# 2. Add Reasoning Adapters (Rank reduced to 16 for stability)
model = FastLanguageModel.get_peft_model(
    model,
    r = TRAINING_LORA_RANK,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = TRAINING_LORA_ALPHA,
    lora_dropout = 0,
    bias = "none",
)

# 3. Load the Identity-Aware Dataset
dataset = load_dataset("json", data_files="sami_brain_v1.jsonl", split="train")

# 4. Formatting Function (The "Translator")
def formatting_prompts_func(examples):
    texts = []
    for instruction, input, output in zip(examples["instruction"], examples["input"], examples["output"]):
        text = f"<|user|>\n{instruction} {input}\n<|assistant|>\n{output}"
        texts.append(text)
    return texts

# 5. Training Setup (The "Evolution")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=TRAINING_MAX_SEQ_LENGTH,
    formatting_func=formatting_prompts_func,
    args=TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_steps=60,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=1,
        optim="adamw_8bit",
        output_dir=TRAINING_OUTPUT_DIR
    ),
)
print("Training has started...")
trainer.train()

# Export to GGUF (For Ollama)
model.save_pretrained_gguf(TRAINING_GGUF_OUTPUT, tokenizer, quantization_method="q4_k_m")
print(f"E.V.E. has evolved. Check your folder for '{TRAINING_GGUF_OUTPUT}' files.")
