import numpy as np

from dak.config.settings import KB, EPSILON, SENSOR_WINDOW


class SzilardEngine:
    def __init__(self, window_size=SENSOR_WINDOW):
        self.window_size = window_size
        self.kB = KB
        self.epsilon = EPSILON

    def compute_H_env(self, sensor_buffer):
        if len(sensor_buffer) < 5:
            return 1.0

        keys = list(sensor_buffer[0].keys())
        H_total = 0.0
        for k in keys:
            values = []
            for s in sensor_buffer:
                if k in s and isinstance(s[k], (int, float)):
                    values.append(s[k])
            if len(values) > 5:
                variance = float(np.var(values))
                H_total += 0.5 * np.log(1.0 + variance)
        return max(H_total, 1e-10)

    def compute_ratio(self, H_env, S_gen):
        if S_gen < 1e-10:
            return float('inf')
        return (self.kB * self.epsilon * H_env) / S_gen
