import hashlib
import json
from typing import Any

from src.shared.schemas import TelemetryEvent


class TelemetryAnonymizer:

    PII_FIELDS = {"user_id", "email", "ip_address", "session_id", "auth_token"}

    @staticmethod
    def hash_value(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def strip_pii(payload: dict) -> dict:
        cleaned = {}
        for k, v in payload.items():
            if k.lower() in TelemetryAnonymizer.PII_FIELDS:
                if isinstance(v, str):
                    cleaned[k] = TelemetryAnonymizer.hash_value(v)
                else:
                    cleaned[k] = "<redacted>"
            elif isinstance(v, dict):
                cleaned[k] = TelemetryAnonymizer.strip_pii(v)
            elif isinstance(v, list):
                cleaned[k] = [
                    TelemetryAnonymizer.strip_pii(item)
                    if isinstance(item, dict)
                    else item
                    for item in v
                ]
            else:
                cleaned[k] = v
        return cleaned

    @staticmethod
    def compute_topology_hash(neuron_ids: list[int]) -> str:
        sorted_ids = sorted(neuron_ids)
        return hashlib.md5(
            json.dumps(sorted_ids, separators=(",", ":")).encode()
        ).hexdigest()

    @staticmethod
    def anonymize_event(
        user_id: str,
        operation: str,
        latency_ms: float,
        resource_usage: dict[str, float],
        topology_hash: str | None = None,
    ) -> TelemetryEvent:
        return TelemetryEvent(
            user_id_hash=TelemetryAnonymizer.hash_value(user_id),
            operation=operation,
            latency_ms=latency_ms,
            resource_usage=resource_usage,
            topology_hash=topology_hash,
        )

    @staticmethod
    def anonymize_payload(
        raw_payload: dict[str, Any],
    ) -> TelemetryEvent:
        cleaned = TelemetryAnonymizer.strip_pii(raw_payload)
        return TelemetryEvent(
            user_id_hash=TelemetryAnonymizer.hash_value(
                raw_payload.get("user_id", "anonymous")
            ),
            operation=cleaned.get("operation", "unknown"),
            latency_ms=cleaned.get("latency_ms", 0.0),
            resource_usage=cleaned.get("resource_usage", {}),
            topology_hash=TelemetryAnonymizer.compute_topology_hash(
                cleaned.get("neuron_ids", [])
            ),
        )
