import json
import numpy as np
from pathlib import Path

def verify_data():
    training_dir = Path("/home/cinni/PitchDeck/SynapTech_IDRE/data/training")
    results = {"anhedonia_mde": [], "manic": []}
    
    for file in training_dir.glob("*.json"):
        with open(file, "r") as f:
            data = json.load(f)
            phenotype = data["phenotype"]
            results[phenotype].append(data["spike_count"])
            
    for p, counts in results.items():
        print(f"Phenotype: {p}")
        print(f"  Avg spike count: {np.mean(counts):.2f}")
        print(f"  Min/Max: {min(counts)}/{max(counts)}")

if __name__ == "__main__":
    verify_data()
