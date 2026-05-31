import threading
import time

import httpx

from dak.config.settings import NETWORK_ALLOWLIST, NETWORK_RATE_LIMIT


class NetworkAccess:
    def __init__(self, allowlist=None, rate_limit=NETWORK_RATE_LIMIT):
        self.allowlist = allowlist or NETWORK_ALLOWLIST
        self.rate_limit = rate_limit
        self._call_times = []
        self._lock = threading.Lock()
        self._client = httpx.Client(timeout=15.0)

    def http_get(self, url, timeout=10.0):
        if not self._is_allowed(url):
            return {'error': f'URL not in allowlist: {url}', 'status_code': 403}

        if not self._check_rate_limit():
            return {'error': 'Rate limit exceeded', 'status_code': 429}

        try:
            response = self._client.get(url, timeout=timeout)
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'text': response.text[:50000],
            }
        except httpx.TimeoutException:
            return {'error': 'Request timed out', 'status_code': 504}
        except Exception as e:
            return {'error': str(e), 'status_code': 0}

    def http_post(self, url, data=None, json=None, timeout=10.0):
        if not self._is_allowed(url):
            return {'error': f'URL not in allowlist: {url}', 'status_code': 403}

        if not self._check_rate_limit():
            return {'error': 'Rate limit exceeded', 'status_code': 429}

        try:
            response = self._client.post(url, data=data, json=json, timeout=timeout)
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'text': response.text[:50000],
            }
        except httpx.TimeoutException:
            return {'error': 'Request timed out', 'status_code': 504}
        except Exception as e:
            return {'error': str(e), 'status_code': 0}

    def _is_allowed(self, url):
        if not self.allowlist:
            return True
        for allowed in self.allowlist:
            if url.startswith(allowed):
                return True
        return False

    def _check_rate_limit(self):
        now = time.time()
        with self._lock:
            self._call_times = [t for t in self._call_times if now - t < 60.0]
            if len(self._call_times) >= self.rate_limit:
                return False
            self._call_times.append(now)
            return True

    def close(self):
        self._client.close()
