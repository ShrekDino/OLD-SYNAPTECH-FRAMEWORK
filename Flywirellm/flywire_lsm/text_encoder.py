import numpy as np

from flywire_lsm.config import CHAR_TO_IDX, SENSORY_NODES, VOCAB_SIZE
from flywire_lsm.logging import get_logger

_LOG = get_logger()


class TextEncoder:
    def __init__(
        self, n_neurons: int, sensory_nodes: list[int] | None = None
    ) -> None:
        self.n_neurons = n_neurons
        self.sensory_nodes = sensory_nodes or SENSORY_NODES
        _LOG.info(
            "[INIT] TextEncoder: vocab=%d chars nodes=[%d..%d]",
            VOCAB_SIZE, min(self.sensory_nodes), max(self.sensory_nodes),
        )

    def encode(self, char: str, strength: float = 1.0) -> np.ndarray:
        inj = np.zeros(self.n_neurons, dtype=np.float64)
        idx = CHAR_TO_IDX.get(char)
        if idx is not None and idx < len(self.sensory_nodes):
            target = self.sensory_nodes[idx]
            inj[target] = strength
            _LOG.info("[TOKEN] Inject '%s' (idx=%d) -> node[%d] = %.3f", char, idx, target, strength)
        else:
            _LOG.warning("[TOKEN] Unknown char '%s' -- skipping", char)
        return inj
