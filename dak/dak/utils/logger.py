import json
import time
from pathlib import Path

from dak.config.settings import LOG_PATH


class DAKLogger:
    def __init__(self, log_path=LOG_PATH):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, **kwargs):
        entry = {'timestamp': time.time(), **kwargs}
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def recent(self, n=10):
        if not self.log_path.exists():
            return []
        with open(self.log_path) as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[-n:]]

    def tail(self, n=1):
        return self.recent(n)
