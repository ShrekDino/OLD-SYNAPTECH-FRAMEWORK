import threading
import time

from dak.config.settings import TICK_INTERVAL


class SafetySentinel:
    def __init__(self, sandbox, workspace, monitor):
        self.sandbox = sandbox
        self.workspace = workspace
        self.monitor = monitor
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)

    def _loop(self):
        while self._running:
            violations = self.monitor.get_violations()
            for v in violations:
                if v.get('severity') == 'critical':
                    self.sandbox.kill_all()
                    enforce_event = {
                        'invariant': v.get('invariant', 'unknown'),
                        'action': 'kill_all_sandbox_processes',
                        'severity': 'critical',
                    }
                    self.monitor.audit.log('enforcement', 'safety_sentinel', enforce_event, 'enforced')
                    break
            time.sleep(TICK_INTERVAL * 5)

    def check_now(self):
        self.sandbox.kill_all()
