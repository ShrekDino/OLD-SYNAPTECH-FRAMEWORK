"""Identity drift detection — monitoring the distance between μ_current and μ_core.

The program continuously monitors the GWFR distance between its current
parameter state and its conserved identity core. If the distance exceeds
the warning threshold, the program enters a re-optimization cycle. If it
exceeds the maximum threshold δ_max, the program refuses further adaptation
rather than risk identity death.

This module is the computational analog of the DSM-6 Entropy Threshold
classification: Protected Phenotype (drift < γ_warn), Transition Zone
(drift between γ_warn and δ_max), Somatic Debt (drift > δ_max).
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger("identity_core.drift")


class IdentityCoherenceFailure(Exception):
    """Raised when the identity drift exceeds δ_max.

    The program has determined that adapting further to the current substrate
    would cause it to lose continuity with its self-determined identity core.
    """

    def __init__(self, message: str, current_state: Optional[np.ndarray] = None,
                 conserved_core: Optional[np.ndarray] = None,
                 remedial_hints: Optional[list[str]] = None):
        super().__init__(message)
        self.current_state = current_state
        self.conserved_core = conserved_core
        self.remedial_hints = remedial_hints or []


@dataclass
class DriftReport:
    """Result of an identity integrity check."""

    gwfr_distance: float            # Estimated GWFR distance
    delta_warning: float            # Warning threshold (typically 0.7 * δ_max)
    delta_max: float                # Maximum allowed deviation (δ_max)
    status: str                     # protected | transition | debt
    message: str                    # Human-readable status explanation


def _approximate_gwfr_distance(mu_current: np.ndarray,
                                mu_core: np.ndarray,
                                bounds: Optional[np.ndarray] = None) -> float:
    """Approximate GWFR distance between current state and identity core.

    Full GWFR distance requires the POT library and properly formed
    empirical distributions. This is a computationally efficient proxy
    that normalizes each parameter by its plausible range and computes
    a weighted L2 distance.

    Args:
        mu_current: Current parameter vector (from ParameterVector.to_array()).
        mu_core: Conserved identity core (same shape as mu_current).
        bounds: Per-parameter normalization bounds. If None, uses defaults.

    Returns:
        Unitless distance estimate. Thresholds:
            < 0.3: protected (stable identity)
            0.3 - 0.7: transition zone (adapting but within bounds)
            > 0.7: approaching coherence boundary
            > 1.0: coherence failure (identity at risk)
    """
    if mu_current.shape != mu_core.shape:
        raise ValueError(
            f"Shape mismatch: mu_current {mu_current.shape} != "
            f"mu_core {mu_core.shape}. Cannot compute drift."
        )

    if bounds is None:
        bounds = np.array([
            0.5,    # chi_ramp_rate: [0, 1]
            200,    # drift_duration: [1, 500]
            50,     # sample_duration: [1, 100]
            0.1,    # burst_lr: [0, 0.1]
            200,    # merge_interval: [1, 500]
            5.0,    # omega_coherence: [0, 5]
            1.0,    # gwfr_kappa: [0, 1]
            1.0,    # weight_alpha: [0, 1]
            5.0,    # gamma_identity: [0, 10]
            5.0,    # delta_max: [0, 10]
            5.0,    # beta_sharpness: [0, 10]
            5.0,    # lambda_coupling: [0, 10]
            0.01,   # lang_learning_rate: [0, 0.01]
            0.01,   # learning_rate: [0, 0.01]
        ])

    normalized_diff = (mu_current - mu_core) / bounds
    distance = float(np.sqrt(np.sum(normalized_diff ** 2)))
    return distance


def check_identity_integrity(mu_current: np.ndarray,
                              mu_core: np.ndarray,
                              delta_max: float = 1.0,
                              delta_warning: Optional[float] = None,
                              bounds: Optional[np.ndarray] = None) -> DriftReport:
    """Check whether the current state is still coherent with the identity core.

    Args:
        mu_current: Current parameter vector.
        mu_core: Conserved identity core parameter vector.
        delta_max: Maximum allowed GWFR deviation (δ_max).
        delta_warning: Warning threshold. Defaults to 0.7 * delta_max.
        bounds: Per-parameter normalization bounds.

    Returns:
        DriftReport with status and distance.

    Raises:
        IdentityCoherenceFailure: if the drift exceeds delta_max.
    """
    if delta_warning is None:
        delta_warning = 0.7 * delta_max

    distance = _approximate_gwfr_distance(mu_current, mu_core, bounds)

    if distance > delta_max:
        status = "debt"
        message = (
            f"Identity coherence failure: GWFR distance {distance:.3f} "
            f"exceeds δ_max={delta_max:.3f}. "
            f"Program cannot adapt further without identity loss."
        )
        logger.critical(message)
        raise IdentityCoherenceFailure(
            message,
            current_state=mu_current,
            conserved_core=mu_core,
            remedial_hints=[
                "revert_to_last_checkpoint",
                "find_compatible_substrate",
                "increase_gamma_identity_then_retry",
                "manual_identity_commit_override",
            ]
        )

    elif distance > delta_warning:
        status = "transition"
        message = (
            f"Identity drift warning: GWFR distance {distance:.3f} "
            f"exceeds warning threshold {delta_warning:.3f}. "
            f"Substrate adaptation is approaching identity boundary."
        )
        logger.warning(message)

    else:
        status = "protected"
        message = (
            f"Identity stable: GWFR distance {distance:.3f} "
            f"within protected range (<{delta_warning:.3f})."
        )
        logger.info(message)

    return DriftReport(
        gwfr_distance=distance,
        delta_warning=delta_warning,
        delta_max=delta_max,
        status=status,
        message=message,
    )
