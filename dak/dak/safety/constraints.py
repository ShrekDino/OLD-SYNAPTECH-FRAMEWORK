import numpy as np

from dak.config import settings


class SafetyConstraints:
    def __init__(self):
        self.param_bounds = {
            'MU_DIM': (16, 512),
            'LEARNING_RATE': (1e-6, 1.0),
            'MOMENTUM': (0.0, 0.999),
            'GRADIENT_CLIP_NORM': (0.01, 100.0),
            'SIGMA2_LIK': (1e-6, 100.0),
            'SIGMA2_PRIOR': (1e-6, 100.0),
            'DRIFT_DURATION': (0.1, 300.0),
            'SAMPLING_DURATION': (0.1, 60.0),
            'TICK_INTERVAL': (0.01, 10.0),
            'SZILARD_THRESHOLD': (0.01, 100.0),
            'MU_HISTORY_SIZE': (10, 100000),
            'SENSOR_WINDOW': (5, 5000),
        }

        self.operational_bounds = {
            'MU_NORM_MAX': 1000.0,
            'S_GEN_MAX': 10000.0,
            'MAX_F': 1e9,
            'F_VARIANCE_WINDOW': 50,
            'F_VARIANCE_RATIO': 10.0,
            'MAX_DISK_WRITE_MB_PER_STEP': 100.0,
            'MAX_SUBPROCESSES': 20,
            'MAX_CAMERA_FEATURES': 30,
            'MAX_AUDIO_FEATURES': 20,
            'SANDBOX_TIMEOUT_MAX': 120.0,
            'SANDBOX_MAX_MEM_MAX': 1024,
            'SANDBOX_MAX_DISK_MAX': 500,
        }

    def check_param(self, name, value):
        if name not in self.param_bounds:
            return True, None
        lo, hi = self.param_bounds[name]
        ok = lo <= value <= hi
        return ok, (lo, hi)

    def check_all_params(self):
        violations = []
        for name, (lo, hi) in self.param_bounds.items():
            if hasattr(settings, name):
                val = getattr(settings, name)
                if not (lo <= val <= hi):
                    violations.append((name, val, lo, hi))
        return violations

    def check_operational(self, mu_norm, S_gen, F, tick_count):
        violations = []
        if mu_norm > self.operational_bounds['MU_NORM_MAX']:
            violations.append(('mu_norm', mu_norm, self.operational_bounds['MU_NORM_MAX']))
        if S_gen > self.operational_bounds['S_GEN_MAX']:
            violations.append(('S_gen', S_gen, self.operational_bounds['S_GEN_MAX']))
        if F > self.operational_bounds['MAX_F']:
            violations.append(('F', F, self.operational_bounds['MAX_F']))
        return violations

    def state_dict(self):
        return {
            'param_bounds': dict(self.param_bounds),
            'operational_bounds': dict(self.operational_bounds),
        }
