import numpy as np

from dak.config.settings import MU_DIM, N_SENSORS, W_INIT_SCALE

SENSOR_KEYS = [
    'cpu_percent', 'cpu_count', 'cpu_freq', 'mem_percent', 'mem_used_gb',
    'mem_available_gb', 'disk_read_mb', 'disk_write_mb',
    'net_recv_mb', 'net_sent_mb', 'load_1min', 'load_5min',
    'load_15min', 'processes', 'uptime',
]

SENSOR_RANGES = {
    'cpu_percent': (0.0, 100.0),
    'cpu_count': (0.0, 1024.0),
    'cpu_freq': (0.0, 5000.0),
    'mem_percent': (0.0, 100.0),
    'mem_used_gb': (0.0, 512.0),
    'mem_available_gb': (0.0, 512.0),
    'disk_read_mb': (0.0, 5000.0),
    'disk_write_mb': (0.0, 5000.0),
    'net_recv_mb': (0.0, 5000.0),
    'net_sent_mb': (0.0, 5000.0),
    'load_1min': (0.0, 100.0),
    'load_5min': (0.0, 100.0),
    'load_15min': (0.0, 100.0),
    'processes': (0.0, 50000.0),
    'uptime': (0.0, 10000000.0),
}


class GenerativeModel:
    def __init__(self, mu_dim=MU_DIM, n_sensors=N_SENSORS):
        self.mu_dim = mu_dim
        self.n_sensors = n_sensors
        rng = np.random.RandomState(42)
        self.W = rng.randn(n_sensors, mu_dim).astype(np.float64) * W_INIT_SCALE
        self.b = np.zeros(n_sensors, dtype=np.float64)

    def predict(self, mu):
        return self.W @ mu + self.b

    def compute_gradient(self, mu, prediction_error, sigma2_lik=0.1):
        grad = -self.W.T @ prediction_error / sigma2_lik
        return grad

    def sensors_to_array(self, sensors):
        n_target = self.n_sensors
        arr = np.zeros(n_target, dtype=np.float64)
        for i, k in enumerate(SENSOR_KEYS):
            if i < n_target and k in sensors:
                val = sensors[k]
                if isinstance(val, (int, float)):
                    lo, hi = SENSOR_RANGES.get(k, (0.0, 1.0))
                    normalized = (float(val) - lo) / (hi - lo) if hi > lo else 0.0
                    normalized = max(0.0, min(1.0, normalized))
                    arr[i] = normalized
        return arr
