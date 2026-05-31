import os
import numpy as np

from dak.config.settings import MU_DIM, MU_DTYPE, MMAP_PATH, CHECKPOINT_PATH, MU_INIT_SCALE, MU_HISTORY_SIZE


class InternalState:
    def __init__(self, mu_dim=MU_DIM, dtype=MU_DTYPE, path=MMAP_PATH, fresh=False):
        self.path = path
        self.dim = mu_dim
        self.dtype = dtype
        self.history = []

        if os.path.exists(path) and not fresh:
            self.mu = np.memmap(path, dtype=dtype, mode='r+', shape=(mu_dim,))
        else:
            if os.path.exists(path):
                os.remove(path)
            self.mu = np.memmap(path, dtype=dtype, mode='w+', shape=(mu_dim,))
            mu_init = np.random.RandomState(0).randn(mu_dim).astype(dtype) * MU_INIT_SCALE
            self.mu[:] = mu_init
            self.mu.flush()

    def read(self):
        return self.mu.copy()

    def write(self, new_mu):
        self.mu[:] = new_mu.astype(self.dtype)
        self.mu.flush()
        self.history.append(new_mu.copy())
        if len(self.history) > MU_HISTORY_SIZE:
            self.history.pop(0)

    def save_checkpoint(self, path=CHECKPOINT_PATH):
        if os.path.exists(path):
            os.remove(path)
        ckpt = np.memmap(path, dtype=self.dtype, mode='w+', shape=(self.dim,))
        ckpt[:] = self.mu[:]
        ckpt.flush()
        del ckpt

    def load_checkpoint(self, path=CHECKPOINT_PATH):
        if os.path.exists(path):
            ckpt = np.memmap(path, dtype=self.dtype, mode='r', shape=(self.dim,))
            self.mu[:] = ckpt[:]
            self.mu.flush()
            del ckpt

    def cleanup(self):
        del self.mu
        for p in [self.path, CHECKPOINT_PATH]:
            if os.path.exists(p):
                os.remove(p)
