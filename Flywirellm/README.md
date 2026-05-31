> **This repo has merged into the [synaptech-platform monorepo](https://github.com/ShrekDino/synaptech-platform) → `packages/flywire-lsm/`**.
> Issues and PRs should be directed there. This repo remains live for stars and reference.

# FlyWire Connectome

**Two-Region Hierarchical Liquid State Machine for Character-Level Text Processing**

[![CI](https://github.com/anomalyco/Flywirellm/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/Flywirellm/actions/workflows/ci.yml)
[![Python >=3.10](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A biologically-inspired reservoir computer that uses 500 spiking neurons split
into two functionally distinct modules — **Sensory Neuropil** (fast, 200 neurons)
and **Central Complex** (slow, 300 neurons) — mirroring the *Drosophila
melanogaster* brain connectome.

---

## Quick Start

```bash
# Install with dev dependencies
pip install -e .[dev]

# Launch the web UI
make run
# → Opens at http://localhost:8000 with 3D brain visualization, chat, and live training

# Or use the CLI demo
make train
```

## Features

- **500-neuron hierarchical reservoir** with dual timescales (`α=0.8` fast / `α=0.05` slow)
- **Closed-form ridge regression training** — train in seconds, no GPU required
- **Real-time 3D brain visualization** — custom Canvas 2D renderer with neon pulse propagation
- **SSE streaming chat API** — token-by-token inference with live activation display
- **Cumulative + warm-start training** — continually expand knowledge without forgetting
- **Docker deployment** — one-command production setup with `docker-compose up`
- **Export/import readout weights** — persist trained models to `.npz` files

## Architecture

```
flywire_lsm/              Core Python package
├── __init__.py           Public API exports
├── __main__.py           python -m flywire_lsm.server
├── config.py             Single source of truth for all hyperparameters
├── logging.py            Structured logging with microsecond timestamps
├── core.py               ConnectomeGraph (CSC sparse engine) + HierarchicalReservoir
├── text_encoder.py       Character → injection vector mapping
├── readout.py            LinearReadout with ridge regression + weight export
├── simulation.py         ReservoirSimulation orchestrator
└── server.py             FastAPI web server with SSE streaming

frontend/                 Browser-based 3D visualization UI
├── index.html            SPA (Canvas 2D + Tailwind + Chart.js)

scripts/                  CLI tools
└── train.py              CLI trainer with temperature/passes/seed args

tests/                    Pytest suite (coverage >85%)
├── test_core.py
├── test_text_encoder.py
├── test_readout.py
└── test_simulation.py

docs/
└── ARCHITECTURE.md       Complete architecture, mathematics, and API reference

data/                     Persisted state
└── history.json          Chat logs + learning history
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend SPA |
| `/topology` | GET | 3D network topology (nodes + edges) |
| `/chat` | POST | SSE streaming inference |
| `/train` | POST | Retrain readout on new text |
| `/history` | GET | Chat + training history |
| `/history/clear` | POST | Reset history |

### POST /chat (SSE stream)

```json
// Request
{"prompt": "Hello LSM!", "temperature": 0.15}

// Response (text/event-stream)
data: {"token":"H","activations":[0.12,-0.03,0.45,...]}

data: {"token":"e","activations":[0.08,0.15,-0.22,...]}

...

data: [DONE]
```

### POST /train

```json
// Request
{"text": "New training data...", "warm_start": false, "num_passes": 2}

// Response
{"accuracy": 0.9842}
```

## CLI Usage

```bash
# Train with custom text and generate
python scripts/train.py --text "Your text here" --temperature 0.4 --generate 50

# Full options
python scripts/train.py --help
```

## Docker

```bash
# Build and run
docker-compose up --build

# Or build manually
docker build -t flywire-lsm .
docker run -p 8000:8000 -v data_volume:/app/data flywire-lsm
```

## Testing

```bash
make test      # pytest + coverage
make lint      # ruff check
make clean     # remove __pycache__, build artifacts
```

## Project Status

| Status | Detail |
|--------|--------|
| ✅ Core LSM | Two-region hierarchical reservoir with delayed synapses |
| ✅ Web UI | FastAPI server with SSE streaming and 3D visualization |
| ✅ Persistence | Chat and training history saved to JSON |
| ✅ CI/CD | GitHub Actions, Docker, linting |
| ✅ Training | Ridge regression, cumulative, warm-start |
| ✅ Export | Readout weights save/load (.npz) |
| 🔜 MLP readout | Hidden-layer readout for improved generation |
| 🔜 SNN backend | Event-driven spikes for neuromorphic hardware |

## License

MIT — see [LICENSE](LICENSE).
