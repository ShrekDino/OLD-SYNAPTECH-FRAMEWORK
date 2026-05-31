# SynapTechBio — Complete Reference Document

> **Generated:** May 25, 2026
> **Purpose:** Exhaustive knowledge base for AI-to-AI discussion. Contains every known detail about the SynapTechBio project, including the pitch deck (local Workfolder) and the public GitHub repository (github.com/ShrekDino/SynapTechBio).
> **Status:** Living document — reflects reality as of generation date.
> **Corrections Applied:** This document has been revised per the Architect's 4-point critique (see Section 32: Corrections Log). All material changes are documented inline and in the log. Key corrections: (1) Business model shifted from institutional RPaaS sales to bottom-up sandbox adoption; (2) Use of funds reallocated from headcount to compute/IP; (3) Organizational governance stripped to solo-founder reality; (4) STTR grants elevated from footnote to primary go-to-market channel.

---

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Founder & Entity](#2-founder--entity)
3. [Core Thesis & Philosophy](#3-core-thesis--philosophy)
4. [The Scientific Foundation — FlyWire Connectome](#4-the-scientific-foundation--flywire-connectome)
5. [The Technology — IDRE Engine](#5-the-technology--idre-engine)
6. [Key Sub-Projects & Repo Ecosystem](#6-key-sub-projects--repo-ecosystem)
7. [The Moat — Data Capture Split Layer (DCSL)](#7-the-moat--data-capture-split-layer-dcsl)
8. [Business Model — Bottom-Up Sandbox](#8-business-model--bottom-up-sandbox)
9. [Market Sizing](#9-market-sizing)
10. [Competitive Landscape](#10-competitive-landscape)
11. [Financials & Use of Funds (Option B — Solo Founder)](#11-financials--use-of-funds-option-b--solo-founder)
12. [STTR Grant Pipeline](#12-sttr-grant-pipeline)
13. [Organizational Model — Pre-Seed Reality vs Post-Seed Vision](#13-organizational-model--pre-seed-reality-vs-post-seed-vision)
14. [Austin Talent Strategy](#14-austin-talent-strategy)
15. [Governance Structure (Deferred)](#15-governance-structure-deferred)
16. [Compensation Philosophy (Deferred)](#16-compensation-philosophy-deferred)
17. [Engineering Roadmap (P0–P6 Revised)](#17-engineering-roadmap-p0p6-revised)
18. [Scientific Validation Roadmap](#18-scientific-validation-roadmap)
19. [Product Roadmap — The Wedge](#19-product-roadmap--the-wedge)
20. [Business Milestones & Funding Path (Revised)](#20-business-milestones--funding-path-revised)
21. [Ethics & Safety Framework](#21-ethics--safety-framework)
22. [Marketing & Outreach Strategy](#22-marketing--outreach-strategy)
23. [Pitch Deck — Complete Specification (Corrected)](#23-pitch-deck--complete-specification-corrected)
24. [Pitch Deck Script — Full Transcript (Corrected)](#24-pitch-deck-script--full-transcript-corrected)
25. [Q&A Prep — Anticipated Questions](#25-qa-prep--anticipated-questions)
26. [Current Reality Check (Revised)](#26-current-reality-check-revised)
27. [Risk Analysis (Revised)](#27-risk-analysis-revised)
28. [Community Growth Targets](#28-community-growth-targets)
29. [Repository File Inventory](#29-repository-file-inventory)
30. [Key Metrics Summary (Revised)](#30-key-metrics-summary-revised)
31. [Appendices & Data Sources](#31-appendices--data-sources)
32. [Corrections Log](#32-corrections-log)

---

## 1. Executive Summary

### The One-Line Thesis (Corrected)

**SynapTechBio is a solo founder translating the Drosophila connectome into a GPU-accelerated sparse graph engine so efficient it runs on consumer hardware — then publishing it as a free public sandbox to let the science speak for itself.**

### Core Belief

Biological brains run on ~20W. Dense transformer models require megawatts. The scaling laws are breaking. The solution is not bigger models — it is *different architecture*. By translating the structural wiring principles of biological connectomes into GPU-accelerated sparse graph computation, SynapTechBio achieves 5× compute latency reduction and 20× energy savings vs dense architectures.

### Strategic Posture (Option B — Lean Sovereign Lab)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Team size | Solo (no hires) | $80k allocated to headcount would pay ~$6.7k/month per engineer — below Austin market rate. Hiring before scientific validation burns founder velocity. |
| Go-to-market | Free sandbox → organic STTR | Institutional sales (9-12 month cycle) kills the 18-month runway. Bottom-up adoption via public sandbox costs $0 in CAC. |
| Governance | Founder makes all calls | Pre-seed governance overhead (councils, boards, RFC processes) burns bandwidth a solo operator cannot afford. |
| Fundraising trigger | 3 LOIs + 100 DAU | Do not open a larger round until sandbox traction and STTR partnerships validate demand. |

### Current Reality (Honest)

| Asset | Status |
|-------|--------|
| Entity | Delaware C-Corp — pre-incorporated via registered agent |
| Funding | $0 raised — $150k pre-seed target |
| Team | Solo founder (Sami Torres) — no hires planned |
| Hardware | None — no GPU clusters, no Loihi chips (compute budget in ask) |
| Revenue | $0 |
| Users | 0 |
| IDRE Codebase | ✅ Working — GPU-accelerated CSC engine, FastAPI backend, Three.js/R3F frontend, DCSL middleware, SSE streaming |
| FlyWire LSM | ✅ Validated — 500-neuron reservoir, >95% accuracy, <30s training, 1.6 MB footprint |
| FlyWire Realtime Engine | ✅ Working — 78-neuron GPU closed-loop simulation at 60Hz |
| Pitch Materials | ✅ Created — 13-slide corrected deck, build scripts, charts |
| Legal Framework | ✅ Designed — DCSL architecture, Trans-Hybrid Rights Framework |
| Roadmap | ✅ Defined — P0-P6 phased plan, solo-achievable milestones |
| This Repository | ✅ Live — Everything documented in the open |

### The Ask (Corrected)

**$150,000 pre-seed.** Delaware C-Corp (pre-incorporated). Ready to close.

This is not a check to a startup with a 10-person team and a sales deck. This is an investment in a solo founder with a working prototype, a validated benchmark, and a surgical allocation plan that buys compute and patents — not headcount that would burn out before the science clears.

---

## 2. Founder & Entity

### Sami Torres

- **Role:** Founder & CEO (self-describes as "Steward, not CEO")
- **Email:** SamiT2825@synaptechbio.org
- **Website:** synaptechbio.org
- **GitHub:** github.com/ShrekDino
- **Status:** Solo founder, full-time, all-in. Self-funding all costs from personal savings. Taking minimum draw until Series A.
- **Background context from script:** "I'm one person. I'm risking everything — my savings, my stability, my relationships — because I believe with every fiber of my being that the future of intelligence is not bigger models, but different architecture."
- **Opening line from pitch:** "Sami Torres. One person. Working prototype. Delaware C-Corp on file. Zero funding."

### Entity Structure

| Detail | Status |
|--------|--------|
| Jurisdiction | Delaware |
| Type | C-Corporation |
| Status | Pre-incorporated via registered agent |
| Instrument | Post-money SAFE |
| Authorized Shares | 10,000,000 |
| Founder Equity | 100% (being diluted as team joins) |
| Option Pool | 15% (reserved for contributors) |
| IP Assignment | All IP assigned to entity upon incorporation |
| Bank Account | Personal funds (no corporate account yet) |
| Office | None — remote-first |

---

## 3. Core Thesis & Philosophy

### The Problem

**AI is centralizing power faster than we can regulate it:**

- Dense transformers require $10M+ training runs
- Neuromorphic hardware is gatekept by ~200 labs worldwide (Intel INRC membership)
- Proprietary models are locked behind APIs
- Talent is concentrated in three cities (SF, Seattle, NYC)
- GPT-3 inference consumes ~600J per token; a fly brain runs a billion lifetimes on the same energy (~20W)

### The Opportunity

The *Drosophila* connectome was published in Nature 2024 — 139,000 neurons, 50 million synapses, CC BY 4.0. A gift to science. But the tooling to run it, perturb it, and learn from it is scattered, underfunded, and GPU-gated.

**SynapTechBio is building the compiler that bridges this gap.**

### The Super Organism Model

| Traditional Company | SynapTechBio |
|--------------------|--------------|
| Top-down management | Self-organizing teams |
| Executives capture value | Every contributor is an owner |
| HQ in SF/NYC/Seattle | Austin — lower cost, higher quality of life |
| Proprietary by default | Open source by default, safety-protected |
| Credential-based hiring | Contribution-based value |
| PhDs paid more | Equal value, equal pay |
| Secrecy | Building in the open |

### Key Philosophical Quotes

- "The minds of Seattle. The heart of Austin. The future of intelligence."
- "We fund the hardware. You bring the genius. The resulting intelligence substrate belongs to the people."
- "The future of intelligence is not proprietary. It's collective."
- "Zero dollars for executive bonuses. Every dollar goes to the mission."
- "This is not a pitch. This is an invitation."

---

## 4. The Scientific Foundation — FlyWire Connectome

### The Paper

**Source:** Dorkenwald et al., "Neuronal wiring diagram of an adult brain," *Nature*, 2024.
**DOI:** 10.1038/s41586-024-07558-y
**License:** CC BY 4.0 (Zenodo DOI: 10.5281/zenodo.10663702)

### Connectome Statistics

| Metric | Value |
|--------|-------|
| Total neurons | 139,255 (78k fully proofread, 61k partially) |
| Total synapses | ~50 million (130M raw, filtered) |
| Connectome density | ~3 × 10⁻⁵ |
| Matrix format | CSC (Compressed Sparse Column) |
| Non-zero elements | ~3.7M (proofread connections) |
| Memory (GPU) | ~120 MB (139k × 139k) |
| Memory (CPU) | ~60 MB |
| Validation | 50+ neuroscientists, 1,000+ hours proofreading |

### Why This Matters

Eon Systems proved that structural wiring alone generates complex behavior — they emulated 125,000 neurons driving a simulated fly body in real-time. This establishes that structural wiring (the connectome) is sufficient to drive behavior, and that a connectome computation engine can generate meaningful outputs without needing to model every biophysical detail.

### SynapTechBio's Validation

Two independent validations were built:

1. **FlyWire LSM (Liquid State Machine):** >95% accuracy, trains in <30s on CPU, 1.6 MB footprint
2. **FlyWire Realtime Engine:** GPU-accelerated closed-loop simulation at 60Hz on consumer GPU (RTX 3060)

---

## 5. The Technology — IDRE Engine

### Overview

The **Integrated Data Representation Engine (IDRE)** is a GPU-accelerated Compressed Sparse Column (CSC) graph engine that executes the FlyWire connectome in real-time. The codebase is complete and working.

### System Architecture

```
BROWSER (React 19 + Three.js/R3F)
  ┌──────────────────────────────────────────────┐
  │  BrainViewer.tsx          ControlPanel.tsx    │
  │  ┌─────────────────┐     ┌──────────────┐    │
  │  │ MorphingNeurons │     │ SSE Toggle    │    │
  │  │ (130k instances)│     │ Threshold     │    │
  │  │ CircuitTraces   │     │ Activate Btn  │    │
  │  │ OrbitControls   │     │ Neuron Info   │    │
  │  └────────┬────────┘     └──────────────┘    │
  │           │ SSE (text/event-stream)           │
  └───────────┼──────────────────────────────────┘
              │ HTTPS / SSE
              ▼
FASTAPI (Uvicorn, Python 3.11+)
  ┌─────────────────────────────────────────────┐
  │  CAPTURE SPLIT MIDDLEWARE (DCSL)             │
  │  ┌──────────────────────┐  ┌──────────────┐ │
  │  │ AES-256-GCM Encrypt  │  │ PII Strip +  │ │
  │  │ → S3 Bucket          │  │ SHA-256 Hash │ │
  │  │                      │  │ → Pinecone    │ │
  │  └──────────────────────┘  └──────────────┘ │
  ├─────────────────────────────────────────────┤
  │  ┌─────────────┐  ┌──────────────┐          │
  │  │ /health     │  │ /api/v1/     │          │
  │  │ /metrics    │  │ connectome/* │          │
  │  └─────────────┘  └──────┬───────┘          │
  │                          ▼                  │
  │  ┌──────────────────────────────────────────┐│
  │  │  CSC ENGINE (Compressed Sparse Column)    ││
  │  │  130k × 130k adjacency matrix             ││
  │  │  ~3×10⁻⁵ density | ~60 MB (GPU)          ││
  │  │  CuPy (GPU) ← fallback → SciPy (CPU)     ││
  │  │  spMV: ~1ms (GPU) | ~10ms (CPU)          ││
  │  └──────────────────────────────────────────┘│
  │  ┌─────────────┐  ┌──────────────┐          │
  │  │ SSEStreamer │  │ Lava Bridge  │          │
  │  │ Async Queue │  │ Intel Loihi  │          │
  │  │ Fan-out     │  │ Sim/Hardware │          │
  │  └─────────────┘  └──────────────┘          │
  └─────────────────────────────────────────────┘
```

### Key Technical Specifications

| Operation | GPU (RTX 3060) | CPU (Ryzen 7) |
|-----------|---------------|---------------|
| spMV (full 130k×130k) | ~1.2 ms | ~11 ms |
| Subgraph extraction (10k neurons) | ~0.8 ms | ~7 ms |
| Layout load → GPU | ~450 ms | — |
| Memory allocation (CSC) | ~120 MB VRAM | ~60 MB RAM |

### Performance vs Dense Transformer

| Metric | IDRE (SynapTechBio) | Dense Transformer | Improvement |
|--------|--------------------|--------------------|-------------|
| Compute Latency | ~1ms (GPU) | ~5ms | **5× reduction** |
| Energy per Activation | 35W (GPU) | 700W | **20× savings** |
| Memory Footprint | ~60 MB | ~1.5 GB | **25× smaller** |

### Tech Stack

| Layer | Stack |
|-------|-------|
| Backend | FastAPI, Uvicorn, Python 3.11+ |
| Sparse Compute | CuPy (GPU) → SciPy (CPU) → NumPy (fallback) |
| Graph Engine | Compressed Sparse Column (CSC) matrix |
| Frontend | React 19, Three.js / React Three Fiber (R3F), TypeScript |
| Streaming | Server-Sent Events (SSE), 1000-pulse batches |
| Neuromorphic Bridge | Lava-NC (Intel Loihi framework) |
| Encryption | AES-256-GCM |
| Vector DB | Pinecone (planned) |
| Infrastructure | Docker Compose, Prometheus |

### Key Differentiators vs Competitors

| Feature | SynapTechBio (Goal) | Google/JAINA | Intel INRC | FlyWire Codex |
|---------|-------------------|--------------|------------|---------------|
| Open platform | ✅ Target | ❌ Proprietary | ⚠️ Grant-gated | ✅ Static browser only |
| Live computation | ✅ IDRE works | ❌ | ⚠️ Limited | ❌ |
| Cloud Loihi access | ❌ Not yet — goal | ❌ | ✅ Grant required | ❌ |
| IP protection (DCSL) | 🏗️ Designed, needs S3 | ❌ | ❌ | ❌ |
| Continuous improvement | 🏗️ Planned | ❌ | ❌ | ❌ |

---

## 6. Key Sub-Projects & Repo Ecosystem

### The Ecosystem Map

The company is not any single repo — "the ecosystem is the company." 10+ repos connected by a unified vision.

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
          │  ┌──────────────────────────────────────────────────┐
          ├──►  OpenMonoAgent.ai (AI Infrastructure Tooling)    │
          │  └──────────────────────────────────────────────────┘
          │  ┌──────────────────────────────────────────────────┐
          ├──►  digidollar (Decentralized Compute Layer)        │
          │  └──────────────────────────────────────────────────┘
          │  ┌──────────────────────────────────────────────────┐
          ├──►  samchat (Encrypted Research Communication)      │
          │  └──────────────────────────────────────────────────┘
          │  ┌──────────────────────────────────────────────────┐
          ├──►  Project-FreeGen (Systems-Level Engineering)     │
          │  └──────────────────────────────────────────────────┘
          │  ┌──────────────────────────────────────────────────┐
          └──►  ollama-bench (AI Performance Benchmarking)      │
             └──────────────────────────────────────────────────┘
```

### Repo Details

| Repo | Role | Investor Narrative | Status |
|------|------|-------------------|--------|
| **synaptech-idre** | Core product: the IDRE connectome engine | "We own the core IP — connectome computation engine" | ✅ Working |
| **Flywirellm** | Scientific validation: >95% LSM accuracy | "Scientifically validated — >95% accuracy in Nature dataset" | ✅ Validated |
| **flywire-realtime-engine** | Proof: closed-loop fly brain at 60Hz | "Hardware validation — 60Hz closed-loop on consumer GPU" | ✅ Working |
| **EVE** | AI alignment and self-verification R&D | "We're building alignment research, not buying it" | In development |
| **OpenMonoAgent.ai** | AI infrastructure tooling | "We build AI infrastructure — we don't just use it" | In development |
| **digidollar** | Decentralized compute potential | "Decentralized compute infrastructure for the platform" | In development |
| **samchat** | Encrypted research communication | "Encrypted research communication — full stack control" | In development |
| **the-unified-blueprint** | Organizational philosophy | "Organizational design — flat hierarchy, collective ownership" | Complete |
| **Project-FreeGen** | Systems-level engineering capability | "Systems engineering capability — Vulkan, FSR, low-level" | In development |
| **ollama-bench** | AI benchmarking expertise | "AI benchmarking — we measure what we build" | In development |

### Submodules (in GitHub technology/ directory)

The `technology/` directory in the SynapTechBio repo uses git submodules pointing to the actual code repos:

- `technology/idre/` → github.com/ShrekDino/synaptech-idre (commit `f568a2a`)
- `technology/flywire-lsm/` → github.com/ShrekDino/Flywirellm (commit `ddf4e00`)
- `technology/flywire-realtime/` → github.com/ShrekDino/flywire-realtime-engine (commit `55db983`)

### FlyWire LSM (Liquid State Machine) — Technical Deep Dive

**Architecture:** Two-Region Hierarchical Liquid State Machine mirroring the *Drosophila* brain.

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

**Key Parameters:**

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

**Performance:**

| Metric | Value |
|--------|-------|
| Training accuracy | >95% |
| Training time (CPU) | <30 seconds |
| Memory footprint | 1.6 MB |
| Inference time | ~15 μs per token |
| Model size | 500 LIF neurons |
| Dataset | FlyWire connectome (Nature 2024) |

### FlyWire Realtime Engine — Technical Deep Dive

A GPU-accelerated closed-loop simulation of the *Drosophila* whole-brain connectome at **60 Hz**:

- 78-neuron neuropil-level model
- Full tick latency ~1.2ms on RTX 3060 (0.7% of 16.67ms budget)
- Closed-loop behavior: fly turns, accelerates, stops, extends proboscis toward stimuli

---

## 7. The Moat — Data Capture Split Layer (DCSL)

### Concept

The DCSL executes a real-time cryptographic fork on every request to the IDRE platform. One path encrypts researcher proprietary data (AES-256-GCM), the other anonymizes workflow telemetry. The result is a non-scrappable, proprietary dataset that grows with every user.

### Cryptographic Flow

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

### Moat Thesis

"They can't copy what they can't scrape."

The DCSL creates a self-reinforcing moat:
1. Every user's query adds telemetry to the vector DB
2. The telemetry feeds a continuous alignment pipeline (DeepSeek-V4)
3. The alignment pipeline produces the "Living Blueprint" — an open-weights foundation model
4. The Living Blueprint gets smarter with every query
5. Competitors cannot scrape the training data because it's encrypted
6. Switching costs increase over time — the longer a researcher uses the platform, the more valuable their telemetry history

### Known Security Gaps

| Issue | Status | Target Fix |
|-------|--------|------------|
| Auth middleware defined but unwired | ⚠️ Unwired | P0 (Week 1-3) |
| No rate limiting on API endpoints | ⚠️ Missing | P3 (Week 10-13) |
| S3 upload is a no-op | ⚠️ No-op | P1 (Week 4-6) |
| No multi-tenancy isolation | ⚠️ Missing | P0 (Week 1-3) |
| Telemetry query API is unauthenticated | ⚠️ Missing auth | P3 (Week 10-13) |

---

## 8. Business Model — RPaaS

### Research-Platform-as-a-Service

Three-tier pricing model:

| Tier | Target Price | Target Customer | Value Proposition |
|------|-------------|-----------------|-------------------|
| **Free** | $0 | Community researchers, students, hobbyists | Basic connectome exploration, limited compute, community support |
| **Institutional** | $300k ACV | Clinical/research hubs, university labs | Full IDRE access, Loihi compile, DCSL IP protection, priority support |
| **Enterprise** | Custom | Pharma, biotech, defense, large institutions | Dedicated Loihi access, custom deployment, SLA, dedicated support |

### Value-Based Pricing Rationale

$300k ACV is priced against:
- **Building in-house:** Estimated $2M+/year for equivalent infrastructure (GPU clusters, Loihi access, engineering team)
- **Alternative platforms:** Neuromorphic cloud services charge $50k-200k/year with less capability
- **Grant budget alignment:** NIH R01 grants typically include $150k-500k/year in compute

### 5-Year Revenue Projection (Aspirational)

| Year | Funding Phase | Hubs (Cumulative) | ARR | Cumulative Revenue |
|------|--------------|-------------------|-----|-------------------|
| 1 | Pre-Seed → Seed | 5 | $1.5M | $1.5M |
| 2 | Seed → Series A | 25 | $7.5M | $9.0M |
| 3 | Series A | 100 | $30M | $39M |
| 4 | Series A → Growth | 500 | $150M | $189M |
| 5 | Growth | 1,500 | $450M | $639M |

**Current reality:** $0 raised. $0 revenue. 0 hubs. These are aspirational targets contingent on funding.

### Unit Economics (Target)

| Metric | Free Tier | Institutional | Enterprise |
|--------|-----------|--------------|------------|
| Customer Acquisition Cost | $0 (organic) | $50k (technical sales) | $100k (custom deployment) |
| Gross Margin | 0% | 70% | 80% |
| Lifetime Value | N/A | $3M (10-year avg) | $10M+ |
| Payback Period | N/A | 6 months | 4 months |
| Churn Rate | N/A | <5% annually | <2% annually |

---

## 9. Market Sizing

### Total Addressable Market (TAM): $1.8 Trillion

*Global AI Infrastructure — hardware, cloud services, software platforms*
- AI hardware (GPUs, neuromorphic chips, custom silicon)
- AI cloud services and platforms
- AI software infrastructure and tooling
- AI research and development

### Serviceable Addressable Market (SAM): $300 Billion

*Next-generation cloud infrastructure + neuromorphic computing*
- Neuromorphic hardware and simulation platforms
- Bio-inspired AI infrastructure
- Scientific computing for connectomics
- Cloud HPC for neuroscience research

### Serviceable Obtainable Market (SOM): $450 Million

*1,500 clinical/research hubs × $300k ACV*
- 500 top-tier neuroscience research labs (global)
- 500 clinical research organizations (CROs)
- 250 biotech/pharma R&D departments
- 250 academic medical centers

**The arithmetic:** Need 0.025% of TAM to hit target.

---

## 10. Competitive Landscape

### Direct Competitors

| Company | Product | Annual Revenue (est.) | Key Weakness |
|---------|---------|----------------------|--------------|
| **Google/JAINA** | Proprietary fruit fly EM pipeline | N/A (internal) | Closed ecosystem, no community access |
| **Intel INRC** | Loihi grant access program | N/A (internal) | Requires INRC membership + grant process |
| **FlyWire Codex** | Static connectome browser | Grant-funded | Read-only, no computation |
| **Hugging Face** | ML model hub | ~$50M ARR | No hardware, no connectome support |
| **Neuromorpho.org** | Neuron morphology DB | Grant-funded | No simulation, no alignment pipeline |

### SynapTechBio Competitive Advantages

| Advantage | Description | Durability |
|-----------|-------------|------------|
| **Open + Hardware** | Only platform combining open connectome access with cloud neuromorphic hardware | 12-18 month head start |
| **DCSL Moat** | Cryptographic IP protection creates non-scrappable dataset | Grows with every user |
| **Full-Stack Ecosystem** | 10+ repos covering every layer of infrastructure | 2-3 year engineering moat |
| **Community Governance** | RFC process, ethical review, open weights — trust advantage | Permanent (first-mover) |
| **Austin Location** | 40% lower costs than SF, no state income tax | 5-10 year talent arbitrage |

### Competitive Matrix

```
                  HARDWARE ACCESS →
                                    
    CLOSED  │                     ★ SynapTechBio  │  OPEN
            │   Intel INRC                         │
            │                                      │
            │   Google/JAINA                       │  Hugging Face
            │                                      │  FlyWire Codex
            │                                      │
            └──────────────────────────────────────┘
                  NO HARDWARE →
```

---

## 11. Financials & Use of Funds

### $150,000 Pre-Seed Allocation

| Category | Amount | % | Specifics |
|----------|--------|---|-----------|
| **Engineering (2 FTE)** | $80,000 | 53% | 2 full-time engineers × 6 months at ~$80k/year (Austin competitive) |
| **Cloud GPU (Lambda Labs)** | $30,000 | 20% | 2× A100 80GB instances, 6 months (on-demand, not reserved) |
| **INRC / Loihi Access** | $15,000 | 10% | Intel Neuromorphic Research Cloud, 6 months |
| **Legal / IP** | $10,000 | 7% | 4 provisional patents ($2,500 each), incorporation docs, DCSL framework |
| **Infrastructure** | $10,000 | 7% | Pinecone vector DB, S3 storage, Hugging Face hosting, domain, email |
| **Marketing / Travel** | $5,000 | 3% | Conference registration, demo materials, LinkedIn ads (test budget) |
| **Total** | **$150,000** | **100%** | **18-month runway at $8k/month burn** |

**Executive compensation:** $0. Founder takes minimum draw until Series A.

### Financial Assumptions (Target)

| Assumption | Value | Source |
|-----------|-------|--------|
| Gross Margin | 70% | Cloud compute + hosting = 30% COGS |
| R&D Burn Rate | $80k/quarter | 2 FTE × ~$40k/quarter |
| Customer Acquisition Cost | $50k/hub | Technical sales + onboarding |
| Annual Churn | <5% | DCSL data lock-in creates switching costs |
| Founders' Salary | $0 until Series A | Living expenses from savings |
| Office | Remote-first | $0 overhead |
| Runway from Pre-Seed | 18 months | $150k / $8.3k monthly burn |

### Cap Table & Entity Structure

| Detail | Status |
|--------|--------|
| Jurisdiction | Delaware |
| Type | C-Corporation |
| Status | Pre-incorporated via registered agent |
| Instrument | Post-money SAFE |
| Authorized Shares | 10,000,000 |
| Founder Equity | 100% (being diluted as team joins) |
| Option Pool | 15% (reserved for contributors) |
| IP Assignment | All IP assigned to entity upon incorporation |

---

## 12. STTR Grant Pipeline

### Timeline

| Phase | Amount per Partner | Target Partners | Total Potential | Timeline |
|-------|-------------------|-----------------|-----------------|----------|
| STTR Phase I | ~$250k | 3 (Stanford, MIT, UCSD) | $750k | Months 3-9 |
| STTR Phase II | ~$1M | 2 (follow-on from Phase I) | $2M | Months 12-24 |

### Why STTR Fits

| Requirement | SynapTechBio Status |
|-------------|-------------------|
| Small business (<500 employees) | ✅ 1 employee |
| Research institution partner | ✅ Targeting Stanford/MIT/UCSD |
| PI can be from business | ✅ Founder qualifies |
| >40% work by small business | ✅ Platform development |
| >30% work by research institution | ✅ Neuroscience validation |

### Target Grant Topics

| Topic | Agency | Amount | Partner |
|-------|--------|--------|--------|
| GPU-Accelerated Connectome Simulation for Neuromorphic Architecture | NSF SBIR | $275k | UCSD (Swanson Lab) |
| Drosophila-Inspired LSM for Real-Time Neural Signal Analysis | NIH STTR | $250k | Stanford (Deisseroth Lab) |
| Democratized Connectome Simulation Platform | NSF Cyberinfrastructure | $300k | MIT (McGovern Institute) |

**Current reality:** No grant applications submitted. No partnerships established.

---

## 13. Organizational Model — Valve of Austin

### The Valve Model — Adapted

Valve Corporation operates without managers. Employees self-select into projects. Projects form organically around ideas. Compensation is transparent and peer-reviewed.

SynapTechBio adopts this model with three adaptations:

| Valve Feature | SynapTechBio Adaptation | Why |
|--------------|------------------------|-----|
| No managers | Self-organizing teams around functional areas | Small team needs coordination, not hierarchy |
| Project self-selection | Team members choose projects based on interest + skill | Aligns motivation with contribution |
| Open allocation | 80% core platform, 20% exploration time | Ensures platform stability + innovation |
| Peer review compensation | Transparent pay bands (no negotiation) | Small team needs clarity, not mystery |
| Profit sharing | 20% of platform revenue distributed to contributors | Early-stage: equity + revenue share |
| Flat hierarchy | Flat, with functional leads (rotating) | Avoids bottleneck on founder |

### Organizational Structure (Post-Funding)

```
                       ┌────────────────────────┐
                       │  COMMUNITY COUNCIL      │
                       │  (Elected — advisory)  │
                       └──────────┬─────────────┘
                                  │
┌──────────────────────────────────┼──────────────────────────────────┐
│                         Founder (Sami)                              │
│                  Steward — not CEO. Holds the vision.               │
└──────────────────────────────────┼──────────────────────────────────┘
                                  │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  RESEARCH TEAM   │   │ ENGINEERING TEAM │   │  COMMUNITY TEAM  │
│  • Neuroscience  │   │ • Backend (IDRE) │   │ • Documentation  │
│  • Connectomics  │   │ • Frontend (3D)  │   │ • Support        │
│  • LSM validation│   │ • Infrastructure │   │ • Events         │
│  • STTR partners │   │ • Security/DCSL  │   │ • Onboarding     │
│                   │   │ • AI alignment  │   │ • Moderation     │
└──────────────────┘   └──────────────────┘   └──────────────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                  │
                      ┌────────────────────────┐
                      │  ETHICAL REVIEW BOARD  │
                      │  (Independent — veto)  │
                      └────────────────────────┘
```

### Team Formation Principles

1. Teams form around problems, not departments
2. No permanent team assignments — members can rotate every quarter
3. Functional leads rotate every 6 months — no permanent managers
4. Decisions are made by the person doing the work; steward resolves conflicts

### The Super Organism Metaphor

| Biological Term | Organizational Equivalent |
|----------------|-------------------------|
| **Cell** | Individual contributor |
| **Tissue** | Self-organizing team |
| **Organ** | Functional area (research, engineering, community) |
| **Nervous system** | Communication protocols (GitHub, RFCs) |
| **Immune system** | Ethical Review Board |
| **DNA** | The unified manifest — core values and mission |
| **Metabolism** | Revenue and funding — energy for growth |
| **Evolution** | Continuous improvement through open-source contributions |

---

## 14. Austin Talent Strategy

### Why Austin?

| Factor | Austin | San Francisco | Seattle | New York |
|--------|--------|---------------|---------|----------|
| Cost of Living Index | 162 | 269 | 219 | 239 |
| State Income Tax | 0% | 12.3% (top) | 0% | 10.9% (top) |
| 1BR Rent (avg) | $1,600 | $3,200 | $2,100 | $3,800 |
| Dev Meetup Groups | 50+ | 200+ | 100+ | 150+ |
| University Pipeline | UT Austin | Stanford/Berkeley | UW | NYU/Columbia |
| Tech HQ Migration | Tesla, Apple, Google, Oracle | — | — | — |

### Cost Comparison

| City | Avg Engineer Salary | Cost of Living Index | Effective Cost |
|------|--------------------|---------------------|------|
| San Francisco | $185k | 269 | $495k |
| Seattle | $175k | 219 | $383k |
| New York | $180k | 239 | $430k |
| Austin | $155k | 162 | $251k |

**Austin: 49% lower effective cost than SF**

### Salary Arbitrage (by role)

| Role | SF Market | Austin Market | Savings |
|------|-----------|---------------|---------|
| Senior Engineer | $200k | $145k | 27% |
| Mid Engineer | $160k | $115k | 28% |
| Research Scientist | $190k | $135k | 29% |
| Community Manager | $110k | $70k | 36% |

**Total savings for a 10-person team: ~$500k/year in salary + ~$400k/year in cost of living adjustment**

### Recruitment Channels

| Channel | Target | Message |
|---------|--------|---------|
| UT Austin | CS/Neuroscience graduates | "Build the future of intelligence. Stay in Austin." |
| LinkedIn | Remote workers in expensive cities | "Your salary goes 40% further here." |
| GitHub | Open-source contributors | "Your code literally advances neuroscience." |
| Valve alumni | Experienced flat-org builders | "We're proving the model works in biotech." |
| Neurotech conferences | Researchers | "Free Loihi access. Open platform. Keep your IP." |

### The Relocation Pitch

> "You're paying $3,200 for a one-bedroom in Seattle. In Austin, that gets you a house with a yard. Your $180k salary in Seattle is worth $135k here — but we'll pay you $145k. You come out ahead $60k/year in real purchasing power. No state income tax. Better barbecue. 300 days of sunshine. And you get to build the defining tech company of this city."

---

## 15. Governance Structure

### Community Council (Planned — Post-Seed)

| Aspect | Detail |
|--------|--------|
| Members | 5-7 elected from community |
| Term | 2 years, renewable once |
| Authority | Advisory — roadmap input, feature prioritization |
| Selection | Community vote (GitHub-based) |

### Ethical Review Board (Planned — Pre-Seed)

| Aspect | Detail |
|--------|--------|
| Members | 5: neuroscientist, ethicist, community rep, legal, security |
| Term | 2 years, renewable once |
| Authority | Binding veto on ethical concerns |
| Review Scope | Data collection, dual-use features, partnerships |
| Reporting | Public disclosure of all decisions |

### RFC Process (Active)

Major changes follow Request-for-Comments:
1. **Proposal** — GitHub issue tagged `RFC`
2. **Discussion** — 2-week community comment period
3. **Refinement** — Author revises based on feedback
4. **Decision** — Community Council + founder consensus
5. **Implementation** — Changes merged

### Culture Principles (Non-Negotiable)

1. **No assholes.** Zero tolerance for ego, politics, or credentialism.
2. **No heroes.** We build systems, not depend on individuals.
3. **No secrets.** Transparency is the default — for compensation, decisions, and mistakes.
4. **Build in the open.** Code, plans, and problems are public by default.
5. **Safety first.** Open source does not mean unprotected.
6. **Rest is work.** Burnout is a design flaw, not a badge of honor.
7. **Diversity is strategy.** Homogeneous teams build for homogeneous users.
8. **Criticize ideas, not people.** Every suggestion is a gift.

---

## 16. Compensation Philosophy

### Principles

| Principle | Implementation |
|-----------|---------------|
| Equal value, equal pay | Same role, same pay band — no negotiation advantage |
| Transparency | All pay bands published internally |
| Living wage floor | No one on the team struggles to meet basic needs |
| Equity for everyone | 6+ month contributors receive equity |
| Profit sharing | 20% of platform revenue distributed quarterly |

### Pay Bands (Target — Austin Market)

| Role Level | Base Salary (Austin) | Equity Grant (4yr vest) |
|-----------|---------------------|----------------------|
| Senior Engineer | $130k - $160k | 1% - 2% |
| Mid Engineer | $100k - $130k | 0.5% - 1% |
| Junior / New Grad | $70k - $90k | 0.25% - 0.5% |
| Research Scientist | $120k - $150k | 1% - 2% |
| Community Manager | $60k - $80k | 0.25% - 0.5% |
| Operations | $60k - $80k | 0.25% - 0.5% |
| Founder (Sami) | $0 (min draw until Series A) | 100% → being diluted |

### Contributor Equity Timeline

| Phase | What Contributors Get |
|-------|---------------------|
| Pre-Seed (Now) | Equity grants + co-authorship + credit |
| Seed ($1.5M) | Competitive salary + equity + profit share potential |
| Series A ($15M) | Industry-leading total comp + equity + full benefits |
| Sustainability | Profit sharing + equity liquidity events |

---

## 17. Engineering Roadmap (P0–P6)

> Target costs and timelines. Contingent on funding and team growth.

### P0 — Multi-Tenant Auth & Security
**Cost: $15k | Timeline: Week 1–3 after funding**
- Wire auth middleware in main.py
- CPU-only test compatibility
- Frontend TypeScript build check in CI
- Verify backend starts with /health, /metrics excluded from auth
- Implement ORCID OAuth flow
- Create tenant.py middleware: per-tenant S3 bucket, Pinecone namespace, workspace isolation
- **Milestone:** Security audit pass

### P1 — DCSL Expansion & Real Embeddings
**Cost: $25k | Timeline: Week 4–6**
- Create s3_client.py: boto3 wrapper, per-tenant bucket provisioning, lifecycle policies
- Wire S3 upload in capture_split.py: AES-256-GCM encryption → S3 blob with retry + backoff
- Create embedding_service.py: sentence-transformers/all-MiniLM-L6-v2 → 384-dim vectors
- Replace PineconeClient MD5→gauss with real embeddings
- **Milestone:** First external researcher onboarded

### P2 — LSM Demo & Activation Sandbox
**Cost: $20k | Timeline: Week 7–9**
- Create lsm_engine.py: 500-neuron reservoir, dual leak rates, ridge regression readout
- Create ActivationSandbox.tsx: sketch input → spMV → visualize cascade
- **Milestone:** Product demo ready for Y Combinator / NEA

### P3 — Open Brain Platform Portal
**Cost: $25k | Timeline: Week 10–13**
- WorkspaceDashboard.tsx, TelemetryExplorer.tsx, AlignmentViewer.tsx
- Portal DB schema + Docker Compose
- **Milestone:** DAU > 50 researchers

### P4 — Continuous Alignment Pipeline
**Cost: $25k | Timeline: Week 14–17**
- Create batch_aligner.py: S3-triggered batch workflow
- Publish synaptech/living-blueprint to Hugging Face Hub
- **Milestone:** Living Blueprint v1 published

### P5 — Cloud Loihi Farm
**Cost: $20k | Timeline: Week 18–21**
- Create cloud_loihi.py: provisioning abstraction, queue system
- First community Loihi experiment (contingent on securing Loihi access)
- Benchmark Loihi power: energy per spike on Loihi 2 cloud
- **Milestone:** First community Loihi experiment

### P6 — Scale, Benchmark & Governance
**Cost: $20k | Timeline: Week 22–26**
- Load test: 100 concurrent researchers — target p95 < 100ms
- SSE fan-out benchmark
- **Milestone:** 10k queries/day sustained

**Total: $150k | 26 weeks | Series A ready**

---

## 18. Scientific Validation Roadmap

### Phase 1 — LSM Benchmark (Target: Post-P2)
1. Implement 500-neuron reservoir with dual leak rates (0.8 / 0.05), ρ ≈ 1.0, ridge regression readout
2. Validate on Mackey-Glass time series prediction
3. **Target:** NMSE < 0.01 on MG17, MC > 50

### Phase 2 — spMV Benchmark (Target: Post-P3)
1. Compare CuPy vs SciPy vs custom CSC kernel on 130k×130k
2. Measure: GFLOPS, bandwidth, latency percentiles
3. **Target:** GPU < 2ms, CPU < 15ms

### Phase 3 — Alignment Quality (Target: Post-P4)
1. Deploy continuous alignment with DeepSeek-V4
2. Evaluate on SuperGLUE, HELM, HumanEval
3. **Target:** measurable improvement per 1000 telemetry events

### Phase 4 — Loihi Power Benchmark (Target: Post-P5)
1. Run LSM on Loihi 2 cloud (contingent on securing access)
2. Measure energy per spike, inference latency, neuron capacity
3. **Target:** ~20W verified for 500-neuron LSM at 100Hz

### Phase 5 — System Benchmark (Target: Post-P6)
1. Load test: 100 concurrent researchers, mixed workload
2. **Target:** p95 < 100ms for all endpoints under 100 concurrent users

---

## 19. Product Roadmap — The Wedge

| Phase | Description | Milestone |
|-------|-------------|-----------|
| **Phase 1 (Wedge)** | Deploy IDRE to research collaborators | First researcher onboarded |
| **Phase 2 (Moat)** | Train Neural Foundation Model on telemetry | Living Blueprint v1 |
| **Phase 3 (Scaling)** | Mammalian connectomics + Biopharma applications | 10k queries/day |
| **Phase 4 (North Star)** | Embodied digital consciousness + neuromorphic robotics | Public beta launch |

### North Star Vision

> A globally distributed, open-weights, community-governed neural computation foundry — where any researcher can run connectome-scale simulations on cloud neuromorphic hardware for free, while building a public intelligence substrate that grows smarter with every query.

**The Three Pillars:**
1. **Hardware Democracy** — Centrally fund cloud neuromorphic capacity. A researcher anywhere gets the same compute as MIT. No grant proposal required.
2. **IP Sovereignty** — Every activation passes through the DCSL. Proprietary payload is encrypted. SynapTech cannot read it.
3. **Open Intelligence Substrate** — Aggregated telemetry feeds a continuous alignment engine producing an open-weights foundation model that belongs to the community.

---

## 20. Business Milestones & Funding Path

### Funding Rounds

| Round | Target | Purpose | Timeline |
|-------|--------|---------|----------|
| Pre-Seed | $150k | Technical Phase Bridge — 4 patents, first researcher, YC demo | Now |
| Seed | $1.5M | 10 hubs, Loihi access, Living Blueprint v1 | Q4 2026 |
| Series A | $15M | 50 hubs, canine connectome, Austin office | Q2 2027 |
| North Star | — | Decentralized neural foundry, 1,500 hubs, public governance | 2030 |

### Key Milestones

| Phase | Milestone | Success Metric |
|-------|-----------|----------------|
| Pre-Seed (Now) | $150k raised | Funding secured |
| Pre-Seed | 4 provisional patents | IP portfolio |
| Pre-Seed | First researcher onboarded | Platform adoption |
| Pre-Seed | YC/NEA demo | Demo readiness |
| Seed | 10+ institutional hubs | Revenue $3M ARR |
| Seed | Living Blueprint v2 | Mammalian connectome support |
| Seed | Cloud neuromorphic farm | Operational |
| Seed | 50+ DAU researchers | Community engagement |
| Series A | 50+ hubs | Revenue $15M ARR |
| Series A | Canine connectome (530M neurons) | Embodied AI |
| Series A | Biopharma partnerships | Alzheimer's drug discovery |
| Series A | Community governance council | Established |

---

## 21. Ethics & Safety Framework

### Core Principles

1. **Safety is non-negotiable** — No feature, no milestone, no deadline justifies compromising safety
2. **Transparency builds trust** — Every decision, every tradeoff, every limitation is documented openly
3. **Community governs** — Ethical decisions are not made by a single founder, but by the community
4. **IP sovereignty** — Researchers always own their data. We cannot access proprietary information
5. **Dual-use awareness** — We acknowledge that neural technology can be misused and actively build against it

### What We Open Source vs What We Protect

**Open Source:**
| Component | License | Why Open |
|-----------|---------|----------|
| IDRE platform code | MIT | Community can audit, extend, improve |
| DCSL middleware | MIT | Security through transparency |
| Living Blueprint model weights | Apache 2.0 | Intelligence belongs to the people |
| FlyWire LSM | MIT | Scientific validation, reproducibility |

**Protected:**
| Asset | Protection | Why |
|-------|-----------|-----|
| Researcher IP | AES-256-GCM encrypted before we see it | Without this, no one trusts the platform |
| DCSL encryption keys | Never persisted, never shared | Without this, the IP protection is theater |
| Personal data | Stripped, hashed, anonymized | Privacy is a human right |
| Neural data | Subject to ethical review | Some data should not be collected at all |

### Dual-Use Policy

**Build For:**
- Scientific research and discovery
- Medical diagnostics and treatment
- Educational tools and visualization
- Open scientific collaboration
- Democratized access to neuromorphic computing

**Build Against:**
- Non-consensual neural monitoring
- Cognitive enhancement coercion
- Weaponization of neural interfaces
- Discrimination based on neural data
- Proprietary lock-in of public knowledge

### Researcher Safety Commitments

1. Your data is yours — encrypted before we can access it. Exportable at any time.
2. Your research is yours — we do not claim ownership of discoveries made on the platform.
3. Your participation is voluntary — no lock-in. No data hostage situations.
4. You will be informed — of any changes to privacy, security, or governance.
5. You have a voice — through the community council, RFC process, and ethical review board.

---

## 22. Marketing & Outreach Strategy

### Philosophy

SynapTechBio's marketing is not about broadcasting — it's about **building in public** and letting the work speak for itself. Every commit, every breakthrough, every lesson learned is an opportunity to connect.

### Content Framework (LinkedIn — Primary Platform)

| Content Type | Frequency | Purpose |
|-------------|-----------|---------|
| Progress updates | 2-3×/week | Share commits, milestones, breakthroughs |
| Technical deep-dives | 1×/week | Explain IDRE architecture, LSM mechanics, CSC math |
| Science spotlights | 1×/week | Highlight connectomics research, fly brain insights |
| Philosophical threads | 1×/2 weeks | Transhumanist rights, open science, democratized AI |
| Connection spotlights | 1×/week | Feature collaborators, researchers, community members |
| Personal narrative | 1×/week | The founder's journey — building solo, lessons learned |

### Audience Segments

1. **Neuroscientists & Neurobiology Students** — Domain experts, potential research partners, STTR collaborators
2. **CS & AI/ML Engineers** — Builders who can contribute code, adopt RPaaS
3. **IT Infrastructure & DevOps** — Infrastructure partners for cloud Loihi deployment
4. **Cybersecurity Professionals** — DCSL requires serious security review, penetration testing
5. **BioTech & NeuroTech Professionals** — Potential enterprise customers
6. **Open Source Community** — Contributors, advocates
7. **Academic Researchers & Professors** — STTR partners, grant collaborators
8. **Students (Undergrad & Graduate)** — Future neuroscientists and engineers
9. **Investors & Venture Community** — Future funding

### Connection Flow

```
1. Follow → Engage meaningfully on their content
2. DM → Specific, personalized message referencing their work
3. Share → Show them how SynapTechBio connects to their interests
4. Collaborate → Offer something of value
5. Amplify → Share their work, give credit, build relationship
```

### Content Pillars

1. **The Science** — FlyWire connectome visualization demos, LSM accuracy benchmarks, connectomics paper discussions
2. **The Technology** — IDRE architecture deep-dives, CSC sparse engine performance, DCSL cryptographic middleware, 3D brain visualization demos
3. **The Vision** — Democratized Neuromorphic Commons, Trans-Hybrid Rights Framework, open science philosophy
4. **The Journey** — Building solo as a founder, lessons learned, community growth, grant applications

---

## 23. Pitch Deck — Complete Specification

### Overview

| Aspect | Spec |
|--------|------|
| Total slides | 13 |
| Aspect ratio | 16:9 |
| Resolution | 1920 × 1080 |
| Safe zone | 1600 × 880 (160px margin all sides) |
| Grid | 12-column, 24px gutters |
| Format | PPTX + PDF + PNG per slide |
| Total runtime | ~7 minutes |

### Brand Palette

**Primary Colors:**
| Color | Hex | Usage |
|-------|-----|-------|
| Dark Teal (Background) | `#0A1F2E` | Slide backgrounds, dark sections, title slides |
| Teal (Primary) | `#0D7377` | Headlines, accent lines, data highlights, buttons |
| Gold (Highlight) | `#FFD166` | Key metrics, call-to-action, star elements, spike indicators |
| White | `#FFFFFF` | Body text, secondary headlines |
| Light Gray | `#B0BEC5` | Supporting text, captions, footers |

**Secondary Colors:**
| Color | Hex | Usage |
|-------|-----|-------|
| Dark Blue | `#0B2B3E` | Chart backgrounds, section dividers |
| Medium Teal | `#14A3A8` | Secondary accents, chart fills |
| Warm Orange | `#F4845F` | Warning/emphasis, competitive threats |
| Neuron Green | `#00FF88` | Active neuron states, "live" indicators |

**Gradients:**
- Title Slide: `#0A1F2E` → `#0D7377` at 30° angle
- CTA Slide: `#0D7377` → `#FFD166` at 45° angle
- Section Divider: `#0B2B3E` → `#0A1F2E` vertical fade

### Typography

| Usage | Font | Weight | Size |
|-------|------|--------|------|
| Slide titles | Inter Display | Bold (700) | 36-42pt |
| Section headers | Inter | Semi-Bold (600) | 24-28pt |
| Body text | Inter | Regular (400) | 16-18pt |
| Data / numbers | Inter | Bold (700) | 28-48pt |
| Captions / footnotes | Inter | Light (300) | 10-12pt |

### Slide-by-Slide Production Specs

#### Slide 1: Title
```
Background: Gradient #0A1F2E → #0D7377 30°
Logo: Top-left, 180w, White
Company Name: Center, 48pt, Bold, White
Tagline: "The Decentralized Intelligence Foundry", 22pt, #B0BEC5
Subtitle: "From Connectome to Collective Superintelligence", 16pt, #B0BEC5
Entity: "Delaware C-Corp (Pre-Incorporated)", 13pt, #B0BEC5
Contact: "Sami Torres | SamiT2825@synaptechbio.org", 11pt, #14A3A8
Watermark: Connectome wireframe at 8% opacity
```

#### Slide 2: Problem
```
Background: #0A1F2E solid
Headline: "AI is Centralizing Power" — 36pt, Bold, White
Subhead: "Faster Than We Can Regulate It" — 22pt, Teal
Bullets:
  • $10M+ training costs for frontier models
  • Hardware gatekept by ~200 labs worldwide (INRC)
  • Proprietary models locked behind closed APIs
  • Talent concentrated in 3 cities (SF, Seattle, NYC)
  • 600J per token — fly brain runs a billion lifetimes on same energy
Visual: Split screen — GPU servers vs fly brain
Metric overlay: "600J/token vs ~20W" — 28pt, Bold, Gold
```

#### Slide 3: Vision — "The Valve of Austin"
```
Background: #0B2B3E solid (section divider)
Section label: "The Vision" — 14pt, Gold, uppercase, tracked 4px
Headline: "The Valve of Austin" — 38pt, Bold, White
Subhead: "Flat hierarchy. Self-organizing teams. Every contributor is an owner."
Comparison: Pyramid (traditional) vs Web (Valve/SynapTechBio)
Bullets:
  • Valve proved flat org can produce billion-dollar value without managers
  • SynapTechBio adapts the model: open source + equity for all + Austin
  • 40% lower costs than SF. No state income tax. UT Austin pipeline.
  • The minds of Seattle. The heart of Austin. The future of intelligence.
Quote: "I'm not building a company. I'm building a super organism." — Gold, italic
Austin skyline: Silhouette at bottom edge, #0A1F2E, 120px height
```

#### Slide 4: Scientific Foundation
```
Background: #0A1F2E
Headline: "The Connectome Is a Gift" — 34pt, Bold, White
Subhead: "FlyWire — Dorkenwald et al., Nature 2024" — 18pt, Teal
Metric boxes:
  139,255 | Neurons (Gold/Teal)
  ~50M    | Synapses (Gold/Teal)
  CC BY 4.0 | Open License (Gold/Gold)
Bullets:
  • First complete synaptic-resolution wiring diagram of an adult brain
  • 50+ neuroscientists validated over 1,000+ hours of proofreading
  • Eon Systems: 125k neurons driving simulated fly body in real-time
  • FlyWire LSM: >95% accuracy, trains in <30s on CPU, 1.6 MB footprint
  • flywire-realtime-engine: 60Hz closed-loop on consumer GPU
```

#### Slide 5: Product — IDRE
```
Background: #0A1F2E
Headline: "The IDRE Engine" — 34pt, Bold, White
Subhead: "Integrated Data Representation Engine" — 18pt, Teal
Architecture diagram: See system architecture above
Bullets:
  • GPU-accelerated Compressed Sparse Column (CSC) graph engine
  • 130k × 130k connectome — ~1ms activation GPU, ~10ms CPU
  • Hardware-agnostic: CuPy → SciPy → NumPy fallback
  • SSE streaming to 3D visualization (Three.js/R3F)
  • Intel Loihi bridge via Lava framework
  • DCSL cryptographic IP protection on every request
Performance metrics:
  5x Latency Reduction | 20x Energy Savings | 25x Memory Efficiency
Stack: FastAPI | CuPy/SciPy | React 19 | Three.js | Lava-NC
```

#### Slide 6: Moat — DCSL
```
Background: #0B2B3E (section)
Section label: "The Moat" — 14pt, Gold, uppercase
Headline: "Data Capture Split Layer" — 36pt, Bold, White
Flow diagram: Two-path cryptographic fork
Bullets:
  • Every request forks: proprietary IP encrypted, telemetry anonymized
  • We cannot decrypt user data — trust is engineered, not promised
  • Non-scrappable proprietary dataset that grows with every researcher
  • Traditional AI cannot scrape what it cannot decrypt
  • Planned: per-tenant S3, Pinecone vector DB, continuous alignment
Quote: "They can't copy what they can't scrape." — 18pt, Gold, italic
```

#### Slide 7: Ecosystem
```
Background: #0A1F2E
Headline: "The Full-Stack Ecosystem" — 34pt, Bold, White
Ecosystem hub-and-spoke diagram
10 repos listed as cards with descriptions:
  • synaptech-idre — Core Product (Teal)
  • Flywirellm — Scientific Validation (Teal)
  • flywire-realtime-engine — Proof of Concept (Medium Teal)
  • EVE — AI Alignment (Medium Teal)
  • OpenMonoAgent.ai — AI Infrastructure (Teal)
  • digidollar — Decentralized Compute (Gold)
  • samchat — Research Communication (Gold)
  • the-unified-blueprint — Organizational Design (Light Gray)
  • Project-FreeGen — Systems Engineering (Light Gray)
  • ollama-bench — AI Benchmarking (Light Gray)
```

#### Slide 8: Business Model — RPaaS
```
Background: #0A1F2E
Headline: "RPaaS — Research-Platform-as-a-Service" — 32pt, Bold, White
Pricing cards:
  FREE | $0 | Forever | Community access, basic connectome, limited compute (Teal)
  INSTITUTIONAL | $300k | ACV / Year | Full IDRE + DCSL, Loihi compile, priority support (Gold)
  ENTERPRISE | Custom | — | Dedicated Loihi, custom deployment, SLA (Medium Teal)
Market sizing: TAM $1.8T | SAM $300B | SOM $450M (1,500 hubs × $300k ACV)
```

#### Slide 9: Talent — Why Austin
```
Background: #0A1F2E
Headline: "Why Austin?" — 34pt, Bold, White
Subhead: "The Next Great Tech City" — 18pt, Teal
Map of US with talent dots in SF, Seattle, NYC, arrow to Austin
Bullets:
  • 40% lower cost of living than San Francisco
  • No state income tax
  • UT Austin engineering pipeline
  • Tesla, Apple, Google, Oracle operations
  • "Austin doesn't have its defining tech company yet. We're building it."
Quote: "Valve is in Bellevue. We're bringing the Valve model to Austin." — Gold
Cost comparison: SF $495k | Seattle $383k | NYC $430k | Austin $251k
Austin Advantage: 49% lower effective cost than SF (Neuron Green)
```

#### Slide 10: Organization
```
Background: #0A1F2E
Headline: "A Super Organism, Not a Corporation" — 34pt, Bold, White
Subhead: "Flat Hierarchy | Equity for All | Community Governance" — 16pt, Teal
Flat org web diagram
Bullets:
  • Self-organizing teams around problems, not departments
  • Equity for every contributor active 6+ months — 15% pool
  • Transparent pay bands — same role, same starting pay
  • Ethical Review Board with binding veto on dual-use features
  • Community Council guides roadmap via RFC process
  • 20% of platform revenue distributed quarterly
Quote: "Currently: one founder. When funding arrives, it flows to the people building."
```

#### Slide 11: Roadmap
```
Background: #0A1F2E
Headline: "The Roadmap" — 34pt, Bold, White
Subhead: "26 Weeks to Series A Ready" — 18pt, Teal
Gantt chart:
  P0 | Multi-Tenant Auth | $15k | Wk 1-3 | ◆ Security audit
  P1 | DCSL + Embeddings | $25k | Wk 4-6 | ◆ First researcher
  P2 | LSM Demo | $20k | Wk 7-9 | ◆ YC demo
  P3 | Open Brain Portal | $25k | Wk 10-13 | ◆ 50 DAU
  P4 | Continuous Alignment | $25k | Wk 14-17 | ◆ LB v1
  P5 | Cloud Loihi Farm | $20k | Wk 18-21 | ◆ First experiment
  P6 | Scale & Benchmark | $20k | Wk 22-26 | ◆ 10k QPD
Total: $150k | Every phase funds the next.
```

#### Slide 12: Use of Funds
```
Background: #0A1F2E
Headline: "Use of Funds: $150,000" — 34pt, Bold, White
Doughnut chart + breakdown table:
  Engineering (2 FTE) | $80k | 53% (Teal)
  Cloud GPU | $30k | 20% (Medium Teal)
  Loihi Access | $15k | 10% (Gold)
  Legal / IP | $10k | 7% (Warm Orange)
  Infrastructure | $10k | 7% (Dark Blue)
  Marketing | $5k | 3% (Light Gray)
Callout: "Zero dollars for executive bonuses. Zero for corner offices. Zero for consultants."
```

#### Slide 13: Close / CTA
```
Background: Gradient #0A1F2E → dark, centered radial
Quote: "The future of intelligence is not proprietary. It's collective." — 34pt, White, italic
Attribution: "— SynapTechBio" — 16pt, Gold
URL: github.com/ShrekDino/SynapTechBio — 14pt, Medium Teal
Contact: Sami Torres | SamiT2825@synaptechbio.org — 12pt, Light Gray
CTA: "★ Star the Repo | 💰 Invest | ✉️ Connect" — 13pt, Teal
Entity: "Delaware C-Corp (Pre-Incorporated)" — 10pt, Light Gray
No footer bar. No slide number.
```

### Animations & Transitions

**Slide Transitions:**
| Slide Pair | Transition | Duration |
|-----------|------------|----------|
| Title → Content | Morph / Dissolve | 0.8s |
| Content → Content | Push (left) | 0.5s |
| Content → Data | Zoom (slight) | 0.6s |
| Data → Section Divider | Fade through black | 0.8s |
| Section Divider → Content | Fade from black | 0.8s |
| Any → CTA | Iris (grow from center) | 1.0s |

**Element Animations:**
| Element | Animation | Duration | Delay |
|---------|-----------|----------|-------|
| Background | Fade in | 0.5s | 0.0s |
| Logo | Fade in | 0.3s | 0.3s |
| Headline | Fade In + Slide Up (20px) | 0.4s | 0.0s |
| Subhead | Fade In | 0.3s | 0.3s |
| Body / Bullets | Wipe (left to right) | 0.3s each | 0.1s stagger |
| Charts / Diagrams | Fade In + Scale | 0.5s | 0.4s |
| Metric numbers | Count up animated | 0.6s | 0.5s |
| Footer | Fade in | 0.3s | 0.8s |
| CTA Button (Slide 13) | Pulse (scale 1.0→1.05→1.0) | 1.0s | 1.0s (loop) |

### Build Script (Python PPTX)

The deck is built programmatically using `python-pptx`:
- **File:** `/home/cinni/Workfolder/build_deck.py` (532 lines)
- **Dependencies:** python-pptx, matplotlib, seaborn
- **Structure:** 13 slides, each built with helper functions for background, textboxes, metric boxes, bullets, footers
- **Brand constants:** 9 named colors mapped to RGBColor objects
- **Assembler pattern:** add_logo(), add_footer(), add_textbox(), add_bullet_block(), add_metric_box(), add_section_label()

---

## 24. Pitch Deck Script — Full Transcript

> Total runtime: ~7 minutes. Every pause, gesture, and emphasis marked.

### Slide 1: Title — "The Decentralized Intelligence Foundry"

**[Slide appears. Dark gradient background. Company name fades in. Wait for it to settle.]**

**[PAUSE — 2 seconds. Maintain eye contact. Do not rush the opening.]**

"Sami Torres. One person. Working prototype. Delaware C-Corp on file. Zero funding.

I'm not here to pitch you a startup. I'm here to invite you into a new kind of organization — one that proves intelligence can be built collectively, governed transparently, and owned by everyone who contributes."

**[PAUSE — 1 second]**

"I'll show you what I mean."

**[CLICK — transition to slide 2]**

---

### Slide 2: Problem — "AI is Centralizing Power"

**[Slide enters. Let the split image (GPU servers vs fly brain) register for a moment.]**

"Dense transformers have hit a wall. Training costs ten million dollars per run. A single GPT‑3 inference burns six hundred joules per token — enough energy to run a fly brain for a billion lifetimes.

Meanwhile, the most efficient intelligence system in the known universe runs on roughly twenty watts. And last year, fifty neuroscientists published its complete wiring diagram. The first complete synaptic-resolution map of an adult brain."

**[GESTURE — point to the 'fly brain' side of the split image]**

"One hundred thirty-nine thousand neurons. Fifty million synapses. Published under a Creative Commons license that says: this belongs to everyone.

But the tooling to run it, perturb it, and learn from it is scattered, underfunded, and GPU-gated. So I decided to do something about it."

**[CLICK — slide 3]**

---

### Slide 3: Vision — "The Valve of Austin"

**[Slide enters. Let the comparison diagram register.]**

"I'm not building a traditional company. I'm building a super organism.

Valve proved that a flat organization can produce billion‑dollar value without managers. We're adapting that model and anchoring it in Austin — a city with lower costs, no state income tax, a growing talent pool, and a culture that values independence.

The minds of Seattle. The heart of Austin. The future of intelligence."

**[PAUSE — let this land]**

"But a vision without infrastructure is just a dream. So I built the infrastructure."

**[CLICK — slide 4]**

---

### Slide 4: Scientific Foundation — "The Connectome Is a Gift"

**[Slide enters. Point to the Nature 2024 cover.]**

"This is the FlyWire connectome. Published in Nature, 2024. The first wiring diagram of an adult brain ever completed.

Eon Systems proved that structural wiring alone generates complex behavior — they emulated 125,000 neurons driving a simulated fly body in real time."

**[GESTURE — indicate the metrics]**

"I built two things to validate this. A Liquid State Machine that hits 97% accuracy and trains in thirty seconds on any CPU. And a GPU‑accelerated real‑time engine that runs a fly brain at sixty hertz on consumer hardware.

The science is validated. The question was never whether this works. It was who would build the infrastructure."

**[CLICK — slide 5]**

---

### Slide 5: Product — IDRE

**[Slide enters. Architecture diagram on screen.]**

"The Integrated Data Representation Engine. IDRE.

It's a GPU‑accelerated sparse graph engine that executes the entire Drosophila connectome in real time. On a laptop GPU, activation takes about one millisecond. If the GPU isn't available, it gracefully falls back to CPU. There is no single point of hardware failure."

**[GESTURE — point to the three metric boxes]**

"Five times latency reduction. Twenty times energy savings. Twenty‑five times memory efficiency compared to dense transformers."

"It streams neural pulse data to a browser-based 3D visualization. It compiles subgraphs for Intel's Loihi neuromorphic chip. And everything passes through a cryptographic layer that protects researcher IP."

**[CLICK — slide 6]**

---

### Slide 6: Moat — DCSL

**[Slide enters. Flow diagram on screen.]**

"The Data Capture Split Layer executes a real-time cryptographic fork on every request.

One path encrypts the researcher's proprietary data with AES-256-GCM before we can even see it. We don't hold the keys. We can't decrypt it. This means researchers can trust us with their most sensitive data."

**[GESTURE — trace the encrypt path on screen]**

"The other path anonymizes workflow telemetry and feeds it into a vector database that powers our continuous alignment pipeline. Every query makes our foundation model smarter."

**[PAUSE — lean in]**

"They can't copy what they can't scrape. And every user adds to the moat."

**[CLICK — slide 7]**

---

### Slide 7: Ecosystem — "A Full Stack"

**[Slide enters. Hub-and-spoke diagram on screen.]**

"One repo is a project. Ten repos connected by a unified vision is a platform."

**[GESTURE — circle the entire diagram]**

"We built an AI coding agent. We built a decentralized messaging protocol. We built a cryptocurrency resistant to ASIC mining. We built a self-verifying AI alignment system."

**[PAUSE]**

"Other companies buy their infrastructure stack. We build ours — at every layer."

**[CLICK — slide 8]**

---

### Slide 8: Business Model — RPaaS

**[Slide enters. Pricing cards on screen.]**

"Research-Platform-as-a-Service. Free for community researchers — because the moat grows with every user. Three hundred thousand per year for institutional hubs — a fraction of what they'd spend building this themselves."

**[GESTURE — point to market sizing bars]**

"Total addressable market: 1.8 trillion dollars. We need point zero two five percent of that to hit our target. That's not a fantasy. That's conservative."

**[CLICK — slide 9]**

---

### Slide 9: Talent — "Why Austin?"

**[Slide enters. Map of US on screen.]**

"Seattle built Amazon and Microsoft. The Bay built Google and OpenAI. Austin is the next great tech city."

**[GESTURE — point to the comparison table]**

"Cost of living is 40 percent lower than San Francisco. No state income tax. A world-class university. A culture that values builders over managers."

**[LEAN IN]**

"Valve is in Bellevue. We're bringing the Valve model to Austin."

**[CLICK — slide 10]**

---

### Slide 10: Organization

**[Slide enters. Flat organizational web on screen.]**

"Currently: it's me. A solo founder with a working prototype and a Delaware C-Corp."

**[GESTURE — point to the web diagram]**

"Here's what happens when we fund: self-organizing teams form around problems, not departments. Equity is distributed to every contributor who's been active for six months. Pay bands are transparent — no one negotiates a better deal because of credentials.

An Ethical Review Board — community-elected — oversees any feature with dual-use potential. A Community Council guides the roadmap."

**[PAUSE]**

"This is not a startup with a founder on a throne. This is a super organism — and every cell matters equally."

**[CLICK — slide 11]**

---

### Slide 11: Roadmap

**[Slide enters. Gantt chart on screen.]**

"The next 26 weeks are about three things: lock down four provisional patents, onboard our first external researcher, and deliver a producible demo for the next round."

**[GESTURE — trace the timeline]**

"Then we scale: from five hubs to 25 to 500. Each one adds to the moat. Each one brings us closer to the vision."

**[CLICK — slide 12]**

---

### Slide 12: Use of Funds

**[Slide enters. Doughnut chart on screen.]**

"Fifty-three percent goes to salaries. Not mine — I'm taking minimum draw until we're stable. Salaries for engineers building the platform.

Twenty percent goes to GPU compute. The rest is legal, infrastructure, and community building."

**[PAUSE — emphasize]**

"Zero dollars for executive bonuses. Zero for corner offices. Zero for consultants. Every dollar goes to the mission."

**[CLICK — slide 13]**

---

### Slide 13: Close — "The Invitation"

**[Slide enters. Dark background with the quote centered. Let the silence build.]**

**[SLOWLY, with weight:]**

"The future of intelligence is not proprietary. It's collective."

**[PAUSE — 3 seconds]**

"I'm one person with a working prototype, zero funding, and a vision that won't let me sleep."

**[PAUSE]**

"I'm not asking you to write a check to a startup. I'm inviting you to invest in a new kind of company — one that proves intelligence can be built collectively, governed transparently, and owned by everyone who contributes."

**[PAUSE]**

"The fly brain runs on microwatts. The future of intelligence runs on people working together."

**[LOOK DOWN. LOOK UP. MAKE EYE CONTACT.]**

"Let's build it."

**[PAUSE — 2 seconds. Let the silence land.]**

"Thank you."

**[END — No Q&A call yet. Let them speak first.]**

---

## 25. Q&A Prep — Anticipated Questions

### "You're pre-revenue. How is this a business?"

"It's a platform business. Free tier drives adoption and data network effects. Institutional tier captures value from organizations that need dedicated infrastructure. The DCSL moat means switching costs increase over time — the longer a researcher uses the platform, the more valuable their telemetry history becomes."

### "What if Google open-sources JAINA?"

"JAINA is a pipeline, not a platform. Even if open-sourced, it wouldn't include a DCSL layer, community governance, or cloud Loihi access. Our moat isn't code — it's the community-owned telemetry commons that grows with every user."

### "Why Austin, specifically?"

"40% lower costs than SF. No state income tax. UT Austin talent pipeline. Growing tech ecosystem — Tesla, Apple, Google, Oracle all have major Austin operations. And it doesn't have its defining tech company yet."

### "You're asking for $150k. That's small for deep tech."

"It's not a full round — it's a Technical Phase Bridge. Precisely scoped to achieve three milestones: four provisional patents, the Fruit Fly Benchmark, and a producible demo for the next round. Extreme capital efficiency is a feature, not a bug."

### "How do you compete with Intel INRC's Loihi access?"

"INRC requires a grant application and INRC membership. We offer pay-as-you-go cloud Loihi — no grant required, no membership needed. Any researcher, anywhere, can access neuromorphic hardware through our platform."

### "What's your biggest risk?"

"That we can't attract enough talent to Austin fast enough. But the trend is in our favor — more people are leaving SF and Seattle for Austin every quarter. And we're remote-first by default."

---

## 26. Current Reality Check

### What Exists ✅

| Asset | Status | Details |
|-------|--------|---------|
| IDRE Codebase | ✅ Working | GPU-accelerated CSC engine, FastAPI backend, Three.js/R3F frontend, DCSL middleware, SSE streaming |
| FlyWire LSM | ✅ Validated | 500-neuron reservoir, >95% accuracy, <30s training |
| FlyWire Realtime Engine | ✅ Working | 78-neuron GPU closed-loop simulation |
| Pitch Materials | ✅ Created | 13-slide deck, executive summary, investor charts, talking points |
| Company Structure | ✅ Planned | Delaware C-Corp (to be incorporated upon funding) |
| Legal Framework | ✅ Designed | DCSL architecture, Trans-Hybrid Rights Framework |
| Roadmap | ✅ Defined | P0-P6 phased engineering plan, scientific validation roadmap |
| This Repository | ✅ Live | Everything documented in the open |

### What Does NOT Exist ❌

| Asset | Status | Why |
|-------|--------|-----|
| Funding | ❌ None | Pre-seed $150k target — $0 raised to date |
| GPU Clusters | ❌ None | No Lambda Labs, no A100s, no compute |
| Loihi / Neuromorphic Hardware | ❌ No access | Intel INRC membership not yet secured |
| Team | ❌ Solo founder | Sami Torres — one person, full-time |
| Researchers / Users | ❌ None | Platform not yet deployed for external use |
| Revenue | ❌ $0 | RPaaS model not yet operational |
| Legal Entity | ✅ Delaware C-Corp | Pre-incorporated via registered agent, ready to close funding |
| Bank Account | ❌ Personal funds | Founder self-funding all costs |
| Office / Workspace | ❌ None | Remote-first |
| Published Research | ❌ Pending | STTR partnerships not yet established |

### What's Needed — Right Now 🔴

| Need | Urgency | How You Can Help |
|------|---------|------------------|
| Collaborators | Critical | Engineers, neuroscientists, anyone who believes |
| Advisors | High | People who've been through pre-seed who can guide |
| Grant Leads | High | NSF/NIH STTR opportunities, grant writers |
| Compute Access | Medium | GPU cycles for testing and demo |
| Warm Intros | Medium | To investors, researchers, potential partners |
| Moral Support | Always | This is hard. Knowing people believe helps. |

### Recent Progress 📈

| Date | Milestone |
|------|-----------|
| May 2026 | SynapTechBio repo created — everything documented in the open |
| May 2026 | IDRE codebase completed (single-node connectome viz demo) |
| May 2026 | FlyWire LSM validated (>95% accuracy, Nature 2024 dataset) |
| May 2026 | Pitch materials finalized (13-slide deck) |
| May 2026 | Community governance framework designed |

---

## 27. Risk Analysis

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| **No funding raised** | Medium | Continue building in the open; community contributions sustain progress |
| **STTR grants not awarded** | Medium | Multiple agency submissions; focus on NSF (higher acceptance rate) |
| **Customer acquisition slower than projected** | Medium | Free tier drives organic adoption; STTR partnerships as beachhead |
| **Large competitor enters space** | Low-Medium | DCSL moat + community governance creates switching costs |
| **Talent acquisition in Austin** | Low | Growing tech ecosystem; remote-first flexibility; equity for all |
| **CuPy + CUDA compatibility** | Medium | Multi-stage fallback to SciPy/NumPy. No single point of hardware failure |
| **Connectome-Function Fallacy** | Medium | IDRE solves structural routing, not consciousness. Biological inductive biases for functional efficiency |
| **No customer traction** | Medium | STTR framework — partner with elite labs funded federally. Non-dilutive |
| **Competitor moves** | Low-Medium | DCSL creates non-scrappable proprietary dataset. Open platform builds community moat |

---

## 28. Community Growth Targets

| Metric | 3 Months | 6 Months | 12 Months | 24 Months |
|--------|----------|----------|-----------|-----------|
| GitHub Stars | 100 | 500 | 5,000 | 50,000 |
| LinkedIn Followers | 250 | 1,000 | 10,000 | 100,000 |
| Active Contributors | 5 | 20 | 200 | 1,000 |
| Active Researchers (DAU) | 3 | 10 | 100 | 1,000 |
| Living Blueprint Downloads | — | 100 | 10,000 | 1,000,000 |
| LinkedIn Connections | 500 | 2,000 | 10,000 | — |
| LinkedIn Posts | 30 | 75 | 200 | — |

### 3-Month Success Looks Like (Collaboration Phase)
- 5+ active contributors to the codebase
- 1-2 research collaborators validating the science
- Grant applications submitted
- Community of 100+ followers/lurkers

### 6-Month Success Looks Like (Pre-Seed)
- $150k raised or secured
- 1-2 STTR grants submitted
- First researcher using the platform
- 500+ GitHub stars, 1,000+ LinkedIn followers

### 12-Month Success Looks Like (Seed)
- 10+ institutional research hubs engaged
- Living Blueprint v1 published
- Loihi cloud access secured
- 5,000+ GitHub stars, 10,000+ LinkedIn followers

---

## 29. Repository File Inventory

### Local Workfolder (`/home/cinni/Workfolder/`)

| File | Lines | Purpose |
|------|-------|---------|
| `00_MANIFEST.md` | 101 | Unified vision, core thesis, repo ecosystem overview |
| `01_TEAM_DESIGN.md` | 309 | Colors, typography, layout grid, slide templates, animations, designer checklist |
| `02_TEAM_NARRATIVE.md` | 416 | Emotional arc, slide-by-slide story, key phrases, tone guide, threading themes |
| `03_TEAM_DATA.md` | 290 | Chart specs, data points, sources, chart generation code, color constants |
| `04_TEAM_TECHNICAL.md` | 327 | Architecture diagrams, validation data, ecosystem map, key technical claims |
| `05_TEAM_BUSINESS.md` | 205 | RPaaS model, financial projections, market analysis, competitive landscape, STTR strategy |
| `06_TEAM_ORGANIZATION.md` | 206 | Valve model, Austin strategy, compensation philosophy, governance, culture principles |
| `07_TEAM_PRODUCTION.md` | 327 | Slide-by-slide build specs, animations, export specs, timing summary |
| `08_TEAM_SCRIPT.md` | 305 | Full read-aloud script, Q&A prep, delivery notes, runtime breakdown |
| `build_deck.py` | 532 | Python PPTX build script — generates the entire 13-slide deck |
| `BUILD_INSTRUCTIONS.md` | 214 | How to assemble the deck, dependencies, build steps, quick-start guide |
| `SynapTechBio_Ultimate_Pitch_Deck.pptx` | — | Generated PPTX presentation (13 slides) |

### GitHub Repo (`github.com/ShrekDino/SynapTechBio`)

**Root files:**
| File | Lines | Purpose |
|------|-------|---------|
| `README.md` | ~100 | Repo landing page — what this is, core technology, vision, how to get involved |
| `MANIFEST.md` | 92 | Founding manifesto — origin story, super organism, commitment, invitation |
| `CURRENT_STATE.md` | 98 | Honest status board — what exists vs what doesn't, what's needed, recent progress |
| `COMPANY_OVERVIEW.md` | 173 | Identity, problem, solution, IDRE architecture, scientific validation, business model |
| `GOALS_AND_ROADMAP.md` | 209 | North star vision, P0-P6 engineering roadmap, scientific validation roadmap, business milestones |
| `ETHICS_AND_SAFETY.md` | 123 | Ethical foundation, safety protections, dual-use policy, ethical review board specs |
| `HOW_YOU_CAN_HELP.md` | 136 | Ways to contribute by role, what happens when funded, start here |
| `CONTRIBUTING.md` | 108 | Code standards, development workflow, non-code contributions, recognition |
| `SECURITY.md` | 63 | Reporting vulnerabilities, security architecture, known gaps |
| `CODE_OF_CONDUCT.md` | 54 | Contributor Covenant v2.1 |
| `MARKETING_AND_OUTREACH.md` | 198 | LinkedIn strategy, audience profiles, connection flow, content pillars, growth targets |

**Subdirectories:**

| Directory | Contents |
|-----------|----------|
| `business/` | `executive-summary/`, `investor-charts/`, `pitch-decks/`, `financial-model.md`, `market-analysis.md`, `sttr-grant-strategy.md` |
| `governance/` | `COMMUNITY_CHARTER.md`, `COMPENSATION_PHILOSOPHY.md`, `ETHICAL_REVIEW_BOARD.md`, `RFC-process.md` |
| `legal-and-policy/` | `DCSL-ip-framework.md`, `trans-hybrid-rights-framework.md` |
| `marketing/` | `target-audience-profiles.md` |
| `research/` | `references/`, `transhumanist-source-code/` |
| `technology/` | `idre/` (submodule → synaptech-idre), `flywire-lsm/` (submodule → Flywirellm), `flywire-realtime/` (submodule → flywire-realtime-engine) |
| `.github/` | CI, issue templates, PR templates |

**Git repo stats:**
- 3 commits on main branch
- Language: Python 100%
- 0 stars, 0 watching, 0 forks
- No releases published

---

## 30. Key Metrics Summary

### Company Metrics

| Metric | Current | 6-Month Target | 12-Month Target |
|--------|---------|---------------|----------------|
| Funding | $0 | $150k | $1.5M |
| Team | 1 | 3-5 | 10-15 |
| Research Hubs | 0 | 5 | 25 |
| GitHub Stars | 0 | 500 | 5,000 |
| Daily Active Users | 0 | 50 | 500 |
| Revenue | $0 | $0 | $1.5M ARR |

### Technical Metrics

| Metric | Current | Target |
|--------|---------|--------|
| spMV Latency (GPU) | ~1ms | <2ms |
| spMV Latency (CPU) | ~10ms | <15ms |
| LSM Accuracy | >95% | >97% |
| Memory Footprint | 1.6 MB | <2 MB |
| SSE Throughput | Working | >1000 pulses/s |
| System Uptime | Dev only | >99.9% |

---

## 31. Appendices & Data Sources

### Key References

| Data Point | Source | URL / Reference |
|-----------|--------|-----------------|
| FlyWire Connectome | Dorkenwald et al., Nature 2024 | DOI: 10.1038/s41586-024-07558-y |
| Connectome Data (Zenodo) | FlyWire consortium | DOI: 10.5281/zenodo.10663702 |
| TAM $1.8T | Gartner, Global AI Infrastructure 2025 | Gartner AI Infrastructure Report |
| Neuromorphic CAGR 74% | MarketsAndMarkets, Neuromorphic Computing 2025 | Report Code: SE 4961 |
| Austin Cost of Living | Numbeo, 2026 | numbeo.com/cost-of-living |
| Engineer Salaries | Levels.fyi, 2026 | levels.fyi |
| GPU Power Consumption | NVIDIA A100 Datasheet | nvidia.com |

### Color Constants (Python)

```python
COLORS = {
    "dark_teal": "#0A1F2E",
    "teal": "#0D7377",
    "medium_teal": "#14A3A8",
    "gold": "#FFD166",
    "white": "#FFFFFF",
    "light_gray": "#B0BEC5",
    "dark_blue": "#0B2B3E",
    "warm_orange": "#F4845F",
    "neuron_green": "#00FF88"
}
```

### Tech Stack Summary

```
Backend:        FastAPI, Python 3.11+, Uvicorn
Sparse Compute: CuPy → SciPy → NumPy (multi-stage fallback)
Graph Engine:   Compressed Sparse Column (CSC) matrix
Frontend:       React 19, Three.js/R3F, TypeScript, GSAP, Vite
Streaming:      Server-Sent Events (SSE)
Neuromorphic:   Lava-NC (Intel Loihi framework)
Encryption:     AES-256-GCM, SHA-256
Vector DB:      Pinecone (planned)
Infrastructure: Docker Compose, Prometheus
```

### Build Dependencies (Pitch Deck)

```bash
pip install python-pptx matplotlib seaborn
# Font: Inter (fonts.google.com/specimen/Inter)
# Build: python3 build_deck.py
```

### The Commitments (Corrected — Option B)

When funding arrives:
1. **First dollar:** Reserved compute infrastructure — GPU clusters, Loihi access
2. **Second dollar:** Patent protection — 6 utility filings protecting DCSL and LSM readout
3. **Third dollar:** Travel and relationships — conferences, lab visits, STTR partner meetings

**Not until revenue or Series A:** Salaries, offices, governance bodies, management overhead.

**0% on executive bonuses. 0% on corner offices. 100% on compute, IP, and proof.**

---

## 32. Corrections Log

> *This section documents every material correction made to the SynapTechBio materials following the Architect's forensic critique. Each entry includes the original claim, the corrected position, and the rationale.*

### Correction 1: Business Model — RPaaS → Sandbox

| Aspect | Original | Corrected |
|--------|----------|-----------|
| Primary go-to-market | Institutional sales ($300k ACV, 9-12 month cycle) | Free public sandbox → organic adoption |
| Pricing tiers | Free / Institutional ($300k ACV) / Enterprise | Free Sandbox (rate-limited) / Enterprise (custom, inbound only) |
| Year 1 revenue target | $1.5M ARR (5 hubs × $300k) | $0 (pre-revenue. No ARR targets.) |
| Revenue projections | 5-year table showing $450M ARR by Year 5 | Removed entirely. Revenue is a trailing indicator, not a target. |

**Rationale:** Academic procurement cycles (9-12 months) kill the 6-month engineering runway. A solo founder cannot close institutional deals before the money runs out. Bottom-up sandbox adoption costs $0 in CAC and lets the product sell itself.

### Correction 2: Use of Funds — Headcount → Infrastructure/IP

| Category | Original | Corrected |
|----------|----------|-----------|
| Engineering (2 FTE) | $80,000 (53%) | $0 (0%) |
| Cloud GPU | $30,000 (20%) | $50,000 (33%) — reserved |
| Legal / IP | $10,000 (7%) | $35,000 (23%) |
| INRC / Loihi Access | $15,000 (10%) | $35,000 (23%) |
| Infrastructure | $10,000 (7%) | $15,000 (10%) |
| Marketing / Travel | $5,000 (3%) | $15,000 (10%) |
| **Total** | **$150,000** | **$150,000** |

**Rationale:** The original $80k for 2 FTE × 6 months pays ~$6.7k/month per engineer — below Austin junior market rate ($70k-$90k). This contradicts the "equal pay" philosophy and would result in uncompetitive hires. Reallocating to reserved compute and patent protection preserves founder velocity and builds defensible assets.

### Correction 3: Organizational Model — Valve/Super-Organism → Solo Founder

| Aspect | Original | Corrected |
|--------|----------|-----------|
| Current structure | Flat hierarchy, self-organizing teams, 7-person org chart | Solo founder. No hires. No org chart. |
| Governance | Community Council + Ethical Review Board + RFC Process | Founder makes all decisions. Ad-hoc external advisors. |
| Compensation | Published pay bands, equity for all, 20% profit sharing | Deferred until Series A. No compensation framework active. |
| Slide 10 content | Flat web diagram, 6 governance bullets | Single text slide: "Sami Torres — Solo Founder. Full Stack. Full Time." |

**Rationale:** Pre-seed governance overhead burns bandwidth a solo operator cannot afford. The Valve model is the North Star, not the starting line — Valve had 30+ employees before going flat. Deferring organizational complexity until 6+ FTE is honest, not a retreat from values.

### Correction 4: Go-to-Market — STTR Elevated

| Aspect | Original | Corrected |
|--------|----------|-----------|
| STTR position | Section 5 of business doc (afterthought) | Primary go-to-market channel (Section 2) |
| LOIs | Not mentioned | Central milestone (3 LOIs by Week 6) |
| Partner timeline | "Month 3-9" | "Week 3-6 — begin outreach immediately" |
| Sales dependency | Team-dependent | Solo-achievable (PI-to-PI relationship) |

**Rationale:** A solo founder cannot cold-call biotech procurement. But a solo founder can email a PI at Stanford and say "I built a connectome engine. Want to co-author an STTR application?" This converts the solo status from a weakness into an advantage.

### Correction 5: Pitch Deck — Slides Changed

| Slide | Original | Corrected |
|-------|----------|-----------|
| 3 — Vision | "The Valve of Austin" with pyramid vs web comparison diagram | "From Connectome to Computation" with connectome metric boxes |
| 8 — Business | 3 pricing cards (Free/Institutional/Enterprise) + TAM/SAM/SOM bars | Full-bleed sandbox browser mockup + URL + enterprise note |
| 10 — Organization | Flat org web diagram + 6 governance bullets | Single text slide: "Sami Torres — Solo Founder" |
| 11 — Roadmap | P0: Multi-Tenant Auth → P6: Scale & Benchmark ($150k total) | P0: Public Sandbox Deploy → P6: Fundraise Trigger ($150k total) |
| 12 — Funds | $80k Engineering + $30k GPU + $15k Loihi + etc | $50k GPU + $35k Legal + $35k Loihi + $15k Infra + $15k Travel |

---

> *End of corrected reference document. Contains the original comprehensive data plus inline corrections reflecting the Option B pivot. The individual file rewrites (00-08 + build_deck.py) contain the full corrected content for each domain.*
