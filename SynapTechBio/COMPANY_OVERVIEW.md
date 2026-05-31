# SynapTechBio — Company Overview (Corrected)

> *Version 2.0 | May 2026 — Corrected for Option B (solo founder, sandbox-first, deferred governance)*

---

## 1. Identity

**SynapTechBio** is a Delaware C-Corporation (pre-incorporated via registered agent) at the intersection of connectomics, neuromorphic computing, and open science. Current state: solo founder with a working IDRE codebase, validated FlyWire LSM, and a plan to deploy a free public sandbox.

### Core Thesis

Biological brains run on ~20W. Dense transformer models require megawatts. The scaling laws are breaking. By translating the structural wiring principles of biological connectomes into GPU-accelerated sparse graph computation, SynapTechBio achieves 5× compute latency reduction and 20× estimated energy savings vs dense architectures.

### Current Reality

| Status | Detail |
|--------|--------|
| Entity | Delaware C-Corp — pre-incorporated via registered agent |
| Funding | $0 raised — $150k pre-seed target |
| Hardware | None — compute budget in ask |
| Team | Solo founder — no hires planned |
| Revenue | $0 |
| Users | 0 |
| What exists | Working IDRE codebase, validated LSM, pitch materials, roadmap |

---

## 2. The Problem

### The Silicon Wall

- GPT-3 inference consumes ~600J per token. A fly brain runs a billion lifetimes on the same energy.
- Training frontier models costs $10M+. Scaling laws are breaking.
- Neuromorphic hardware (Intel Loihi 2) requires INRC membership + grant process. ~200 labs worldwide.

### The Opportunity

The *Drosophila* connectome (Dorkenwald et al., *Nature* 2024) is the first complete synaptic-resolution wiring diagram of an adult brain — 139,255 neurons, ~50 million synapses, CC BY 4.0. SynapTechBio built the engine that runs it.

---

## 3. The Solution: IDRE

The **Integrated Data Representation Engine (IDRE)** is a GPU-accelerated Compressed Sparse Column (CSC) graph engine that executes the FlyWire connectome in real-time. The codebase is complete and working.

### Technical Architecture

```
Browser (Three.js R3F) ← SSE streaming → FastAPI (Uvicorn) → CSC Engine
  → CuPy (GPU) → SciPy (CPU) → NumPy (fallback)
  → spMV: ~1.2ms GPU / ~11ms CPU (130k×130k)
  → Lava Bridge for Intel Loihi compilation
  → DCSL middleware (designed, S3 upload pending)
```

### Key Metrics

| Metric | IDRE | Dense Transformer | Improvement |
|--------|------|-------------------|-------------|
| Compute Latency | ~1ms | ~5ms | **5×** |
| Energy per Activation | ~35W | ~700W | **20× (est.)** |
| Memory Footprint | ~60 MB | ~1.5 GB | **25×** |

---

## 4. Go-to-Market: Bottom-Up Sandbox

SynapTechBio does not have a sales team. The go-to-market is a free public sandbox deployed to the web.

| Channel | Timeline | Cost | Solo-Achievable |
|---------|----------|------|-----------------|
| Free sandbox | Week 1-2 | $0 CAC | ✅ |
| STTR grants | Month 3-9 | $0 (non-dilutive) | ✅ |
| Enterprise inbound | When sandbox proves traction | $0 | ✅ |

**No revenue projections. No ARR targets. Revenue is a trailing indicator of sandbox adoption.**

---

## 5. Use of Funds (Corrected)

| Category | Amount | % |
|----------|--------|---|
| Cloud GPU (Reserved) | $50,000 | 33% |
| Legal / IP | $35,000 | 23% |
| INRC / Loihi Access | $35,000 | 23% |
| Infrastructure | $15,000 | 10% |
| Marketing / Travel | $15,000 | 10% |
| Engineering Salaries | $0 | 0% |
| **Total** | **$150,000** | **100%** |

**Rationale:** The original allocation of $80k for 2 FTE × 6 months paid ~$6.7k/month per engineer — below Austin market rate for even junior hires. Reallocating to reserved compute and patent protection preserves founder velocity and builds defensible assets.

---

## 6. STTR Strategy (Primary Channel)

STTR grants are the primary initial revenue channel for a solo operator.

| Phase | Amount | Timeline | Partner Target |
|-------|--------|----------|----------------|
| Phase I | ~$250k each | Month 3-9 | Stanford, MIT, UCSD |
| Phase II | ~$1M each | Month 12-24 | Follow-on from Phase I |

**Current reality:** No LOIs secured. Outreach begins Week 3-6 post-funding.

---

## 7. Competitive Positioning

| Competitor | Weakness | SynapTechBio Advantage |
|------------|----------|----------------------|
| Google/JAINA | Proprietary, no community access | Open platform + DCSL IP protection |
| Intel INRC | Grant-gated Loihi access | Pay-as-you-go cloud Loihi (planned) |
| FlyWire Codex | Static browser, no computation | Live 1.2ms spMV + LSM |
| Hugging Face | ML hub only, no hardware | Hardware-integrated, continuously improving |

---

## 8. Governance (Corrected)

**Phase 1 (Pre-Seed):** Solo founder. No formal governance bodies. Founder makes all decisions. Ad-hoc external advisors consulted as needed.

**Phase 2 (Post-Seed, 6+ FTE):** Community Council (advisory), Ethical Review Board (binding veto), transparent pay bands, equity for all.

The Valve model is deferred until the team reaches critical mass.

---

## 9. Contact

**Sami Torres** — Founder & Solo Operator
SamiT2825@synaptechbio.org

*For a complete audit trail of corrections, see CHANGELOG.md and SYNAPTECHBIO_CRITIQUE_AND_CORRECTIONS.md*
