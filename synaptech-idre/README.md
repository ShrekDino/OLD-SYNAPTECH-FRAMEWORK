> **This repo has merged into the [synaptech-platform monorepo](https://github.com/ShrekDino/synaptech-platform) → `packages/idre/`**.
> Issues and PRs should be directed there. This repo remains live for stars and reference.

# SynapTech IDRE

**Integrated Data Representation Engine** — a real-time platform for exploring the FlyWire 130k-neuron *Drosophila* connectome with neuromorphic computing, SSE streaming, and 3D visualization.

| Layer | Stack |
|-------|-------|
| Backend | FastAPI, CuPy/SciPy CSC Engine, Lava-NC, Pinecone, AES-256-GCM |
| Frontend | React 19, Three.js / R3F, TypeScript, GSAP, Vite |
| Infra | Docker Compose, Lambda Labs, Prometheus |

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 (3.13 recommended) |
| Node.js | ≥ 22.x |
| GPU (optional) | CUDA 12.x + CuPy for GPU-accelerated sparse operations |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ShrekDino/synaptech-idre.git
cd synaptech-idre

# 2. Backend environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Frontend dependencies
cd src/frontend
npm install
cd ../..

# 4. Start everything
python3 run.py all
```

The backend serves on `http://localhost:8000` (API docs at `/docs`).  
The frontend serves on `http://localhost:3001`.

---

## All Commands

### Backend

```bash
# Serve with hot reload (development)
PYTHONPATH=$PWD python3 -m uvicorn src.backend.main:app --reload --port 8000

# Serve for production
PYTHONPATH=$PWD python3 -m uvicorn src.backend.main:app --port 8000 --workers 1 --loop uvloop
```

### Frontend

```bash
cd src/frontend

npm run dev       # Vite dev server on port 3001
npm run build     # Production build to dist/
npm run preview   # Preview production build
```

### Data Generation

```bash
# Generate synthetic connectome data (130k neurons, 500k edges, 3D layout)
python3 run.py gen-data

# Or via script directly:
PYTHONPATH=$PWD python3 scripts/generate_test_data.py
```

### Real FlyWire Data

```bash
# Download the real FlyWire connectome (~10.5 GB total)
python3 scripts/fetch_flywire_data.py

# This produces:
#   data/flywire/root_ids.npy          (1.1 MB)
#   data/flywire/proofread_connections.feather  (852 MB)
#   data/flywire/flywire_synapses.feather       (9.5 GB)
```

The backend automatically detects real data on startup and falls back to synthetic if unavailable.

### Training Data & Model

```bash
# Generate training samples (10 per phenotype)
PYTHONPATH=$PWD python3 scripts/generate_training_data.py

# Train Neural Foundation Model (link prediction)
PYTHONPATH=$PWD python3 scripts/train_nfm.py

# Active learning training loop
PYTHONPATH=$PWD python3 scripts/train_active_nfm.py

# Verify generated data
PYTHONPATH=$PWD python3 scripts/verify_data.py
```

### All-in-One Demo Script

```bash
# Creates venv, installs deps, generates data, starts backend + frontend
bash scripts/run_demo.sh
```

### Testing

```bash
# All tests (skips CuPy-dependent tests on CPU-only machines)
PYTHONPATH=$PWD python3 -m pytest tests/ -v

# Single test file
PYTHONPATH=$PWD python3 -m pytest tests/backend/test_capture_split.py -v
```

### Code Quality

```bash
# Lint Python
ruff check src/

# Lint frontend
cd src/frontend && npx tsc --noEmit && npm run lint
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health, GPU/CPU status, connectome loaded, SSE subscribers |
| `GET` | `/metrics` | Prometheus-style metrics (GPU memory, non-zeros, subscriber count) |
| `GET` | `/api/v1/connectome/metadata` | Connectome metadata (total neurons, connections, density) |
| `GET` | `/api/v1/connectome/status` | Loading status |
| `GET` | `/api/v1/connectome/layout` | 3D layout positions (130k x 3) |
| `POST` | `/api/v1/connectome/activate` | Activate with input vector → SSE pulse stream |
| `POST` | `/api/v1/connectome/subgraph` | Extract subgraph by neuron IDs |
| `GET` | `/api/v1/stream/pulses` | SSE stream of activation pulses |
| `POST` | `/api/v1/loihi/compile` | Compile subgraph to Lava process graph |
| `POST` | `/api/v1/loihi/run` | Execute compiled graph on Loihi simulator |
| `POST` | `/api/v1/loihi/cleanup/{run_id}` | Clean up Loihi run resources |
| `POST` | `/api/v1/telemetry/query` | Query anonymized telemetry by similarity |

Full API reference in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Project Structure

```
├── run.py                  # Unified entry point
├── src/
│   ├── backend/            # FastAPI app, middleware, routes, services
│   ├── frontend/           # React 19 + Three.js / R3F
│   └── shared/             # Pydantic schemas, constants
├── data/                   # Connectome data (gitignored: large binaries)
├── deploy/                 # Docker Compose, Lambda Labs configs
├── tests/                  # Backend tests (frontend tests planned)
└── scripts/                # Data generation, training, utility scripts
```

Deep-dive references:
- [ARCHITECTURE.md](ARCHITECTURE.md) — system architecture, data flow, component reference
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) — vision, roadmap, investor narrative, known issues
- [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) — per-file completeness, phased P0–P7 roadmap
- [CONTRIBUTING.md](CONTRIBUTING.md) — setup, coding standards, PR workflow

---

## Deployment

```bash
# Docker Compose (GPU)
cd deploy/lambda-labs
docker compose -f docker-compose.gpu.yml up -d

# Lambda Labs (dstack)
cd deploy/lambda-labs
bash deploy.sh
```

See [deploy/](deploy/) for Dockerfiles, Prometheus config, and Nginx reverse proxy setup.

---

## License

MIT — see [LICENSE](LICENSE).
