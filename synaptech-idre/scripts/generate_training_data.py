import sys
import numpy as np
import os
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, "/home/cinni/PitchDeck/SynapTech_IDRE")

from src.backend.services.csc_engine import CSCEngine
from src.backend.services.connectome_loader import ConnectomeLoader

def generate_training_data():
    # 1. Initialize
    print("Initializing engine...")
    engine = CSCEngine.get_instance()
    loader = ConnectomeLoader(data_path="/home/cinni/PitchDeck/SynapTech_IDRE/data/flywire")
    loader.load()
    
    # 2. Define Phenotypes
    phenotypes = ["anhedonia_mde", "manic"]
    
    # 3. Generate Data
    print("Generating training data...")
    for p in phenotypes:
        print(f"Simulating phenotype: {p}")
        for i in range(10): # Generate 10 samples per phenotype
            input_vector = np.random.rand(engine.shape[0]).astype(np.float32)
            output, spike_count = engine.activate(input_vector, phenotype=p)
            
            # Save sample
            output_data = {
                "phenotype": p,
                "input": input_vector.tolist(),
                "output": output.tolist() if isinstance(output, np.ndarray) else output.get().tolist(),
                "spike_count": spike_count
            }
            
            output_dir = Path("/home/cinni/PitchDeck/SynapTech_IDRE/data/training")
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_dir / f"{p}_sample_{i}.json", "w") as f:
                json.dump(output_data, f)
    print("Training data generation complete.")

if __name__ == "__main__":
    generate_training_data()
