# SynapTechBio

**From connectome to computation — a solo founder translating the Drosophila brain into the most efficient neural graph engine ever built.**

A GPU-accelerated sparse graph engine that executes the entire 139k-neuron Drosophila connectome in real-time on consumer hardware. Published as a free public sandbox. No grants required. No membership needed.

---

## What This Is

This is the public blueprint for a vision that's becoming real — corrected and grounded in current reality.

**Current reality:** One founder. No funding. No hardware. No team. No users. A working IDRE codebase, a validated FlyWire LSM at >95% accuracy, and a clear roadmap to deploy a free public sandbox.

**Strategic posture (Option B):** Stay solo. Max compute and patents. Free sandbox as the only sales motion. STTR grants as the primary funding channel. Governance deferred until the team reaches 6+ FTE.

**What we're building toward:** The democratized neuromorphic commons — but first, we need the sandbox to prove people want it.

---

## Core Technology

| Layer | Stack |
|-------|-------|
| **Backend** | FastAPI, CuPy/SciPy CSC Engine, Lava-NC (Intel Loihi), Pinecone, AES-256-GCM |
| **Frontend** | React 19, Three.js / R3F, TypeScript, GSAP, Vite |
| **Infra** | Docker Compose, Prometheus |
| **Consciousness Validation** | [CSDF](https://github.com/ShrekDino/uploaded-consciousness-framework) — PyTorch, POT, GPT-2, Rich |

### Ecosystem Modules

| Module | Repository | Status |
|--------|------------|--------|
| **IDRE** — Graph Engine | `synaptech-idre` | ✅ Working |
| **FlyWire LSM** — Reservoir Computing | `Flywirellm` | ✅ Validated (>95%) |
| **FlyWire Realtime Engine** — 60Hz Visualization | `flywire-realtime-engine` | ✅ Working |
| **Consciousness Validation Suite (CSDF)** | [`uploaded-consciousness-framework`](https://github.com/ShrekDino/uploaded-consciousness-framework) | ✅ Active |
| **EVE** — Self-Aware Knowledge Entity | `EVE` | ⚡ In Development |

### Key Metrics

| Metric | Value |
|--------|-------|
| spMV Latency (RTX 3060) | ~1.2ms (130k×130k full connectome) |
| LSM Accuracy | >95% next-token prediction (Nature 2024 dataset) |
| LSM Memory | 1.6 MB — fits on a microcontroller |
| LSM Training | <30 seconds on any CPU |
| Latency Reduction | 5× vs dense transformers |
| Energy Savings | 20× estimated (pending Loihi validation) |

---

## Current Focus

1. **Deploy free public sandbox** — A browser-based connectome simulator. Free. Rate-limited. No auth required.
2. **Secure STTR Letters of Intent** — Partner with university labs on federal grant applications.
3. **File utility patents** — Protect DCSL split-layer architecture and closed-form Ridge Regression readout.
4. **Prove adoption** — 100 daily active sandbox users before opening a larger funding round.

---

## How to Get Involved

See [HOW_YOU_CAN_HELP.md](HOW_YOU_CAN_HELP.md) for everything you can do right now.

- **Neuroscientists** — Validate the science. Propose research collaborations.
- **Engineers** — Contribute to IDRE, FlyWire LSM, or the visualization stack.
- **Students** — Learn, contribute, spread the word.
- **Grant writers** — Help identify and apply for funding opportunities.
- **Believers** — Star the repo. Share the vision. Tell one person.
- **Collaborators** — Reach out: SamiT2825@synaptechbio.org

---

## Legal & Contact

**Entity:** Delaware C-Corporation (pre-incorporated via registered agent)
**Founder:** Sami Torres — Solo operator. No hires. No governance overhead.
**Contact:** SamiT2825@synaptechbio.org

*"The fly brain runs on microwatts. I run on coffee and conviction."*
