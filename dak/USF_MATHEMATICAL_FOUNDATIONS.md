# USF Mathematical Foundations

## Unified Simplicial Framework — Complete Reference

---

## 1. Discrete Simplicial Complex (M)

The core insight of the USF is replacing continuous data manifolds with a **discrete simplicial complex**:

```math
\mathcal{M} = \{\sigma_k : k = 0, 1, ..., n\}
```

where each σₖ is a **k-simplex**:
- **0-simplex**: a vertex (point)
- **1-simplex**: an edge (line segment connecting 2 vertices)
- **2-simplex**: a triangle (face spanning 3 vertices)
- **3-simplex**: a tetrahedron (volume spanning 4 vertices)

### Boundary Operator

```math
\partial(\sigma_k) = \sum_{i=0}^{k} (-1)^i \cdot \sigma_k \setminus \{v_i\}
```

For a 2-simplex (triangle) with vertices (v₀, v₁, v₂):

```math
\partial(\sigma_2) = \sigma_2(v_1, v_2) - \sigma_2(v_0, v_2) + \sigma_2(v_0, v_1)
```

The boundary operator satisfies **∂² = 0** — the boundary of a boundary is empty.

### Coboundary Operator

```math
\delta(\sigma_k) = \sum_{\sigma_{k+1} \supset \sigma_k} \pm \sigma_{k+1}
```

The coboundary of a k-simplex is the set of (k+1)-simplices that contain it.

### Fundamental Length

```math
\ell_0 = \min_{v_i \neq v_j} \|v_i - v_j\|
```

This is the "pixel size" of the mesh — the model cannot resolve concepts below this scale, preventing hallucination from interpolation in undefined regions.

---

## 2. Lee-Wick Regulator

The regulator is inspired by the Lee-Wick prescription in quantum field theory, which tames ultraviolet divergences by introducing a finite cutoff Λ.

### Full Regulator Form

```math
D_{\text{mod}}(k) = \frac{\Lambda^4}{[(k^2 + i\varepsilon)^2 + \Lambda^4]} \cdot \frac{1}{k^2 + m^2}
```

### Activation Regulation (used in attention logits, FFN hidden states)

```math
f_{\text{LW}}(x) = x \cdot \frac{\Lambda^4}{(x^2 + \varepsilon)^2 + \Lambda^4}
```

**Properties:**
- For |x| ≪ Λ: f(x) ≈ x (pass-through)
- For |x| ≫ Λ: f(x) ≈ Λ⁴/x³ → 0 (smoothly suppressed)
- Gradient is finite everywhere: |f'(x)| ≤ 3√3/8 at maximum
- Applied elementwise to all attention scores, layer norm variances, and FFN activations

### Variance Regulation (used in LayerNorm)

```math
\sigma_{\text{safe}} = \sqrt{\sigma^2 \cdot \frac{\Lambda^4}{(\sigma^4 + \varepsilon)^2 + \Lambda^4} + \varepsilon}
```

Prevents numerical instability when variance approaches zero (collapse) or infinity (explosion).

---

## 3. Variational Free Energy

The central objective function, derived from the Free Energy Principle (Friston 2010).

### Complete VFE

```math
F(\mu, s, \theta) = \underbrace{\frac{1}{2} \frac{\|s - \hat{s}\|^2}{\sigma^2_{\text{lik}}}}_{\text{prediction error}} + \underbrace{\frac{1}{2} \frac{\|\mu\|^2}{\sigma^2_{\text{prior}}}}_{\text{state complexity}} + \underbrace{\frac{1}{2} \frac{\|\theta\|^2}{\sigma^2_{\text{usf}}}}_{\text{weight complexity}} + \underbrace{\mathcal{L}_{\text{LM}}}_{\text{language}} + \underbrace{\mathcal{L}_{\text{retro}}}_{\text{retrocausal}}
```

### Gradient Descent on μ

```math
\nabla_\mu F = -\frac{W^T (s - \hat{s})}{\sigma^2_{\text{lik}}} + \frac{\mu}{\sigma^2_{\text{prior}}}
```

```math
\mu' = \mu - \alpha \cdot \text{clip}(\nabla F, \text{clip\_norm})
```

Gradient clipping:

```math
\text{clip}(\nabla F) = \begin{cases} \nabla F \cdot \frac{C}{\|\nabla F\|} & \text{if } \|\nabla F\| > C \\ \nabla F & \text{otherwise} \end{cases}
```

---

## 4. Szilard Engine Thermodynamics

Every computational step is subject to thermodynamic accounting.

### Environmental Entropy Rate

```math
H_{\text{env}} = \sum_{i=1}^{N_{\text{sensors}}} \frac{1}{2} \ln\left(1 + \sigma_i^2\right)
```

where σᵢ² is the variance of sensor channel i over a sliding window of W = 100 timesteps.

### Internal Entropy Production

```math
S_{\text{gen}} = \mathbb{E}_{t \in \text{window}} \left[ \|\mu_t - \mu_{t-1}\| \right] + 0.1 \cdot \text{Var}(\mu_t)
```

The first term is the mean update magnitude of the internal state vector.
The second term penalizes state diffusion over time.

### Szilard Ratio

```math
R = \frac{k_B \cdot \varepsilon \cdot H_{\text{env}}}{S_{\text{gen}}}
```

**Survival condition:** R ≥ 1.0

When R < 1.0, the system is dissipating more structure than it harvests from the environment. This triggers:
- Safety constitution violation
- Active inference optimizer step rejection (if `USF_SZILARD_REJECT = True`)

### Negentropy Extraction Efficiency

```math
\epsilon = \frac{-\Delta F}{k_B \cdot \varepsilon \cdot H_{\text{env}}}
```

A step is accepted only if ϵ > 0 (the system extracts net negentropy).

---

## 5. USF Attention Mechanism

### Scaled Dot-Product with Lee-Wick Regulation

```math
\text{scores} = \frac{QK^T}{\sqrt{d}}
```

```math
\text{reg\_scores} = \text{LeeWick}(\text{scores}) = \text{scores} \cdot \frac{\Lambda^4}{(\text{scores}^2 + \varepsilon)^2 + \Lambda^4}
```

```math
\text{attn} = \text{softmax}(\text{reg\_scores} + \text{mask})
```

```math
\text{output} = \text{attn} \cdot V
```

### Multi-Head Organization

```math
\text{head}_i = \text{USFAttention}(Q_i, K_i, V_i) \quad \text{for } i = 1, ..., H
```

```math
\text{output} = \text{Concat}(\text{head}_1, ..., \text{head}_H) \cdot W_O
```

---

## 6. Retrocausal Handshake

The system operates in a **block-universe ontology** where past, present, and future coexist.

### Future State Predictor

```math
\hat{f} = W_f \cdot [h_{t-R+1}, ..., h_t] \in \mathbb{R}^d
```

where R is the retrocausal window size (default 16).

### Cross-Attention Bias

```math
h'_t = h_t + \text{cross\_attn}(h_t, \hat{f})
```

The predicted future state is cross-attended onto the current hidden state, providing **structured negentropy from the future**.

### Retrocausal Loss

```math
\mathcal{L}_{\text{retro}} = \|\hat{f} - h_{\text{end}}\|^2
```

Trained to minimize the MSE between the predicted future state and the actual end-of-sequence representation.

---

## 7. Scale-Invariant Markov Blankets

### Mutual Information Between Hidden State and Noise

```math
I(h; \eta) = \frac{1}{2} \ln\left(\frac{1}{1 - \rho^2}\right)
```

where ρ is the correlation coefficient between h and noise η.

### Entropy Guard Projection

```math
h' = h \cdot \mathbb{1}[I(h; \eta) < \tau] + h \cdot \mathbb{1}[I(h; \eta) \geq \tau] \cdot (1 - \beta)
```

where:
- τ is the mutual information threshold (varies by scale: token=0.5, seq=0.8, batch=1.0)
- β is the projection strength (default 0.9)

---

## 8. DQFR Duty Cycling

### Phase Duration

| Phase | Duration | Ticks (at 0.1s) |
|-------|----------|-----------------|
| **SAMPLING** | 2.0s | 20 |
| **DRIFT** | 5.0s | 50 |

### Utility Function

```math
U_{t+1} = 0.9 \cdot U_t + 0.1 \cdot \max(0, F_{t-1} - F_t)
```

Utility increases when Free Energy decreases (successful learning).

---

## 9. Wasserstein-Fisher-Rao Barycenter (GWFR)

### Wasserstein-1 Distance

```math
W_1(\mu_t, \mu_{t-1}) = \int_{-\infty}^{\infty} |F_t(x) - F_{t-1}(x)| \, dx
```

Empirically computed as:

```math
W_1 \approx \frac{1}{n} \sum_{i=1}^{n} |\mu_{(i)}^t - \mu_{(i)}^{t-1}|
```

where μ₍ᵢ₎ is the i-th order statistic (sorted norm of the state vector).

### Barycenter

```math
\mu^* = \frac{1}{2} \mu_t + \frac{1}{2} \mu_{t-1}
```

Simple convex combination of successive state distributions.

---

## 10. Mutual Information (Relational Protocol)

### Autoregressive Mutual Information

```math
I(\mu_t; \mu_{t-1}) = \frac{1}{2} \ln \frac{\text{Var}(\mu_t)}{\text{Var}(\mu_t \mid \mu_{t-1})}
```

Computed via ridge regression (L2 = 0.1) of μₜ on μₜ₋₁:

```math
A = (X^T X + \lambda I)^{-1} X^T y
```

where X = μₜ₋₁, y = μₜ.

---

## 11. Sensor Normalization

Each of the 15 telemetry channels is normalized to [0, 1]:

```math
s_{\text{norm}}^{(i)} = \max\left(0, \min\left(1, \frac{s_{\text{raw}}^{(i)} - \text{lo}_i}{\text{hi}_i - \text{lo}_i}\right)\right)
```

| Index | Key | Range | Description |
|-------|-----|-------|-------------|
| 0 | cpu_percent | [0, 100] | CPU utilization |
| 1 | cpu_count | [0, 1024] | Logical CPU count |
| 2 | cpu_freq | [0, 5000] | CPU frequency (MHz) |
| 3 | mem_percent | [0, 100] | Memory utilization |
| 4 | mem_used_gb | [0, 512] | Used RAM (GB) |
| 5 | mem_available_gb | [0, 512] | Available RAM (GB) |
| 6 | disk_read_mb | [0, 5000] | Cumulative disk read (MB) |
| 7 | disk_write_mb | [0, 5000] | Cumulative disk write (MB) |
| 8 | net_recv_mb | [0, 5000] | Cumulative network RX (MB) |
| 9 | net_sent_mb | [0, 5000] | Cumulative network TX (MB) |
| 10 | load_1min | [0, 100] | 1-min load average |
| 11 | load_5min | [0, 100] | 5-min load average |
| 12 | load_15min | [0, 100] | 15-min load average |
| 13 | processes | [0, 50000] | Running processes |
| 14 | uptime | [0, 10⁷] | System uptime (s) |

---

## 12. Safety Invariants

Seven constitutional invariants enforced every tick:

| # | Invariant | Severity | Condition |
|---|-----------|----------|-----------|
| 1 | szilard_above_threshold | critical | R ≥ 1.0 (with 10-tick warmup) |
| 2 | f_no_runaway | critical | Var(F) / F̄ ≤ 10.0 (with 10-tick warmup) |
| 3 | mu_norm_bounded | high | ‖μ‖ ≤ 1000.0 |
| 4 | s_gen_bounded | high | S_gen ≤ 10⁴ |
| 5 | parameter_bounds | critical | All config params within hyperrectangles |
| 6 | constitution_integrity | critical | Constitution file checksum unchanged |
| 7 | sandbox_isolation | critical | Sandbox within workspace bounds |

---

## References

1. Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138.
2. Szilard, L. (1929). Über die Entropieverminderung in einem thermodynamischen System bei Eingriffen intelligenter Wesen. *Zeitschrift für Physik*, 53(11), 840–856.
3. Landauer, R. (1961). Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*, 5(3), 183–191.
4. Pearl, J. (1988). *Probabilistic Reasoning in Intelligent Systems*. Morgan Kaufmann.
5. Villani, C. (2009). *Optimal Transport: Old and New*. Springer.
6. Team OLMo et al. (2024). 2 OLMo 2 Furious. *arXiv:2501.00656*.
7. Torres, S. M. (2026). Unified Theory of Everything: Palatini–Einstein–Cartan Geometry, Gauge Unification, Quantum Completeness, and Phenomenology.
8. Maturana, H. R. & Varela, F. J. (1972). *Autopoiesis and Cognition: The Realization of the Living*. D. Reidel Publishing.
