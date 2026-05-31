from dataclasses import dataclass, field
from typing import Optional

import torch
import torch.nn.functional as F

from dak.usf.config import USF_DTYPE, USF_DEVICE


@dataclass
class ScaleInvariantMarkovBlanketConfig:
    mi_threshold_token: float = 0.5
    mi_threshold_seq: float = 0.8
    mi_threshold_batch: float = 1.0
    projection_scale: float = 0.9


class ScaleInvariantMarkovBlanket:
    def __init__(self, config: Optional[ScaleInvariantMarkovBlanketConfig] = None):
        self.config = config or ScaleInvariantMarkovBlanketConfig()
        self._sealed = False
        self._internal_states: list = []
        self._sensory_states: list = []
        self._active_states: list = []

    def seal(self):
        self._sealed = True

    def unseal(self):
        self._sealed = False

    def is_sealed(self) -> bool:
        return self._sealed

    def compute_mutual_info(
        self,
        hidden: torch.Tensor,
        noise: torch.Tensor,
    ) -> torch.Tensor:
        h_var = hidden.var(dim=-1, keepdim=True) + 1e-8
        n_var = noise.var(dim=-1, keepdim=True) + 1e-8
        h_n_cov = (hidden * noise).mean(dim=-1, keepdim=True)
        corr = (h_n_cov / (h_var.sqrt() * n_var.sqrt())).abs()
        mi = -0.5 * torch.log(1.0 - corr ** 2 + 1e-8)
        return mi

    def entropy_guard(
        self,
        hidden: torch.Tensor,
        context_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        if self._sealed:
            return hidden

        noise = torch.randn_like(hidden) * 0.01

        mi = self.compute_mutual_info(hidden, noise)

        if context_mask is not None:
            threshold = self.config.mi_threshold_seq
        else:
            threshold = self.config.mi_threshold_token

        scale = (mi < threshold).float()
        filtered = hidden * scale + hidden * (1.0 - scale) * (1.0 - self.config.projection_scale)

        return filtered

    def update(self, mu=None, s=None, a=None, eta=None):
        if mu is not None:
            self._internal_states.append(mu)
        if s is not None:
            self._sensory_states.append(s)
        if a is not None:
            self._active_states.append(a)

    def get_state_dict(self) -> dict:
        return {
            'sealed': self._sealed,
            'internal_count': len(self._internal_states),
            'sensory_count': len(self._sensory_states),
            'active_count': len(self._active_states),
        }
