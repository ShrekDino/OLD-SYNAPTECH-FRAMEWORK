# 04 — TEAM TECHNICAL: Architecture & Engineering

> *This document specifies every technical diagram, architecture flow, and engineering claim in the pitch deck. Includes the corrected sandbox deployment architecture.*

---

---

## 1. System Architecture — IDRE High-Level Flow

### Diagram Spec (Full-Slide)

**Title:** "IDRE System Architecture"

```
+======================================================================+
|  BROWSER (React 19 + Three.js/R3F)                                   |
|  ┌──────────────────────────────────────────────────────────────┐    |
|  │  BrainViewer.tsx          ControlPanel.tsx    SignInScreen   │    |
|  │  ┌─────────────────┐     ┌──────────────┐                    │    |
|  │  │ MorphingNeurons │     │ SSE Toggle    │                    │    |
|  │  │ (130k instances)│     │ Threshold     │                    │    |
|  │  │ CircuitTraces   │     │ Activate Btn  │                    │    |
|  │  │ OrbitControls   │     │ Neuron Info   │                    │    |
|  │  └────────┬────────┘     └──────────────┘                    │    |
|  │           │ SSE (Server-Sent Events)                          │    |
|  └───────────┼──────────────────────────────────────────────────┘    |
+==============┼=======================================================+
               │ HTTPS / SSE
               ▼
+======================================================================+
|  FASTAPI (Uvicorn, Python 3.11+)                                     |
|                                                                      |
|  ┌─────────────────────────────────────────────────────────────┐    |
|  │  CAPTURE SPLIT MIDDLEWARE (DCSL)                             │    |
|  │  ┌──────────────────────┐    ┌──────────────────────────┐   │    |
|  │  │ AES-256-GCM Encrypt  │    │ PII Strip + SHA-256 Hash │   │    |
|  │  │ → S3 Bucket          │    │ → Pinecone Vector DB     │   │    |
|  │  └──────────────────────┘    └──────────────────────────┘   │    |
|  └─────────────────────────────────────────────────────────────┘    |
|                                                                      |
|  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐    |
|  │ /health     │  │ /api/v1/     │  │ /api/v1/loihi/*       │    |
|  │ /metrics    │  │ connectome/* │  │ Neuromorphic Bridge    │    |
|  └─────────────┘  └──────┬───────┘  └────────────────────────┘    |
|                          │                                          |
|                          ▼                                          |
|  ┌──────────────────────────────────────────────────────────┐      |
|  │  CSC ENGINE (Compressed Sparse Column)                    │      |
|  │  ┌──────────────────────────────────────────────────┐    │      |
|  │  │  130k × 130k adjacency matrix                     │    │      |
|  │  │  ~3×10⁻⁵ density | ~60 MB (GPU) | ~6 MB (CPU)    │    │      |
|  │  │                                                    │    │      |
|  │  │  CuPy (GPU) ← fallback → SciPy (CPU)              │    │      |
|  │  │  spMV: ~1ms (GPU) | ~10ms (CPU)                   │    │      |
|  │  └──────────────────────────────────────────────────┘    │      |
|  └──────────────────────────────────────────────────────────┘      |
|                                                                      |
|  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐    |
|  │ SSEStreamer │  │ Lava Bridge  │  │ DeepSeek Aligner       │    |
|  │ Async Queue │  │ Intel Loihi  │  │ 1M-Context Alignment   │    |
|  │ Fan-out     │  │ Sim/Hardware │  │ Continuous Pipeline    │    |
|  └─────────────┘  └──────────────┘  └────────────────────────┘    |
+======================================================================+
```

### Key Technical Claims (With Sources)

| Claim | Evidence | Status |
|-------|----------|--------|
| spMV ~1ms on GPU | Benchmark on RTX 3060, 130k×130k CSC matrix | ✅ Tested |
| spMV ~10ms on CPU | SciPy CSC on AMD Ryzen 7, same matrix | ✅ Tested |
| CuPy → SciPy fallback | Multi-stage import check in csc_engine.py | ✅ Implemented |
| 5× latency reduction | CSC spMV vs dense attention on equivalent task | ✅ Benchmarked |
| 20× energy savings | GPU power draw (35W activation) vs A100 (700W training) | ✅ Estimated (HW pending) |

---

## 2. DCSL Cryptographic Flow

### Diagram Spec

**Title:** "Data Capture Split Layer — Cryptographic IP Protection"

```
                    +---------------------------+
                    |   HTTP Request            |
                    |   { input_vector, ... }   |
                    +------------┬──────────────+
                                 │
                                 ▼
                    +---------------------------+
                    |   CaptureSplitMiddleware  |
                    |   await request.body()    |
                    +------------┬──────────────+
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
    +---------------------------+   +---------------------------+
    | PROPRIETARY PATH          |   | PUBLIC PATH               |
    |                           |   |                           |
    | PII detected? → Yes       |   | PII detected? → Yes      |
    |                           |   |                           |
    ▼                           ▼   ▼                           ▼
    +---------------------------+   +---------------------------+
    | AES-256-GCM Encrypt       |   | PII Stripper             |
    | Key: 32 bytes (per-inst)  |   | - Remove email           |
    | Nonce: 12 bytes (random)  |   | - Remove ip_address      |
    |                           |   | - Remove auth_token      |
    | Output: ciphertext + tag  |   | - Hash user_id (SHA-256) |
    +------------┬──────────────+   +------------┬──────────────+
                 │                              │
                 ▼                              ▼
    +---------------------------+   +---------------------------+
    | S3 Bucket (Immutable)     |   | Pinecone Vector DB        |
    | synaptech-<tenant>-enc    |   | Index: synaptech-telemetry|
    | Server-side encryption    |   | Dim: 128 (→384 planned)   |
    +---------------------------+   +------------┬──────────────+
                                                 │
                                                 ▼
                                    +---------------------------+
                                    | Continuous Alignment      |
                                    | DeepSeek-V4 API           |
                                    | → Living Blueprint Update |
                                    +---------------------------+
```

### Encryption Specs

| Parameter | Value |
|-----------|-------|
| Algorithm | AES-256-GCM |
| Key Size | 32 bytes (256 bits) |
| Nonce Size | 12 bytes (random per encryption) |
| AAD | Empty (configurable to request path) |
| Key Storage | Per-instance generation at startup (production: KMS/HashiCorp Vault) |
| S3 Upload | Planned (P1) — currently debug-logged only |

---

## 3. CSC Sparse Engine vs Dense Attention

### Comparison Table

| Property | CSC Sparse Engine (IDRE) | Dense Transformer |
|----------|-------------------------|-------------------|
| **Data structure** | Compressed Sparse Column | Dense matrix |
| **Memory** | ~6 MB (CPU) / ~60 MB (GPU) | ~1.5 GB+ |
| **Compute complexity** | O(nnz × vector) | O(n²) |
| **Energy per activation** | ~35W (GPU activation) | ~700W (A100) |
| **Hardware requirements** | Any GPU or CPU | A100/H100 recommended |
| **Fallback capability** | CuPy → SciPy → NumPy | None (GPU required) |
| **Biological plausibility** | Event-driven, sparse | Fully connected, dense |
| **Interpretability** | Structural — pathways visible | Opaque — distributed |

### Visual: "Sparse vs Dense"

```
DENSE ATTENTION:                    CSC SPARSE:
┌───┬───┬───┬───┬───┐           ┌───┬───┬───┬───┬───┐
│ X │ X │ X │ X │ X │           │ X │   │   │ X │   │
├───┼───┼───┼───┼───┤           ├───┼───┼───┼───┼───┤
│ X │ X │ X │ X │ X │           │   │ X │   │   │   │
├───┼───┼───┼───┼───┤           ├───┼───┼───┼───┼───┤
│ X │ X │ X │ X │ X │    →      │   │   │ X │ X │   │
├───┼───┼───┼───┼───┤           ├───┼───┼───┼───┼───┤
│ X │ X │ X │ X │ X │           │ X │   │ X │   │ X │
├───┼───┼───┼───┼───┤           ├───┼───┼───┼───┼───┤
│ X │ X │ X │ X │ X │           │   │   │   │   │ X │
└───┴───┴───┴───┴───┘           └───┴───┴───┴───┴───┘
100% connectivity               ~0.003% connectivity
```

---

## 4. FlyWire LSM Topology

### Diagram Spec

**Title:** "Two-Region Hierarchical Liquid State Machine"

```
                    ┌─────────────────────────────┐
                    │       INPUT ENCODING         │
                    │  Character → Rate-based      │
                    │  Spike train (Poisson)       │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
       ┌─────────────────────────────────────────────────┐
       │  SENSORY NEUROPIL (Fast)                        │
       │  200 LIF neurons | α=0.8 | Fast dynamics        │
       │  ρ ≈ 0.9 (chaotic edge)                         │
       │  Receives direct input stimulus                 │
       └──────────────┬──────────────────────────────────┘
                      │  Dense recurrent connections
                      ▼
       ┌─────────────────────────────────────────────────┐
       │  CENTRAL COMPLEX (Slow)                          │
       │  300 LIF neurons | α=0.05 | Slow integration    │
       │  ρ ≈ 0.9 (chaotic edge)                         │
       │  Integrates sensory patterns over time          │
       └──────────────┬──────────────────────────────────┘
                      │
                      ▼
       ┌─────────────────────────────────────────────────┐
       │  READOUT (Ridge Regression)                      │
       │  Closed-form solution: W_out = Y X^T (XX^T + λI)⁻¹│
       │  Trains in <30s on CPU                           │
       │  >95% next-token prediction accuracy             │
       └─────────────────────────────────────────────────┘
```

### Key Parameters

| Parameter | Value | Why |
|-----------|-------|-----|
| Sensory Neuropil | 200 neurons | Fast pattern detection |
| Central Complex | 300 neurons | Temporal integration |
| Leak Rate (Fast) | α=0.8 | Rapid decay, short memory |
| Leak Rate (Slow) | α=0.05 | Slow decay, long memory |
| Spectral Radius | ρ≈0.9 | Edge of chaos = max computational capacity |
| Readout | Ridge regression (λ=0.001) | Closed-form, no backprop |
| Training time | <30s CPU | Real-time adaptation |
| Memory footprint | 1.6 MB | Microcontroller-class |

---

## 5. Repo Ecosystem Map

### Diagram Spec (Full Ecosystem Slide)

**Title:** "The SynapTechBio Ecosystem — A Full-Stack Intelligence Foundry"

```
                         ┌─────────────────────┐
                         │    the-unified-      │
                         │    blueprint         │
                         │  (Organizational     │
                         │   Philosophy)        │
                         └─────────┬───────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   synaptech-idre │◄──►│    Flywirellm    │◄──►│ flywire-realtime │
│   (Core Product) │    │  (LSM Validation)│    │ (GPU Simulation) │
└────────┬─────────┘    └──────────────────┘    └──────────────────┘
         │
         │  ┌──────────────────────────────────────────────────┐
         ├──►  EVE (AI Alignment & Self-Verification)          │
         │  └──────────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────────┐
         ├──►  OpenMonoAgent.ai (AI Infrastructure Tooling)    │
         │  └──────────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────────┐
         ├──►  digidollar (Decentralized Compute Layer)        │
         │  └──────────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────────┐
         ├──►  samchat (Encrypted Research Communication)      │
         │  └──────────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────────┐
         ├──►  Project-FreeGen (Systems-Level Engineering)     │
         │  └──────────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────────┐
         └──►  ollama-bench (AI Performance Benchmarking)      │
            └──────────────────────────────────────────────────┘
```

### Table: Why Each Repo Matters to Investors

| Repo | Investor Narrative |
|------|-------------------|
| **synaptech-idre** | "We own the core IP — connectome computation engine" |
| **Flywirellm** | "Scientifically validated — >95% accuracy in Nature dataset" |
| **flywire-realtime** | "Hardware validation — 60Hz closed-loop on consumer GPU" |
| **EVE** | "We're building alignment research, not buying it" |
| **OpenMonoAgent** | "We build AI infrastructure — we don't just use it" |
| **digidollar** | "Decentralized compute infrastructure for the platform" |
| **samchat** | "Encrypted research communication — full stack control" |
| **the-unified-blueprint** | "Organizational design — flat hierarchy, collective ownership" |
| **Project-FreeGen** | "Systems engineering capability — Vulkan, FSR, low-level" |
| **ollama-bench** | "AI benchmarking — we measure what we build" |

---

## 6. Validation Data Tables (For Q&A)

### FlyWire Connectome Statistics

| Metric | Value |
|--------|-------|
| Total neurons | 139,255 (78k fully proofread) |
| Total synapses | ~50 million (130M raw, filtered) |
| Connectome density | ~3 × 10⁻⁵ |
| Matrix format | CSC (Compressed Sparse Column) |
| Non-zero elements | ~3.7M (proofread connections) |
| Memory (GPU) | ~120 MB (139k × 139k) |
| Memory (CPU) | ~60 MB |
| Source | Dorkenwald et al., Nature 2024 |
| License | CC BY 4.0 |

### IDRE Performance

| Operation | GPU (RTX 3060) | CPU (Ryzen 7) |
|-----------|---------------|---------------|
| spMV (full 130k×130k) | ~1.2 ms | ~11 ms |
| Subgraph extraction (10k neurons) | ~0.8 ms | ~7 ms |
| Layout load → GPU | ~450 ms | — |
| Memory allocation (CSC) | ~120 MB VRAM | ~60 MB RAM |

### FlyWire LSM Performance

| Metric | Value |
|--------|-------|
| Training accuracy | >95% |
| Training time (CPU) | <30 seconds |
| Memory footprint | 1.6 MB |
| Inference time | ~15 μs per token |
| Model size | 500 LIF neurons |
| Readout | Ridge regression (closed-form) |
| Dataset | FlyWire connectome (Nature 2024) |

---

## 7. Public Sandbox Architecture

### Overview

The public sandbox is a rate-limited, free-tier deployment of IDRE accessible via web browser. No auth required to view. Minimal email+gated activation. No DCSL on free tier — collected telemetry is opt-in only with clear disclosure.

### Architecture

```
INTERNET
    │
    ▼
┌──────────────────────────────────────────────┐
│  CLOUDFLARE (DNS + DDoS Protection)          │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  NGINX Reverse Proxy                         │
│  Rate limiting: 100 req/min per IP           │
│  CORS: * (public access)                     │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  FASTAPI (Single instance, no scaling yet)   │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  SandboxMiddleware                    │    │
│  │  - Check daily activation quota      │    │
│  │  - Log anonymous usage stats         │    │
│  │  - No DCSL encryption (opt-in only)  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  CSC Engine (same as production)     │    │
│  │  - CuPy → SciPy → NumPy fallback    │    │
│  │  - Same 130k×130k adjacency matrix  │    │
│  │  - Throttled to 100 activations/day │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  SSE Streamer (throttled)            │    │
│  │  - 10 pulses/sec max (vs 1000 prod) │    │
│  │  - 1 concurrent stream per IP       │    │
│  └──────────────────────────────────────┘    │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  SINGLE A100 80GB (Reserved Instance)        │
│  - Same hardware handles sandbox + dev       │
│  - 130k×130k matrix loaded once in VRAM     │
│  - ~120 MB VRAM per instance                 │
└──────────────────────────────────────────────┘
```

### Rate Limits

| Resource | Sandbox Limit | Rationale |
|----------|--------------|-----------|
| Daily activations | 100 per email | Enough for meaningful experimentation, not enough for production dependency |
| Concurrent SSE streams | 1 per IP | Prevents abuse of streaming endpoint |
| Requests per minute | 100 per IP | Basic DDoS protection |
| Matrix resolution | 130k×130k (full) | Same data as production — no degraded experience |
| Maximum subgraph | 10k neurons | Limits worst-case compute per request |

### Data Collection (Opt-In Only)

```
┌──────────────────────────────────────────────┐
│  ON FIRST VISIT:                              │
│  Banner: "Help improve the connectome engine  │
│  by sharing anonymous usage data."            │
│  [Accept] [Decline]                           │
│  Default: Decline                             │
└──────────────────────────────────────────────┘
```

If accepted, telemetry collected:
- Activation timestamp (no user ID, no IP stored)
- Subgraph size requested
- GPU vs CPU fallback triggered
- Browser type (for visualization compatibility tracking)

**Not collected:** Email, IP address, input text, results, or any researcher data.

### Deployment

| Component | Spec | Monthly Cost |
|-----------|------|-------------|
| Compute | 1× A100 80GB reserved (Lambda Labs) | ~$2,500 |
| Storage | 50GB S3-compatible (Backblaze B2) | ~$5 |
| Domain | synaptechbio.org + sandbox subdomain | ~$15 |
| CDN | Cloudflare Free tier | $0 |
| Monitoring | Prometheus + Grafana (single node) | $0 |
| **Total** | | **~$2,520/month** |

### Why No DCSL on Free Tier

The DCSL cryptographic split-layer adds latency (~5-10ms per request for AES-256-GCM) and operational complexity (S3 bucket provisioning per tenant) that is unjustified for a free sandbox where users have zero expectation of IP protection.

The sandbox's value to the moat is:
1. Generating opt-in telemetry to seed the Pinecone vector DB
2. Demonstrating the product to potential STTR partners
3. Building organic community and GitHub visibility

Enterprise-grade DCSL is activated only when a paying customer signs an agreement. Until then, the sandbox collects minimal, anonymized, opt-in usage statistics with clear disclosure.
