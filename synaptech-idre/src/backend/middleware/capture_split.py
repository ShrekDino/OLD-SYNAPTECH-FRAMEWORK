import json
import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.backend.services.encryption import EncryptionService
from src.backend.services.telemetry_anon import TelemetryAnonymizer

logger = logging.getLogger(__name__)


class CaptureSplitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._encryption = EncryptionService.get_instance()
        self._anonymizer = TelemetryAnonymizer()
        self._pinecone: Optional[object] = None
        self._s3_bucket = None

    async def _init_pinecone(self) -> None:
        if self._pinecone is not None:
            return
        try:
            from src.backend.services.pinecone_client import PineconeClient
            if PineconeClient.available():
                self._pinecone = PineconeClient.get_instance()
        except Exception as e:
            logger.debug(f"Pinecone not available: {e}")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="replace")

        response = await call_next(request)

        latency_ms = (time.time() - start_time) * 1000

        try:
            await self._process_capture_split(
                request=request,
                body=body_str,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.error(f"Capture-split processing error: {e}")

        return response

    async def _process_capture_split(
        self,
        request: Request,
        body: str,
        status_code: int,
        latency_ms: float,
    ) -> None:
        await self._init_pinecone()

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {}

        user_id = payload.get("user_id", request.headers.get("X-User-Id", "anonymous"))

        contains_ip = any(
            key in payload
            for key in ["user_id", "email", "ip_address", "auth_token"]
        )

        if contains_ip:
            encrypted = self._encryption.encrypt_dict(payload)
            encrypted.key_id = self._encryption.key_id
            logger.info(
                f"Encrypted IP data for user={user_id[:8]}... "
                f"key_id={encrypted.key_id} size={len(encrypted.ciphertext)}B"
            )

        anon_event = self._anonymizer.anonymize_payload(payload)
        anon_event.latency_ms = latency_ms
        anon_event.resource_usage = {
            "status_code": status_code,
        }

        if self._pinecone:
            try:
                self._pinecone.upsert_telemetry(anon_event)
            except Exception as e:
                logger.debug(f"Pinecone upsert failed: {e}")
