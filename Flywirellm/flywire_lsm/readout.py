import time

import numpy as np

from flywire_lsm.config import DEFAULT_SEED, IDX_TO_CHAR, RIDGE_ALPHA
from flywire_lsm.logging import get_logger

_LOG = get_logger()


class LinearReadout:
    def __init__(
        self, n_input: int, n_output: int, rng: np.random.Generator | None = None,
    ) -> None:
        t0 = time.perf_counter()
        self.n_input = n_input
        self.n_output = n_output
        rng = rng or np.random.default_rng(DEFAULT_SEED)

        self.W = rng.normal(0.0, 0.1, size=(n_output, n_input))
        self.b = np.zeros(n_output)
        self.trained = False

        _LOG.info(
            "[INIT] LinearReadout: %d->%d (%d weights) init=%.3f ms",
            n_input, n_output, n_input * n_output,
            (time.perf_counter() - t0) * 1000,
        )

    def train_ridge(
        self, X: np.ndarray, Y: np.ndarray, alpha: float = RIDGE_ALPHA,
    ) -> float:
        t0 = time.perf_counter()
        n = X.shape[0]

        _LOG.info("[TRAIN] Readout: %d samples %d->%d alpha=%g", n, self.n_input, self.n_output, alpha)

        X_aug = np.hstack([X, np.ones((n, 1))])
        reg = alpha * np.eye(self.n_input)
        reg = np.pad(reg, ((0, 1), (0, 1)))
        A = X_aug.T @ X_aug + reg
        B = X_aug.T @ Y
        W_aug = np.linalg.solve(A, B)

        self.W = W_aug[:-1, :].T.copy()
        self.b = W_aug[-1, :].copy()

        Y_pred = X @ self.W.T + self.b
        predicted = np.argmax(Y_pred, axis=1)
        targets = np.argmax(Y, axis=1)
        errors = int(np.sum(predicted != targets))
        acc = 1.0 - errors / n

        _LOG.info("[TRAIN] Solved in %.3f ms  train_acc=%.4f (%d/%d errors)",
                  (time.perf_counter() - t0) * 1000, acc, errors, n)
        _LOG.info("[TRAIN] W mu=%.6f sigma=%.6f [%.6f, %.6f]",
                  float(np.mean(self.W)), float(np.std(self.W)),
                  float(np.min(self.W)), float(np.max(self.W)))
        _LOG.info("[TRAIN] b mu=%.6f sigma=%.6f", float(np.mean(self.b)), float(np.std(self.b)))

        self.trained = True
        return acc

    def predict(self, a_out: np.ndarray) -> np.ndarray:
        return self.W @ a_out + self.b

    def decode(self, logits: np.ndarray) -> tuple[str, int]:
        idx = int(np.argmax(logits))
        return IDX_TO_CHAR.get(idx, "?"), idx

    def save_weights(self, path: str) -> None:
        np.savez_compressed(path, W=self.W, b=self.b)
        _LOG.info("[WEIGHTS] Saved readout to %s (W=%s, b=%s)", path, self.W.shape, self.b.shape)

    def load_weights(self, path: str) -> None:
        data = np.load(path)
        self.W = data["W"]
        self.b = data["b"]
        self.trained = True
        _LOG.info("[WEIGHTS] Loaded readout from %s (W=%s, b=%s)", path, self.W.shape, self.b.shape)
