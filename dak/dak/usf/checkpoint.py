import os
from pathlib import Path
from typing import Optional

import torch

from dak.usf.config import USF_MODEL_PATH


class USFCheckpoint:
    def __init__(self, model: torch.nn.Module, path: str = USF_MODEL_PATH):
        self.model = model
        self.path = path

    def save(self, optimizer_state: Optional[dict] = None, metadata: Optional[dict] = None):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        state = {
            'model_state_dict': self.model.state_dict(),
        }
        if optimizer_state is not None:
            state['optimizer_state_dict'] = optimizer_state
        if metadata is not None:
            state['metadata'] = metadata
        torch.save(state, self.path)

    def load(self, optimizer: Optional[torch.optim.Optimizer] = None, device: Optional[torch.device] = None):
        if not os.path.exists(self.path):
            return {}
        model_device = device or next(self.model.parameters()).device
        state = torch.load(self.path, map_location=model_device, weights_only=True)
        ckpt_sd = state['model_state_dict']
        model_sd = self.model.state_dict()
        filtered = {k: v for k, v in ckpt_sd.items()
                    if k in model_sd and v.shape == model_sd[k].shape}
        self.model.load_state_dict(filtered, strict=False)
        if optimizer is not None and 'optimizer_state_dict' in state:
            optimizer.load_state_dict(state['optimizer_state_dict'])
        return state.get('metadata', {})

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def get_path_for_tick(self, tick: int) -> str:
        base, ext = os.path.splitext(self.path)
        return f'{base}_{tick}{ext}'
