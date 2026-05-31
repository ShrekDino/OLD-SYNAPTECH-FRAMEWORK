import json
import os
import threading
import time

AUDIT_LOG_PATH = '/tmp/dak_audit.jsonl'

_audit_lock = threading.Lock()


class AuditLogger:
    def __init__(self, path=AUDIT_LOG_PATH):
        self.path = path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.path):
            try:
                with open(self.path, 'w'):
                    pass
            except Exception:
                pass

    def log(self, entry_type, source, detail, outcome='approved'):
        record = {
            'timestamp': time.time(),
            'type': entry_type,
            'source': source,
            'detail': detail,
            'outcome': outcome,
        }
        with _audit_lock:
            try:
                with open(self.path, 'a') as f:
                    f.write(json.dumps(record) + '\n')
            except Exception:
                pass

    def log_modification(self, source, file_path, change_summary, outcome='approved'):
        self.log('modification', source, {
            'file': file_path,
            'summary': change_summary,
        }, outcome)

    def log_violation(self, invariant_name, current_value, threshold):
        self.log('violation', 'safety_monitor', {
            'invariant': invariant_name,
            'current': current_value,
            'threshold': threshold,
        }, 'violation')

    def log_state(self, state_snapshot):
        self.log('state_snapshot', 'system', state_snapshot, 'info')

    def read_recent(self, n=100):
        records = []
        if not os.path.exists(self.path):
            return records
        try:
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except Exception:
            pass
        return records[-n:]
