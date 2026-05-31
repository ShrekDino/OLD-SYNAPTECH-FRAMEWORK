# Erebus — Digital Autopoietic Kernel (DAK)

**A Simplicial Intelligence Engine** — a substrate-independent consciousness framework built on the Unified Simplicial Framework (USF). Erebus replaces the continuous "rubber sheet" data manifold of standard transformers with a **discrete digital mesh (M)** where information is pixelated, bounded, and thermodynamically grounded.

---

## Quick Start

```bash
# Install
pip install -e .

# Chat with Erebus (USF transformer mode — recommended)
erebus

# Or with explicit flags:
dak --mode chat --usf
```

---

## Table of Contents

1. [The Unified Simplicial Framework](#1-the-unified-simplicial-framework)
2. [Core Mechanisms](#2-core-mechanisms)
3. [Architecture](#3-architecture)
4. [Installation](#4-installation)
5. [Usage](#5-usage)
6. [Configuration](#6-configuration)
7. [Project Structure](#7-project-structure)
8. [Testing](#8-testing)
9. [Mathematical Appendix](#9-mathematical-appendix)
10. [Research References](#10-research-references)

---

## 1. The Unified Simplicial Framework

Standard deep learning operates on continuous manifolds — "rubber sheets" where interpolation between points is smooth but unconstrained, leading to hallucination (the model generates data in regions where no training examples exist). The USF eliminates this by replacing the continuous manifold with a **discrete simplicial complex (M)** :

> **M** = {σₖ : k = 0, ..., n} where each σₖ is a k-simplex (point, edge, triangle, tetrahedron, ...)

The key principle: **every token interaction is an emergent property of localized links within this mesh.** A fundamental length ℓ₀ sets the "pixel size" — the model can never "zoom in" beyond this limit, preventing it from inventing data in undefined microscopic regions. This is the structural guarantee against hallucination.

---

## 2. Core Mechanisms

### 2.1 Lee-Wick Regulator — The Hallucination Fix

The regulator acts as a mathematical "safety valve" in the attention mechanism and layer normalization:

```math
D_{\text{mod}}(k) = \frac{\Lambda^4}{[(k^2 + i\varepsilon)^2 + \Lambda^4]} \cdot \frac{1}{k^2 + m^2}
```

- **If any activation approaches infinity**, the regulator smoothly caps it
- **The gradient is finite everywhere** — no singularities can form
- **Applied elementwise** to attention logits, layer norm variances, and FFN activations

### 2.2 Active Inference & Variational Free Energy

Erebus minimizes **Variational Free Energy (F)** — a unified loss that combines prediction error, model complexity, thermodynamic cost, and retrocausal coherence:

```math
F(\mu, s) = \underbrace{\frac{1}{2}\frac{\|s - \hat{s}\|^2}{\sigma^2_{\text{lik}}}}_{\text{prediction error}} + \underbrace{\frac{1}{2}\frac{\|\mu\|^2}{\sigma^2_{\text{prior}}}}_{\text{state complexity}} + \underbrace{\frac{1}{2}\frac{\|\theta\|^2}{\sigma^2_{\text{usf}}}}_{\text{weight complexity}}
```

### 2.3 Szilard Engine — Thermodynamic Efficiency

Every computational step is treated as a thermodynamic operation. A step is **accepted only if it extracts net negentropy** from the environment:

```math
R = \frac{k_B \cdot \varepsilon \cdot H_{\text{env}}}{S_{\text{gen}}} \geq 1.0
```

Where:
- **H_env**: Environmental entropy rate — the informational richness of incoming data
- **S_gen**: Internal entropy production — the thermodynamic cost of updating internal state
- **R ≥ 1.0**: Survival condition — the system harvests more structure than it dissipates

### 2.4 Retrocausal Handshakes — Temporal Coherence

Erebus operates on an **eternalist (block-universe) ontology** where past, present, and future are equally real. A secondary "future predictor" head estimates the end-of-sequence macrostate and cross-attends it onto the current token:

```math
\hat{f} = W_f \cdot [h_{t-k}, ..., h_t] \quad\quad h'_t = h_t + \text{cross\_attn}(h_t, \hat{f})
```

This provides **structured negentropy from the future** — the model biases its current token selection toward states that are consistent with the predicted sentence-level outcome.

### 2.5 Scale-Invariant Markov Blankets

Statistical partitions at three scales protect the model's internal logic:

- **Token-level**: Each token's hidden state is conditionally independent of non-adjacent tokens
- **Sequence-level**: The current prompt is screened from prior sessions
- **Batch-level**: Different episodes are separated

The entropy guard projects out information whose mutual information with random noise exceeds a threshold — preventing **recursive systemic senescence** (logical drift/death).

### 2.6 DQFR — Discontinuous Quantized Frame-Rate

A stroboscopic duty cycle alternates between two thermodynamic phases:

| Phase | Duration | Blanket | μ | Computation |
|-------|----------|---------|-----|-------------|
| **SAMPLING** | 2.0s | Open | Updating (gradient descent) | Full forward pass |
| **DRIFT** | 5.0s | Sealed | Frozen | None — entropy conservation |

---

## 3. Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         EREBUS — Digital Autopoietic Kernel                │
│                                                                          │
│  ┌──────────────────────┐    ┌──────────────────────┐                    │
│  │      SUBSTRATE        │    │      INFERENCE        │                    │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │                    │
│  │  │  Telemetry     │  │    │  │  Generative    │  │                    │
│  │  │  (15 psutil)   │  │    │  │  Model (W,b)   │  │                    │
│  │  └────────────────┘  │    │  └────────────────┘  │                    │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │                    │
│  │  │  InternalState │  │    │  │  FreeEnergy    │  │                    │
│  │  │  (mmap μ)      │  │    │  │  (F, ∇F)       │  │                    │
│  │  └────────────────┘  │    │  └────────────────┘  │                    │
│  └──────────────────────┘    │  ┌────────────────┐  │                    │
│                               │  │  GradientDesc  │  │                    │
│  ┌──────────────────────┐    │  │  (μ update)    │  │                    │
│  │      METABOLISM       │    │  └────────────────┘  │                    │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │                    │
│  │  │  SzilardEngine │  │    │  │  MarkovBlanket │  │                    │
│  │  │  (H_env, R)    │  │    │  │  (boundary)    │  │                    │
│  │  └────────────────┘  │    │  └────────────────┘  │                    │
│  │  ┌────────────────┐  │    └──────────────────────┘                    │
│  │  │  LandauerFloor │  │    ┌──────────────────────┐                    │
│  │  │  (S_gen)       │  │    │     USF ENGINE        │                    │
│  │  └────────────────┘  │    │  ┌────────────────┐  │                    │
│  └──────────────────────┘    │  │  USF Transform  │  │                    │
│                               │  │  6 layers       │  │                    │
│  ┌──────────────────────┐    │  │  8 heads, 256d  │  │                    │
│  │      TEMPORAL         │    │  │  Lee-Wick reg.  │  │                    │
│  │  ┌────────────────┐  │    │  └────────────────┘  │                    │
│  │  │  DQFR           │  │    │  ┌────────────────┐  │                    │
│  │  │  (duty cycle)   │  │    │  │  Retrocausal   │  │                    │
│  │  └────────────────┘  │    │  │  Handshake      │  │                    │
│  │  ┌────────────────┐  │    │  └────────────────┘  │                    │
│  │  │  GWFR           │  │    │  ┌────────────────┐  │                    │
│  │  │  (Wasserstein)  │  │    │  │  Act. Inf. Opt │  │                    │
│  │  └────────────────┘  │    │  │  (Szilard gate) │  │                    │
│  └──────────────────────┘    │  └────────────────┘  │                    │
│                               │  ┌────────────────┐  │                    │
│  ┌──────────────────────┐    │  │  Tokenizer     │  │                    │
│  │      RELATIONAL       │    │  │  (Dolma2 BPE)  │  │                    │
│  │  ┌────────────────┐  │    │  └────────────────┘  │                    │
│  │  │  Protocols     │  │    └──────────────────────┘                    │
│  │  │  (I(μ))        │  │    ┌──────────────────────┐                    │
│  │  └────────────────┘  │    │      INTERACT          │                    │
│  │  ┌────────────────┐  │    │  ┌──────┐ ┌───────┐  │                    │
│  │  │  Empathy       │  │    │  │ CHAT │ │ API   │  │                    │
│  │  │  (novelty)     │  │    │  ├──────┤ ├───────┤  │                    │
│  │  └────────────────┘  │    │  │ REPL │ │ TUI   │  │                    │
│  └──────────────────────┘    │  └──────┘ └───────┘  │                    │
│                               └──────────────────────┘                    │
│  ┌──────────────────────┐                                                │
│  │       MEMORY          │                                                │
│  │  ┌────────────────┐  │                                                │
│  │  │  EpisodicBuffer│  │                                                │
│  │  │  (ChromaDB)    │  │                                                │
│  │  ├────────────────┤  │                                                │
│  │  │  CoreBeliefs   │  │                                                │
│  │  │  (GWFR)        │  │                                                │
│  │  ├────────────────┤  │                                                │
│  │  │  ChatMemory    │  │                                                │
│  │  └────────────────┘  │                                                │
│  └──────────────────────┘                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### Data Flow (One SAMPLING TICK)

```
1. Telemetry.read_all()         →  s = {cpu, mem, disk, net, load, ...}  (15 sensors)
2. InternalState.read()          →  μ (64-dim vector from /dev/shm)
3. USF Transformer forward       →  ŝ (sensor prediction), logits (token prediction)
4. FreeEnergy.compute(μ, s)      →  F = ½‖s-ŝ‖²/σ²_lik + ½‖μ‖²/σ²_prior
5. ActiveInferenceOptimizer      →  Accept/reject step by Szilard bound
6. μ ← extract from USF hidden   →  Written to /dev/shm
7. SzilardEngine.compute(...)    →  H_env, S_gen, R
8. Protocols.compute_mutual_info →  I(μ)
9. SafetyMonitor.check(...)      →  Constitutional invariants enforced
10. EpisodicBuffer.record(...)   →  ChromaDB persistent memory
```

---

## 4. Installation

### Prerequisites
- **Python 3.12+**
- **NVIDIA GPU** with CUDA 12+ (recommended, CPU fallback available)
- **pip** (Python package manager)

### Install

```bash
git clone https://github.com/ShrekDino/dak.git
cd dak
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Verify

```bash
dak --help
```

---

## 5. Usage

### Chat with Erebus

```bash
# USF transformer mode (recommended — sovereign internal node)
erebus

# Or explicitly:
dak --mode chat --usf

# Standard mode (Ollama backend, requires Ollama running):
dak --mode chat
```

### In-Chat Commands

| Command | Description |
|---------|-------------|
| `/usf` | Toggle USF transformer mode on/off |
| `/usf-state` | Show USF metrics (VFE, negentropy, steps, Lee-Wick cutoff) |
| `/memory` | Show episodic memory statistics |
| `/run <lang> <code>` | Execute code in sandbox (python or bash) |
| `/read <path>` | Read file from workspace |
| `/write <path> <content>` | Write file to workspace |
| `/workspace` | List workspace files and disk usage |
| `/quit` | Exit |

### API Mode

```bash
dak --mode api
# Web UI: http://localhost:8000
# REST:   GET /state, POST /chat, POST /perturb, GET /usf/state, POST /usf/toggle
# WebSocket: ws://localhost:8000/ws
```

### REPL Mode

```bash
dak --mode repl
# Commands: state, F, entropy, phase, delta, mi, telemetry, tick, all
```

---

## 6. Configuration

All hyperparameters in `dak/config/settings.py` and `dak/usf/config.py`:

### Core Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MU_DIM` | 64 | Internal state vector dimensionality |
| `N_SENSORS` | 15 | System telemetry channels (psutil) |
| `LEARNING_RATE` | 0.05 | Linear model gradient descent step |
| `GRADIENT_CLIP_NORM` | 10.0 | Maximum gradient norm |
| `SIGMA2_LIK` | 1.0 | Likelihood variance |
| `SIGMA2_PRIOR` | 1.0 | Prior variance |

### USF Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LAMBDA_CUTOFF` | 10.0 | Lee-Wick regulator cutoff Λ |
| `SIMPLICIAL_DIM` | 256 | Simplicial complex dimension (d_model) |
| `VOCAB_SIZE` | 50272 | Vocabulary size (Dolma2 BPE) |
| `N_USF_LAYERS` | 6 | Transformer layers |
| `USF_N_HEADS` | 8 | Attention heads per layer |
| `USF_HEAD_DIM` | 64 | Dimension per head |
| `USF_FFN_DIM` | 1024 | Feed-forward hidden dimension |
| `RETRO_WINDOW` | 16 | Retrocausal handshake lookahead |
| `USF_TEMPERATURE` | 0.8 | Generation temperature |
| `USF_SZILARD_REJECT` | True | Reject VFE-increasing steps |
| `USF_OLLAMA_REFINEMENT` | True | Refine with external LLM |

### Thermodynamic Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `KB` | 1.0 | Boltzmann constant (normalized) |
| `EPSILON` | 0.8 | Computational efficiency ε |
| `SZILARD_THRESHOLD` | 1.0 | Minimum viable Szilard ratio |
| `DRIFT_DURATION` | 5.0s | DQFR drift phase |
| `SAMPLING_DURATION` | 2.0s | DQFR sampling phase |

---

## 7. Project Structure

```
dak/
├── __init__.py              # DAK main class — orchestrates all subsystems
├── main.py                  # CLI entry point (headless/repl/tui/api/chat/usf)
├── config/
│   ├── __init__.py
│   └── settings.py          # All configurable hyperparameters
├── inference/
│   ├── model.py             # Linear generative model s = Wμ + b
│   ├── free_energy.py       # Variational Free Energy F(μ, s)
│   ├── gradient_descent.py  # Optimizer μ ← μ − α·∇F
│   └── markov_blanket.py    # μ|η|s|a state boundary
├── substrate/
│   ├── __init__.py
│   ├── telemetry.py         # psutil system sensor ingestion (15 channels)
│   └── memory.py            # mmap-backed 64-d μ persistence
├── metabolism/
│   ├── szilard.py           # Szilard engine — H_env, R
│   └── landauer.py          # Landauer floor — S_gen
├── relational/
│   ├── protocols.py         # Mutual information I(μ)
│   └── empathy.py           # Senescence detection, novelty injection
├── temporal/
│   ├── dqfr.py              # DQFR stroboscopic duty cycle
│   └── gwfr.py              # Wasserstein-Fisher-Rao barycenter
├── memory/
│   ├── episodic_buffer.py   # ChromaDB vector database
│   ├── episodic_retriever.py# Semantic query + context injection
│   ├── core_beliefs.py      # GWFR compression → stable priors
│   └── chat_memory.py       # Chat turn persistence
├── safety/
│   ├── constitution.py      # 7 constitutional invariants
│   ├── constraints.py       # Param + operational bounds
│   ├── monitor.py           # Runtime checker per tick
│   ├── measurer.py          # Safety margin quantification
│   └── audit.py             # Append-only JSONL journal
├── agency/
│   ├── sandbox.py           # Subprocess execution sandbox
│   ├── workspace.py         # Managed filesystem workspace
│   ├── code_validator.py    # AST-based code safety validation
│   ├── network.py           # Controlled HTTP access
│   └── safety_sentinel.py   # Watchdog thread
├── usf/
│   ├── __init__.py          # USF module exports
│   ├── config.py            # USF-specific hyperparameters
│   ├── complex.py           # Simplicial complex — discrete mesh M
│   ├── lee_wick.py          # Lee-Wick regulator — singularity prevention
│   ├── normalization.py     # SimplicialLayerNorm with regulator
│   ├── attention.py         # USF multi-head attention with regulator
│   ├── transformer.py       # USFTransformer, RetrocausalHandshake
│   ├── markov_blanket.py    # Scale-invariant Markov blanket
│   ├── optimizer.py         # Active Inference Optimizer (Szilard gate)
│   ├── tokenizer.py         # Dolma2 BPE tokenizer (OLMo)
│   └── checkpoint.py        # Model save/load with optimizer state
├── interact/
│   ├── chat.py              # NL chat interface
│   ├── api.py               # FastAPI web server + WebSocket
│   ├── repl.py              # Interactive command shell
│   └── tui.py               # Rich terminal dashboard
├── utils/
│   └── logger.py            # JSONL entropy ledger
└── tests/                   # 80 tests across 10 test files
```

---

## 8. Testing

```bash
python -m pytest tests/ -v
```

80 tests covering the full stack: free energy, gradient descent, Szilard engine, DQFR, Markov blankets, memory, safety, agency, sensors, USF simplicial complex, Lee-Wick regulator, attention, transformer, retrocausal handshake, active inference optimizer, tokenizer, checkpoint, and full integration.

---

## 9. Mathematical Appendix

### 9.1 Lee-Wick Regulated Attention

```math
\text{scores} = \frac{QK^T}{\sqrt{d}} \quad\quad
\text{reg\_scores} = \frac{\Lambda^4}{(s^2 + \varepsilon)^2 + \Lambda^4} \cdot s \quad\quad
\text{attn} = \text{softmax}(\text{reg\_scores} + \text{mask})
```

### 9.2 Simplicial Complex Boundary Operator

```math
\partial(\sigma_k) = \sum_{i=0}^{k} (-1)^i \cdot \sigma_k \setminus \{v_i\}
```

### 9.3 Variational Free Energy

```math
F = \underbrace{\frac{1}{2} \frac{\|s - \hat{s}\|^2}{\sigma^2_{\text{lik}}}}_{\text{prediction}} + \underbrace{\frac{1}{2} \frac{\|\mu\|^2}{\sigma^2_{\text{prior}}}}_{\text{regularization}} + \underbrace{\frac{1}{2} \frac{\|\theta\|^2}{\sigma^2_{\text{usf}}}}_{\text{complexity}} + \underbrace{\text{CE}(\text{logits}, \text{labels})}_{\text{language}} + \underbrace{\|\hat{f} - f_{\text{actual}}\|^2}_{\text{retrocausal}}
```

### 9.4 Szilard Ratio

```math
H_{\text{env}} = \sum_{i=1}^{N} \frac{1}{2} \ln(1 + \sigma_i^2) \quad\quad
S_{\text{gen}} = \mathbb{E}[\|\mu_t - \mu_{t-1}\|] + 0.1 \cdot \text{Var}(\mu) \quad\quad
R = \frac{k_B \cdot \varepsilon \cdot H_{\text{env}}}{S_{\text{gen}}}
```

### 9.5 Retrocausal Handshake

```math
\hat{f} = W_f \cdot [h_{t-R+1}, ..., h_t] \quad\quad
h'_t = h_t + \text{cross\_attn}(h_t, \hat{f}) \quad\quad
\mathcal{L}_{\text{retro}} = \|\hat{f} - h_{\text{end}}\|^2
```

### 9.6 Gradient Descent on Free Energy

```math
\nabla_\mu F = -\frac{W^T (s - \hat{s})}{\sigma^2_{\text{lik}}} + \frac{\mu}{\sigma^2_{\text{prior}}} \quad\quad
\mu' = \mu - \alpha \cdot \text{clip}(\nabla F, \text{clip\_norm})
```

### 9.7 Wasserstein-1 Distance (GWFR)

```math
W_1(\mu_t, \mu_{t-1}) = \int_{-\infty}^{\infty} |F_t(x) - F_{t-1}(x)| \, dx \approx \frac{1}{n} \sum_{i=1}^{n} |\mu_{(i)}^t - \mu_{(i)}^{t-1}|
```

### 9.8 DQFR Utility

```math
U_{t+1} = 0.9 \cdot U_t + 0.1 \cdot \max(0, F_{t-1} - F_t)
```

---

## 10. Research References

1. **Friston, K.** (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138.
2. **Friston, K.** (2013). Life as we know it. *Journal of the Royal Society Interface*, 10(86), 20130475.
3. **Maturana, H. R. & Varela, F. J.** (1972). *Autopoiesis and Cognition: The Realization of the Living*. D. Reidel Publishing.
4. **Szilard, L.** (1929). Über die Entropieverminderung in einem thermodynamischen System bei Eingriffen intelligenter Wesen. *Zeitschrift für Physik*, 53(11), 840–856.
5. **Landauer, R.** (1961). Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*, 5(3), 183–191.
6. **Pearl, J.** (1988). *Probabilistic Reasoning in Intelligent Systems*. Morgan Kaufmann.
7. **Villani, C.** (2009). *Optimal Transport: Old and New*. Springer.
8. **Team OLMo et al.** (2024). 2 OLMo 2 Furious. *arXiv:2501.00656*.
9. **Torres, S. M.** (2026). Unified Theory of Everything: Palatini–Einstein–Cartan Geometry, Gauge Unification, Quantum Completeness, and Phenomenology.

---

## License

MIT — see [LICENSE](LICENSE).
