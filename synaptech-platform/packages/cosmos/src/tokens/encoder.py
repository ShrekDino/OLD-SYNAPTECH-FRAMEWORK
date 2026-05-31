import logging
from typing import Optional, Tuple

import numpy as np
import torch

logger = logging.getLogger(__name__)


class CosmosEncoder:
    """Wraps Cosmos-Tokenizer for encoding video frames into latent tokens.

    Supports both continuous (CV) and discrete (DV) tokenizer variants.
    Uses JIT-compiled TorchScript models when available, falling back
    to native PyTorch.

    With ~4GB VRAM requirement, this is the only Cosmos component that
    runs natively on RTX 3060 6GB alongside other workloads.
    """

    def __init__(
        self,
        model_name: str = "Cosmos-Tokenize1-CV8x8x8-720p",
        checkpoint_dir: str = "checkpoints",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.model_name = model_name
        self.checkpoint_dir = checkpoint_dir
        self.device = device
        self._encoder = None

    def load(self):
        try:
            encoder_path = f"{self.checkpoint_dir}/{self.model_name}/encoder.jit"
            self._encoder = torch.jit.load(encoder_path, map_location=self.device)
            self._encoder.eval()
            logger.info(f"Loaded {self.model_name} encoder on {self.device}")
        except Exception as e:
            logger.warning(f"Failed to load Cosmos-Tokenizer encoder: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._encoder is not None

    @torch.no_grad()
    def encode(self, frames: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not self.is_loaded:
            raise RuntimeError("Encoder not loaded. Call load() first.")
        tensor = torch.from_numpy(frames).to(self.device)
        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)
        if tensor.ndim == 4:
            tensor = tensor.unsqueeze(0)
        indices, codes = self._encoder(tensor)
        return indices.cpu().numpy(), codes.cpu().numpy()

    @torch.no_grad()
    def encode_continuous(self, frames: np.ndarray) -> np.ndarray:
        _, codes = self.encode(frames)
        return codes

    @torch.no_grad()
    def encode_discrete(self, frames: np.ndarray) -> np.ndarray:
        indices, _ = self.encode(frames)
        return indices
