import logging
from typing import Optional

import numpy as np
import torch

logger = logging.getLogger(__name__)


class CosmosDecoder:
    """Decodes latent tokens back into video frames using Cosmos-Tokenizer.

    Inverse of CosmosEncoder. Reconstructs visual frames from
    continuous or discrete latent representations.
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
        self._decoder = None

    def load(self):
        try:
            decoder_path = f"{self.checkpoint_dir}/{self.model_name}/decoder.jit"
            self._decoder = torch.jit.load(decoder_path, map_location=self.device)
            self._decoder.eval()
            logger.info(f"Loaded {self.model_name} decoder on {self.device}")
        except Exception as e:
            logger.warning(f"Failed to load Cosmos-Tokenizer decoder: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._decoder is not None

    @torch.no_grad()
    def decode(self, latents: np.ndarray) -> np.ndarray:
        if not self.is_loaded:
            raise RuntimeError("Decoder not loaded. Call load() first.")
        tensor = torch.from_numpy(latents).to(self.device)
        reconstructed = self._decoder(tensor)
        return reconstructed.cpu().numpy()
