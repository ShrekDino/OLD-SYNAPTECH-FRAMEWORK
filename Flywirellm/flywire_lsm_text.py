#!/usr/bin/env python3
"""
FlyWire Connectome — Legacy monolithic entry point (deprecated).

This file re-exports the core LSM components from the canonical
``flywire_lsm`` package.  Use ``scripts/train.py`` for the CLI trainer
or import from ``flywire_lsm`` directly.

Usage
-----
    python scripts/train.py                # preferred CLI trainer
    python -m flywire_lsm.server           # web server
    from flywire_lsm import ReservoirSimulation   # programmatic API
"""

import warnings

warnings.warn(
    "flywire_lsm_text.py is deprecated. Use 'python scripts/train.py' "
    "or import from the 'flywire_lsm' package.",
    DeprecationWarning,
    stacklevel=2,
)

from flywire_lsm import *  # noqa: F401, F403 — re-export everything
from flywire_lsm.simulation import ReservoirSimulation  # noqa: F401, F403

if __name__ == "__main__":

    from flywire_lsm.config import (
        LEAK_RATE_A,
        LEAK_RATE_B,
        N_A,
        N_B,
        SPECTRAL_RADIUS_A,
        SPECTRAL_RADIUS_B,
    )
    from flywire_lsm.logging import get_logger
    from flywire_lsm.simulation import ReservoirSimulation

    _LOG = get_logger()

    _LOG.info("=" * 70)
    _LOG.info("Two-Region Hierarchical LSM — Demo Run (legacy compat)")
    _LOG.info("=" * 70)
    _LOG.info("  N_A=%d (Sensory Neuropil)  α=%.2f  ρ=%.2f  |  "
              "N_B=%d (Central Complex)  α=%.2f  ρ=%.2f",
              N_A, LEAK_RATE_A, SPECTRAL_RADIUS_A,
              N_B, LEAK_RATE_B, SPECTRAL_RADIUS_B)

    sim = ReservoirSimulation()

    BASELINE_TRAIN_TEXT = (
        "The FlyWire Connectome is a two-region hierarchical liquid state machine. "
        "It has five hundred neurons split into two modules. Module A handles fast "
        "sensory input. Module B provides slow deep memory retention. "
        "Hello there! How are you today? I am doing well thank you for asking. "
        "What is your name? My name is FlyWire. I am a brain simulation. "
        "Can you help me with this task? Yes I can help you with it. "
        "What is the answer to the question? The answer is forty two. "
        "Where is the library located? It is on the left side of the building. "
        "The quick brown fox jumps over the lazy dog near the river. "
        "She sells sea shells by the sea shore. The shells she sells are sea shells. "
        "The rain in Spain falls mainly on the plain. That is a fact. "
        "The end of the training text is here. Thank you for reading it."
    )
    sim.train_readout(BASELINE_TRAIN_TEXT, num_passes=2)

    _LOG.info("")
    sim.generate(seed_text="Hello there how are you", max_gen_len=30)

    _LOG.info("")
    _LOG.info("=" * 70)
    _LOG.info("DEMO COMPLETE")
    _LOG.info("=" * 70)
