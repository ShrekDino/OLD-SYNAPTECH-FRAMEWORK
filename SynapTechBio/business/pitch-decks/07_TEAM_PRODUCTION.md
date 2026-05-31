# 07 — TEAM PRODUCTION: Slide-by-Slide Build Specs

> *This document specifies the exact layout, elements, and animations for every slide. A presentation designer can build the entire deck from this document without questions.*

---

## Build Order & Dependencies

```
1. Generate charts (matplotlib) → assets/charts/
2. Design background assets → assets/backgrounds/
3. Position logo and footer template
4. Build each slide following specs below
5. Apply animations per element
6. Export PPTX + PDF
```

---

## Slide 1: Title

| Element | Type | Position | Size | Color | Font | Animation |
|---------|------|----------|------|-------|------|-----------|
| Background | Gradient | Full bleed | 1920×1080 | `#0A1F2E` → `#0D7377` 30° | — | Fade in (0.5s) |
| Connectome watermark | Background overlay | Centered | Full | `#0D7377` 8% opacity | — | Fade in (1.0s) |
| Logo | SVG | Top-left | 180w | White | — | Fade in (0.3s) |
| Company name | Text | Center-vertical, center-horizontal | 48pt | White | Inter Display Bold | Slide up + fade (0.4s) |
| Tagline | Text | Below company name | 22pt | `#B0BEC5` | Inter Regular | Fade in (0.6s) |
| Subtitle | Text | Below tagline | 16pt | `#B0BEC5` | Inter Light | Fade in (0.8s) |
| Entity line | Text | Bottom-center | 12pt | `#B0BEC5` 70% | Inter Light | Fade in (1.0s) |
| Contact | Text | Bottom-right | 11pt | `#14A3A8` | Inter Regular | Fade in (1.0s) |

### Exact Wording

```
SYNAPTECHBIO
[16px spacing]
The Decentralized Intelligence Foundry
From Connectome to Collective Superintelligence
[24px spacing]
Delaware C-Corp (Pre-Incorporated)
[40px spacing]
Sami Torres | SamiT2825@synaptechbio.org
```

---

## Slide 2: Problem

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` solid |
| Logo | Top-left | 180w |
| Headline | Top-left (160, 160) | 36pt, Bold, White |
| Subhead | Below headline | 22pt, Inter Semi-Bold, White |
| Problem list (4 items) | Left column | 16pt, `#B0BEC5`, bullet points with `●` teal markers |
| Visual | Right 40% | Split image: GPU servers vs fly brain |
| Metric callout (top-right) | Overlay | "600J/token vs ~20W" — 28pt, Bold, `#FFD166` |
| Footer | Bottom | Slide 02 | The OS for Neuromorphic Intelligence | Confidential |

### Layout

```
| LOGO | HEADLINE (36pt): "AI is Centralizing Power"     |              |
|      |                                                   |  GPU SERVERS |
|      | Subhead: "Faster Than We Can Regulate It"        |   vs FLY    |
|      |                                                   |   BRAIN     |
|      | ● $10M+ training costs                           |              |
|      | ● Hardware gatekept by ~200 labs                 |  "600J/token |
|      | ● Proprietary models locked behind APIs          |   vs ~20W"  |
|      | ● Talent concentrated in 3 cities                |              |
```

---

## Slide 3: Vision — "From Connectome to Computation"

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0B2B3E` solid (section divider) |
| Section label | Top-left | "The Vision" — 14pt, `#FFD166`, uppercase, tracked 4px |
| Headline | Center | 40pt, Bold, White |
| Subhead | Below headline | 22pt, Regular, `#B0BEC5` |
| Key stats (3 metric boxes) | Center | 139,255 Neurons / ~50M Synapses / CC BY 4.0 |
| Vision description | Below stats | 16pt, `#B0BEC5`, max 3 lines |
| Footer | Bottom | Slide 03 | The OS for Neuromorphic Intelligence | Confidential |

### Layout

```
| LOGO | "The Vision" — 14pt, Gold, uppercase     |
|      |                                            |
|      | FROM CONNECTOME TO COMPUTATION             |
|      | 40pt, Bold, White, centered               |
|      |                                            |
|      | "The most efficient intelligence system   |
|      |  in the universe runs on 20W. Its wiring  |
|      |  diagram was published in Nature 2024.    |
|      |  I built the engine that runs it."        |
|      |                                            |
|      | ┌──────────┐  ┌──────────┐  ┌──────────┐ |
|      | │  139,255 │  │   ~50M   │  │CC BY 4.0 │ |
|      | │  Neurons │  │ Synapses │  │  License  │ |
|      | └──────────┘  └──────────┘  └──────────┘ |
```

**Note:** No Valve comparison diagram. No pyramid vs web. The Valve model is a deferred reference, not a slide element. The vision is grounded in the connectome data, not organizational theory.

---

## Slide 4: Scientific Foundation

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Subhead | Below headline | 22pt, Semi-Bold, `#0D7377` |
| Nature 2024 cover thumbnail | Left center | 240w, corner radius 8px |
| Key stats (3 metric boxes) | Right of image | Side-by-side, each 200w × 120h |
| Repo badges | Below stats | "Flywirellm" + "flywire-realtime-engine" with language badges |
| Footer | Bottom | Standard |

### Metric Boxes

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│     139,255      │  │     ~50M         │  │     CC BY 4.0    │
│    Neurons       │  │   Synapses       │  │     License       │
│    White 48pt    │  │   White 48pt     │  │   White 48pt     │
│    Teal label    │  │   Teal label     │  │   Gold label     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Slide 5: Product — IDRE

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Architecture diagram | Center 70% | See 04_TEAM_TECHNICAL.md section 1 |
| Key metrics (3 side-by-side) | Below diagram | 5× latency, 20× energy, 25× memory |
| Hardware-agnostic badge | Bottom-right | "CuPy → SciPy → NumPy" in code font |
| Footer | Bottom | Standard |

### Key Metric Boxes (Gold)

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│     5×         │  │     20×        │  │     25×        │
│  Latency       │  │  Energy         │  │  Memory        │
│  Reduction     │  │  Savings        │  │  Efficiency    │
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## Slide 6: Moat — DCSL

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0B2B3E` (section) |
| Section label | Top-left | "The Moat" — 14pt, `#FFD166`, uppercase |
| Headline | Below section label | 36pt, Bold, White |
| Flow diagram | Center | Two-path fork (see 04_TEAM_TECHNICAL.md section 2) |
| AES-256-GCM callout | Right of encrypt path | "Military-grade" + key icon |
| Quote | Bottom-center | 18pt, Italic, `#B0BEC5` |
| Footer | Bottom | Standard |

### Quote

> *"They can't copy what they can't scrape."*

---

## Slide 7: Ecosystem

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Ecosystem hub-and-spoke diagram | Center 85% | See 04_TEAM_TECHNICAL.md section 5 |
| Each repo as a card | Spoke positions | 160w × 80h, rounded, with repo name + language color bar |
| IDRE at center | Center | Larger, gold border |
| Connectors | Lines between | `#0D7377` at 50% opacity |
| Footer | Bottom | Standard |

---

## Slide 8: Go-to-Market — "The Sandbox"

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Subhead | Below headline | 22pt, Semi-Bold, `#0D7377` |
| Browser mockup | Center 70% | Full-bleed screenshot of ActivationSandbox.tsx showing: neuron visualization, text input, activation button, pulse stream |
| URL display | Below mockup | "sandbox.synaptechbio.org" — 18pt, `#14A3A8`, code font |
| Value proposition | Bottom-left | 3 short lines: "Free. No auth. 100 activations/day. Built on the same engine that runs at 1.2ms." |
| Enterprise note | Bottom-right | "Enterprise: custom pricing for labs that outgrow the sandbox" — 11pt, `#B0BEC5` |
| Footer | Bottom | Standard |

### Layout

```
| LOGO | GO-TO-MARKET: THE SANDBOX (36pt)        |
|      | "Free Connectome Simulation. Any Browser." |
|      |                                            |
|      | ┌────────────────────────────────────────┐ |
|      | │                                        │ |
|      | │     BROWSER MOCKUP (FULL WIDTH)        │ |
|      | │     ActivationSandbox.tsx              │ |
|      | │     [Text Input] [Activate]            │ |
|      | │     Neuron cascade visualization       │ |
|      | │     Pulse stream: ▓▓▓▓▓▓░░░░ 47Hz     │ |
|      | │                                        │ |
|      | └────────────────────────────────────────┘ |
|      |                                            |
|      | sandbox.synaptechbio.org — 18pt, #14A3A8  |
|      |                                            |
| Free. No auth. 100/day.       Enterprise: custom |
| Same engine. 1.2ms spMV.      for labs that need |
|                                dedicated infra.  |
```

**Note:** No pricing cards. No TAM/SAM/SOM. No institutional tier. The product demo IS the go-to-market strategy.

---

## Slide 9: Talent — Why Austin

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Map of US | Left 50% | Dots on SF, Seattle, NYC, Austin |
| Comparison table | Right 50% | City | Salary | COL Index | Effective Cost |
| Austin highlight | Bottom-right | "40% lower effective cost than SF" — Gold |
| Footer | Bottom | Standard |

---

## Slide 10: Organization — "Solo Founder"

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Founder text | Center | Large centered text block (see layout below) |
| Subtext | Below founder text | 3 key principles, 16pt, `#B0BEC5` |
| Phase note | Bottom-right | "Governance model scales with team. Valve model deferred until 6+ FTE." — 11pt, `#B0BEC5` |
| Footer | Bottom | Standard |

### Layout

```
| LOGO | THE ORGANIZATION (36pt)                   |
|      |                                            |
|      |                                            |
|      |         SAMI TORRES                        |
|      |     Solo Founder. Full Stack. Full Time.   |
|      |        48pt Bold White / 22pt Light Gray   |
|      |                                            |
|      |                                            |
|      |    • Decision-making: founder makes all calls |
|      |    • Governance: ad-hoc advisors, no board  |
|      |    • Ethical review: external, as needed   |
|      |                                            |
|      |                                            |
|      | Governance model scales with team.         |
|      | Valve model deferred until 6+ FTE.        |
```

**Note:** No org chart. No web diagram. No governance bodies. Simple text slide that communicates focus and honesty. The flat org diagram and Valve references are removed entirely. The slide communicates: this is a solo operation, and that's a feature, not a bug.

---

## Slide 11: Roadmap — 26-Week Execution

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Subhead | Below headline | 18pt, `#0D7377` — "Solo-achievable milestones. No team dependencies." |
| Gantt chart | Center 80% | See 03_TEAM_DATA section — Chart 2 (revised roadmap) |
| Milestone diamonds | On timeline | Gold `#FFD166` |
| Phase labels | Left of bars | P0-P6 in teal |
| Total callout | Bottom | "Total: $150k | Every milestone is independently achievable by a solo operator." |
| Footer | Bottom | Standard |

### Phase List

| Phase | Cost | Timeline | Milestone |
|-------|------|----------|-----------|
| P0 — Public Sandbox | $5k | Week 1-2 | Live sandbox URL |
| P1 — STTR Outreach | $5k | Week 3-6 | 3 LOIs in hand |
| P2 — Patent Filings | $20k | Week 4-8 | 4 utility patents filed |
| P3 — Sandbox Iteration | $5k | Week 6-10 | 100 DAU |
| P4 — STTR Submissions | $10k | Week 10-14 | 3 grants submitted |
| P5 — Loihi Benchmark | $15k | Week 12-18 | Published power/performance |
| P6 — Fundraise Trigger | $10k | Week 18-26 | Next round open |

---

## Slide 12: Use of Funds — $150k Solo Allocation

| Element | Position | Spec |
|---------|----------|------|
| Background | Full bleed | `#0A1F2E` |
| Headline | Top-left | 36pt, Bold, White |
| Subhead | Below headline | 18pt, `#0D7377` — "Zero dollars for salaries. Every dollar buys compute, patents, and proof." |
| Doughnut chart | Left 40% | See 03_TEAM_DATA — Chart 1 (revised) |
| Breakdown table | Right 55% | Category | Amount | % |
| Zero-overhead callout | Bottom-right | "$0 salaries | $0 office | $0 management | 100% infrastructure + IP" |
| Footer | Bottom | Standard |

### Breakdown Table

| Category | Amount | % |
|----------|--------|---|
| Cloud GPU (Reserved) | $50k | 33% |
| Legal / IP | $35k | 23% |
| INRC / Loihi Access | $35k | 23% |
| Infrastructure | $15k | 10% |
| Marketing / Travel | $15k | 10% |
| Engineering Salaries | $0 | 0% |

---

## Slide 13: Close / CTA

| Element | Position | Spec |
|---------|----------|------|
| Background | Gradient | `#0A1F2E` → dark, centered radial |
| Quote | Center-vertical | 32pt, Italic, White, centered, 60% width |
| Attribution | Below quote | "— SynapTechBio" — 16pt, `#FFD166` |
| CTA buttons | Below attribution | 3x row: "Star the Repo" "Invest" "Connect" |
| URL | Below buttons | github.com/ShrekDino/SynapTechBio — 14pt, `#14A3A8` |
| Contact | Bottom | SamiT2825@synaptechbio.org |
| No footer | — | No slide number, no confidentiality |

### CTA Buttons

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ★ Star the    │  │  💰 Invest      │  │  ✉️ Connect     │
│      Repo       │  │                  │  │                  │
│   GitHub        │  │  $150k Pre-Seed  │  │  Sami@...       │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

(All buttons: rounded 8px, `#0D7377` fill, white text, 16pt, hover state: `#FFD166` text)

---

## Animation Timing Summary

| Slide | Element | Start | Duration |
|-------|---------|-------|----------|
| All | Background | 0.0s | 0.5s |
| All | Logo | 0.3s | 0.3s |
| All | Headline | 0.0s | 0.4s |
| All | Subhead | 0.3s | 0.3s |
| All | Body / Bullets | 0.5s | 0.3s each (stagger) |
| All | Charts / Diagrams | 0.6s | 0.5s |
| All | Footer | 0.8s | 0.3s |
| 13 | CTA pulse | 1.0s | 1.0s (loop) |

---

## Export Specs

| Format | Specs |
|--------|-------|
| **PowerPoint** | .pptx, 16:9, fonts embedded |
| **PDF** | .pdf, 16:9, print quality (300 DPI) |
| **Image** | .png per slide, 1920×1080 |
| **Video** | .mp4, 1920×1080, 30fps, slide transitions included |
