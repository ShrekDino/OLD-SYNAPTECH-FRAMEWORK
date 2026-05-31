# ==============================================================================
# CENTRAL CONFIGURATION FOR EVE PROJECT
# All hardcoded paths, model names, and taxonomy roots are defined here.
# Scripts should import from this file: `from config import *`
# ==============================================================================

import os

# --- CORE PATHS ---
# Primary Knowledge Vault Location
VAULT_ROOT = "/home/cinni/Documents/KB/Sami's KB"
VAULT_PATH = VAULT_ROOT  # Alias for training scripts

# Sub-directories
INBOX_DIR = os.path.join(VAULT_ROOT, "00_Inbox")
BACKUP_DIR = os.path.join(VAULT_ROOT, "99_System/Original_Backups")  # For processed originals
BACKUP_ROOT = "/home/cinni/Documents/KB/Vault_Backups"  # For full vault backups

# --- AI MODELS (OLLAMA) ---
# High-Authority Writer (DeepSeek-R1) - Updated to local model
WRITER_MODEL = "huihui_ai/deepseek-r1-abliterated:8b-0528-qwen3"

# Librarian / Logic Models (Gemma 4) - Updated to local model (26B, more capable)
LIBRARIAN_MODEL = "gemma4:26b"
LOGIC_MODEL = LIBRARIAN_MODEL  # Alias used in organizerandwriter.py
MODEL_NAME = LIBRARIAN_MODEL  # Alias used in import_organizer.py

# Vision Model - Needs to be pulled: ollama pull llama3.2-vision:latest
VISION_MODEL = "llama3.2-vision:latest"

# Flash / Sorter Models - Updated to local models
SORTER_MODEL = "qwen3.5:4b-q8_0"  # Fast 4B model
FLASH_MODEL = "gemma4:e4b"  # Alias for fast tasks

# --- TAXONOMY ---
TAXONOMY_ROOTS = [
    "Applied Sciences",
    "Formal Sciences",
    "Humanities",
    "Natural Sciences",
    "Social Sciences"
]

# --- TRAINING SPECIFICS ---
# Dataset generation
TRAINING_DATA_OUTPUT = "sami_brain_v1.jsonl"

# Unsloth / Training Params - Updated to local model
TRAINING_MODEL_NAME = "olmo-3:7b-think"  # Local model (4.5 GB)
TRAINING_MAX_SEQ_LENGTH = 512
TRAINING_LORA_RANK = 16
TRAINING_LORA_ALPHA = 16
TRAINING_OUTPUT_DIR = "outputs"
TRAINING_GGUF_OUTPUT = "eve_v1"
