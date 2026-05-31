import torch
import torch.nn as nn
import torch.nn.functional as F

from dak.usf.config import USF_DTYPE
from dak.usf.lee_wick import LeeWickRegulator


class SimplicialLayerNorm(nn.Module):
    def __init__(self, normalized_shape: int, eps: float = 1e-5, elementwise_affine: bool = True):
        super().__init__()
        if isinstance(normalized_shape, int):
            normalized_shape = (normalized_shape,)
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.elementwise_affine = elementwise_affine

        if elementwise_affine:
            self.weight = nn.Parameter(torch.ones(normalized_shape, dtype=USF_DTYPE))
            self.bias = nn.Parameter(torch.zeros(normalized_shape, dtype=USF_DTYPE))
        else:
            self.register_parameter('weight', None)
            self.register_parameter('bias', None)

        self.regulator = LeeWickRegulator()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)

        safe_std = self.regulator.regulate_variance(var)

        x_norm = (x - mean) / safe_std

        if self.elementwise_affine:
            x_norm = x_norm * self.weight + self.bias

        return self.regulator.regulate_activation(x_norm)
