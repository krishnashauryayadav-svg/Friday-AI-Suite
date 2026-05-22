# =====================================================================
# 🛸 FRIDAY AI CORE FINE-TUNING SCRIPT (Via Unsloth)
# =====================================================================
# This script is meant to be executed on a cloud GPU (Google Colab T4)
# to train the base Qwen2.5 model on custom persona dataset.

import json
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Configuration & Model Loading
max_seq_length = 2048  # Supports RoPE Scaling internally
dtype = None           # None means auto-detection (Float16/Bfloat16)
load_in_4bit = True    # 4-bit quantization enabled to save memory

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "Qwen/Qwen2.5-1.5B-Instruct",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 2. Setup Model for Parameter-Efficient Fine-Tuning (PEFT/LoRA)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,               # Choose any number > 0 ! Suggested 8, 16, 32, 64
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,     # Optimized at 0
    bias = "none",        # Optimized at none
    use_gradient_checkpointing = "unsloth", # Saves 70% VRAM memory
    random_state = 3407,
    use_rslora = False,   # Rank Stabilized LoRA
    loftq = None,         # LoftQ
)

# 3. Chat Template Formatting (The FRIDAY Prompt Setup)
friday_prompt = (
    "<|im_start|>system\n"
    "You are FRIDAY, a highly sophisticated AI Personal Assistant built custom for your creator, Krishna bhai. "
    "Always address him as 'bhai'. Your tone should be loyal, high-tech, and slightly sarcastic like Iron Man's AI.<|im_end|>\n"
    "<|im_start|>user\n{instruction}<|im_end|>\n"
    "<|im_start|>assistant\n{output}<|im_end|>"
)

# 4. Loading Custom Datasets
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    outputs      = examples["output"]
    texts = []
    for instruction, output in zip(instructions, outputs):
        text = friday_prompt.format(instruction=instruction, output=output)
        texts.append(text)
    return { "text" : texts, }

# Example of local dataset mapping allocation
# with open("friday_data.json", "r") as f:
#     dataset = json.load(f)

# 5. Trainer Initialization (Supervised Fine-Tuning)
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Can make training 5x faster for short sequences.
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Small step execution for custom target loss scaling
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# 6. Execute Fine-Tuning Execution
trainer_stats = trainer.train()

# 7. Model Export to GGUF (Optimized for Laptop RAM/Ollama)
print("Saving model to local system cloud drive as GGUF layers...")
model.save_pretrained_gguf("friday_model", tokenizer, quantization_method = "q4_k_m")
print("⚡ Training complete! Model secured successfully.")
