import logging
from typing import Optional, Tuple

import numpy as np

from .spatial_reasoner import SpatialReasoner
from ..tokens import CosmosEncoder

logger = logging.getLogger(__name__)


class CosmosEnvironment:
    """Replaces CSDF's synthetic EmbeddingEnvironment with Cosmos-grounded world state.

    Instead of generating abstract structured/chaotic embedding sequences
    (the original EmbeddingEnvironment's 85%/45%/5% resolvability modes),
    this environment produces agent macrostate vectors mu that are
    conditioned on Cosmos-Reason2's physical world understanding.

    The agent no longer models abstract embeddings — it models the
    physical world as encoded by Cosmos.
    """

    def __init__(
        self,
        reasoner: SpatialReasoner,
        encoder: Optional[CosmosEncoder] = None,
        latent_dim: int = 64,
    ):
        self.reasoner = reasoner
        self.encoder = encoder
        self.latent_dim = latent_dim
        self._step_count = 0
        self._last_mu: Optional[np.ndarray] = None

    def step(self, agent_state: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
        self._step_count += 1
        if agent_state is not None and self.reasoner.is_loaded:
            reasoning = self.reasoner.analyze_agent_trajectory(agent_state)
            mu = self._embed_reasoning(reasoning)
        else:
            mu = self._fallback_embedding()
        self._last_mu = mu
        entropy = float(np.random.exponential(0.1))
        return mu, entropy

    def _embed_reasoning(self, reasoning: dict) -> np.ndarray:
        keys = ["spatial_coherence", "state_variance", "temporal_regularity"]
        base = np.array([reasoning.get(k, 0.0) for k in keys], dtype=np.float32)
        noise = np.random.randn(self.latent_dim - 3).astype(np.float32) * 0.01
        return np.concatenate([base, noise])

    def _fallback_embedding(self) -> np.ndarray:
        t = self._step_count * 0.1
        structured = 0.85 * np.sin(np.linspace(t, t + 6.28, self.latent_dim))
        noise = np.random.randn(self.latent_dim).astype(np.float32) * 0.15
        return (structured + noise).astype(np.float32)

    def reset(self):
        self._step_count = 0
        self._last_mu = None
