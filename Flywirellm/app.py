#!/usr/bin/env python3
"""
FlyWire Connectome — Web Application (legacy shim).

This module re-exports the FastAPI application from the canonical
``flywire_lsm.server`` module.  It exists only for backward compatibility.

Usage
-----
    python -m flywire_lsm.server          # preferred
    python app.py                         # legacy (delegates to package)
"""

import warnings

warnings.warn(
    "app.py is a legacy wrapper. Use 'python -m flywire_lsm.server' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from flywire_lsm.server import app  # noqa: E402, F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("flywire_lsm.server:app", host="0.0.0.0", port=8000, reload=False)
