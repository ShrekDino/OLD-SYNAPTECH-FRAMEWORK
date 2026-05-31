import math
from dataclasses import dataclass, field
from typing import Optional

import torch
from torch import nn

from dak.usf.config import (
    USF_LEARNING_RATE, USF_SZILARD_REJECT, SIGMA2_USF_PRIOR,
    USF_NEGENTROPY_WINDOW, USF_DEVICE,
)


@dataclass
class SzilardStepRejection:
    step_rejected: bool = False
    vfe_before: float = 0.0
    vfe_after: float = 0.0
    vfe_delta: float = 0.0
    h_env: float = 0.0
    negentropy_extracted: float = 0.0
    efficiency: float = 0.0


class ActiveInferenceOptimizer:
    def __init__(
        self,
        model: nn.Module,
        lr: float = USF_LEARNING_RATE,
        sigma2_prior: float = SIGMA2_USF_PRIOR,
        kB: float = 1.0,
        epsilon: float = 0.8,
        szilard_reject: bool = USF_SZILARD_REJECT,
        negentropy_window: int = USF_NEGENTROPY_WINDOW,
    ):
        self.model = model
        self.base_optimizer = torch.optim.AdamW(
            model.parameters(), lr=lr, betas=(0.9, 0.95), weight_decay=0.0,
        )
        self.sigma2_prior = sigma2_prior
        self.kB = kB
        self.epsilon = epsilon
        self.szilard_reject = szilard_reject
        self.negentropy_window = negentropy_window

        self._vfe_history = []
        self._negentropy_history = []
        self._previous_params = None
        self._step_count = 0

    def check_szilard_bound(self, vfe_current: float, h_env: float) -> tuple[bool, float]:
        if len(self._vfe_history) < 1:
            return True, 0.0

        vfe_prev = self._vfe_history[-1]
        vfe_delta = vfe_current - vfe_prev

        negentropy_extracted = -vfe_delta

        szilard_product = self.kB * self.epsilon * h_env
        bound_ok = negentropy_extracted >= 0

        efficiency = 0.0
        if szilard_product > 1e-10:
            efficiency = negentropy_extracted / szilard_product

        return bound_ok, efficiency

    def step(
        self,
        loss_dict: dict,
        h_env: float,
    ) -> SzilardStepRejection:
        vfe = loss_dict.get('loss', loss_dict.get('total_vfe', 0.0))
        if isinstance(vfe, torch.Tensor):
            vfe = vfe.item()

        self._step_count += 1

        result = SzilardStepRejection(
            vfe_before=self._vfe_history[-1] if self._vfe_history else vfe,
            h_env=h_env,
        )

        bound_ok, efficiency = self.check_szilard_bound(vfe, h_env)

        if self.szilard_reject and not bound_ok and len(self._vfe_history) > 0:
            self.base_optimizer.zero_grad()
            result.step_rejected = True
            result.efficiency = efficiency
            result.vfe_after = vfe
            result.vfe_delta = vfe - result.vfe_before
            return result

        loss = loss_dict.get('loss', 0.0)
        if isinstance(loss, torch.Tensor) and loss.requires_grad:
            self.base_optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=10.0)
            self.base_optimizer.step()

        self._vfe_history.append(vfe)
        if len(self._vfe_history) > self.negentropy_window:
            self._vfe_history.pop(0)

        result.step_rejected = False
        result.vfe_after = vfe
        result.vfe_delta = vfe - result.vfe_before
        result.negentropy_extracted = -result.vfe_delta
        result.efficiency = max(0.0, efficiency)

        if result.negentropy_extracted > 0:
            self._negentropy_history.append(result.negentropy_extracted)
            if len(self._negentropy_history) > self.negentropy_window:
                self._negentropy_history.pop(0)

        return result

    def get_avg_negentropy(self) -> float:
        if not self._negentropy_history:
            return 0.0
        return sum(self._negentropy_history) / len(self._negentropy_history)

    def get_avg_vfe(self) -> float:
        if not self._vfe_history:
            return 0.0
        return sum(self._vfe_history) / len(self._vfe_history)

    def state_dict(self) -> dict:
        return {
            'step_count': self._step_count,
            'vfe_history': list(self._vfe_history),
            'negentropy_history': list(self._negentropy_history),
            'avg_negentropy': self.get_avg_negentropy(),
            'avg_vfe': self.get_avg_vfe(),
        }
