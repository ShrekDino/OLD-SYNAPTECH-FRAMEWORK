import torch
import pandas as pd
from torch_geometric.data import Data
from src.backend.services.nfm_model import NFM
from pathlib import Path

# Load synthetic data
csv_path = Path("/home/cinni/PitchDeck/SynapTech_IDRE/data/flywire/connectome.csv")
df = pd.read_csv(csv_path)

# Prepare graph
edge_index = torch.tensor(df[["source", "target"]].values.T, dtype=torch.long)
num_nodes = 130_000
x = torch.randn((num_nodes, 16))

# Model setup
model = NFM(in_channels=16, hidden_channels=32, embedding_dim=16)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

def train_active():
    model.train()
    optimizer.zero_grad()
    
    # 1. Generate node embeddings
    z = model(x, edge_index)
    
    # 2. Sample random edges for uncertainty estimation
    test_edge_index = torch.randint(0, num_nodes, (2, 1000))
    
    # 3. Calculate uncertainty for sampled edges
    uncertainty = model.get_uncertainty(z, test_edge_index)
    
    # 4. Select top-k high-uncertainty edges for active learning
    top_k = 500
    _, top_indices = torch.topk(uncertainty, top_k)
    active_edge_index = test_edge_index[:, top_indices]
    
    # 5. Train on active edges
    pred = model.predict_link(z, active_edge_index)
    # Using 1.0 (existent) as target for active discovery
    loss = -torch.log(pred + 1e-15).mean()
    
    loss.backward()
    optimizer.step()
    return loss.item()

for epoch in range(10):
    loss = train_active()
    print(f"Epoch {epoch}: Active Loss {loss:.4f}")
