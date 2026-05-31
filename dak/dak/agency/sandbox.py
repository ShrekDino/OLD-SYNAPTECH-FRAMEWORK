import os
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from dak.config.settings import SANDBOX_TIMEOUT, SANDBOX_MAX_MEM_MB, SANDBOX_WORK_DIR


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timed_out: bool = False
    error: Optional[str] = None


class Sandbox:
    def __init__(self, work_dir=SANDBOX_WORK_DIR,
                 timeout=SANDBOX_TIMEOUT,
                 max_memory_mb=SANDBOX_MAX_MEM_MB):
        self.work_dir = work_dir
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self._running = {}
        self._lock = threading.Lock()
        self._ensure_work_dir()

    def _ensure_work_dir(self):
        os.makedirs(self.work_dir, exist_ok=True)

    def run_code(self, code_str, language='python', cwd=None):
        if cwd is None:
            cwd = self.work_dir

        ext = {'python': '.py', 'bash': '.sh', 'shell': '.sh'}.get(language, '.py')
        with tempfile.NamedTemporaryFile(
            mode='w', suffix=ext, dir=cwd, delete=False
        ) as f:
            f.write(code_str)
            fpath = f.name

        if language in ('bash', 'shell'):
            cmd = ['bash', fpath]
        else:
            cmd = [self._python_path(), fpath]

        start = time.time()
        timed_out = False

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                text=True,
            )

            with self._lock:
                self._running[proc.pid] = proc

            try:
                stdout, stderr = proc.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                timed_out = True

            duration = time.time() - start

            with self._lock:
                self._running.pop(proc.pid, None)

            os.unlink(fpath)

            return SandboxResult(
                exit_code=proc.returncode,
                stdout=stdout or '',
                stderr=stderr or '',
                duration=duration,
                timed_out=timed_out,
            )

        except Exception as e:
            duration = time.time() - start
            if os.path.exists(fpath):
                os.unlink(fpath)
            return SandboxResult(
                exit_code=-1, stdout='', stderr='',
                duration=duration, error=str(e),
            )

    def run_command(self, cmd_args, cwd=None):
        if cwd is None:
            cwd = self.work_dir

        start = time.time()
        try:
            proc = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                text=True,
            )
            with self._lock:
                self._running[proc.pid] = proc

            stdout, stderr = proc.communicate(timeout=self.timeout)
            duration = time.time() - start

            with self._lock:
                self._running.pop(proc.pid, None)

            return SandboxResult(
                exit_code=proc.returncode,
                stdout=stdout or '',
                stderr=stderr or '',
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            duration = time.time() - start
            with self._lock:
                self._running.pop(proc.pid, None)
            return SandboxResult(
                exit_code=proc.returncode,
                stdout=stdout or '',
                stderr=stderr or '',
                duration=duration,
                timed_out=True,
            )
        except Exception as e:
            duration = time.time() - start
            return SandboxResult(
                exit_code=-1, stdout='', stderr='',
                duration=duration, error=str(e),
            )

    def kill_all(self):
        with self._lock:
            pids = list(self._running.keys())
            for pid in pids:
                proc = self._running.get(pid)
                if proc and proc.poll() is None:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            self._running.clear()

    def _python_path(self):
        import sys
        return sys.executable

    def cleanup(self):
        self.kill_all()
