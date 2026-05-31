import torch
import torch.nn as nn

from dak.usf.config import LAMBDA_CUTOFF, M_REGULATOR, USF_DTYPE


class LeeWickRegulator(nn.Module):
    def __init__(self, cutoff: float = LAMBDA_CUTOFF, mass: float = M_REGULATOR):
        super().__init__()
        self.cutoff = cutoff
        self.mass = mass
        self.eps = 1e-6

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_sq = x ** 2
        numerator = self.cutoff ** 4
        denominator = (x_sq + self.eps) ** 2 + self.cutoff ** 4
        lee_wick_factor = numerator / denominator
        mass_term = 1.0 / (x_sq + self.mass ** 2 + self.eps)
        return x * lee_wick_factor * mass_term * (self.mass ** 2)

    def regulate_activation(self, x: torch.Tensor) -> torch.Tensor:
        x_sq = x ** 2
        numerator = self.cutoff ** 4
        denominator = (x_sq + self.eps) ** 2 + self.cutoff ** 4
        factor = numerator / denominator
        return x * factor

    def regulate_variance(self, var: torch.Tensor) -> torch.Tensor:
        var_sq = var ** 2
        numerator = self.cutoff ** 4
        denominator = (var_sq + self.eps) ** 2 + self.cutoff ** 4
        factor = numerator / denominator
        safe_var = var * factor + self.eps
        return safe_var.sqrt()

    def check_stability(self, x: torch.Tensor) -> dict:
        x_abs = x.abs()
        return {
            'max_abs': float(x_abs.max()),
            'mean_abs': float(x_abs.mean()),
            'fraction_capped': float((x_abs > self.cutoff * 0.8).float().mean()),
            'all_finite': bool(torch.isfinite(x).all()),
            'stable': bool(x_abs.max() < self.cutoff * 10),
        }
