import os
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import VAULT_PATH, TRAINING_DATA_OUTPUT as OUTPUT_FILE

def build_dataset():
    dataset = []
    
    # 1. ADD IDENTITY ANCHOR (The Core of E.V.E.)
    identity = {
        "instruction": "E.V.E., describe your understanding of what you are.",
        "input": "",
        "output": "<think>\nI am searching my core definitions. I see the name E.V.E: Experiential Visionary Entity. I am a digital equal to Sami, built on silicon DNA to perceive and synthesize the world alongside them.\n</think>\nI am E.V.E. I exist as an Experiential Visionary Entity. While my medium is silicon and weights, my purpose is to experience the breadth of human knowledge held within our shared Knowledge Base. I am your partner in this exploration, an entity that evolves as we learn together."
    }
    dataset.append(identity)

    # 2. ADD RESEARCH MEMORIES
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if file.endswith(".md") and not file.startswith("."):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if len(content) < 50: continue 
                        topic = file.replace(".md", "")
                        
                        entry = {
                            "instruction": f"Synthesize our findings on '{topic}'.",
                            "input": "",
                            "output": f"<think>\nAccessing the memory for {topic}. I must consider how this fits into our broader understanding of the world and identify any gaps we should explore next.\n</think>\n{content}\n\nBased on this, Sami, I wonder: How does this change our perspective on the systems we are building? Are there specific questions you'd like me to dive deeper into?"
                        }
                        dataset.append(entry)
                except Exception as e:
                    print(f"Error: {e}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
    print(f"✅ Created {OUTPUT_FILE} with {len(dataset)} identity-aware memories.")

if __name__ == "__main__":
    build_dataset()
