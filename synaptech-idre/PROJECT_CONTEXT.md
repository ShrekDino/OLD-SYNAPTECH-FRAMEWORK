# SynapTech IDRE — Project Context for LLM Planning

**Developed via opencode with DeepSeek-V4** — This project is designed for multi-agent AI collaboration. The system prompt architecture supports intricate agent handoffs, role-specific personas (Principal Architect, Venture Partner, Research Scientist), and self-contained context files for autonomous continuation. All agent instructions, handoff protocols, and persona definitions are managed through AGENTS.md, PROJECT_CONTEXT.md, and inline system prompt engineering within the opencode framework.

## 1. Identity

**SynapTech IDRE** (Integrated Data Representation Engine) is evolving from a localized connectome computation engine into a globally distributed, hybrid-cloud research ecosystem — **The Democratized Neuromorphic Commons**. It bridges institutional researchers and the open-source developer community. By leveraging a unified, secure Data Capture Split Layer (DCSL) and cloud-offloaded neuromorphic hardware, it acts as a decentralized sandbox for mapping, simulating, and training bio-inspired AI models. **We fund the hardware, you bring the genius, the resulting intelligence substrate belongs to the people.**

The core IDRE loads the FlyWire *Drosophila* brain graph (130k neurons, ~50M synapses) as a GPU-accelerated CSC matrix, exposes REST + SSE endpoints for real-time activation, streams neural pulse data to a browser-based Three.js 3D viewer, and provides a neuromorphic bridge to Intel Loihi via Lava — all gated behind a transparent Data Capture Split Layer that ensures IP sovereignty while building a public telemetry commons.

## 2. Architecture — The Democratized Neuromorphic Commons (Three-Tier Model)

```
       [ Institutional Researchers ]       [ Open Source Devs / Citizens ]
                     \                                    /
                      \                                  /
                       v                                v
  ═══════════════════════════════════════════════════════════════════════
  TIER 1 — COLLABORATIVE SIMULATION (Three.js BrainViewer + FastAPI)
  ═══════════════════════════════════════════════════════════════════════
                     [ SynapTech IDRE Compute Nodes ]
                       │                     │
                       │ (REST/SSE)          │ (Lava Compile/Run)
                       v                     v
              CSCEngine.spMV()        LavaBridge.compile_subgraph()
              (~1ms GPU / ~10ms CPU)  (Loihi1SimCfg / Loihi2HwCfg)
                       │                     │
                       └─────────┬───────────┘
                                 │
  ═══════════════════════════════════════════════════════════════════════
  TIER 2 — DATA CAPTURE SPLIT LAYER (Legal + Technical Gatekeeper)
  ═══════════════════════════════════════════════════════════════════════
                     CaptureSplitMiddleware
                     ┌──────────────────────┐
                     │  request.body() fork  │
                     └──────────┬───────────┘
                           /          \
        (Proprietary IP) /            \ (Anonymized Telemetry)
                      v                v
           AES-256-GCM encrypt    PII strip + SHA-256 hash
                 │                      │
                 v                      v
          S3/MinIO ────┐    Pinecone Vector DB
          (immutable)  │    (MD5→gauss fingerprint)
                       │           │
                       └──────┬────┘
                              │
  ═══════════════════════════════════════════════════════════════════════
  TIER 3 — CONTINUOUS ALIGNMENT + CLOUD NEUROMORPHIC
  ═══════════════════════════════════════════════════════════════════════
                    Continuous DeepSeek-V4 Alignment Engine
                    (S3-triggered batch, 1M-token context)
                              │
                              v
                    Public AI Foundation Model Matrix
                    ("Living Blueprint" — open weights)
                              │
                              v
              Cloud Neuromorphic Compute Farm (Intel Loihi 2)
              (Centrally funded, zero cost to researchers)
```

## 2.1 The People's Connectome — Lifecycle

| Phase | What Happens | Tech |
|-------|-------------|------|
| **1. Discovery** | Researcher signs up via Open Brain Portal, selects brain region / neuron type. | ORCID OAuth, FastAPI auth, React onboarding |
| **2. Simulation** | Runs activation, subgraph extraction, or LSM reservoir on IDRE GPU nodes. | CSCEngine.spMV(), REST/SSE, Three.js viewer |
| **3. IP Lockbox** | Proprietary activations / derived models → AES-256-GCM → S3 immutable bucket. | CaptureSplitMiddleware, encryption.py, boto3 |
| **4. Telemetry** | Anonymized operation + topology hash → Pinecone vector DB → public similarity search. | telemetry_anon.py, pinecone_client.py |
| **5. Alignment** | S3 trigger → DeepSeek-V4 digest → continuous fine-tuning of Public Foundation Model. | deepseek_aligner.py, S3 events, batch scheduler |
| **6. Foundry** | Community-contributed neurons get deployed to Cloud Loihi Farm; results feed back to the matrix. | LavaBridge, lava_processes.py, provisioning layer |
| **7. Governance** | All model weights are open. No single entity owns the "Living Blueprint." | Open weights license, transparent pipeline |

**Core Principle:** The researcher always retains full ownership and control of their IP (Phase 3). The community benefits from the aggregated, anonymized telemetry (Phase 4) and the ever-improving open model (Phase 5). Hardware is centrally funded (Phase 6). No lock-in, no data extraction.

## 3. Complete File Tree

```
.
├── PROJECT_CONTEXT.md           ← THIS FILE: LLM planning context
├── AGENTS.md                    ← Agent handoff / resume file
├── ARCHITECTURE.md              ← Legacy architecture doc (663 lines, comprehensive)
├── run.py                       ← Root entry: python run.py [backend|frontend|gen-data|all]
├── pyproject.toml               ← Build metadata, optional deps (neuromorphic, s3, dev)
├── requirements.txt             ← Pip deps (fastapi, uvicorn, pydantic, numpy, etc.)
├── requirements.gpu.txt         ← cupy-cuda12x
├── .env.example                 ← 35 config keys with defaults

├── src/
│   ├── shared/
│   │   ├── constants.py         ← N_NEURONS=130k, SSE_BATCH_SIZE=1000, AES key sizes, etc.
│   │   └── schemas.py           ← All Pydantic models (Neuron, Edge, PulseBatch, Activation*,
│   │                               Subgraph*, Compile*, Run*, Telemetry*, Alignment*, EncryptedBlob)
│   │
│   ├── backend/
│   │   ├── main.py              ← FastAPI app, lifespan (try real FlyWire → fallback synthetic),
│   │   │                           CORS, CaptureSplitMiddleware, router registration, /health, /metrics
│   │   ├── config.py            ← pydantic-settings Settings class, reads .env / env vars
│   │   ├── exceptions.py        ← IDREException hierarchy + FastAPI exception handler
│   │   │
│   │   ├── middleware/
│   │   │   ├── capture_split.py ← ASGI middleware: forks request → encryption + telemetry
│   │   │   ├── auth.py          ← JWT + API key validation (DEFINED BUT NOT WIRED into main.py)
│   │   │   └── tenant.py        ← Multi-tenant isolation: per-tenant S3 bucket, Pinecone namespace (📋 Planned)
│   │   │
│   │   ├── routes/
│   │   │   ├── connectome.py    ← /api/v1/connectome/{metadata,status,layout,activate,subgraph}
│   │   │   ├── visualization.py ← /api/v1/stream/{pulses,status} (SSE endpoint)
│   │   │   ├── neuromorphic.py  ← /api/v1/loihi/{status,compile,run,cleanup}
│   │   │   └── telemetry.py     ← /api/v1/telemetry/{status,query}
│   │   │
│   │   └── services/
│   │       ├── csc_engine.py     ← CSCMatrix singleton, CuPy/SciPy fallback, spMV, subgraph, layout
│   │       ├── connectome_loader.py ← File discovery, CSV/JSON/Parquet loaders, real FlyWire loader
│   │       ├── sse_streamer.py   ← Async queue fan-out, heartbeat, batch publish
│   │       ├── encryption.py     ← AES-256-GCM encrypt/decrypt, per-instance key
│   │       ├── telemetry_anon.py ← PII stripper, SHA-256 hasher, topology hash
│   │       ├── pinecone_client.py← Pinecone Index wrapper, conditional import, deterministic vectors
│   │       ├── lava_bridge.py    ← Lava RunConfig factory, compile/run lifecycle
│   │       ├── lava_processes.py ← FlyWireNetwork dataclass, LIF model, Monitor
│   │       ├── deepseek_aligner.py ← DeepSeek-V4 API client, 1M-context alignment prompt
│   │       ├── batch_aligner.py  ← S3-triggered batch scheduler for continuous alignment (📋 Planned)
│   │       ├── embedding_service.py ← sentence-transformers/all-MiniLM-L6-v2 → 384-dim vectors (📋 Planned)
│   │       ├── s3_client.py      ← boto3 S3 wrapper, per-tenant bucket management (📋 Planned)
│   │       ├── lsm_engine.py     ← 500-neuron Liquid State Machine, ridge regression readout (📋 Planned)
│   │       └── cloud_loihi.py    ← Cloud Loihi 2 farm: provisioning, queue, scheduling (📋 Planned)
│   │
│   └── frontend/
│       ├── package.json          ← React 19, Three.js 0.170, R3F 9, Drei 10, Zustand 5, GSAP, Vite 6
│       ├── package-lock.json
│       ├── tsconfig.json
│       ├── vite.config.ts        ← Proxies /api, /stream, /health → backend
│       ├── index.html            ← White background, Inter font, SynapTechBio title
│       └── src/
│           ├── main.tsx          ← ReactDOM.createRoot
│           ├── App.tsx           ← Stage machine: SIGN_IN → DASHBOARD
│           ├── types/connectome.ts ← TS interfaces (Neuron, PulseBatch, NeuronState, GraphLayout)
│           │
│           ├── pages/
│           │   ├── SignInScreen.tsx    ★ Entry point: R3F Canvas + FractalScene + SignInCard + GSAP fly-through
│           │   ├── BrainDashboard.tsx  ★ Extracted dashboard: BrainViewer + ControlPanel
│           │   ├── PortalHome.tsx      ← Open Brain Platform landing page (📋 Planned)
│           │   ├── WorkspaceDashboard.tsx ← Per-user workspace (📋 Planned)
│           │   ├── ActivationSandbox.tsx  ← Upload/sketch input vector → run spMV → viz cascade (📋 Planned)
│           │   ├── LSMDemo.tsx        ← LSM live text generation demo (📋 Planned)
│           │   ├── TelemetryExplorer.tsx ← Query anonymized operations (📋 Planned)
│           │   ├── AlignmentViewer.tsx ← Track Living Blueprint evolution (📋 Planned)
│           │   └── LoihiJobManager.tsx ← Request Loihi time, check queue (📋 Planned)
│           │
│           ├── components/
│           │   ├── FractalScene.tsx    ★ R3F scene: MorphingNeurons + CircuitTraces + OrbitControls
│           │   ├── MorphingNeurons.tsx ★ 130k InstancedMesh, ShaderMaterial, fractal→neuron vertex morph
│           │   ├── CircuitTraces.tsx   ★ ~2000-hub LineSegments, ShaderMaterial, pulsing tech-blue/gold traces
│           │   ├── SignInCard.tsx      ★ Glassmorphism card: logo, username/password fields, gradient CTA
│           │   ├── BrainViewer.tsx    ← Unchanged dashboard viewer (R3F Canvas, lights, OrbitControls)
│           │   ├── NeuronInstances.tsx← Fixed `sizeAttenuation` TS error
│           │   ├── ControlPanel.tsx   ← Unchanged (SSE toggle, threshold, activate buttons)
│           │   ├── ActivationPulse.tsx← Unchanged, NOT yet integrated
│           │   ├── ResevoirRender.tsx ← LSM neuron activity visualization (📋 Planned)
│           │   ├── TelemetryHeatmap.tsx← Pinecone similarity heatmap (📋 Planned)
│           │   └── PortalNav.tsx      ← Top-level portal navigation bar (📋 Planned)
│           │
│           ├── hooks/
│           │   ├── useCameraTransition.ts ★ GSAP timeline hook for camera fly-through + morph + card fade
│           │   ├── useSSE.ts         ← Unchanged (EventSource → Zustand store, auto-reconnect)
│           │   ├── useGraphLayout.ts ← Unchanged (Fetch layout, Web Worker refinement)
│           │   ├── usePineconeQuery.ts ← Query telemetry by similarity (📋 Planned)
│           │   └── useLSM.ts         ← LSM connection + text generation state (📋 Planned)
│           │
│           └── shaders/
│               ├── morph.vert.glsl       ★ Fractal→neuron morph vertex with per-instance fractal jitter
│               ├── morph.frag.glsl       ★ Point sprite fragment with glow + ripple
│               ├── circuit.vert.glsl     ★ Circuit trace vertex with source/target interpolation
│               ├── circuit.frag.glsl     ★ Circuit trace fragment with time-based pulse glow
│               ├── vertex.glsl           ← Orphaned (not yet wired into NeuronInstances)
│               └── fragment.glsl         ← Orphaned (not yet wired into NeuronInstances)
│
├── scripts/
│   ├── generate_test_data.py    ← Synthetic 130k-neuron, 12 communities, 500k edges, 3D layout
│   ├── fetch_flywire_data.py    ← Resumable Zenodo download (CC BY 4.0), centroid extraction
│   └── run_demo.sh              ← All-in-one: venv, deps, data gen, backend, frontend

├── tests/
│   ├── backend/
│   │   ├── test_csc_engine.py   ← activate, subgraph, shape validation (requires CuPy)
│   │   ├── test_capture_split.py← Anonymization, encryption round-trip, topology hash
│   │   ├── test_sse_streamer.py ← Publish/subscribe, heartbeat (asyncio)
│   │   ├── test_auth.py         ← JWT + API key validation (📋 Planned)
│   │   ├── test_tenant.py       ← Multi-tenant isolation (📋 Planned)
│   │   ├── test_embeddings.py   ← sentence-transformers integration (📋 Planned)
│   │   ├── test_s3_client.py    ← S3 upload/download (📋 Planned)
│   │   ├── test_lsm_engine.py   ← Reservoir dynamics + readout (📋 Planned)
│   │   └── test_batch_aligner.py ← Alignment pipeline (📋 Planned)
│   └── frontend/                    (📋 Planned)
│       ├── test_SignInScreen.tsx
│       ├── test_BrainDashboard.tsx
│       └── test_ActivationSandbox.tsx

├── deploy/
│   ├── lambda-labs/
│   │   ├── Dockerfile.backend   ← CUDA 12.4 + Python 3.11 + CuPy + Uvicorn
│   │   ├── Dockerfile.frontend  ← node:22-alpine build → nginx:1.27-alpine serve
│   │   ├── docker-compose.gpu.yml ← backend (nvidia) + frontend + MinIO + Prometheus
│   │   ├── docker-compose.cpu.yml ← CPU-only deployment (📋 Planned)
│   │   ├── dstack.yml           ← Lambda Labs service def: 1×GPU, auto-scale 1-4, 30min idle
│   │   ├── nginx.conf           ← Proxy /api → backend, /stream → backend (no buffering), / → SPA
│   │   └── deploy.sh            ← Build, push, dstack apply / compose up
│   ├── portal/                      (📋 Planned)
│   │   ├── Dockerfile.portal    ← Portal frontend + API
│   │   ├── docker-compose.portal.yml ← Portal + PostgreSQL + Redis
│   │   └── schema.sql           ← Portal database schema (users, workspaces, jobs)
│   └── monitoring/
│       └── prometheus.yml       ← Scrape backend:8000/metrics + MinIO

└── data/
    ├── layout.json              ← 130k × 3 float32 positions (synth or real)
    └── flywire/
        ├── manifest.json        ← Dataset metadata
        ├── connectome.csv       ← Generated: source,target,weight (500k edges)
        ├── root_ids.npy         ← Real FlyWire: 139k neuron IDs (downloaded)
        ├── proofread_connections.feather ← Real: 3.7M connections (downloaded, 852 MB)
        ├── flywire_synapses.feather      ← Real: 130M synapses (downloaded, 9.5 GB)
        └── positions.npy        ← Extracted centroids from synapses
```

## 3.5 The Democratized Neuromorphic Commons — Manifesto

**Problem:** Brain connectome research is fragmented. Institutions guard their pipelines, hardware access is gated by grants, and there is no shared "living blueprint" of neural computation that the entire field can build on.

**SynapTech's Thesis:** The fruit fly connectome is a gift. For the first time, we have a complete synaptic-resolution wiring diagram of a biological brain (~130k neurons, ~50M synapses). The next step is not just to stare at it, but to *run* it, *perturb* it, *learn from* it — and to do that collectively, in the open, at internet scale.

**The Three Pillars:**

1. **Hardware Democracy.** SynapTech centrally funds Cloud Loihi 2 capacity. A researcher in Mumbai or Nairobi gets the same compute as MIT. No grant proposal required.

2. **IP Sovereignty.** Every activation, every subgraph extraction, every derived model passes through the Data Capture Split Layer. The proprietary payload is encrypted and stored immutably in the researcher's S3 bucket. SynapTech cannot read it. The anonymized metadata (operation type, topology hash, timing) flows to the public commons.

3. **Open Intelligence Substrate.** The aggregated telemetry feeds a Continuous DeepSeek-V4 Alignment Engine that produces an ever-improving, open-weights Foundation Model Matrix — the "Living Blueprint." This model belongs to the community. It grows smarter with every researcher who contributes.

**Quote for Investors:**
> *"We fund the hardware. You bring the genius. The resulting intelligence substrate belongs to the people. This is not a SaaS trap — it's a planetary-scale neural foundry."*

## 3.6 Open Brain Platform — Portal Specifications

The Open Brain Platform is the public-facing web portal where researchers discover, simulate, and contribute to the Living Blueprint.

### Core Features (MVP)

| Feature | Description | Status |
|---------|-------------|--------|
| **ORCID Registration** | Researcher signs in via ORCID OAuth. No passwords needed. | 🔲 Planned |
| **Workspace Dashboard** | Per-user workspace: recent activations, telemetry exports, Loihi runs. | 🔲 Planned |
| **Connectome Explorer** | 3D BrainViewer with region highlighting, neuron search, tooltip stats. | ✅ Implemented (dashboard) |
| **Activation Sandbox** | Upload or sketch an input vector → run spMV → visualize pulse cascade. | ✅ Backend, needs portal UI |
| **LSM Demo** | Pre-built Liquid State Machine demo: 500-neuron reservoir, live text generation. | 🔲 Planned (spec only) |
| **Telemetry Query** | Search anonymized operations by similarity (Pinecone). | 🔲 Backend exists, needs portal UI |
| **Alignment Viewer** | Track the Living Blueprint's evolution. See what the community contributed. | 🔲 Planned |
| **Loihi Job Scheduler** | Request Loihi 2 time. See queue status, estimated wait. | 🔲 Planned |

### Multi-Tenant Architecture

```
┌───────────────────────────────────────────────────┐
│             Open Brain Platform (Portal)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ ORCID    │  │Workspace │  │Connectome        │ │
│  │ Auth     │  │Dashboard │  │Explorer          │ │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
│       └──────────────┼─────────────────┘           │
└──────────────────────┼─────────────────────────────┘
                       │
┌──────────────────────┼─────────────────────────────┐
│         IDRE Core (per-tenant isolation)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Auth     │  │Capture   │  │CSCEngine         │ │
│  │Middleware│  │Split     │  │(shared matrix,    │ │
│  │ (JWT +   │  │(per-     │  │ per-tenant state) │ │
│  │  API key)│  │ tenant)  │  │                   │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │Pinecone  │  │ S3       │  │DeepSeek Aligner  │ │
│  │(per-     │  │(per-     │  │(shared, batch)   │ │
│  │ tenant)  │  │ tenant)  │  │                   │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
└───────────────────────────────────────────────────┘
```

### Registration Flow
1. Researcher visits portal → clicks "Sign in with ORCID"
2. ORCID OAuth returns verified identity + email
3. SynapTech provisions:
   - JWT tokens (access + refresh)
   - API key
   - S3 bucket (synaptech-<tenant-id>-encrypted)
   - Pinecone namespace (telemetry-<tenant-id>)
   - Workspace entry in PostgreSQL
4. Researcher is redirected to Dashboard with onboarding wizard

## 3.7 Telemetry Commons & Continuous Alignment Pipeline

### Telemetry Commons

Every researcher action generates an anonymized telemetry event:

| Field | Example | Type |
|-------|---------|------|
| `operation` | `connectome.activate` | string |
| `topology_hash` | `sha256(edge_list[:1000])` | string |
| `n_neurons` | 10000 | int |
| `latency_ms` | 2.3 | float |
| `backend` | `cupy` | string |
| `user_hash` | `sha256(orcid_id + salt)` | string |
| `timestamp` | `2026-05-23T12:00:00Z` | ISO8601 |

These events are:
1. Stripped of all PII by `telemetry_anon.py`
2. Embedded into Pinecone as MD5→gauss vectors (dim=128) — **slated for replacement with real sentence-transformers/all-MiniLM-L6-v2 embeddings**
3. Queryable via `/api/v1/telemetry/query` — "find similar operations by topology + behavior"

### Continuous Alignment Pipeline

```
[S3 Put Event] → [Lambda/Argo Workflow] → [DeepSeek-V4 API] → [Weight Update] → [Publish to HF Hub]
     │                    │                       │                    │                  │
     │                    │                       │                    │                  v
 encrypted_ip.enc     batch_aligner.py       1M-context prompt    model_delta.bin    synaptech/living-blueprint
```

**Pipeline Steps:**
1. S3 bucket triggers on new `.enc` files (encrypted IP blobs)
2. Batch scheduler (`batch_aligner.py` — **not yet implemented**) decrypts, extracts topology + metadata
3. Constructs a DeepSeek-V4 prompt describing the operation and its outcome
4. DeepSeek-V4 returns a structured model diff (weight adjustments, architectural insights)
5. Diff is applied to the Public Foundation Model Matrix
6. Updated model published to Hugging Face Hub (`synaptech/living-blueprint`)

**Current Reality:** `deepseek_aligner.py` exists as a single-shot async client. No batch scheduling, no S3 trigger, no weight application. This is a Phase 6 item.

## 4. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **CSC over CSR** | Column-wise access for activation (vector × matrix) and subgraph (column slicing) |
| **CuPy/SciPy fallback** | Multi-stage check at import: `import cupy` → `cuda.is_available()` → `import cupyx.cusparse`. Any failure → `_HAS_CUPY = False` → all ops use SciPy + NumPy |
| **Singleton services** | `CSCEngine`, `SSEStreamer`, `EncryptionService`, `PineconeClient`, `LavaBridge`, `DeepSeekAligner` all use `get_instance()` classmethod pattern |
| **AES-256-GCM per-instance key** | Key generated at service startup, NOT persisted. Production would derive from KMS |
| **Conditional imports** | Pinecone, Lava, CuPy all optional. Code degrades gracefully with stubs/logging |
| **SSE fan-out** | Single `asyncio.Queue` per subscriber, `put_nowait` drops if subscriber is slow |
| **Capture-split middleware** | Transparently intercepts ALL requests. No route handler awareness needed |
| **Pinecone vectors** | Deterministic MD5→seed→gauss(0,0.1) vectors (not embeddings). Suitable for similarity by operation+topology hash |
| **Layout scale 35×** | Positions normalized to unit sphere; frontend scales by 35 for visual spacing |

## 5. API Reference

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Status, GPU/CPU, connectome loaded, SSE subscriber count |
| GET | `/metrics` | GPU memory (if available), nnz, backend type |

### Connectome
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/api/v1/connectome/metadata` | — | `{n_neurons, n_synapses, format, source}` |
| GET | `/api/v1/connectome/status` | — | `{loaded, shape, nonzeros, backend, ...}` |
| GET | `/api/v1/connectome/layout` | — | `{positions: [[x,y,z],...], shape, metadata}` |
| POST | `/api/v1/connectome/activate` | `{input_vector: float[130000], threshold}` | `{output_vector, spike_count, latency_ms}` |
| POST | `/api/v1/connectome/subgraph` | `{neuron_ids: int[1..10000]}` | `{adjacency, neuron_ids}` |

### Streaming
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/stream/pulses` | SSE endpoint (no-store, keep-alive, no buffering) |
| GET | `/api/v1/stream/status` | `{subscribers, protocol, batch_size}` |

### Neuromorphic
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/api/v1/loihi/status` | — | `{available, backend, active_runs}` |
| POST | `/api/v1/loihi/compile` | `{neuron_ids, backend}` | `{run_id, backend, n_neurons}` |
| POST | `/api/v1/loihi/run` | `{run_id, num_steps}` | `{run_id, spikes, step_count}` |
| POST | `/api/v1/loihi/cleanup/{run_id}` | — | `{status, run_id}` |

### Telemetry
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/api/v1/telemetry/status` | — | `{available, index}` |
| POST | `/api/v1/telemetry/query` | `{similar_operation, top_k}` | `{results, count}` |

## 6. SSE Pulse Frame Format

```
data: {"batch":{"neuron_ids":[0,1,2,...],"voltages":[0.8,0.3,...],"spikes":[true,false,...],"ts":1234567890.123},"ts":1234567890.123}\n\n
```

- 1000 neurons per batch (sampled from all 130k)
- Heartbeat every 15s silence: `: heartbeat 1234567890\n\n`

## 7. Config (via .env or env vars)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATA_PATH` | `{project}/data/flywire` | Edge-list directory |
| `LAYOUT_PATH` | `{project}/data/layout.json` | 3D layout file |
| `PINECONE_API_KEY` | — | Vector DB key (optional) |
| `PINECONE_INDEX` | `synaptech-telemetry` | Index name |
| `DEEPSEEK_API_KEY` | — | DeepSeek-V4 key (optional) |
| `LAVA_BACKEND` | `sim` | `sim` or `loihi2` |
| `INRC_ENABLED` | `false` | Loihi hardware access |
| `JWT_SECRET` | — | Auth secret (optional) |
| `API_KEYS` | — | Comma-separated API keys (optional) |
| `S3_ENDPOINT` | `http://minio:9000` | S3-compatible storage |
| `S3_BUCKET` | `synaptech-ip-encrypted` | Encrypted IP bucket |
| `LOG_LEVEL` | `INFO` | Logging level |

## 8. Current Completeness Status

### ✅ Implemented & Working

| Component | Notes |
|-----------|-------|
| CSC Engine (GPU/CPU) | CuPy/SciPy fallback, spMV, subgraph, layout |
| Connectome Loader | CSV/JSON/Parquet + real FlyWire (proofread_connections + flywire_synapses) |
| SSE Streamer | Fan-out, asyncio.Queue, heartbeat, batch publish |
| Encryption | AES-256-GCM, dict/blob round-trip, per-instance key |
| Telemetry Anonymizer | PII strip, SHA-256 hash, topology hash |
| Pinecone Client | Deterministic MD5→gauss vectors, query/upsert |
| DeepSeek Aligner | Async HTTP client, 1M-context prompt, 300s timeout |
| Connectome Routes | metadata, status, layout, activate, subgraph |
| Visualization Routes | SSE pulses, status |
| Neuromorphic Routes | compile, run, cleanup, status |
| Telemetry Routes | status, query |
| Capture Split Middleware | Wired into main.py, Pinecone upsert works |
| Frontend SignInScreen | R3F Canvas + FractalScene + SignInCard + GSAP fly-through |
| Frontend BrainDashboard | BrainViewer + ControlPanel, stage-routed from App.tsx |
| Frontend FractalScene | MorphingNeurons + CircuitTraces + OrbitControls |
| Frontend MorphingNeurons | 130k InstancedMesh, ShaderMaterial, fractal→neuron morph |
| Frontend CircuitTraces | ~2000-hub LineSegments, pulsing tech-blue/gold ShaderMaterial |
| Frontend SignInCard | Glassmorphism, Inter font, username/password, gradient CTA |
| Frontend useCameraTransition | GSAP timeline: camera zoom + morph + card fade |
| Frontend BrainViewer | R3F Canvas, lights, OrbitControls, layout fetch |
| Frontend NeuronInstances | 130k instanced mesh, raycast, per-frame vertexColors |
| Frontend ControlPanel | SSE toggle, threshold slider, activate button |
| Frontend useSSE | Zustand store, auto-reconnect |
| Frontend useGraphLayout | Fetch layout + Web Worker refinement |
| GLSL morph.vert/.frag | Wired into MorphingNeurons ShaderMaterial |
| GLSL circuit.vert/.frag | Wired into CircuitTraces ShaderMaterial |
| Synthetic Data Generator | 12 communities, ~130k neurons, 500k edges, 3D layout |
| Real FlyWire Download | Resumable Zenodo, MD5-verified, centroid extraction |
| Docker Backend | CUDA 12.4 multi-stage build |
| Docker Frontend | node:22-alpine build → nginx:1.27-alpine serve |
| Docker Compose (GPU) | backend (nvidia) + frontend + MinIO + Prometheus |
| Lambda Labs Deploy | dstack.yml + deploy.sh |

### 🔄 In Progress / Needs Work

| Component | Status | What's Missing |
|-----------|--------|----------------|
| Auth Middleware | ⚠️ Defined, unwired | `auth.py` exists; needs `app.add_middleware()` in `main.py` |
| Lava Bridge | ⚠️ Stub-safe | Works if lava-nc installed; no cloud provisioning |
| Lava Processes | ⚠️ Stub-safe | FlyWireNetwork + LIF model defined, no LSM reservoir topology |
| ActivationPulse | ⚠️ Unintegrated | Component exists, not wired into BrainViewer SceneContent |
| GLSL vertex/fragment | ❌ Orphaned | On disk, not wired into NeuronInstances (uses meshStandardMaterial) |
| BrainDashboard XorShift128 | ❌ Bug | References `(window as any).XorShift128`, falls back to Math.random |
| Tests | ⚠️ Partial | 3 test files, CuPy-dependent |
| S3 Upload | ❌ No-op | `capture_split.py` sets `self._s3_bucket = None`, never writes |
| Pinecone Embeddings | ❌ Placeholder | Uses MD5→gauss, not real embeddings |

### 📋 Planned (Phased Roadmap)

| Component | Phase | Notes |
|-----------|-------|-------|
| Multi-Tenant Auth (JWT + ORCID) | P0 | Auth middleware + tenant isolation + ORCID OAuth flow |
| S3 Client (per-tenant buckets) | P0 | boto3 wrapper, bucket provisioning, lifecycle policies |
| Real Embeddings (MiniLM-L6-v2) | P1 | Replace MD5→gauss with 384-dim sentence-transformers |
| Activation Sandbox (Portal UI) | P1 | Upload/sketch input vector → spMV → visualize cascade |
| LSM Demo (500-neuron) | P1 | Liquid State Machine with ridge regression readout |
| Continuous Alignment Pipeline | P2 | S3-triggered batch, DeepSeek-V4 diff, HF Hub publish |
| Open Brain Portal (full) | P2 | Multi-page portal: home, workspace, sandbox, telemetry |
| Telemetry Explorer (Portal UI) | P2 | Pinecone similarity search with heatmap visualization |
| Cloud Loihi Farm | P3 | Provisioning, queue, scheduling abstraction |
| Portal Database (PostgreSQL) | P2 | Users, workspaces, job history |
| Docker Compose (CPU) | P2 | CPU-only deployment for non-GPU envs |
| Frontend Tests | P2 | Component + integration tests |
| WebSocket Transport | P3 | Alternative to SSE for higher throughput |

## 9. Known Issues

1. **CuPy + CUDA 13.2**: `libnvJitLink.so` missing → `_HAS_CUPY = False` fallback. Workaround: symlink or wait for CuPy 13.4+.
2. **CPU spMV ~10ms**: Limits activation to ~100 Hz. Acceptable for real-time viz. GPU mode ~1ms.
3. **SSE browser limit**: 6 per host. Fix: HTTP/2 or nginx proxy.
4. **`BrainDashboard.tsx` XorShift128 bug**: References `(window as any).XorShift128` which doesn't exist → falls back to `Math.random`. Works but ugly.
5. **Orphaned dashboard shaders** (`vertex.glsl`, `fragment.glsl`): exist on disk but `NeuronInstances.tsx` uses `meshStandardMaterial` with `vertexColors`, not a `ShaderMaterial`. Unused.
6. **Tests need CuPy**: `test_csc_engine.py` imports `cupy` directly → will skip/fail on CPU-only machines.
7. **Vite build timeout**: Production build may exceed 2-minute tool limit due to 130k Float32Array allocations in MorphingNeurons `useMemo`. Dev mode works fine.
8. **Auth middleware unwired**: `auth.py` fully defined but never added to `main.py`. All routes are public.
9. **S3 upload is a no-op**: `capture_split.py` never writes to S3 — `self._s3_bucket = None`.
10. **Pinecone uses hash, not embeddings**: MD5→gauss vectors are not semantically meaningful. Scheduled for replacement with MiniLM.
11. **No multi-tenancy**: No per-tenant S3 buckets, Pinecone namespaces, or user workspace isolation.
12. **No ORCID OAuth**: Only a synthetic username/password SignInCard — no real identity provider.
13. **LSM is a spec, not a feature**: `lava_processes.py` defines LIF neurons but no reservoir topology or ridge regression readout.
14. **Continuous alignment is single-shot**: `deepseek_aligner.py` does one request-response. No batch scheduling, no S3 trigger, no weight application.
15. **No public telemetry API**: `/api/v1/telemetry/query` exists but has no auth, rate limiting, or usage tracking.
16. **`CaptureSplitMiddleware` consumes `request.body()`**: Route handlers must use cached body. Works currently but fragile if middleware order changes.

## 10. Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, NumPy, SciPy, CuPy (optional)
- **Frontend**: React 19, TypeScript, Three.js 0.170, R3F 9, Drei 10, Zustand 5, GSAP, Vite 6
- **Neuromorphic**: Lava framework (Intel Loihi), lava-nc
- **Database**: Pinecone vector DB (optional)
- **Storage**: S3/MinIO (AES-256-GCM encrypted)
- **AI**: DeepSeek-V4 API (1M-token context)
- **Monitoring**: Prometheus
- **Deploy**: Docker, dstack (Lambda Labs)

## 11. Investor Narrative — $150k Pre-Seed Milestone (Liam / Procyon)

### The Ask

$150k pre-seed to scale SynapTech IDRE from a single-node connectome viz demo into a globally distributed, multi-tenant Open Brain Platform — the Democratized Neuromorphic Commons.

### The Problem

| Domain | Problem |
|--------|---------|
| **Neuromorphic Hardware** | Intel Loihi 2 access requires INRC membership + grant process. Only ~200 labs worldwide have it. |
| **Connectome Research** | Every lab builds their own pipeline. No shared infrastructure, no standard benchmark, no "ImageNet for neural computation." |
| **AI Safety / Alignment** | Alignment research happens in secret at frontier labs. No public, auditable, continuously-improving foundation model exists. |
| **Open Science** | Drosophila connectome (FlyWire, 2024) is a gift — but the tooling to *run* it is scattered, underfunded, and GPU-gated. |

### Our Solution (7-Phase Rollout)

| Phase | Description | Cost | Timeline | Investor Milestone |
|-------|-------------|------|----------|--------------------|
| **P0 — Multi-Tenant Auth** | JWT + ORCID OAuth + per-tenant S3/Pinecone isolation + wire middleware | $15k | Week 1–3 | Security audit pass |
| **P1 — DCSL + Embeddings** | Real MiniLM embeddings (384-dim), S3 upload working, telemetry query UI | $25k | Week 4–6 | First external researcher onboarded |
| **P2 — LSM Live Demo** | 500-neuron Liquid State Machine, text generation, ridge regression readout | $20k | Week 7–9 | Product demo ready for YC/NEA |
| **P3 — Open Brain Portal** | Multi-page portal: home, workspace, activation sandbox, telemetry explorer | $25k | Week 10–13 | DAU > 50 researchers |
| **P4 — Continuous Alignment** | S3-triggered batch scheduler, DeepSeek-V4 diff, HF Hub publish | $25k | Week 14–17 | Living Blueprint v1 published |
| **P5 — Cloud Loihi Farm** | Provisioning layer: queue + scheduling + cost tracking per Loihi run | $20k | Week 18–21 | First community Loihi experiment |
| **P6 — Scale & Benchmark** | Benchmark suite (spMV, LSM, alignment), load testing, redundancy | $20k | Week 22–26 | 10k queries/day sustained |

### Competitive Landscape

| Competitor | Focus | SynapTech Advantage |
|------------|-------|---------------------|
| **Google/JAINA** | Fruit Fly EM pipeline (proprietary) | Open platform, multi-tenant, DCSL |
| **Intel INRC** | Loihi access via grant | Pay-as-you-go Loihi, zero grant overhead |
| **FlyWire Codex** | Static connectome browser | IDRE runs it live (spMV, pulses, LSM) |
| **Neuromorpho.org** | Neuron morphology DB | Full simulation + alignment pipeline |
| **Hugging Face** | ML model hub | Living Blueprint is *continuously improving* from community data |

### Use of Funds

| Category | Amount |
|----------|--------|
| Cloud GPU (Lambda Labs, 2× A100 80GB) | $30k (6 months) |
| INRC / Loihi 2 cloud access | $15k (6 months) |
| Engineering (2 FTE, 6 months) | $80k |
| Pinecone + S3 + Hugging Face infra | $10k |
| Legal / IP counsel (DCSL framework) | $10k |
| Demo / marketing / conference travel | $5k |

### The Vision in One Sentence

> *SynapTech is building the first globally distributed, open-weights, community-governed neural computation foundry — where any researcher can run connectome-scale simulations on cloud Loihi hardware for free, while building a public intelligence substrate that grows smarter with every query.*

## 12. Scientific Validation Status

### Peer-Reviewed Foundation: The FlyWire Connectome

The core dataset is **not synthetic** — it is the Cricket FlyWire *Drosophila melanogaster* whole-brain connectome (Dorkenwald et al., *Nature* 2024), the first complete synaptic-resolution wiring diagram of an adult brain.

| Metric | Value |
|--------|-------|
| Neurons | 139,255 (78k fully proofread, 61k partially) |
| Synapses | ~50 million (130M in flywire_synapses, filtered) |
| Publication | Dorkenwald et al., *Neuronal wiring diagram of an adult brain*, Nature 2024 |
| License | CC BY 4.0 (Zenodo DOI: 10.5281/zenodo.10663702) |
| Human validation | 50+ neuroscientists proofread 1000+ hours |

### IDRE Implementation Validity

| Claim | Evidence |
|-------|----------|
| **CSC + spMV is correct** | Column-wise CSC is textbook for activation (vector × matrix). Verified against SciPy sparse. |
| **SSE streaming works** | `test_sse_streamer.py` validates publish/subscribe with asyncio. |
| **AES-256-GCM encryption** | Standard AES-GCM mode. `test_capture_split.py` validates encrypt→decrypt round-trip. |
| **Pinecone similarity search** | Deterministic vector generation and cosine-similarity query work end-to-end. |
| **Lava bridge (stub)** | Lava Process graph compiles in simulation mode. Loihi2 path untested (no hardware). |

### What Is NOT Yet Scientifically Validated

| Claim | Status | Path to Validation |
|-------|--------|--------------------|
| LSM (500 neurons, dual leak rates) | ❌ Not implemented | Implement `lsm_engine.py`, test on Mackey-Glass benchmark |
| ~20W energy claim | ❌ Not benchmarked | Need hardware Loihi access + power meter |
| Continuous alignment produces useful diffs | ❌ Not implemented | Build batch pipeline, evaluate on NLP benchmark |
| Living Blueprint outperforms static models | ❌ Not tested | A/B test alignment frequency, measure perplexity/accuracy |
| Cloud Loihi farm at scale | ❌ No provisioning | Build queue layer, benchmark latency/cost per neuron |

## 13. Scientific Validation Roadmap

### Phase 1 — LSM Benchmark (Weeks 7–9)
1. Implement 500-neuron reservoir with dual leak rates (0.8 / 0.05), ρ ≈ 1.0, ridge regression readout
2. Validate on Mackey-Glass time series prediction (standard reservoir computing benchmark)
3. Measure: NMSE, memory capacity (MC), Lyapunov exponent
4. Target: NMSE < 0.01 on MG17, MC > 50

### Phase 2 — spMV Benchmark (Weeks 10–13)
1. Compare CuPy vs SciPy vs custom CSC kernel on 130k×130k matrix
2. Measure: GFLOPS, bandwidth, latency percentiles (p50/p95/p99)
3. Compare against CSR format (is CSC really faster for activation?)
4. Target: GPU < 2ms, CPU < 15ms, CSC > CSR for column-style access

### Phase 3 — Alignment Quality (Weeks 14–17)
1. Deploy continuous alignment pipeline with DeepSeek-V4
2. Evaluate model on: SuperGLUE, HELM, code generation (HumanEval)
3. Compare against: DeepSeek-V4 base, weekly fine-tune, no alignment
4. Target: measurable improvement per 1000 telemetry events

### Phase 4 — Loihi Power Benchmark (Weeks 18–21)
1. Run LSM on Loihi 2 cloud (INRC access)
2. Measure: energy per spike, inference latency, neuron capacity
3. Compare against GPU (A100) equivalent
4. Target: ~20W verified for 500-neuron LSM at 100Hz

### Phase 5 — System Benchmark (Weeks 22–26)
1. Load test: 100 concurrent researchers, mixed activation/subgraph/query workload
2. Measure: p50/p95/p99 latency, throughput, error rate
3. SSE fan-out bottleneck test: 100 subscribers, max sustainable batch rate
4. Target: p95 < 100ms for all endpoints under 100 concurrent users
