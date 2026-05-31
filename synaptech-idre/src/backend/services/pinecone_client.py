import logging
import os
from typing import Optional

_HAS_PINECONE = False
try:
    from pinecone import Pinecone, ServerlessSpec
    _HAS_PINECONE = True
except ImportError:
    Pinecone = None
    ServerlessSpec = None

from src.shared.constants import PINECONE_NAMESPACE  # noqa: E402
from src.shared.schemas import TelemetryEvent  # noqa: E402

logger = logging.getLogger(__name__)


class PineconeClient:
    _instance: Optional["PineconeClient"] = None

    def __init__(self, api_key: str, index_name: str = "synaptech-telemetry"):
        if not _HAS_PINECONE:
            raise RuntimeError("Pinecone SDK not installed. Run: pip install pinecone-client")
        self._pc = Pinecone(api_key=api_key)
        self._index_name = index_name
        self._ensure_index()
        self._index = self._pc.Index(index_name)

    @classmethod
    def available(cls) -> bool:
        return _HAS_PINECONE

    @classmethod
    def from_env(cls) -> "PineconeClient":
        if not _HAS_PINECONE:
            raise RuntimeError("Pinecone SDK not installed. Run: pip install pinecone-client")
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY environment variable required")
        index = os.environ.get("PINECONE_INDEX", "synaptech-telemetry")
        return cls(api_key=api_key, index_name=index)

    @classmethod
    def get_instance(cls) -> "PineconeClient":
        if cls._instance is None:
            if not _HAS_PINECONE:
                raise RuntimeError("Pinecone SDK not installed")
            cls._instance = cls.from_env()
        return cls._instance

    def _ensure_index(self) -> None:
        existing = [i["name"] for i in self._pc.list_indexes()]
        if self._index_name not in existing:
            logger.info(f"Creating Pinecone index: {self._index_name}")
            self._pc.create_index(
                name=self._index_name,
                dimension=128,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-west-2"),
            )

    def _event_to_vector(self, event: TelemetryEvent) -> list[float]:
        from hashlib import md5
        features = f"{event.operation}:{event.topology_hash or ''}:{event.latency_ms}"
        h = md5(features.encode())
        seed = int(h.hexdigest()[:8], 16)
        import random
        rng = random.Random(seed)
        return [rng.gauss(0, 0.1) for _ in range(128)]

    def upsert_telemetry(self, event: TelemetryEvent) -> None:
        vector = self._event_to_vector(event)
        self._index.upsert(
            vectors=[{
                "id": (
                    f"{event.user_id_hash}:{event.operation}:"
                    f"{int(event.timestamp.timestamp() * 1e6)}"
                ),
                "values": vector,
                "metadata": {
                    "user_id_hash": event.user_id_hash,
                    "operation": event.operation,
                    "latency_ms": event.latency_ms,
                    "resource_usage": str(event.resource_usage),
                    "topology_hash": event.topology_hash or "",
                    "timestamp": event.timestamp.isoformat(),
                },
            }],
            namespace=PINECONE_NAMESPACE,
        )

    def query_similar(
        self,
        operation: str,
        top_k: int = 10,
        filter_dict: Optional[dict] = None,
    ) -> list[dict]:
        import hashlib
        import random
        h = hashlib.md5(operation.encode())
        seed = int(h.hexdigest()[:8], 16)
        rng = random.Random(seed)
        query_vector = [rng.gauss(0, 0.1) for _ in range(128)]

        results = self._index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=PINECONE_NAMESPACE,
            filter=filter_dict,
            include_metadata=True,
        )
        return [
            {
                "id": r["id"],
                "score": r["score"],
                "metadata": r.get("metadata", {}),
            }
            for r in results.get("matches", [])
        ]

    def delete_index(self) -> None:
        self._pc.delete_index(self._index_name)
        logger.info(f"Deleted Pinecone index: {self._index_name}")
