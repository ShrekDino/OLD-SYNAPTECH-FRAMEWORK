import hashlib
import hmac
import os
from typing import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._api_keys: set[str] = set()
        self._jwt_secret: str | None = os.environ.get("JWT_SECRET")
        self._load_keys()

    def _load_keys(self) -> None:
        keys_env = os.environ.get("API_KEYS", "")
        if keys_env:
            self._api_keys.update(k.strip() for k in keys_env.split(",") if k.strip())

    def validate_api_key(self, token: str) -> bool:
        return token in self._api_keys

    def validate_jwt(self, token: str) -> bool:
        if not self._jwt_secret:
            return False
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False
            payload = parts[1]
            expected_sig = hmac.new(
                self._jwt_secret.encode(),
                f"{parts[0]}.{payload}".encode(),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected_sig, parts[2])
        except Exception:
            return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        bypass_paths = {"/docs", "/openapi.json", "/redoc", "/health", "/metrics"}
        if request.url.path in bypass_paths:
            return await call_next(request)

        if self._jwt_secret or self._api_keys:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Missing authorization")

            parts = auth_header.split()
            if len(parts) != 2:
                raise HTTPException(status_code=401, detail="Invalid authorization header")

            scheme, token = parts
            scheme = scheme.lower()

            if scheme == "bearer":
                if not (self.validate_jwt(token) or self.validate_api_key(token)):
                    raise HTTPException(status_code=403, detail="Invalid token")
            elif scheme == "apikey":
                if not self.validate_api_key(token):
                    raise HTTPException(status_code=403, detail="Invalid API key")
            else:
                raise HTTPException(status_code=401, detail="Unsupported auth scheme")

        return await call_next(request)
