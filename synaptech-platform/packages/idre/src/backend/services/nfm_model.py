import torch
import torch.nn.functional as F  # noqa: N812
from torch import nn
from torch_geometric.nn import GCNConv


class NFM(nn.Module):
    """Neural Foundation Model for Connectome Structural Completion."""
    def __init__(self, in_channels: int, hidden_channels: int, embedding_dim: int):
        super(NFM, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, embedding_dim)
        self.link_predictor = nn.Bilinear(embedding_dim, embedding_dim, 1)

    def forward(self, x, edge_index):
        # Generate node embeddings
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index)
        return x

    def predict_link(self, z, edge_index):
        """Predict probability of connection."""
        src, dst = edge_index
        logits = self.link_predictor(z[src], z[dst]).squeeze()
        probs = torch.sigmoid(logits)
        return probs

    def get_uncertainty(self, z, edge_index):
        """Calculate uncertainty (entropy) for link predictions."""
        probs = self.predict_link(z, edge_index)
        # Entropy for Bernoulli distribution: -p*log(p) - (1-p)*log(1-p)
        log_p = torch.log(probs + 1e-15)
        log_1mp = torch.log(1 - probs + 1e-15)
        uncertainty = -(probs * log_p + (1 - probs) * log_1mp)
        return uncertainty
