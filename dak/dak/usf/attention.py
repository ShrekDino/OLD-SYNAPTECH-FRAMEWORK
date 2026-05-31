import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from dak.usf.config import USF_N_HEADS, USF_HEAD_DIM, USF_DTYPE
from dak.usf.lee_wick import LeeWickRegulator


class USFAttention(nn.Module):
    def __init__(
        self,
        d_model: int,
        n_heads: int = USF_N_HEADS,
        head_dim: int = USF_HEAD_DIM,
        dropout: float = 0.1,
        bias: bool = True,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = head_dim
        self.total_dim = n_heads * head_dim

        self.q_proj = nn.Linear(d_model, self.total_dim, bias=bias, dtype=USF_DTYPE)
        self.k_proj = nn.Linear(d_model, self.total_dim, bias=bias, dtype=USF_DTYPE)
        self.v_proj = nn.Linear(d_model, self.total_dim, bias=bias, dtype=USF_DTYPE)
        self.out_proj = nn.Linear(self.total_dim, d_model, bias=bias, dtype=USF_DTYPE)

        self.dropout = nn.Dropout(dropout)
        self.regulator = LeeWickRegulator()

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.q_proj.weight, gain=1.0 / math.sqrt(2))
        nn.init.xavier_uniform_(self.k_proj.weight, gain=1.0 / math.sqrt(2))
        nn.init.xavier_uniform_(self.v_proj.weight, gain=1.0 / math.sqrt(2))
        nn.init.xavier_uniform_(self.out_proj.weight, gain=1.0)
        if self.q_proj.bias is not None:
            nn.init.zeros_(self.q_proj.bias)
            nn.init.zeros_(self.k_proj.bias)
            nn.init.zeros_(self.v_proj.bias)
            nn.init.zeros_(self.out_proj.bias)

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor = None,
        return_weights: bool = False,
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
        batch, seq_len, _ = x.shape

        q = self.q_proj(x).view(batch, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch, seq_len, self.n_heads, self.head_dim).transpose(1, 2)

        scale = math.sqrt(self.head_dim)
        scores = torch.matmul(q, k.transpose(-2, -1)) / scale

        scores = self.regulator.regulate_activation(scores)

        if mask is not None:
            scores = scores + mask

        attn_weights = F.softmax(scores, dim=-1, dtype=torch.float32).to(scores.dtype)
        attn_weights = self.dropout(attn_weights)

        output = torch.matmul(attn_weights, v)
        output = output.transpose(1, 2).contiguous().view(batch, seq_len, -1)
        output = self.out_proj(output)

        output = self.regulator.regulate_activation(output)

        if return_weights:
            return output, attn_weights.detach()
        return output
