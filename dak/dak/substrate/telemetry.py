import subprocess
import time

import psutil

from dak.config.settings import SENSOR_WINDOW


class Telemetry:
    def __init__(self, window_size=SENSOR_WINDOW):
        self.buffer = []
        self.window_size = window_size
        self._baseline = None

    def read_all(self):
        sensors = {}

        sensors['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        sensors['cpu_count'] = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        sensors['cpu_freq'] = cpu_freq.current if cpu_freq else 0.0

        mem = psutil.virtual_memory()
        sensors['mem_percent'] = mem.percent
        sensors['mem_used_gb'] = mem.used / (1024 ** 3)
        sensors['mem_available_gb'] = mem.available / (1024 ** 3)

        disk = psutil.disk_io_counters()
        sensors['disk_read_mb'] = (disk.read_bytes / (1024 ** 2)) if disk else 0.0
        sensors['disk_write_mb'] = (disk.write_bytes / (1024 ** 2)) if disk else 0.0

        net = psutil.net_io_counters()
        sensors['net_recv_mb'] = (net.bytes_recv / (1024 ** 2)) if net else 0.0
        sensors['net_sent_mb'] = (net.bytes_sent / (1024 ** 2)) if net else 0.0

        load = psutil.getloadavg()
        sensors['load_1min'] = load[0]
        sensors['load_5min'] = load[1]
        sensors['load_15min'] = load[2]

        sensors['processes'] = len(psutil.pids())
        sensors['uptime'] = time.time() - psutil.boot_time()

        self.buffer.append(sensors)
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0)

        if self._baseline is None:
            self._baseline = dict(sensors)

        return sensors

    def get_baseline(self):
        if self._baseline is None:
            return self.read_all()
        return self._baseline

    def release_sensors(self):
        pass
