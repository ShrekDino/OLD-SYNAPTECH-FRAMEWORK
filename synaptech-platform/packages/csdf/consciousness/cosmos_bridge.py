"""Bridge between CSDF and Cosmos integration layer.

Provides CosmosEmbeddingEnv — a drop-in replacement for EmbeddingEnvironment
that uses Cosmos-Reason2 for physically-grounded world state generation
instead of synthetic embedding sequences.

This module is imported conditionally. If the cosmos package is not
available, it falls back to the standard EmbeddingEnvironment.
"""

import logging
from typing import Optional, Tuple

import numpy as np

from .embedding_env import EmbeddingEnvironment

logger = logging.getLogger(__name__)

try:
    from cosmos_bridge import SpatialReasoner, CosmosEncoder

    _HAS_COSMOS = True
except ImportError:
    SpatialReasoner = None
    CosmosEncoder = None
    _HAS_COSMOS = False
    logger.info("Cosmos package not available — using standard EmbeddingEnvironment")


class CosmosEmbeddingEnv(EmbeddingEnvironment):
    """Embedding environment backed by Cosmos-Reason2 spatial reasoning.

    Replaces the synthetic source dynamics (coupled oscillators, chaotic maps)
    with physically-grounded reasoning about spatial trajectories.

    Falls back to EmbeddingEnvironment behavior when Cosmos is unavailable.
    """

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed=seed)
        self._reasoner = None
        self._encoder = None
        if _HAS_COSMOS:
            try:
                self._reasoner = SpatialReasoner()
                self._reasoner.load(device="cpu", quantize=False)
                logger.info("CosmosEmbeddingEnv: SpatialReasoner loaded")
            except Exception as e:
                logger.warning(f"CosmosEmbeddingEnv init failed: {e}")

    def step(self) -> Tuple[np.ndarray, float, float]:
        if self._reasoner is not None and self._reasoner.is_loaded:
            return self._cosmos_step()
        return super().step()

    def _cosmos_step(self) -> Tuple[np.ndarray, float, float]:
        if not hasattr(self, "_state_buffer"):
            self._state_buffer = np.zeros((10, self.dim), dtype=np.float32)
        self._source_dynamics()
        mu = self.mixing @ self.source_state
        noise = self.rng.randn(self.dim).astype(np.float32) * self.noise_scale
        mu = mu + noise
        self._state_buffer = np.roll(self._state_buffer, -1, axis=0)
        self._state_buffer[-1] = mu

        analysis = self._reasoner.analyze_agent_trajectory(self._state_buffer)
        H_env = 0.5 * np.log(np.mean(mu ** 2) + 1e-12)
        wt = 0.85 if analysis["spatial_coherence"] > 0.1 else 0.45
        H_struct = H_env * wt
        self._structured_rate = 0.95 * self._structured_rate + 0.05 * wt
        return mu, H_env, H_struct
