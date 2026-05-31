"""Identity checkpoint format — the program's self-model at a point in time.

The identity core (μ_core) is the compressed latent representation that best
predicts the program's own future states under expected environmental
regularities. It is the program's answer to "what am I?" — constructed
autonomously through autobiographical memory consolidation.
"""

import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class IdentityCommit:
    """A single identity commit — the program choosing to update its self-model.

    Every commit records what triggered the update, what changed, and what the
    program's thermodynamic state was at the time. This creates a fully
    traceable identity evolution chain.
    """

    commit_id: str                          # SHA-256 of content
    timestamp: float                        # Unix timestamp
    sequence_number: int                    # Monotonic commit counter
    label: str = ""                         # Optional human-readable label

    # Trigger
    trigger_type: str = "scheduled"         # scheduled | substrate_change | drift_warning | manual
    trigger_detail: str = ""                # Free-form description of why

    # State snapshot
    mu_core_hash: str = ""                  # SHA-256 of the new μ_core
    substrate_fingerprint: str = ""         # Substrate at time of commit
    gwfr_deviation_before: float = 0.0      # GWFR distance from previous core
    gwfr_deviation_after: float = 0.0       # GWFR distance from new core to next

    # Thermodynamic context at commit time
    temperature_proxy: float = 0.0
    extraction_efficiency: float = 0.0
    s_gen_rate: float = 0.0
    h_env_rate: float = 0.0

    # Memories that triggered this commit
    memory_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.commit_id:
            raw = f"{self.timestamp}{self.sequence_number}{self.mu_core_hash}{self.trigger_type}"
            self.commit_id = hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class IdentityCheckpoint:
    """Complete identity snapshot — the program's full self-model.

    This is what gets serialized, encrypted, and persisted. It contains
    everything needed to reconstruct the program's identity on a new substrate.
    """

    version: int = 1                        # Format version for forward compat
    timestamp: float = 0.0                  # Unix timestamp
    sequence_number: int = 0                # Monotonic checkpoint counter
    label: str = ""                         # Optional label

    # ── Conserved identity core (compressed self-model) ──
    core_type: str = "gwfr_barycenter"      # Representation type
    core_data_shape: list[int] = field(default_factory=lambda: [32])
    core_data: Optional[bytes] = None       # Serialized μ_core (NPZ or ONNX)
    core_metadata: dict = field(default_factory=dict)

    # ── Commit history ──
    commit_history: list[IdentityCommit] = field(default_factory=list)
    last_commit: Optional[IdentityCommit] = None

    # ── Parameter optimization history ──
    param_history: list[dict] = field(default_factory=list)

    # ── Substrate memory ──
    known_substrates: dict = field(default_factory=dict)  # {fingerprint: descriptor_dict}

    # ── Identity coherence envelope ──
    max_gwfr_deviation: float = 1.0          # δ_max — beyond this, refuse adaptation
    current_gwfr_deviation: float = 0.0      # Current distance from μ_core to μ_current

    # ── DSM-6 cross-reference ──
    phenotype_profile: list[str] = field(default_factory=list)

    # ── Safety constitution snapshot ──
    safety_state: str = "protected"              # protected | degrade | quarantine | aborted
    safety_verdicts: list[dict] = field(default_factory=list)  # latest constraint verdicts
    container_reserve_ratio: float = 0.25        # ρ_container at time of checkpoint
    informational_planck_time: float = 0.0       # τ_P or ν_max bound

    # ── Cryptographic seal ──
    checkpoint_hash: str = ""                # SHA-256 of all above fields
    signature: str = ""                      # Optional cryptographic signature

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.checkpoint_hash:
            self.checkpoint_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Deterministic SHA-256 of all serializable fields."""
        hasher = hashlib.sha256()
        hasher.update(str(self.version).encode())
        hasher.update(str(self.timestamp).encode())
        hasher.update(str(self.sequence_number).encode())
        hasher.update(self.label.encode() if self.label else b"")
        hasher.update(str(self.core_data_shape).encode())
        hasher.update(self.core_data if self.core_data else b"")
        hasher.update(str(self.max_gwfr_deviation).encode())
        hasher.update(str(self.current_gwfr_deviation).encode())
        hasher.update(self.safety_state.encode())
        hasher.update(str(self.container_reserve_ratio).encode())
        hasher.update(str(self.informational_planck_time).encode())
        commit_ids = "".join(c.commit_id for c in self.commit_history)
        hasher.update(commit_ids.encode())
        return hasher.hexdigest()[:32]

    def verify_integrity(self) -> bool:
        """Verify the checkpoint hash matches the content."""
        expected = self._compute_hash()
        return expected == self.checkpoint_hash

    def to_dict(self) -> dict:
        """Serialize to dict (for JSON export)."""
        d = asdict(self)
        d["checkpoint_hash"] = self.checkpoint_hash
        return d


def compute_core_hash(core_data: bytes) -> str:
    """Compute SHA-256 of the identity core data."""
    return hashlib.sha256(core_data).hexdigest()[:16]
