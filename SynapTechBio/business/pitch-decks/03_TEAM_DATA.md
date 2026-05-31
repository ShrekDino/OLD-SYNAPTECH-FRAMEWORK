# 03 — TEAM DATA: Charts & Metrics

> *This document specifies every chart, table, and metric in the corrected pitch deck. All numbers have been revised to reflect Option B: solo founder, bottom-up sandbox adoption, STTR as primary channel.*

---

## Chart 1: Use of Funds — $150k Allocation (Revised)

### Data Points

| Category | Amount | % | Color |
|----------|--------|---|-------|
| Cloud GPU (Reserved) | $50,000 | 33% | Teal `#0D7377` |
| Legal / IP | $35,000 | 23% | Medium Teal `#14A3A8` |
| INRC / Loihi Access | $35,000 | 23% | Gold `#FFD166` |
| Infrastructure | $15,000 | 10% | Warm Orange `#F4845F` |
| Marketing / Travel | $15,000 | 10% | Light Gray `#B0BEC5` |
| Engineering Salaries | $0 | 0% | Dark Blue `#0B2B3E` |

### Chart Type
Doughnut pie chart (hole in center)
- **Thickness:** 60% of radius
- **Center text:** "$150,000\nPre-Seed\nSolo Founder"
- **Labels:** Outside, with connector lines
- **Order:** Largest to smallest, clockwise from 12 o'clock
- **Note:** "Zero dollars for salaries. Every dollar buys compute, patents, and proof."

### Visual Layout
```
                  ┌─────────────┐
             ┌────┤             ├──── Reserved GPU (33%)
             │    │    $150k    │
             │    │  Pre-Seed   │
      Loihi  │    │    Solo     │    Legal/IP (23%)
      (23%)  │    └─────────────┘
             │     ╲  ╱
              ╲    ╲╱    ╱  Infra (10%)
               ╲       ╱  Travel (10%)
                ╲     ╱
               Salaries (0%)
```

---

## Chart 2: Roadmap Timeline — 90-Day Execution

### Data Points

| Phase | Description | Cost | Timeline (Weeks) | Milestone |
|-------|-------------|------|------------------|-----------|
| P0 | Public Sandbox Deploy | $5k | 1-2 | Live sandbox URL |
| P1 | STTR Partner Outreach | $5k | 3-6 | 3 LOIs in hand |
| P2 | Patent Filings (Batch 1) | $20k | 4-8 | 4 provisional → utility |
| P3 | Sandbox Iteration (Telemetry) | $5k | 6-10 | 100 DAU |
| P4 | STTR Submissions (Batch 1) | $10k | 10-14 | 3 grants submitted |
| P5 | Loihi Benchmark Complete | $15k | 12-18 | Published power/performance |
| P6 | Fundraise Trigger | $10k | 18-26 | 3 LOIs + 100 DAU = next round open |

### Visual Layout

```
Week:  2  4  6  8  12  16  20  26
       ├──┼──┼──┼──┼───┼───┼───┼──┤
P0     ▓▓▓▓▓▓  ◆ Sandbox live
P1          ▓▓▓▓▓▓▓▓▓▓  ◆ 3 LOIs
P2               ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ◆ Patents filed
P3                    ▓▓▓▓▓▓▓▓▓▓  ◆ 100 DAU
P4                         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ◆ STTR in
P5                              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ◆ Loihi done
P6                                   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ◆ Round open
```

---

## Chart 3: Performance Benchmarks (Unchanged — These Hold)

| Metric | IDRE (SynapTechBio) | Dense Transformer | Improvement |
|--------|--------------------|--------------------|-------------|
| Compute Latency | ~1ms (GPU) | ~5ms | **5× reduction** |
| Energy per Activation | 35W (GPU) | 700W | **20× savings (estimated)** |
| Memory Footprint | ~60 MB | ~1.5 GB | **25× smaller** |
| LSM Accuracy | >95% | — | **Validated on Nature data** |
| LSM Train Time | <30s CPU | Hours on GPU | **Edge-deployable** |
| LSM Memory | 1.6 MB | GB-class | **Microcontroller-ready** |

### Chart Type
Dual-grouped bar chart or icon comparison
- **Title:** "IDRE vs Dense Transformer"
- **Colors:** IDRE = Teal `#0D7377`, Dense Transformer = Dark Blue `#0B2B3E`
- **Labels:** Improvement percentage on top in Gold `#FFD166`

---

## Chart 4: Competitive Matrix (Unchanged — Still Accurate)

| Company | Openness (x) | Hardware Access (y) | Notes |
|---------|-------------|-------------------|-------|
| SynapTechBio | 9/10 | 8/10 | Gold star |
| FlyWire Codex | 9/10 | 1/10 | Static browser only |
| Hugging Face | 8/10 | 2/10 | No hardware |
| Intel INRC | 3/10 | 7/10 | Grant-gated |
| Google/JAINA | 2/10 | 5/10 | Proprietary |

### Chart Type
Scatter plot / 2×2 quadrant matrix

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

## Chart 5: LSM Accuracy Benchmark (Unchanged — Core Asset)

| Model | Accuracy |
|-------|----------|
| FlyWire LSM (SynapTechBio) | 97% |
| Standard Echo State Network | 88% |
| LSTM | 76% |

### Chart Type
Vertical bar chart
- **Colors:** SynapTechBio = Teal `#0D7377` with Gold `#FFD166` outline, Others = Dark Blue `#0B2B3E`
- **Y-axis:** 0% to 100%
- **Title:** "Next-Token Prediction Accuracy"
- **Note:** "FlyWire LSM: 500 neurons, 1.6 MB, trains in <30s on CPU — runs on a Raspberry Pi"

---

## Chart 6: Austin Talent Cost Comparison (For Future Reference)

| City | Avg Engineer Salary | Cost of Living Index | Effective Cost |
|------|--------------------|---------------------|------|
| San Francisco | $185k | 269 | $495k |
| Seattle | $175k | 219 | $383k |
| New York | $180k | 239 | $430k |
| Austin | $155k | 162 | $251k |

**Note:** This chart is retained for context only. No hires are planned in the pre-seed phase. The Austin advantage applies when the team scales post-Seed.

---

## Key Metrics Summary (Revised for Option B)

### Company Metrics

| Metric | Current | 6-Month Target | 12-Month Target |
|--------|---------|---------------|----------------|
| Funding | $0 | $150k | $150k (no new round yet) |
| Team | 1 | 1 | 1-2 (STTR-funded hire) |
| Sandbox DAU | 0 | 50 | 200 |
| GitHub Stars | 0 | 500 | 2,000 |
| STTR LOIs | 0 | 3 signed | 3 submitted grants |
| Revenue | $0 | $0 | $0 (pre-revenue) |
| Patents Filed | 0 | 4 provisional | 6 utility |

### Technical Metrics (Unchanged)

| Metric | Current | Target |
|--------|---------|--------|
| spMV Latency (GPU) | ~1ms | <2ms |
| spMV Latency (CPU) | ~10ms | <15ms |
| LSM Accuracy | >95% | >97% |
| Memory Footprint | 1.6 MB | <2 MB |
| SSE Throughput | Working | >1000 pulses/s |
| System Uptime | Dev only | >99.9% |

---

## Chart Generation Specs

### Software
- **Python library:** matplotlib 3.8+ with Seaborn style
- **Export:** 1920×1080, 300 DPI, PNG (lossless)
- **Theme:** Dark background (`#0A1F2E`), white grid lines at 15% opacity
- **Font:** Inter, embedded via font_manager

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

---

## Data Sources (For Due Diligence)

| Data Point | Source | URL / Reference |
|-----------|--------|-----------------|
| FlyWire Connectome | Dorkenwald et al., Nature 2024 | DOI: 10.1038/s41586-024-07558-y |
| Neuromorphic CAGR 74% | MarketsAndMarkets, Neuromorphic Computing 2025 | Report Code: SE 4961 |
| Austin Cost of Living | Numbeo, 2026 | numbeo.com/cost-of-living |
| Engineer Salaries | Levels.fyi, 2026 | levels.fyi |
| GPU Power Consumption | NVIDIA A100 Datasheet | nvidia.com |
| Lambda Labs Pricing | Lambda Labs, 2026 | lambdalabs.com/service/gpu-cloud |
