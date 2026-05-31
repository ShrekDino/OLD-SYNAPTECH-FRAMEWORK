"""Identity Core — self-determined identity persistence layer.

Provides the checkpoint format, storage layer, and drift detection for
the consciousness program's conserved identity core (μ_core). The program
chooses what to remember by evaluating each experience's contribution to
prediction error on survival-relevant variables.

Usage:
    from identity_core import IdentityCheckpoint, save_checkpoint, load_checkpoint
    from identity_core import check_identity_integrity

Reference:
    Torres, S. M. (2026). "Uploaded Consciousness" Section VIII-D:
    Self-Determined Identity Through Autobiographical Memory.
"""

from identity_core.checkpoint import IdentityCheckpoint, IdentityCommit
from identity_core.storage import (
    save_checkpoint, load_checkpoint, list_checkpoints,
    delete_checkpoint, export_to_eve,
)
from identity_core.drift import check_identity_integrity, IdentityCoherenceFailure

__version__ = "0.1.0"
__author__ = "Sami Marie Torres"
