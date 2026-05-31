# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-24

### Added
- Two-region hierarchical Liquid State Machine (Sensory Neuropil 200 + Central Complex 300)
- CSC sparse graph engine with per-edge synaptic delays
- Ridge regression readout with L2 regularization
- FastAPI web server with SSE streaming for real-time inference
- Custom 3D brain visualization (Canvas 2D perspective projection)
- Interactive chat UI with token-by-token streaming
- "Distill" training panel for online learning
- Persistent chat and learning history (JSON)
- CLI trainer (`scripts/train.py`) with temperature/passes/seed customization
- Export/import readout weights to `.npz` files
- Docker deployment with docker-compose
- GitHub Actions CI pipeline (lint + test + Docker build)
- Comprehensive architecture documentation (`docs/ARCHITECTURE.md`)
- Ruff linting configuration
- `.editorconfig` and pre-commit hooks
- `__main__.py` for `python -m flywire_lsm` support

### Changed
- Refactored monolithic `app.py` into thin shim importing from `flywire_lsm` package
- Deprecated standalone `flywire_lsm_text.py` in favor of package API
- Consolidated all hyperparameters into `flywire_lsm/config.py` as single source of truth
- Unified history path to `data/history.json`

### Removed
- Duplicate root-level `index.html` (kept `frontend/index.html`)
- Duplicate root-level `history.json` (kept `data/history.json`)
- Hardcoded absolute file paths

## [0.1.0] — 2026-05-21

### Added
- Initial prototype: monolithic `flywire_lsm_text.py` and `app.py`
- Basic LSM with two-module architecture
- Sparse graph generation and spectral normalization
- Character-level text encoder
- Simple web server with 3D visualization
