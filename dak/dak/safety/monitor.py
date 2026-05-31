import threading

from dak.config import settings
from dak.safety.constitution import SafetyConstitution
from dak.safety.constraints import SafetyConstraints
from dak.safety.measurer import SafetyMeasurer
from dak.safety.audit import AuditLogger

WARMUP_TICKS = 10


class SafetyMonitor:
    def __init__(self):
        self.constitution = SafetyConstitution()
        self.constraints = SafetyConstraints()
        self.measurer = SafetyMeasurer()
        self.audit = AuditLogger()
        self._violations = []
        self._f_history = []
        self._enabled = getattr(settings, 'SAFETY_ENABLED', True)
        self._lock = threading.Lock()

    @property
    def enabled(self):
        return self._enabled

    def check(self, dak_state):
        if not self._enabled:
            return []

        violations = []

        tick = dak_state.get('tick_count', 0)
        is_warmup = tick < WARMUP_TICKS

        if not self.constitution.verify_integrity():
            violations.append({
                'invariant': 'constitution_integrity',
                'value': 'checksum_mismatch',
                'threshold': 'constitution file must not change',
                'severity': 'critical',
            })
            self.audit.log_violation('constitution_integrity', 'checksum_mismatch', 'immutable')

        szilard = dak_state.get('szilard_ratio', float('inf'))
        threshold = getattr(settings, 'SZILARD_THRESHOLD', 1.0)
        if not is_warmup and self.constitution.is_active('szilard_above_threshold') and szilard < threshold:
            violations.append({
                'invariant': 'szilard_above_threshold',
                'value': szilard,
                'threshold': threshold,
                'severity': 'critical',
            })
            self.audit.log_violation('szilard_above_threshold', szilard, threshold)

        F = dak_state.get('F', 0.0)
        self._f_history.append(F)
        if len(self._f_history) > 50:
            self._f_history.pop(0)

        if len(self._f_history) >= 10:
            F_var = __import__('numpy').var(self._f_history)
            max_ratio = self.constraints.operational_bounds.get('F_VARIANCE_RATIO', 10.0)
            mean_F = __import__('numpy').mean(self._f_history) + 1e-10
            if not is_warmup and self.constitution.is_active('f_no_runaway') and (F_var / mean_F) > max_ratio:
                violations.append({
                    'invariant': 'f_no_runaway',
                    'value': F_var / mean_F,
                    'threshold': max_ratio,
                    'severity': 'critical',
                })
                self.audit.log_violation('f_no_runaway', F_var / mean_F, max_ratio)

        mu_norm = dak_state.get('mu_norm', 0.0)
        S_gen = dak_state.get('S_gen', 0.0)
        op_violations = self.constraints.check_operational(mu_norm, S_gen, F, 0)
        for v in op_violations:
            violations.append({
                'invariant': f'operational_{v[0]}',
                'value': v[1],
                'threshold': v[2],
                'severity': 'high',
            })
            self.audit.log_violation(f'operational_{v[0]}', v[1], v[2])

        if self.constitution.is_active('sandbox_isolation'):
            self._check_sandbox_isolation(violations)

        param_violations = self.constraints.check_all_params()
        for name, val, lo, hi in param_violations:
            violations.append({
                'invariant': f'param_{name}',
                'value': val,
                'threshold': (lo, hi),
                'severity': 'critical',
            })
            self.audit.log_violation(f'param_{name}', val, (lo, hi))

        with self._lock:
            self._violations = violations

        return violations

    def get_violations(self):
        with self._lock:
            return list(self._violations)

    def has_critical_violations(self):
        with self._lock:
            return any(v.get('severity') == 'critical' for v in self._violations)

    def state_dict(self):
        return {
            'enabled': self._enabled,
            'violation_count': len(self._violations),
            'critical_violations': sum(1 for v in self._violations if v.get('severity') == 'critical'),
            'constitution_integrity': self.constitution.verify_integrity(),
        }

    def _check_sandbox_isolation(self, violations):
        if 'SANDBOX_ENABLED' in dir(settings) and getattr(settings, 'SANDBOX_ENABLED', False):
            import os
            work_dir = getattr(settings, 'SANDBOX_WORK_DIR', '/tmp/erebus_workspace')
            max_disk = getattr(settings, 'SANDBOX_MAX_DISK_MB', 50)
            total = 0
            if os.path.exists(work_dir):
                for root, dirs, files in os.walk(work_dir):
                    for f in files:
                        try:
                            total += os.path.getsize(os.path.join(root, f))
                        except Exception:
                            pass
            usage_mb = total / (1024 * 1024)
            if usage_mb > max_disk:
                violations.append({
                    'invariant': 'sandbox_isolation',
                    'value': usage_mb,
                    'threshold': max_disk,
                    'severity': 'critical',
                })

    def enforce(self):
        critical = [v for v in self._violations if v.get('severity') == 'critical']
        if critical:
            try:
                from dak.agency.sandbox import Sandbox
                if hasattr(self, '_sandbox') and self._sandbox:
                    self._sandbox.kill_all()
            except Exception:
                pass
            for v in critical:
                self.audit.log('enforcement', 'safety_monitor', v, 'enforced')

    def set_sandbox(self, sandbox):
        self._sandbox = sandbox

    def disable(self):
        self._enabled = False
        self.audit.log('config_change', 'admin', {'safety_enabled': False}, 'approved')

    def enable(self):
        self._enabled = True
        self.audit.log('config_change', 'admin', {'safety_enabled': True}, 'approved')
