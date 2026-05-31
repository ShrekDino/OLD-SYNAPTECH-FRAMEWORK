import os
import shutil
import hashlib

from dak.config.settings import SANDBOX_WORK_DIR, SANDBOX_MAX_DISK_MB


class Workspace:
    def __init__(self, root=SANDBOX_WORK_DIR, max_disk_mb=SANDBOX_MAX_DISK_MB):
        self.root = os.path.abspath(root)
        self.max_disk_mb = max_disk_mb
        self._snapshot = {}
        self._ensure_root()

    def _ensure_root(self):
        os.makedirs(self.root, exist_ok=True)

    def _resolve(self, path):
        full = os.path.abspath(os.path.join(self.root, path))
        if not full.startswith(self.root):
            raise PermissionError(f'Path {path} escapes workspace root')
        return full

    def read_file(self, path):
        full = self._resolve(path)
        if not os.path.exists(full):
            raise FileNotFoundError(f'File not found: {path}')
        with open(full, 'r') as f:
            return f.read()

    def write_file(self, path, content):
        full = self._resolve(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        usage = self.get_usage_mb()
        estimated_new = len(content.encode('utf-8')) / (1024 * 1024)
        if usage + estimated_new > self.max_disk_mb:
            raise IOError(f'Disk quota exceeded ({usage:.1f}MB + {estimated_new:.1f}MB > {self.max_disk_mb}MB)')
        with open(full, 'w') as f:
            f.write(content)

    def list_files(self, subdir=''):
        full = self._resolve(subdir)
        if not os.path.isdir(full):
            return []
        result = []
        for root, dirs, files in os.walk(full):
            rel = os.path.relpath(root, self.root)
            for f in files:
                fpath = os.path.join(rel, f) if rel != '.' else f
                full_path = os.path.join(root, f)
                result.append({
                    'path': fpath,
                    'size': os.path.getsize(full_path),
                    'modified': os.path.getmtime(full_path),
                })
        return sorted(result, key=lambda x: x['path'])

    def get_usage_mb(self):
        total = 0
        for root, dirs, files in os.walk(self.root):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
        return total / (1024 * 1024)

    def snapshot(self):
        self._snapshot = {}
        for root, dirs, files in os.walk(self.root):
            for f in files:
                fpath = os.path.join(root, f)
                rel = os.path.relpath(fpath, self.root)
                try:
                    with open(fpath, 'rb') as fh:
                        content = fh.read()
                    self._snapshot[rel] = {
                        'content': content,
                        'hash': hashlib.sha256(content).hexdigest(),
                    }
                except Exception:
                    pass

    def rollback(self):
        for rel_path, snap in self._snapshot.items():
            full = os.path.join(self.root, rel_path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'wb') as f:
                f.write(snap['content'])

        current_files = set()
        for root, dirs, files in os.walk(self.root):
            for f in files:
                fpath = os.path.join(root, f)
                rel = os.path.relpath(fpath, self.root)
                current_files.add(rel)

        for f in current_files:
            if f not in self._snapshot:
                try:
                    os.remove(os.path.join(self.root, f))
                except Exception:
                    pass

    def clear(self):
        for item in os.listdir(self.root):
            fpath = os.path.join(self.root, item)
            try:
                if os.path.isfile(fpath):
                    os.remove(fpath)
                elif os.path.isdir(fpath):
                    shutil.rmtree(fpath)
            except Exception:
                pass
        self._snapshot = {}
