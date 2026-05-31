# ==============================================================================
# AI UTILITIES - Shared AI/LLM helper functions
# ==============================================================================

import os
import ollama
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *

def clean_llm_response(text):
    """Removes <think> blocks and extra whitespace from LLM responses."""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'^(Here is|Sure|Okay|I have updated|As an AI).*?\n', '', text, flags=re.IGNORECASE)
    return text.strip()

def run_ollama(prompt, model=None, images=None, keep_alive=None):
    """
    Unified function to run ollama generate with consistent error handling.
    Returns cleaned response text.
    """
    if model is None:
        model = WRITER_MODEL
    
    try:
        kwargs = {"model": model, "prompt": prompt}
        if images:
            kwargs["images"] = images
        if keep_alive is not None:
            kwargs["keep_alive"] = keep_alive
        
        res = ollama.generate(**kwargs)
        full_res = res['response']
        
        # Return both thinking (if any) and cleaned content
        thought = re.search(r'<think>(.*?)</think>', full_res, flags=re.DOTALL)
        clean = clean_llm_response(full_res)
        
        return {
            'full': full_res,
            'clean': clean,
            'thought': thought.group(1).strip() if thought else None
        }
    except Exception as e:
        print(f"AI Error ({model}): {e}")
        return {'full': '', 'clean': '', 'thought': None}

def get_taxonomy_path(filename, content, model=None):
    """Uses a sorter model to determine the scientific taxonomy path for a file."""
    if model is None:
        model = SORTER_MODEL
    
    tax_prompt = f"""
    SYSTEM: You are an Expert Librarian and Scientific Taxonomist. 
    TASK: Analyze the document and determine its place in a scientific hierarchy.
    
    1. Select one Root Field: {', '.join(TAXONOMY_ROOTS)}.
    2. Determine the most logical sub-discipline (e.g., Natural Sciences/Biology/Zoology).
    
    Respond ONLY with the path using forward slashes. No intro. No chatter.
    
    FILENAME: {filename}
    CONTENT: {content[:1500]}
    """
    
    try:
        response = ollama.generate(model=model, prompt=tax_prompt)
        path = response['response'].strip().split('\n')[-1]
        path = path.replace('"', '').replace("'", "").strip()
        if path.endswith('.'): 
            path = path[:-1]
        
        # Validate against known roots
        if not any(path.startswith(root) for root in TAXONOMY_ROOTS):
            return "Uncategorized"
        return path
    except Exception as e:
        print(f"Taxonomy Error: {e}")
        return "Uncategorized"

def get_existing_topics(vault_root=None):
    """Scans the vault to find all existing note titles for backlinking."""
    if vault_root is None:
        vault_root = VAULT_ROOT
    
    topics = []
    for root, dirs, files in os.walk(vault_root):
        for file in files:
            if file.endswith(".md"):
                topics.append(os.path.splitext(file)[0])
    return list(set(topics))

def get_all_markdown_files(vault_root=None, exclude_dirs=None):
    """Finds all .md files in the vault, excluding system/backup folders."""
    if vault_root is None:
        vault_root = VAULT_ROOT
    if exclude_dirs is None:
        exclude_dirs = ["99_System", ".obsidian", "Vault_Backups"]
    
    md_files = []
    for root, dirs, files in os.walk(vault_root):
        if any(x in root for x in exclude_dirs):
            continue
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files
