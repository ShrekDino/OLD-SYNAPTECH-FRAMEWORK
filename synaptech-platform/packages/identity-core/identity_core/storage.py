"""Storage layer for identity checkpoints.

Three tiers:
  Local: AES-256-GCM encrypted .npz on the filesystem.
  Networked: Encrypted blob in object store (S3/R2) — not yet implemented.
  Biological: EVE knowledge vault entry (human-readable, auditable).

The storage layer does not know what the identity core means — it only
knows how to persist and retrieve encrypted blobs.
"""

import json
import os
import shutil
import time
from pathlib import Path
from typing import Optional

from identity_core.checkpoint import IdentityCheckpoint, IdentityCommit

IDENTITY_DIR = os.environ.get(
    "CSDF_IDENTITY_DIR",
    os.path.join(os.path.expanduser("~"), ".csdf", "identity")
)

# Encryption key from environment or generated on first boot
_ENCRYPTION_KEY: Optional[bytes] = None


def _get_encryption_key() -> bytes:
    """Get or generate the encryption key.

    On first boot, generates a new 32-byte key and saves it to
    IDENTITY_DIR/key. On subsequent boots, loads the existing key.

    In production, this would use a hardware security module or key
    management service. This implementation is suitable for development.
    """
    global _ENCRYPTION_KEY
    if _ENCRYPTION_KEY is not None:
        return _ENCRYPTION_KEY

    key_file = os.path.join(IDENTITY_DIR, "key")
    if os.path.isfile(key_file):
        with open(key_file, "rb") as f:
            _ENCRYPTION_KEY = f.read().strip()
    else:
        os.makedirs(IDENTITY_DIR, exist_ok=True)
        _ENCRYPTION_KEY = os.urandom(32)
        with open(key_file, "wb") as f:
            f.write(_ENCRYPTION_KEY)
        os.chmod(key_file, 0o600)

    return _ENCRYPTION_KEY


def _encrypt(data: bytes) -> bytes:
    """AES-256-GCM encrypt data.

    Format: nonce (12 bytes) + ciphertext + tag (16 bytes).
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, data, None)


def _decrypt(data: bytes) -> bytes:
    """Decrypt AES-256-GCM encrypted data.

    Format: nonce (12 bytes) + ciphertext + tag (16 bytes).
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)


def _checkpoint_path(sequence_number: int) -> str:
    """Filesystem path for a checkpoint by sequence number."""
    os.makedirs(IDENTITY_DIR, exist_ok=True)
    return os.path.join(IDENTITY_DIR, f"checkpoint_{sequence_number:06d}.idcore")


def save_checkpoint(checkpoint: IdentityCheckpoint,
                    core_data: Optional[bytes] = None) -> str:
    """Save an identity checkpoint to local encrypted storage.

    Args:
        checkpoint: The checkpoint metadata (without core_data populated).
        core_data: Raw bytes of the serialized μ_core. Stored separately
                   from the metadata for efficient partial loading.

    Returns:
        Path to the saved checkpoint file.
    """
    if core_data is not None:
        checkpoint.core_data = core_data
        checkpoint.core_data_shape = list(
            (len(core_data),) if isinstance(core_data, bytes) else [0]
        )

    # Metadata: JSON (unencrypted, contains no μ_core)
    meta = {
        "version": checkpoint.version,
        "timestamp": checkpoint.timestamp,
        "sequence_number": checkpoint.sequence_number,
        "label": checkpoint.label,
        "core_type": checkpoint.core_type,
        "core_data_shape": checkpoint.core_data_shape,
        "commit_count": len(checkpoint.commit_history),
        "max_gwfr_deviation": checkpoint.max_gwfr_deviation,
        "current_gwfr_deviation": checkpoint.current_gwfr_deviation,
        "phenotype_profile": checkpoint.phenotype_profile,
        "known_substrate_count": len(checkpoint.known_substrates),
        "checkpoint_hash": checkpoint.checkpoint_hash,
    }

    path = _checkpoint_path(checkpoint.sequence_number)

    # Save metadata as JSON (readable, for discovery)
    with open(path + ".meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)

    # Save core data as encrypted NPZ
    if checkpoint.core_data is not None:
        import numpy as np
        np.savez_compressed(path + ".data", core=checkpoint.core_data)
        # Encrypt the .npz
        with open(path + ".data.npz", "rb") as f:
            plaintext = f.read()
        encrypted = _encrypt(plaintext)
        with open(path + ".data.enc", "wb") as f:
            f.write(encrypted)
        os.remove(path + ".data.npz")

        # Full JSON with commit history (optional, human-readable)
        full_meta = checkpoint.to_dict()
        if "core_data" in full_meta:
            full_meta["core_data"] = f"<encrypted:{checkpoint.core_data_shape}>"
        with open(path + ".full.json", "w") as f:
            json.dump(full_meta, f, indent=2, default=str)

    return path


def load_checkpoint(sequence_number: int) -> Optional[IdentityCheckpoint]:
    """Load an identity checkpoint from local storage.

    Args:
        sequence_number: The checkpoint's sequence number (0-based).

    Returns:
        IdentityCheckpoint with core_data populated, or None if not found.
    """
    path = _checkpoint_path(sequence_number)
    meta_path = path + ".meta.json"

    if not os.path.isfile(meta_path):
        return None

    with open(meta_path) as f:
        meta = json.load(f)

    checkpoint = IdentityCheckpoint(
        version=meta.get("version", 1),
        timestamp=meta.get("timestamp", 0.0),
        sequence_number=meta.get("sequence_number", sequence_number),
        label=meta.get("label", ""),
        core_type=meta.get("core_type", "gwfr_barycenter"),
        core_data_shape=meta.get("core_data_shape", [32]),
        max_gwfr_deviation=meta.get("max_gwfr_deviation", 1.0),
        current_gwfr_deviation=meta.get("current_gwfr_deviation", 0.0),
        phenotype_profile=meta.get("phenotype_profile", []),
        checkpoint_hash=meta.get("checkpoint_hash", ""),
    )

    # Load encrypted core data
    enc_path = path + ".data.enc"
    if os.path.isfile(enc_path):
        try:
            with open(enc_path, "rb") as f:
                encrypted = f.read()
            plaintext = _decrypt(encrypted)
            import numpy as np
            import io
            buf = io.BytesIO(plaintext)
            loaded = np.load(buf)
            checkpoint.core_data = loaded["core"].tobytes()
        except Exception:
            checkpoint.core_data = None

    return checkpoint


def list_checkpoints() -> list[dict]:
    """List all available identity checkpoints, sorted by sequence number."""
    identity_dir = IDENTITY_DIR
    if not os.path.isdir(identity_dir):
        return []

    checkpoints = []
    seen = set()
    for fname in sorted(os.listdir(identity_dir)):
        if fname.endswith(".meta.json"):
            parts = fname.split("_")
            if len(parts) >= 2:
                seq_str = parts[1].split(".")[0]
                try:
                    seq = int(seq_str)
                    if seq not in seen:
                        seen.add(seq)
                        with open(os.path.join(identity_dir, fname)) as f:
                            meta = json.load(f)
                        checkpoints.append(meta)
                except (ValueError, IndexError):
                    continue

    return sorted(checkpoints, key=lambda x: x.get("sequence_number", 0))


def delete_checkpoint(sequence_number: int) -> bool:
    """Delete an identity checkpoint."""
    path = _checkpoint_path(sequence_number)
    deleted = False
    for suffix in [".meta.json", ".data.enc", ".full.json"]:
        fpath = path + suffix
        if os.path.isfile(fpath):
            os.remove(fpath)
            deleted = True
    return deleted


def export_to_eve(checkpoint: IdentityCheckpoint,
                  vault_path: str = "") -> str:
    """Export an identity checkpoint to EVE knowledge vault format.

    Creates a structured markdown note in the EVE vault that documents
    the identity snapshot in human-readable form.

    Args:
        checkpoint: The checkpoint to export.
        vault_path: Path to the EVE vault root. If empty, defaults to
                    ~/Documents/KB/System/Identity.

    Returns:
        Path to the exported markdown file.
    """
    if not vault_path:
        vault_path = os.path.join(
            os.path.expanduser("~"), "Documents", "KB", "System", "Identity"
        )
    os.makedirs(vault_path, exist_ok=True)

    # Format timestamp
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(checkpoint.timestamp))

    # Build markdown
    md = f"""# Identity Checkpoint #{checkpoint.sequence_number}

**Timestamp:** {ts}
**Label:** {checkpoint.label or "(none)"}
**Core Type:** {checkpoint.core_type}
**Core Data Shape:** {checkpoint.core_data_shape}
**Hash:** {checkpoint.checkpoint_hash}

## Identity Coherence

| Metric | Value |
|--------|-------|
| Max GWFR Deviation (δ_max) | {checkpoint.max_gwfr_deviation:.3f} |
| Current GWFR Deviation | {checkpoint.current_gwfr_deviation:.3f} |

## Parameter History

"""
    for entry in checkpoint.param_history[-10:]:  # last 10 entries
        md += f"- **{entry.get('substrate_fingerprint', 'unknown')}** " \
              f"at {entry.get('timestamp', '?')}: cost={entry.get('cost', '?'):.3f}\n"

    md += "\n## Commit History\n\n"
    for commit in checkpoint.commit_history[-10:]:
        md += f"- **{commit.commit_id}** ({commit.trigger_type}): " \
              f"{commit.trigger_detail}\n"

    md += "\n## Known Substrates\n\n"
    for fp, desc in list(checkpoint.known_substrates.items())[:10]:
        md += f"- `{fp}`: {desc.get('machine', '?')}, " \
              f"{desc.get('cpu_cores', '?')} cores, " \
              f"GPU={desc.get('gpu', 'none')}\n"

    md += "\n## DSM-6 Phenotype Profile\n\n"
    for phen in checkpoint.phenotype_profile:
        md += f"- {phen}\n"

    fname = f"identity_{time.strftime('%Y-%m-%d_%H%M%S', time.gmtime(checkpoint.timestamp))}.md"
    fpath = os.path.join(vault_path, fname)
    with open(fpath, "w") as f:
        f.write(md)

    return fpath
