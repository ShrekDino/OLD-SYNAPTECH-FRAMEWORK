from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

MAX_N_NEURONS = 200_000


class Neuron(BaseModel):
    id: int = Field(..., ge=0, lt=MAX_N_NEURONS)
    pos: List[float] = Field(..., min_length=3, max_length=3)
    color: Optional[str] = "#4488ff"


class Edge(BaseModel):
    source: int = Field(..., ge=0, lt=MAX_N_NEURONS)
    target: int = Field(..., ge=0, lt=MAX_N_NEURONS)
    weight: float = Field(default=1.0, ge=0.0)


class ConnectomeMetadata(BaseModel):
    n_neurons: int = MAX_N_NEURONS
    n_synapses: int
    format: str = "CSC"
    source: str = "FlyWire"
    version: str = "v1.0"


class ActivationInput(BaseModel):
    input_vector: List[float] = Field(
        ..., min_length=1, max_length=MAX_N_NEURONS,
        description="Activation vector (length = n_neurons)"
    )
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class ActivationResult(BaseModel):
    output_vector: List[float]
    spike_count: int
    latency_ms: float


class PulseBatch(BaseModel):
    neuron_ids: List[int]
    voltages: List[float]
    spikes: List[bool]
    ts: float = Field(default_factory=lambda: datetime.utcnow().timestamp)


class SSEFrame(BaseModel):
    batch: PulseBatch
    ts: float


class SubgraphRequest(BaseModel):
    neuron_ids: List[int] = Field(..., min_length=1, max_length=10_000)


class SubgraphResponse(BaseModel):
    adjacency: List[List[float]]
    neuron_ids: List[int]


class CompileRequest(BaseModel):
    neuron_ids: List[int] = Field(..., min_length=1, max_length=10_000)
    backend: str = Field(default="sim", pattern="^(sim|loihi2)$")


class CompileResponse(BaseModel):
    run_id: str
    backend: str
    n_neurons: int


class RunRequest(BaseModel):
    run_id: str
    num_steps: int = Field(default=100, ge=1, le=1_000_000)


class RunResponse(BaseModel):
    run_id: str
    spikes: List[int]
    step_count: int


class TelemetryEvent(BaseModel):
    user_id_hash: str
    operation: str
    latency_ms: float
    resource_usage: dict[str, float]
    topology_hash: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TelemetryQuery(BaseModel):
    similar_operation: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100)


class TelemetryQueryResult(BaseModel):
    results: List[dict[str, Any]]
    count: int


class AlignmentRequest(BaseModel):
    edge_list: List[Edge]
    source_dataset: str
    target_dataset: str


class AlignmentResponse(BaseModel):
    aligned_edges: List[Edge]
    id_mapping: dict[int, int]
    confidence: float


class EncryptedBlob(BaseModel):
    ciphertext: bytes
    nonce: bytes
    tag: bytes
    key_id: str
    s3_uri: str
