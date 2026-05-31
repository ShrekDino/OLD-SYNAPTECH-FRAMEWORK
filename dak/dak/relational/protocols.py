import numpy as np

from dak.config.settings import MU_DIM


class Protocols:
    def __init__(self, mu_dim=MU_DIM):
        self.mu_dim = mu_dim
        self.shadow_history = []

    def compute_mutual_info(self, mu_current, mu_history):
        if len(mu_history) < 5:
            return 0.0

        recent = np.array(mu_history[-10:])
        var_current = float(np.var(recent, axis=0).mean())
        if var_current < 1e-10:
            return 0.0

        X = recent[:-1]
        y = recent[1:]
        n = len(X)
        if n < 2 or n <= self.mu_dim:
            return 0.0

        try:
            XTX = X.T @ X
            reg = np.eye(self.mu_dim) * 0.1
            A = np.linalg.solve(XTX + reg, X.T @ y)
            pred = X @ A
            errors = y - pred
            var_conditional = float(np.var(errors, axis=0).mean())
            if var_conditional < 1e-10:
                return 10.0
            return float(0.5 * np.log(var_current / var_conditional))
        except np.linalg.LinAlgError:
            return 0.0
