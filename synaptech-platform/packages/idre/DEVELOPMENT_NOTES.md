# SynapTech IDRE — Development Notes

**Date:** 2026-05-25
**Python:** 3.13 | **Node:** 22.x
**Purpose:** Internal reference for per-file completeness, phased roadmap, and engineering context. Designed for AI agent handoffs and collaborator onboarding.

---

## Current State

The project is **fully scaffolded** — every module has at least a stub or complete implementation. The backend starts and serves on port 8000. The frontend starts and renders on port 3000.

### Per-File Completeness

| File | Status | Notes for next agent |
|------|--------|----------------------|
| `run.py` | ✅ Done | Entry point. Works. |
| `ARCHITECTURE.md` | ✅ Done | 663-line reference. Already exhaustive. |
| `PROJECT_CONTEXT.md` | ✅ Rewritten | 700+ lines, Democratized Neuromorphic Commons vision, investor narrative, scientific validation roadmap. |
| `src/shared/constants.py` | ✅ Done | All constants defined. |
| `src/shared/schemas.py` | ✅ Done | All Pydantic models. |
| `src/backend/main.py` | ✅ Done | App creation, lifespan, CORS, AuthMiddleware, CaptureSplit, router reg. |
| `src/backend/config.py` | ✅ Done | pydantic-settings with .env support. |
| `src/backend/exceptions.py` | ✅ Done | IDREException hierarchy + handler. |
| `src/backend/middleware/capture_split.py` | ✅ Done | Wired in main.py. S3 upload is a no-op (`self._s3_bucket = None`). |
| `src/backend/middleware/auth.py` | ✅ Done | Wired as ASGI middleware in `main.py` via `AuthMiddleware(BaseHTTPMiddleware)`. |
| `src/backend/middleware/tenant.py` | 📋 Planned | Multi-tenant isolation: per-tenant S3 bucket, Pinecone namespace. |
| `src/backend/routes/*.py` | ✅ All 4 done | connectome, visualization, neuromorphic, telemetry. |
| `src/backend/services/csc_engine.py` | ✅ Done | Singleton, CuPy/SciPy fallback, spMV, subgraph, layout. |
| `src/backend/services/connectome_loader.py` | ✅ Done | File discovery + real FlyWire loader. |
| `src/backend/services/sse_streamer.py` | ✅ Done | Fan-out, batch, heartbeat. |
| `src/backend/services/encryption.py` | ✅ Done | AES-256-GCM. |
| `src/backend/services/telemetry_anon.py` | ✅ Done | PII strip, hash, topology hash. |
| `src/backend/services/pinecone_client.py` | ✅ Done | Deterministic MD5→gauss vectors (placeholder — needs real embeddings). |
| `src/backend/services/lava_bridge.py` | ⚠️ Stub-safe | Works if lava-nc installed. |
| `src/backend/services/lava_processes.py` | ⚠️ Stub-safe | FlyWireNetwork with LIF model. NO reservoir topology, NO ridge regression. |
| `src/backend/services/deepseek_aligner.py` | ✅ Done | Async HTTP client, 1M-context. Single-shot only. |
| `src/backend/services/embedding_service.py` | 📋 Planned | sentence-transformers/all-MiniLM-L6-v2 → 384-dim vectors. |
| `src/backend/services/s3_client.py` | 📋 Planned | boto3 S3 wrapper, per-tenant bucket management. |
| `src/backend/services/batch_aligner.py` | 📋 Planned | S3-triggered batch scheduler for continuous alignment. |
| `src/backend/services/lsm_engine.py` | 📋 Planned | 500-neuron Liquid State Machine, ridge regression readout. |
| `src/backend/services/cloud_loihi.py` | 📋 Planned | Cloud Loihi 2 farm: provisioning, queue, scheduling. |
| `src/frontend/src/App.tsx` | ✅ Done | Stage-based routing: `SIGN_IN` → `DASHBOARD`. |
| `src/frontend/src/pages/SignInScreen.tsx` | ✅ Done | Entry point: R3F Canvas + FractalScene + SignInCard + GSAP fly-through. |
| `src/frontend/src/pages/BrainDashboard.tsx` | ✅ Done | BrainViewer + ControlPanel. |
| `src/frontend/src/pages/PortalHome.tsx` | 📋 Planned | Open Brain Platform landing page. |
| `src/frontend/src/pages/WorkspaceDashboard.tsx` | 📋 Planned | Per-user workspace. |
| `src/frontend/src/pages/ActivationSandbox.tsx` | 📋 Planned | Upload/sketch input → spMV → viz cascade. |
| `src/frontend/src/pages/LSMDemo.tsx` | 📋 Planned | LSM live text generation demo. |
| `src/frontend/src/pages/TelemetryExplorer.tsx` | 📋 Planned | Query anonymized operations. |
| `src/frontend/src/pages/AlignmentViewer.tsx` | 📋 Planned | Track Living Blueprint evolution. |
| `src/frontend/src/pages/LoihiJobManager.tsx` | 📋 Planned | Request Loihi time, check queue. |
| `src/frontend/src/components/FractalScene.tsx` | ✅ Done | R3F scene: MorphingNeurons + CircuitTraces + OrbitControls. |
| `src/frontend/src/components/MorphingNeurons.tsx` | ✅ Done | 130k InstancedMesh with ShaderMaterial, fractal→neuron vertex morph. |
| `src/frontend/src/components/CircuitTraces.tsx` | ✅ Done | ~2000-hub LineSegments with ShaderMaterial, pulsing tech-blue/gold traces. |
| `src/frontend/src/components/SignInCard.tsx` | ✅ Done | Glassmorphism card: logo, username/password fields, gradient CTA. |
| `src/frontend/src/components/BrainViewer.tsx` | ✅ Done | Unchanged. ActivationPulse NOT integrated. |
| `src/frontend/src/components/NeuronInstances.tsx` | ✅ Done | Fixed `sizeAttenuation` TS error. Uses meshStandardMaterial. |
| `src/frontend/src/components/ControlPanel.tsx` | ✅ Done | Unchanged. |
| `src/frontend/src/components/ActivationPulse.tsx` | ✅ Done | Still not integrated into BrainViewer. |
| `src/frontend/src/components/ResevoirRender.tsx` | 📋 Planned | LSM neuron activity visualization. |
| `src/frontend/src/components/TelemetryHeatmap.tsx` | 📋 Planned | Pinecone similarity heatmap. |
| `src/frontend/src/components/PortalNav.tsx` | 📋 Planned | Top-level portal navigation bar. |
| `src/frontend/src/hooks/useCameraTransition.ts` | ✅ Done | GSAP timeline hook for camera fly-through + morph + card fade. |
| `src/frontend/src/hooks/useSSE.ts` | ✅ Done | Unchanged. |
| `src/frontend/src/hooks/useGraphLayout.ts` | ✅ Done | Unchanged. |
| `src/frontend/src/hooks/usePineconeQuery.ts` | 📋 Planned | Query telemetry by similarity. |
| `src/frontend/src/hooks/useLSM.ts` | 📋 Planned | LSM connection + text generation state. |
| `src/frontend/src/shaders/morph.vert.glsl` | ✅ Done | Fractal→neuron morph vertex shader. |
| `src/frontend/src/shaders/morph.frag.glsl` | ✅ Done | Point sprite fragment with glow + ripple. |
| `src/frontend/src/shaders/circuit.vert.glsl` | ✅ Done | Circuit trace vertex with source/target interpolation. |
| `src/frontend/src/shaders/circuit.frag.glsl` | ✅ Done | Circuit trace fragment with time-based pulse glow. |
| `src/frontend/src/shaders/vertex.glsl` | 🗑️ Removed | Dead code — not wired anywhere. Recreate from spec when P1 wiring is implemented. |
| `src/frontend/src/shaders/fragment.glsl` | 🗑️ Removed | Dead code — not wired anywhere. Recreate from spec when P1 wiring is implemented. |
| `tests/backend/test_csc_engine.py` | ⚠️ CuPy-dependent | Uses `import cupy`. Will skip/fail on CPU-only. |
| `tests/backend/test_capture_split.py` | ✅ Works | No external deps. |
| `tests/backend/test_sse_streamer.py` | ✅ Works | Pure asyncio. |
| `tests/backend/test_auth.py` | 📋 Planned | JWT + API key validation. |
| `tests/backend/test_tenant.py` | 📋 Planned | Multi-tenant isolation. |
| `tests/backend/test_embeddings.py` | 📋 Planned | sentence-transformers integration. |
| `tests/backend/test_s3_client.py` | 📋 Planned | S3 upload/download. |
| `tests/backend/test_lsm_engine.py` | 📋 Planned | Reservoir dynamics + readout. |
| `tests/backend/test_batch_aligner.py` | 📋 Planned | Alignment pipeline. |
| `deploy/lambda-labs/docker-compose.cpu.yml` | 📋 Planned | CPU-only deployment. |
| `deploy/portal/Dockerfile.portal` | 📋 Planned | Portal frontend + API. |
| `deploy/portal/docker-compose.portal.yml` | 📋 Planned | Portal + PostgreSQL + Redis. |
| `deploy/portal/schema.sql` | 📋 Planned | Portal database schema. |

### Environment

- `.venv/` exists with FastAPI, Uvicorn, NumPy, SciPy, Pandas, httpx, cryptography installed
- **CuPy status**: Check with `python -c "import cupy; print(cupy.__version__)"`. If not found, backend falls back to CPU.
- `src/frontend/node_modules/` exists (React, Three.js, R3F, etc.)
- **Data**: `data/flywire/connectome.csv` and `data/layout.json` exist (synthetic)
- Real FlyWire data is NOT downloaded (9.5 GB synapse file not present)
- `.env` file: NOT present (use `.env.example` for reference)
- **Pinecone**: No API key configured. Deterministic fallback works without it.
- **DeepSeek-V4**: No API key configured. Aligner will log warning and skip.

### Running

```bash
# Backend
PYTHONPATH=$PWD python3 -m uvicorn src.backend.main:app --reload --port 8000

# Frontend (separate terminal)
cd src/frontend && npm run dev

# Data gen
python3 run.py gen-data

# TypeScript check
cd src/frontend && npx tsc --noEmit

# Tests
PYTHONPATH=$PWD python3 -m pytest tests/

# Single test
PYTHONPATH=$PWD python3 -m pytest tests/backend/test_capture_split.py -v
```

---

## Next Steps — Phased Engineering Roadmap

### P0 — Multi-Tenant Auth & Security (Cost: $15k | Timeline: Week 1–3)
- [x] **Wire auth middleware** in `main.py` — converted to `AuthMiddleware(BaseHTTPMiddleware)`, added `app.add_middleware(AuthMiddleware)`.
- [x] **CPU-only tests**: `test_csc_engine.py` now conditionally skips via `@pytest.mark.skipif`.
- [x] **Frontend build check**: CI workflow runs `npx tsc --noEmit`.
- [x] **Verify backend starts**: `/health` and `/metrics` endpoints excluded from auth.
- [ ] **Implement ORCID OAuth flow**: redirect → ORCID authorize → callback → JWT issue. Store ORCID ID in workspace context.
- [ ] **Create `tenant.py` middleware**: per-tenant S3 bucket, Pinecone namespace, workspace isolation.

### P1 — DCSL Expansion & Real Embeddings (Cost: $25k | Week 4–6)
- [ ] **Create `s3_client.py`**: boto3 wrapper. Per-tenant bucket provisioning (server-side encryption). Lifecycle policies.
- [ ] **Wire S3 upload in `capture_split.py`**: after AES-256-GCM encryption, write blob to `s3://synaptech-<tenant-id>-encrypted/`. Add retry + backoff.
- [ ] **Create `embedding_service.py`**: sentence-transformers/all-MiniLM-L6-v2 → 384-dim vectors. Replace `PineconeClient._event_to_vector()` MD5→gauss with real embeddings.
- [ ] **Integrate custom GLSL shaders**: rewrite `NeuronInstances.tsx` to use `ShaderMaterial` with per-instance vertex/fragment shading (replacing `meshStandardMaterial`).
- [ ] **Wire ActivationPulse component**: integrate into `SceneContent` in `BrainViewer.tsx`.
- [ ] **Add `usePineconeQuery` hook**: frontend query to `/api/v1/telemetry/query` with debounce and cache.

### P2 — LSM Demo & Activation Sandbox (Cost: $20k | Week 7–9)
- [ ] **Create `lsm_engine.py`**: 500-neuron reservoir, dual leak rates (0.8 / 0.05), ρ ≈ 1.0, ridge regression readout. Validate on Mackey-Glass (NMSE < 0.01, MC > 50).
- [ ] **Create `LSMDemo.tsx`**: portal page with input text → reservoir → output text. Visualize neuron activity.
- [ ] **Create `ActivationSandbox.tsx`**: sketch/manual input vector → POST `/api/v1/connectome/activate` → visualize pulse cascade on 3D brain.
- [ ] **Create `PortalHome.tsx`**: landing page with "Get Started" ORCID OAuth CTA, feature overview, live demo embed.
- [ ] **Create `PortalNav.tsx`**: navigation between PortalHome, ActivationSandbox, LSMDemo, TelemetryExplorer.
- [ ] **Add `.env` file** from `.env.example` with dev defaults.

### P3 — Open Brain Platform Portal (Cost: $25k | Week 10–13)
- [ ] **Create `WorkspaceDashboard.tsx`**: per-user workspace with recent activations, telemetry exports, Loihi run history.
- [ ] **Create `TelemetryExplorer.tsx`**: Pinecone similarity search with heatmap visualization (TelemetryHeatmap component).
- [ ] **Create `AlignmentViewer.tsx`**: track Living Blueprint evolution — version history, contributor stats, performance charts.
- [ ] **Create portal DB schema** (`deploy/portal/schema.sql`): users, workspaces, api_keys, job_queue, alignment_versions.
- [ ] **Create portal Docker Compose** (`docker-compose.portal.yml`): portal API + PostgreSQL + Redis.
- [ ] **Add `docker-compose.cpu.yml`** for non-GPU deployments.
- [ ] **Lint codebase**: `ruff check src/ && cd src/frontend && npx eslint .`

### P4 — Continuous Alignment Pipeline (Cost: $25k | Week 14–17)
- [ ] **Create `batch_aligner.py`**: S3-triggered batch workflow. On new `.enc` file → decrypt → extract topology → build DeepSeek-V4 prompt → parse diff → apply weights → publish to HF Hub.
- [ ] **Create test `test_batch_aligner.py`**: mock S3 events, validate prompt construction and diff parsing.
- [ ] **Publish `synaptech/living-blueprint`** to Hugging Face Hub. Set up automated CI/CD.
- [ ] **Add `test_embeddings.py`**: validate MiniLM dimension (384), cosine similarity correctness.
- [ ] **Add `test_s3_client.py`**: upload/download round-trip, bucket provisioning, lifecycle policy.

### P5 — Cloud Loihi Farm (Cost: $20k | Week 18–21)
- [ ] **Create `cloud_loihi.py`**: provisioning abstraction layer. Queue system (Redis-backed). Job lifecycle: queued → provisioning → running → completed → cleanup.
- [ ] **Create `LoihiJobManager.tsx`**: portal page to request Loihi time, check queue status, view results.
- [ ] **Create `ResevoirRender.tsx`**: real-time LSM reservoir activity visualization (R3F, animated ring/sphere layout).
- [ ] **Add `test_lsm_engine.py`**: reservoir dynamics, readout training, Mackey-Glass benchmark.
- [ ] **Benchmark Loihi power**: run LSM on Loihi 2 cloud, measure energy per spike.

### P6 — Scale, Benchmark & Governance (Cost: $20k | Week 22–26)
- [ ] **Load test**: 100 concurrent researchers, mixed workload. Target p95 < 100ms.
- [ ] **SSE fan-out benchmark**: 100 subscribers, max sustainable batch rate.
- [ ] **Implement `/api/v1/connectome/load`** endpoint for dataset switching at runtime.
- [ ] **Implement FlyWire streaming loader**: chunked 9.5 GB feather reading (memory-safe).
- [ ] **Add WebSocket fallback**: alternative to SSE for higher throughput.
- [ ] **Add user-facing error toasts**: frontend error boundary + toast notifications.
- [ ] **Type-check backend**: `mypy src/`.

### P7 — Public Launch & Community (Post-Seed)
- [ ] **Public beta launch**: Open Brain Platform open for registration.
- [ ] **Benchmark suite**: automated CI benchmarks (spMV GFLOPS, LSM NMSE, alignment quality).
- [ ] **Community governance**: open weights license, contributor guidelines, RFC process.
- [ ] **Academic outreach**: demo at Neuromorphic Computing Conference, Cosyne, NeurIPS.

---

## Key Technical Notes

- `PYTHONPATH=$PWD` is required for all backend commands (the `run.py` sets it automatically)
- `CSCEngine` is a singleton — call `CSCEngine.get_instance()` everywhere
- CuPy detection happens at **import time** in `csc_engine.py`. Restart needed to re-detect.
- The `_HAS_CUPY` flag is checked by `connectome_loader.py` and routes to decide CuPy vs NumPy
- `SSEStreamer()` is also a singleton (module-level class holds state)
- `CaptureSplitMiddleware` reads `request.body()` — this consumes the body stream. FastAPI route handlers must use `request.body()` AFTER middleware, or use cached body. Currently works because middleware calls `await request.body()` then passes to `call_next`.
- `PineconeClient._event_to_vector()` uses MD5 hash → seed → `random.gauss(0, 0.1)` to produce deterministic 128-dim vectors. This is NOT an embedding — it's a hash-based fingerprint for similarity by operation+topology. Replace with real embeddings for semantic search.
- The real FlyWire pipeline expects `root_ids.npy` + `proofread_connections.feather` + `positions.npy` in `data/flywire/`. These are produced by `scripts/fetch_flywire_data.py`.
- The test data generator creates 12 brain regions of ~10,833 neurons each with intra-community edge probability 0.7 and inter-community 0.3.
- PROJECT_CONTEXT.md (700+ lines) is the **primary reference** for all architecture, data flows, completeness, investor narrative, and scientific validation. Consult it before making architectural decisions.
- LSM is a **spec, not a feature** — `lava_processes.py` defines LIF neurons but no reservoir topology or ridge regression readout. Must build `lsm_engine.py` from scratch.
- DeepSeek-V4 alignment is **single-shot only** — no batch scheduling, no S3 trigger, no weight application. Must build `batch_aligner.py`.
- Vite production build may time out under 2-minute tool limit due to 130k Float32Array allocations in `MorphingNeurons useMemo`. Dev mode works fine.
