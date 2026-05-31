import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Request
from src.backend.middleware.capture_split import CaptureSplitMiddleware
from src.backend.services.encryption import EncryptionService
from src.backend.services.telemetry_anon import TelemetryAnonymizer


def test_anonymizer_strips_pii():
    payload = {
        "user_id": "alice@example.com",
        "email": "alice@example.com",
        "ip_address": "192.168.1.1",
        "operation": "activate",
        "latency_ms": 12.5,
        "neuron_ids": [1, 2, 3],
        "resource_usage": {"gpu_mb": 600},
    }
    event = TelemetryAnonymizer.anonymize_payload(payload)
    assert event.user_id_hash == TelemetryAnonymizer.hash_value("alice@example.com")
    assert event.operation == "activate"
    assert event.latency_ms == 12.5
    assert "alice@example.com" not in str(event.resource_usage)


def test_encryption_roundtrip():
    svc = EncryptionService()
    blob = svc.encrypt_dict({"user_id": "test", "secret": "s3cr3t"})
    decrypted = svc.decrypt_dict(blob)
    assert decrypted["user_id"] == "test"
    assert decrypted["secret"] == "s3cr3t"


def test_topology_hash_consistency():
    h1 = TelemetryAnonymizer.compute_topology_hash([3, 1, 2])
    h2 = TelemetryAnonymizer.compute_topology_hash([1, 2, 3])
    assert h1 == h2
