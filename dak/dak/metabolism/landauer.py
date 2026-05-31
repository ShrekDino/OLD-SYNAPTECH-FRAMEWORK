import numpy as np

from dak.config.settings import SENSOR_WINDOW


class LandauerFloor:
    def __init__(self, window_size=SENSOR_WINDOW):
        self.window_size = window_size

    def compute_S_gen(self, mu_history):
        if len(mu_history) < 2:
            return 0.0
        recent = mu_history[-self.window_size:]
        diffs = np.diff(recent, axis=0)
        if len(diffs) == 0:
            return 0.0
        update_magnitude = float(np.mean(np.linalg.norm(diffs, axis=1)))
        state_variance = float(np.mean(np.var(recent, axis=0)))
        return update_magnitude + 0.1 * state_variance
