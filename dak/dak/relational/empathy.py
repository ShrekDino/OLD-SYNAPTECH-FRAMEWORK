import os
import struct
import numpy as np

from dak.config.settings import MI_THRESHOLD


class Empathy:
    def __init__(self, threshold=MI_THRESHOLD):
        self.threshold = threshold
        self.novelty_source = '/dev/urandom'

    def inject_novelty(self, telemetry):
        try:
            if os.path.exists(self.novelty_source):
                with open(self.novelty_source, 'rb') as f:
                    raw = f.read(8)
                noise_val = abs(struct.unpack('d', raw)[0]) % 1.0
            else:
                noise_val = float(np.random.random())
        except Exception:
            noise_val = float(np.random.random())

        perturbed = dict(telemetry)
        keys = [k for k in perturbed if isinstance(perturbed[k], (int, float))]
        if keys:
            key = np.random.choice(keys)
            perturbed[key] = perturbed[key] * (1.0 + 0.1 * noise_val)
        return perturbed

    def check_senescence(self, mutual_info):
        return mutual_info < self.threshold
