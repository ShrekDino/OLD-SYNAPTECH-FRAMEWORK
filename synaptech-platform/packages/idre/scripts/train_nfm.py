import torch
import pandas as pd
import numpy as np
from torch_geometric.data import Data
from src.backend.services.nfm_model import NFM
from pathlib import Path

# Load synthetic data
csv_path = Path("/home/cinni/PitchDeck/SynapTech_IDRE/data/flywire/connectome.csv")
df = pd.read_csv(csv_path)

# Prepare graph
edge_index = torch.tensor(df[["source", "target"]].values.T, dtype=torch.long)
num_nodes = 130_000
x = torch.randn((num_nodes, 16)) # Placeholder node features

# Model setup
model = NFM(in_channels=16, hidden_channels=32, embedding_dim=16)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

def train():
    model.train()
    optimizer.zero_grad()
    
    # Simple link prediction loop (all edges as positive, sample negative)
    z = model(x, edge_index)
    
    # Train on existing edges (positive)
    pos_pred = model.predict_link(z, edge_index)
    pos_loss = -torch.log(pos_pred + 1e-15).mean()
    
    # Train on negative samples
    neg_edge_index = torch.randint(0, num_nodes, (2, edge_index.size(1)))
    neg_pred = model.predict_link(z, neg_edge_index)
    neg_loss = -torch.log(1 - neg_pred + 1e-15).mean()
    
    loss = pos_loss + neg_loss
    loss.backward()
    optimizer.step()
    return loss.item()

for epoch in range(10):
    loss = train()
    print(f"Epoch {epoch}: Loss {loss:.4f}")
