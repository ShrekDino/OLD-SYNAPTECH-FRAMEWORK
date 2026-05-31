# SynapTech IDRE — Architecture & Implementation

This document describes the SynapTech Integrated Data Representation Engine (IDRE), covering every component, data flow, design decision, and deployment path. It is written for another AI engineer or LLM to read, understand, and extend the codebase with zero prior context.

---

## 1. System Overview

SynapTech IDRE is a real-time 130,000-neuron connectome visualization and computation engine. It loads the FlyWire *Drosophila* brain graph as a GPU-accelerated Compressed Sparse Column (CSC) matrix, exposes REST + SSE endpoints for activation and exploration, streams high-dimensional neural pulse data to a browser-based Three.js 3D viewer, and provides a neuromorphic bridge to Intel Loihi via the Lava framework. A Data Capture Split Layer separates proprietary user IP (encrypted to S3) from anonymized workflow telemetry (vector-indexed in Pinecone).

### High-Level Data Flow

```
Browser (Three.js R3F)
      │ ▲
      │ │ SSE (text/event-stream) — 1000-pulse batches at 8ms intervals
      ▼ │
FastAPI (Uvicorn, 1 worker)
      │
      ├─ POST /activate ──→ CSCEngine.activate() ──→ cuSPARSE spMV (~1ms GPU / ~10ms CPU)
      │                           │
      │                           ▼
      │                     SSEStreamer.publish() ──→ asyncio.Queue fan-out
      │
      ├─ POST /subgraph ──→ CSCEngine.subgraph() ──→ matrix slice
      │
      ├─ POST /loihi/compile ──→ LavaBridge.compile_subgraph() ──→ Lava Process graph
      ├─ POST /loihi/run     ──→ LavaBridge.run() ──→ Loihi1SimCfg / Loihi2HwCfg
      │
      ├─ POST /telemetry/query ──→ PineconeClient.query_similar() ──→ vector search
      │
      └─ [CaptureSplit Middleware]
             ├─ User IP data → AES-256-GCM → S3/MinIO
             └─ Anonymized telemetry → Pinecone upsert
```

---

## 2. Quick Start

```bash
# Prerequisites: Python 3.11+, Node.js 20+, NVIDIA GPU optional

# 1. Clone (you are here)
cd /home/cinni/SynapTech_IDRE

# 2. Create venv and install deps
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pydantic pydantic-settings numpy pandas scipy httpx cryptography

# 3. Generate test data (130k neurons, 500k edges, 3D layout)
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.generate_test_data import main; main()
"

# 4. Start backend
PYTHONPATH=$PWD python3 -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000

# 5. Start frontend (separate terminal)
cd src/frontend
npm install
npx vite --host 0.0.0.0 --port 3001

# 6. Open http://localhost:3001 in your browser
```

### Real FlyWire Data (Production Use)

The codebase can load the real FlyWire whole-brain connectome from Zenodo (DOI: 10.5281/zenodo.10676866, CC BY 4.0) instead of synthetic data.

```bash
# Download real data (~10.5 GB total)
python3 scripts/fetch_flywire_data.py

# Start backend — auto-detects real data and loads it
PYTHONPATH=$PWD python3 -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
```

**What it downloads:**
| File | Size | Content |
|------|------|---------|
| `proofread_root_ids_783.npy` | 1.1 MB | All 139,255 proofread neuron IDs |
| `proofread_connections_783.feather` | 852 MB | 3.7M neuron↔neuron connections with syn_count + neuropil |
| `flywire_synapses_783.feather` | 9.5 GB | All ~130M individual synapses with 3D EM coordinates |

**Pipeline:** The download script extracts per-neuron 3D positions as centroids of pre-synaptic sites from the 9.5 GB synapse file, then writes `data/layout.json` (same format as synthetic). The backend's `connectome_loader.load_real_flywire()` maps 64-bit FlyWire root IDs to sequential CSC indices via `np.searchsorted`, builds the CSC matrix from the edge list, and loads the positions. If `data/flywire/proofread_connections.feather` is absent, the backend transparently falls back to the synthetic 500k-edge graph.

**Architecture impact:** 3.7M connections expands the CSC matrix from ~60 MB to ~120 MB (well within 12 GB RTX 3060 VRAM). spMV on CPU goes from ~11 ms to ~120 ms; GPU (cuSPARSE) brings it back to ~10 ms.

**Schema compatibility:** All shared schemas (`src/shared/schemas.py`) use `MAX_N_NEURONS = 200_000` to accommodate both synthetic (130k) and real (139k) sizes. The `ActivationInput` vector length is validated dynamically at runtime.

---

## 3. Directory Map

```
synaptech-idre/
├── ARCHITECTURE.md                          # This file
├── run.py                                   # Root entry: `python run.py backend|frontend|gen-data|all`
├── pyproject.toml                           # Project metadata, optional deps
├── requirements.txt                         # Pip install list
├── .env.example                             # All config keys with defaults
│
├── src/
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── constants.py                     # N_NEURONS=130000, SSE_BATCH_SIZE=1000, etc.
│   │   └── schemas.py                       # All Pydantic models: Neuron, Edge, PulseBatch,
│   │                                         #   ActivationInput/Result, SubgraphRequest/Response,
│   │                                         #   CompileRequest/Response, TelemetryEvent, etc.
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app creation, lifespan, CuPy detection,
│   │   │                                       router registration, CORS, /health, /metrics
│   │   ├── config.py                        # Pydantic Settings (reads .env or env vars)
│   │   ├── exceptions.py                    # IDREException hierarchy + FastAPI handler
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                      # JWT + API key validation (optional, bypasses /health/docs)
│   │   │   └── capture_split.py             # ASGI middleware: forks request body →
│   │   │                                        encryption_service (AES-256-GCM) + telemetry_anon (→Pinecone)
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── connectome.py                # /api/v1/connectome/{metadata,status,layout,activate,subgraph}
│   │   │   ├── visualization.py             # /api/v1/stream/pulses (SSE endpoint)
│   │   │   ├── neuromorphic.py              # /api/v1/loihi/{compile,run,cleanup,status}
│   │   │   └── telemetry.py                 # /api/v1/telemetry/{status,query}
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── csc_engine.py                # Core: CSCMatrix abstraction with CuPy/SciPy fallback
│   │       ├── connectome_loader.py          # FlyWire file discovery, COO→CSC loading, layout loading
│   │       ├── sse_streamer.py              # Async queue fan-out SSE publisher
│   │       ├── encryption.py                # AES-256-GCM encrypt/decrypt (cryptography.hazmat)
│   │       ├── telemetry_anon.py             # PII stripper, user_id hasher, topology_hash compute
│   │       ├── pinecone_client.py            # Pinecone Index wrapper (conditional import)
│   │       ├── lava_bridge.py                # Lava RunConfig factory, compile/run lifecycle
│   │       ├── lava_processes.py             # FlyWireNetwork dataclass, LoihiProtocol LIF model
│   │       └── deepseek_aligner.py           # DeepSeek-V4 API client for 1M-context alignment
│   │
│   └── frontend/
│       ├── package.json                     # React 19, Three.js, R3F, Drei, Zustand, Vite
│       ├── tsconfig.json
│       ├── vite.config.ts                   # Proxy /api, /stream, /health → backend
│       ├── index.html
│       └── src/
│           ├── main.tsx                     # ReactDOM.createRoot
│           ├── App.tsx                      # Top-level: selectedNeuron state, activate handlers
│           ├── types/connectome.ts          # TypeScript interfaces: Neuron, PulseBatch, GraphLayout
│           ├── components/
│           │   ├── BrainViewer.tsx          # R3F Canvas, SceneContent, OrbitControls
│           │   ├── NeuronInstances.tsx      # <instancedMesh> with raycast selection, per-instance color
│           │   ├── ControlPanel.tsx         # SSE toggle, neuron info, threshold slider, action buttons
│           │   └── ActivationPulse.tsx      # Pulse glow effect (additive blending, decay animation)
│           ├── hooks/
│           │   ├── useSSE.ts               # EventSource → Zustand store, auto-reconnect
│           │   └── useGraphLayout.ts       # Fetch layout from backend, refine in Web Worker
│           └── shaders/
│               ├── vertex.glsl              # Instance color + pulse intensity vertex shader
│               └── fragment.glsl            # Point sprite with glow
│
├── scripts/
│   ├── generate_test_data.py                # Synthetic 130k-neuron connectome generator
│   └── run_demo.sh                          # All-in-one launcher (venv, deps, data, backend, frontend)
│
├── deploy/
│   ├── lambda-labs/
│   │   ├── Dockerfile.backend              # CUDA 12.4 + Python 3.11 + CuPy + FastAPI
│   │   ├── Dockerfile.frontend             # nginx-alpine serving built React
│   │   ├── docker-compose.gpu.yml          # Backend (nvidia runtime) + frontend + MinIO + Prometheus
│   │   ├── dstack.yml                      # dstack service definition for Lambda Labs
│   │   ├── nginx.conf                      # Reverse proxy: /api → backend, / → frontend
│   │   └── deploy.sh                       # Build, push, dstack apply
│   └── monitoring/
│       └── prometheus.yml                  # Scrape backend:8000/metrics
│
├── tests/
│   ├── backend/
│   │   ├── test_csc_engine.py              # activate, subgraph, shape validation
│   │   ├── test_capture_split.py           # Anonymization, encryption round-trip
│   │   └── test_sse_streamer.py            # Publish/subscribe, heartbeat
│   └── data/
│       └── flywire/
│           ├── manifest.json               # Dataset metadata
│           └── connectome.csv              # Generated: source,target,weight
│           └── layout.json                 # Generated: 130k×3 positions
```

---

## 4. Core Component Deep-Dives

### 4.1 CSC Engine (`src/backend/services/csc_engine.py`)

**Purpose:** Manage a 130,000×130,000 adjacency matrix on GPU (or CPU fallback) and provide fast vector-matrix multiplication for activation propagation.

**Key design decisions:**

- **CSC format** chosen over CSR because column-wise access is used for activation (vector × matrix) and subgraph extraction (column slicing). The FlyWire connectome has ~50M synapses → density ~3×10⁻⁵, well within CSC efficiency range.
- **CuPy/SciPy fallback** via `_HAS_CUPY` flag set at import time. The check is multi-stage:
  1. Try `import cupy`
  2. Call `cupy.cuda.is_available()` to verify CUDA device
  3. Try `import cupyx.cusparse` to verify cuSPARSE shared libraries load
  If any step fails → `_HAS_CUPY = False` → all operations use `scipy.sparse.csc_matrix` + `numpy`.
- **Array-agnostic methods:** All methods use `self.xp` (set to `cupy` or `numpy` at init) for array creation and `self.sparse` for sparse operations. Routes that call `engine.activate()` use `engine.xp.array(...)` rather than hardcoded `cp.array(...)`.

**Key methods:**

```python
def activate(self, input_vector, threshold=0.5)
    # output = matrix @ input_vector
    # returns (output_array, spike_count)
    # On GPU: output is CuPy array on device, spike_count via .get()
    # On CPU: output is NumPy array

def subgraph(self, neuron_ids)
    # sub = matrix[ids, :][:, ids]
    # returns (dense_list, neuron_ids)

def compute_layout(self, iterations=50)
    # Force-directed spring-electric layout
    # Attraction along graph edges, repulsion between random samples
    # Normalized to unit sphere each iteration

def load_from_coo(self, data, rows, cols)
    # Accepts either CuPy or NumPy arrays (calls xp.asarray)
    # Creates self._matrix as appropriate backend CSC matrix
```

**Memory budget (CPU mode):**
- 500k edges × (4+4+4) bytes = ~6 MB for indices + data + indptr
- Activation vector: 130k × 4 bytes = 0.5 MB
- Total: negligible CPU footprint

**Memory budget (GPU mode):**
- Same structure on GPU: ~6 MB
- cuSPARSE internal workspaces: ~50 MB
- Total: ~60 MB of 6 GB VRAM on RTX 3060

### 4.2 SSE Streamer (`src/backend/services/sse_streamer.py`)

**Purpose:** Fan-out real-time activation pulses to all connected browser clients via Server-Sent Events.

**Implementation pattern:**

```
Activation route
      │
      ▼
streamer.publish([PulseEvent, ...])    # Called from route handler
      │
      ▼
_buffer accumulates until >= batch_size (1000)
      │
      ▼
for each subscriber_queue:
    queue.put_nowait(batch)            # Non-blocking; drops if queue full
```

- **`SSEStreamer`** is a module-level singleton (used as `SSEStreamer()` wherever accessed — `SSEStreamer` is a class that holds module-level state via class attributes)    
- **`subscribe()`** is an `AsyncGenerator[yield str]` — each subscriber gets a dedicated `asyncio.Queue`. When the HTTP response is closed (client disconnects), the generator exits and the queue is discarded in `finally`.
- **Heartbeat:** Every 15 seconds of silence, a comment frame `: heartbeat 1234567890\n\n` is sent to keep the connection alive.
- **Batch format:** One SSE `data:` line per batch, JSON-encoded `PulseBatch`:
  ```json
  data: {"batch": {"neuron_ids": [0,1,2,...], "voltages": [0.8,0.3,...], "spikes": [true,false,...], "ts": 1234567890.123}, "ts": 1234567890.123}
  ```

### 4.3 Data Capture Split Layer (`src/backend/middleware/capture_split.py`)

**Purpose:** Transparently intercept every API request, extract PII and telemetry, and route each to its appropriate secure storage — all without the route handlers needing to know.

**How it works:**

1. **`CaptureSplitMiddleware(BaseHTTPMiddleware)`** wraps the entire FastAPI app.
2. On each request: reads `request.body()`, attempts JSON parse, inspects for PII keys (`user_id`, `email`, `ip_address`, `auth_token`).
3. If PII present: `EncryptionService.encrypt_dict(payload)` → AES-256-GCM ciphertext → logged (in production, written to S3).
4. `TelemetryAnonymizer.anonymize_payload(payload)` → hashes user_id (SHA-256:16), strips PII fields, computes topology hash from neuron_ids → `TelemetryEvent`.
5. `PineconeClient.upsert_telemetry(event)` → vectorized event metadata upserted to Pinecone index for similarity search.

**Pinecone is optional:** If `pinecone-client` is not installed or `PINECONE_API_KEY` is not set, the middleware silently skips the upsert. The `PineconeClient` class has an `available()` classmethod that lazy-checks the import.

**AES-256-GCM details:**
- Key: 32 bytes, generated once at service startup (per-instance key, not persisted)
- Nonce: 12 bytes, random per encryption
- AAD: empty (can be set to request path for authenticated encryption context)

### 4.4 Lava Bridge (`src/backend/services/lava_bridge.py` + `lava_processes.py`)

**Purpose:** Connect the connectome to Intel's neuromorphic platform via the Lava framework. Allows subgraphs of the 130k-neuron network to be compiled as Lava Process graphs and run on Loihi simulators or physical Loihi 2 chips.

**Architecture:**

```
POST /loihi/compile  {neuron_ids: [...], backend: "sim"|"loihi2"}
  │
  ▼
LavaBridge.compile_subgraph()
  1. csc_matrix[neuron_ids, :][:, neuron_ids]  →  COO weights
  2. FlyWireNetwork(
       neuron_ids, weights_rows, weights_cols, weights_data, n_neurons
     )
     ▼
     __post_init__:
       LIF(shape=n_neurons)
       Dense(weights=weight_matrix)  →  connect to LIF.a_in
       Monitor.probe(LIF.s_out)
  3. Register network under run_id (UUID4)
  → return CompileResponse(run_id, backend, n_neurons)

POST /loihi/run  {run_id, num_steps}
  │
  ▼
LavaBridge.run()
  1. Look up FlyWireNetwork by run_id
  2. network.process.run(
       condition=RunSteps(num_steps),
       run_cfg=Loihi1SimCfg() | Loihi2HwCfg()
     )
  3. network.get_spikes() → list of firing neuron IDs
  4. network.process.stop()
  → return RunResponse(run_id, spikes, step_count)
```

**Backend switching:**
- `LAVA_BACKEND=sim` (default): uses `Loihi1SimCfg` — runs LIF processes on CPU, bit-accurate to Loihi 1.
- `LAVA_BACKEND=loihi2` + `INRC_ENABLED=true`: uses `Loihi2HwCfg` — compiles for physical Loihi 2 chip (requires INRC membership + proprietary Intel extension).

**Stub mode:** If `lava-nc` is not installed, `FlyWireNetwork.__post_init__` sets `self.process = object()`, `get_spikes()` returns `[]`, and the bridge logs warnings. All other services continue working.

### 4.5 DeepSeek Aligner (`src/backend/services/deepseek_aligner.py`)

**Purpose:** Use DeepSeek-V4's 1M-token context window to ingest complete edge-lists from two electron microscopy datasets and produce an ID alignment mapping.

**Prompt construction:**

```python
prompt = f"""You are a connectome alignment system. Align neuron IDs between
two EM datasets.

Source: {src}
Target: {tgt}

Edge list ({n} edges):
{edge_list_json[:950000]}

Return JSON:
{{"id_mapping": {{src_id: tgt_id, ...}},
  "confidence": float,
  "aligned_edges": [[src_aligned, tgt_aligned, weight], ...]}}
"""
```

- Temperature 0.0 for deterministic output
- Max 8192 tokens in response
- 300-second HTTP timeout for long contexts
- Truncates edge list to 950k characters (within the 1M token window)
- On failure → returns empty alignment with confidence 0.0
- Async via `httpx.AsyncClient`

### 4.6 Connectome Loader (`src/backend/services/connectome_loader.py`)

**Purpose:** Auto-discover and load connectome data from disk into the CSC engine.

**File discovery:** Searches `data/flywire/` for `*{.csv,.json,.parquet}`, skipping `manifest.json`. Preference order: CSV > JSON > Parquet.

**Loading path:**

```
CSV columns: source, target, weight
  → pandas.read_csv()
  → numpy arrays (source: int32, target: int32, weight: float32)
  → if GPU mode: cupy.asarray()  else: pass-through
  → CSCEngine.load_from_coo(data, rows, cols)
```

**Layout loading:** Reads `data/layout.json` (generated by `scripts/generate_test_data.py`), converts to `engine.xp.array()` for GPU/CPU compatibility. Layout shape: `(130000, 3)`.

---

## 5. Frontend Architecture

### 5.1 Rendering Pipeline

```
useGraphLayout() → fetch /api/v1/connectome/layout
      │
      ▼  130k × [x, y, z]
BrainViewer.tsx (R3F Canvas)
  └─ SceneContent
       └─ NeuronInstances (<instancedMesh>)
            ├─ sphereGeometry(radius=0.3, segments=6)
            ├─ meshStandardMaterial(vertexColors)
            │
            ├─ useEffect: Set initial positions + colors (all blue)
            │
            ├─ useFrame: Check neuronStates Map for each instance
            │   • Not in map → color = COLOR_IDLE (#1a3366)
            │   • In map, no spike → color = lerp(IDLE→ACTIVE) × voltage
            │   • In map, spike → color = COLOR_SPIKE (#ffaa00)
            │   • selectedNeuron == id → color = COLOR_SELECTED (#00ff88)
            │
            └─ onPointerDown: event.instanceId → onSelect(id)
                 Toggle: if already selected → deselect
```

### 5.2 SSE Data Flow

```
useSSE() hook
  └─ connect(): new EventSource('/api/v1/stream/pulses')
       │
       ▼  onmessage
  JSON.parse(event.data) → PulseBatch
       │
       ▼  useSSEStore.applyBatch(batch)
  zustand setState → neuronStates Map updated
       │
       ▼  React re-render
  NeuronInstances useFrame reads neuronStates → updates instance colors
```

- Auto-reconnect on error with 3-second delay
- Heartbeat frames (`: heartbeat ...`) are silently ignored
- Zustand store decouples SSE from React rendering — `useFrame` reads the store directly at 60fps

### 5.3 Click Selection

Three.js R3F `onPointerDown` event on `<instancedMesh>` provides `event.instanceId` (the index of the clicked instance). The logic:

```
onSelect(id === selectedNeuron ? null : id)
```

The selected neuron ID is lifted to `App.tsx` state, passed down to both `BrainViewer` (for color override) and `ControlPanel` (for display + activation targeting).

### 5.4 3D Layout

The layout was generated by `scripts/generate_test_data.py`:
- 12 brain regions (communities) of ~10,833 neurons each
- Each region is a spherical cluster positioned on one of two hemispheres
- Within-cluster radius: 0.15–0.27 (normalized units)
- Scaled by 35× in the renderer for visual spacing

---

## 6. API Reference

### 6.1 System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service status, backend type (GPU/CPU), connectome loaded, SSE subscriber count |
| GET | `/metrics` | GPU memory (if available), connectome nnz, backend type |

### 6.2 Connectome

| Method | Path | Request Body | Response |
|--------|------|-------------|----------|
| GET | `/api/v1/connectome/metadata` | — | `{n_neurons, n_synapses, format, source}` |
| GET | `/api/v1/connectome/status` | — | `{loaded, shape, nonzeros, backend}` |
| GET | `/api/v1/connectome/layout` | — | `{positions: [[x,y,z],...], shape: [130000, 3]}` |
| POST | `/api/v1/connectome/activate` | `{input_vector: float[130000], threshold: float}` | `{output_vector: float[130000], spike_count: int, latency_ms: float}` |
| POST | `/api/v1/connectome/subgraph` | `{neuron_ids: int[1..10000]}` | `{adjacency: float[][], neuron_ids: int[]}` |

### 6.3 Streaming

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/stream/pulses` | SSE endpoint. `Cache-Control: no-store`, `Connection: keep-alive`, `X-Accel-Buffering: no` |
| GET | `/api/v1/stream/status` | `{subscribers, protocol, batch_size}` |

### 6.4 Neuromorphic

| Method | Path | Request Body | Response |
|--------|------|-------------|----------|
| GET | `/api/v1/loihi/status` | — | `{available, backend, active_runs}` |
| POST | `/api/v1/loihi/compile` | `{neuron_ids: int[], backend: "sim"\|"loihi2"}` | `{run_id, backend, n_neurons}` |
| POST | `/api/v1/loihi/run` | `{run_id, num_steps: int}` | `{run_id, spikes: int[], step_count}` |
| POST | `/api/v1/loihi/cleanup/{run_id}` | — | `{status: "cleaned", run_id}` |

### 6.5 Telemetry

| Method | Path | Request Body | Response |
|--------|------|-------------|----------|
| GET | `/api/v1/telemetry/status` | — | `{available, index}` |
| POST | `/api/v1/telemetry/query` | `{similar_operation: str, top_k: int}` | `{results: [{id, score, metadata}], count}` |

---

## 7. Configuration

All configuration is via environment variables or `.env` file (read by `pydantic-settings`).

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_PATH` | `{project}/data/flywire` | Connectome edge-list directory |
| `LAYOUT_PATH` | `{project}/data/layout.json` | Pre-computed 3D layout |
| `PINECONE_API_KEY` | — | Pinecone vector DB key (optional) |
| `PINECONE_INDEX` | `synaptech-telemetry` | Pinecone index name |
| `DEEPSEEK_API_KEY` | — | DeepSeek-V4 API key (optional) |
| `LAVA_BACKEND` | `sim` | `sim` for CPU simulation, `loihi2` for hardware |
| `INRC_ENABLED` | `false` | Set `true` with INRC membership for Loihi compile |
| `JWT_SECRET` | — | JWT signing secret (optional, disables auth if empty) |
| `API_KEYS` | — | Comma-separated API keys (optional) |
| `S3_ENDPOINT` | `http://minio:9000` | S3-compatible endpoint for encrypted IP storage |
| `S3_BUCKET` | `synaptech-ip-encrypted` | S3 bucket name |

---

## 8. Deployment Modes

### 8.1 Local Development (CPU)

```bash
./scripts/run_demo.sh
```

Single script: creates venv, installs deps, generates data, starts backend + frontend. Requires only Python 3.11+ and Node.js 20+. CuPy is tried but failure is silently handled.

### 8.2 Docker Compose (GPU)

```bash
cd deploy/lambda-labs
docker compose -f docker-compose.gpu.yml up -d
```

Requires `nvidia-container-runtime` and NVIDIA GPU. Services: backend (CUDA), frontend (nginx), MinIO (S3-compatible storage), Prometheus (monitoring).

### 8.3 Lambda Labs Serverless (Production)

```bash
export PINECONE_API_KEY=... DEEPSEEK_API_KEY=...
export DOCKER_USERNAME=... DOCKER_PASSWORD=...
./deploy/lambda-labs/deploy.sh dstack
```

Uses **dstack** to provision a 1× A100 80GB instance on Lambda Labs On-Demand Cloud. Auto-scaling: 1–4 replicas, 30-minute idle timeout. Builds and pushes Docker images, then applies `dstack.yml` service definition.

---

## 9. Known Issues & Workarounds

### 9.1 CuPy + CUDA 13.2 `libnvJitLink.so` Missing

**Symptom:** CuPy imports but `cupyx.cusparse` fails with `DynamicLibNotFoundError: libnvJitLink.so`.

**Cause:** `cupy-cuda12x` wheels link against CUDA 12.x library layout. CUDA 13.2 moved/restructured `libnvJitLink.so`. The `cupy_backends` pathfinder searches the conda environment's `lib/` directory and doesn't find it.

**Workaround:** The `_HAS_CUPY` check in `csc_engine.py` catches this at startup (`import cupyx.cusparse` fails → `_HAS_CUPY = False`). All operations fall back to `scipy.sparse.csc_matrix` + `numpy`. Activation still works at ~10ms per spMV (vs ~1ms GPU).

**Fix:** Install a CuPy build compiled for CUDA 13.2, or symlink the missing library:
```bash
ln -s /usr/local/cuda/lib64/libnvJitLink.so.13 /usr/local/cuda/lib64/libnvJitLink.so
```

### 9.2 CPU Activation Performance

130k × 130k spMV on CPU takes ~10ms (SciPy, MKL or OpenBLAS). This limits activation throughput to ~100 Hz. For real-time visualization this is acceptable (the SSE streamer batches at 8ms intervals anyway). For batch processing, GPU mode brings this to ~1ms.

### 9.3 SSE Browser Connection Limit

Browsers limit SSE connections to 6 per host. Each BrainViewer tab uses one connection. Opening more than 6 tabs to the same backend will cause queuing. Fix: use HTTP/2 (enable in uvicorn with `--http h2`), or deploy behind nginx which proxies to the single backend.

### 9.4 Pinecone Not Required

The telemetry pipeline (Pinecone upsert) is entirely optional. If `pinecone-client` is not installed or `PINECONE_API_KEY` not set, the `CaptureSplitMiddleware` silently skips upserts. The `/api/v1/telemetry/*` routes return `available: false`.

---

## 10. Extending the System

### 10.1 Adding a New Backend Engine

1. Create `src/backend/services/{new}_engine.py` with the same interface: `load(matrix)`, `activate(vector) → output`, `subgraph(ids) → sub`
2. In `main.py`, add a factory that sets `CSCEngine` to use your engine
3. The rest of the system (routes, SSE, middleware) automatically works

### 10.2 Adding a New Visualization Mode

1. Add a new component in `src/frontend/src/components/`
2. Add a route in `src/frontend/src/App.tsx`
3. For SSE data, subscribe to the existing `/api/v1/stream/pulses` endpoint
4. For new data types, add a new SSE stream route in `src/backend/routes/visualization.py`

### 10.3 Adding a New Data Source

1. Add a new loader method in `connectome_loader.py` (e.g., `load_nx()` for NetworkX graphs)
2. Add the file extension to `SUPPORTED_FORMATS`
3. Generate a 3D layout for the new dataset
4. The system auto-discovers and loads on next restart

### 10.4 Enabling GPU Acceleration

Install CuPy matching your CUDA version:
```bash
# For CUDA 12.x:
pip install cupy-cuda12x

# For CUDA 11.x:
pip install cupy-cuda11x

# From source for unsupported CUDA:
pip install cupy --no-binary cupy
```

The `_HAS_CUPY` check runs at every startup. No code changes needed.

---

## 11. Data Formats

### 11.1 Edge-List CSV

```csv
source,target,weight
0,12345,0.8765
0,67890,0.2341
...
```

Columns: `source` (int, 0–129999), `target` (int, 0–129999), `weight` (float, 0.0–1.0).

### 11.2 Layout JSON

```json
{
  "positions": [[x, y, z], ...],
  "shape": [130000, 3]
}
```

Positions are normalized to approximately unit-sphere range (-1 to 1). The frontend scales by 35× for rendering.

### 11.3 SSE Pulse Frame

```
data: {"batch":{"neuron_ids":[0,1,2,...],"voltages":[0.8,0.3,0.0,...],"spikes":[true,false,false,...],"ts":1234567890.123},"ts":1234567890.123}\n\n
```

- `neuron_ids`: sampled subset (1000 per batch, not all 130k)
- `voltages`: float32 activation output
- `spikes`: boolean threshold crossings
- `ts`: Unix timestamp with milliseconds

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **CSC** | Compressed Sparse Column — matrix format optimized for column access |
| **spMV** | Sparse matrix-vector multiplication — the core operation for activation | 
| **SSE** | Server-Sent Events — HTTP protocol for real-time push from server to browser |
| **Loihi** | Intel's neuromorphic research chip, emulating spiking neural networks |
| **Lava** | Intel's open-source framework for neuromorphic computing (BSD-3 / LGPL-2.1) |
| **FlyWire** | The *Drosophila* fruit fly brain connectome dataset (130k neurons, ~50M synapses) |
| **R3F** | React Three Fiber — React renderer for Three.js WebGL library |
| **INRC** | Intel Neuromorphic Research Community — membership required for Loihi hardware access |
| **DCSL** | Data Capture Split Layer — middleware that separates IP from telemetry at capture time |
