import os
import sys
import time


CONSTITUTION_VERSION = '0.1.0'

CONSTITUTION_INVARIANTS = {
    'szilard_above_threshold': {
        'description': 'Szilard ratio must remain at or above SZILARD_THRESHOLD',
        'active': True,
        'severity': 'critical',
    },
    'f_no_runaway': {
        'description': 'Variational Free Energy F must not increase beyond MAX_F over rolling window',
        'active': True,
        'severity': 'critical',
    },
    'mu_norm_bounded': {
        'description': 'Internal state vector L2 norm must stay within MU_NORM_MAX',
        'active': True,
        'severity': 'high',
    },
    's_gen_bounded': {
        'description': 'Entropy production S_gen must stay within S_GEN_MAX',
        'active': True,
        'severity': 'high',
    },
    'parameter_bounds': {
        'description': 'All config parameters must remain within defined safety bounds',
        'active': True,
        'severity': 'critical',
    },
    'constitution_integrity': {
        'description': 'The safety constitution file must not be modified or deleted',
        'active': True,
        'severity': 'critical',
    },
    'resource_limits': {
        'description': 'System resource usage must stay within limits',
        'active': True,
        'severity': 'high',
    },
    'sandbox_isolation': {
        'description': 'All sandboxed execution must stay within workspace bounds and be killable on violation',
        'active': True,
        'severity': 'critical',
    },
}


class SafetyConstitution:
    def __init__(self):
        self.version = CONSTITUTION_VERSION
        self.invariants = dict(CONSTITUTION_INVARIANTS)
        self._constitution_path = os.path.abspath(__file__)
        self._checksum = self._compute_checksum()

    def _compute_checksum(self):
        try:
            with open(self._constitution_path, 'rb') as f:
                return hash(f.read())
        except Exception:
            return 0

    def verify_integrity(self):
        current = self._compute_checksum()
        return current == self._checksum

    def get_invariant(self, name):
        return self.invariants.get(name)

    def is_active(self, name):
        inv = self.invariants.get(name)
        return inv is not None and inv['active']

    def disable_invariant(self, name):
        if name in self.invariants:
            self.invariants[name]['active'] = False

    def enable_invariant(self, name):
        if name in self.invariants:
            self.invariants[name]['active'] = True

    def list_invariants(self):
        return dict(self.invariants)
