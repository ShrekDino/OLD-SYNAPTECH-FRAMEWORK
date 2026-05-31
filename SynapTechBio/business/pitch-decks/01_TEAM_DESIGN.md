# 01 — TEAM DESIGN: Look & Feel

> *This document specifies every visual element of the pitch deck. A professional designer can execute this without questions.*

---

## Brand Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Dark Teal (Background) | `#0A1F2E` | Slide backgrounds, dark sections, title slides |
| Teal (Primary) | `#0D7377` | Headlines, accent lines, data highlights, buttons |
| Gold (Highlight) | `#FFD166` | Key metrics, call-to-action, star elements, spike indicators |
| White | `#FFFFFF` | Body text, secondary headlines |
| Light Gray | `#B0BEC5` | Supporting text, captions, footers |

### Secondary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Dark Blue | `#0B2B3E` | Chart backgrounds, section dividers |
| Medium Teal | `#14A3A8` | Secondary accents, chart fills |
| Warm Orange | `#F4845F` | Warning/emphasis, competitive threats |
| Neuron Green | `#00FF88` | Active neuron states, "live" indicators |

### Gradients

- **Title Slide Gradient:** `#0A1F2E` → `#0D7377` at 30° angle
- **Call-to-Action Gradient:** `#0D7377` → `#FFD166` at 45° angle
- **Section Divider Gradient:** `#0B2B3E` → `#0A1F2E` vertical fade

---

## Typography

### Font Stack

| Usage | Font | Weight | Size | Case |
|-------|------|--------|------|------|
| Slide titles | Inter Display | Bold (700) | 36-42pt | Sentence case |
| Section headers | Inter | Semi-Bold (600) | 24-28pt | Sentence case |
| Body text | Inter | Regular (400) | 16-18pt | Normal |
| Data / numbers | Inter | Bold (700) | 28-48pt (metric sizing) | Normal |
| Captions / footnotes | Inter | Light (300) | 10-12pt | Normal |
| Speaker notes (build script) | Inter | Regular | 11pt | Normal |

**Fallback:** system-ui, -apple-system, sans-serif

### Type Hierarchy on Slides

```
Title Slide:
    Company Name: 48pt, Bold, White
    Tagline: 22pt, Regular, Light Gray (#B0BEC5)
    
Content Slide:
    Headline: 36pt, Bold, White or Teal (#0D7377)
    Subhead: 22pt, Semi-Bold, White
    Body: 16pt, Regular, Light Gray (#B0BEC5)
    
Data Slide:
    Metric Number: 48pt, Bold, Gold (#FFD166)
    Metric Label: 16pt, Regular, Light Gray

Footer:
    Slide number: 10pt, Light Gray, opacity 50%
    Tagline: 10pt, Teal (#0D7377)
    Confidential: 9pt, italic, opacity 40%
```

---

## Slide Layout Grid

### Frame Dimensions

- **Aspect Ratio:** 16:9
- **Resolution:** 1920 × 1080 pixels (HD)
- **Safe Zone:** 1600 × 880 (160px margin all sides)

### Grid System

```
+------------------------------------------------------------------+
|  (160px margin)                                                   |
|                                                                    |
|   +-----+---------------------------+----------------------------+ |
|   |     |   TITLE / HEADLINE        |   (optional visual)        | |
|   | LOGO |   (left-aligned)         |                            | |
|   |     |   Subhead here            |                            | |
|   |     |                           |                            | |
|   |     +---------------------------+----------------------------+ |
|   |     |                                                         | |
|   |     |   BODY CONTENT / DATA / CHARTS                          | |
|   |     |                                                         | |
|   |     +--------------------------------------------------------+ |
|   |     |                                                         | |
|   |     |   FOOTER: Slide # | Tagline | Confidential              | |
|   +-----+--------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+

Columns: 12-column grid
Gutters: 24px
Margins (top/bottom/left/right): 160px fixed
```

### Slide Type Templates

#### Slide Type 1: Title Slide
```
+------------------------------------------------------------------+
|                                                                    |
|                                                                    |
|           SYNAPTECHBIO                                             |
|           (48pt, Bold, White)                                     |
|                                                                    |
|           The Decentralized Intelligence Foundry                   |
|           (22pt, Regular, #B0BEC5)                                |
|                                                                    |
|                                                                    |
|           [Subtle connectome wireframe watermark]                  |
|                                                                    |
|           Sami Torres | Delaware C-Corp                            |
|           (14pt, Regular, #B0BEC5)                                |
+------------------------------------------------------------------+
```

#### Slide Type 2: Content Slide (60/40 Split)
```
| LOGO | HEADLINE (36pt)                      | FULL-BLEED IMAGE |
|      | Subhead (22pt)                       | OR ILLUSTRATION  |
|      |                                       | (40% width)      |
|      | • Bullet one (16pt)                   |                  |
|      | • Bullet two                          |                  |
|      | • Bullet three                        |                  |
|      |                                       |                  |
+------+---------------------------------------+------------------+
```

#### Slide Type 3: Data / Metrics Slide
```
| LOGO | HEADLINE (36pt)                      |                  |
|      |                                       |                  |
|      | ┌──────────┐  ┌──────────┐           |  CHART           |
|      | │ $1.8T    │  │ $300B    │           |  (60% width)     |
|      | │  TAM     │  │  SAM     │           |                  |
|      | └──────────┘  └──────────┘           |                  |
|      | ┌──────────┐                          |                  |
|      | │ $450M    │                          |                  |
|      | │  SOM     │                          |                  |
|      | └──────────┘                          |                  |
+------+---------------------------------------+------------------+
```

#### Slide Type 4: Full-Bleed Quote / CTA
```
+------------------------------------------------------------------+
|                                                                    |
|                                                                    |
|                                                                    |
|           "The future of intelligence                              |
|            is not proprietary.                                     |
|            It's collective."                                       |
|           (32pt, Italic, White, centered)                         |
|                                                                    |
|                                                                    |
|           [CTA Button: Star the Repo]                             |
|           [Contact: SamiT2825@synaptechbio.org]                    |
|                                                                    |
+------------------------------------------------------------------+
```

---

## Background & Texture

### Slide Background
- **Default:** Solid `#0A1F2E` (Dark Teal)
- **Title Slide:** Gradient `#0A1F2E` → `#0D7377` 30°
- **Section Divider:** Solid `#0B2B3E`
- **CTA Slide:** Gradient `#0A1F2E` → vertical dark

### Watermark Elements
- **Connectome wireframe:** Subtle 130k-neuron graph lines at 15% opacity on title and section slides
- **Circuit traces:** Gold (#FFD166) at 8% opacity on data slides
- **Neural pulse dots:** Teal (#0D7377) at 5% opacity, randomly distributed

### Image Treatment
- **3D brain renders:** High-contrast, teal/gold colorization, dark background
- **Person photos:** Desaturated with teal overlay, rounded corners
- **Screenshots:** Clean device mockups (not raw screenshots)
- **Icons:** Line-style, 2px stroke, rounded caps, teal or gold

---

## Logo Specifications

### Logo Lockup
```
[SYNAPTECHBIO]
 The OS for Neuromorphic Intelligence
```

- **Format:** SVG preferred, PNG fallback (transparent background)
- **Position:** Top-left corner, 120px from left, 60px from top
- **Size:** 180px wide × auto-height
- **Color:** White on dark backgrounds
- **Never:** Change logo colors, warp, rotate, or add effects

### Slide Footer Bar

Fixed footer on every slide (except title):
```
Slide ##  |  The OS for Neuromorphic Intelligence  |  Confidential
```

- **Position:** 60px from bottom edge
- **Divider line:** 1px solid `#0D7377` at 30% opacity
- **Text:** 10pt, `#B0BEC5`, Regular
- **Confidential:** 9pt, italic, `#B0BEC5` at 50% opacity

---

## Animations & Transitions (Keynote/PowerPoint Spec)

### Slide Transitions
| Slide Pair | Transition | Duration |
|-----------|------------|----------|
| Title → Content | Morph / Dissolve | 0.8s |
| Content → Content | Push (left) | 0.5s |
| Content → Data | Zoom (slight) | 0.6s |
| Data → Section Divider | Fade through black | 0.8s |
| Section Divider → Content | Fade from black | 0.8s |
| Any → CTA | Iris (grow from center) | 1.0s |

### Element Animations (Per Slide)

| Element | Animation | Direction | Duration | Delay |
|---------|-----------|-----------|----------|-------|
| Headline | Fade In + Slide Up | Up (20px) | 0.4s | 0.0s |
| Subhead | Fade In | — | 0.3s | 0.3s |
| Body bullets | Wipe (left to right) | Left | 0.3s each | 0.1s stagger |
| Metric numbers | Count up (animated) | — | 0.6s | 0.5s |
| Chart | Fade In + Scale | — | 0.5s | 0.4s |
| Image | Fade In | — | 0.4s | 0.3s |
| CTA Button | Pulse (scale 1.0→1.05→1.0) | — | 1.0s | 1.0s (loop) |

---

## File Structure for Production

```
build/
├── assets/
│   ├── logo/
│   │   ├── synaptechbio-logo.svg
│   │   └── synaptechbio-logo-white.svg
│   ├── icons/
│   │   ├── neuron-line.svg
│   │   ├── circuit-line.svg
│   │   ├── brain-icon.svg
│   │   └── ...
│   ├── backgrounds/
│   │   ├── title-bg.png
│   │   ├── content-bg.png
│   │   └── section-bg.png
│   ├── images/
│   │   ├── brain-3d-render.png
│   │   ├── flywire-visualization.png
│   │   ├── austin-skyline.png
│   │   └── ...
│   └── charts/
│       ├── market-sizing.png
│       ├── competitive-matrix.png
│       ├── use-of-funds.png
│       ├── accuracy-benchmark.png
│       ├── roadmap.png
│       └── benchmarks.png
│
├── slides/
│   ├── slide-01-title.pptx
│   ├── slide-02-problem.pptx
│   ├── slide-03-vision.pptx
│   └── ...
│
├── build_deck.py
├── generate_charts.py
└── README_BUILD.md
```

---

## Designer's Checklist

- [ ] All 13 slides follow typography hierarchy exactly
- [ ] Brand colors are hex-perfect (no eyeballing)
- [ ] Logo in top-left on every slide
- [ ] Footer bar on every slide (except title)
- [ ] No image pixelation at 1920×1080
- [ ] All text is readable against backgrounds
- [ ] Animations are subtle, not distracting
- [ ] Slide numbers sequential
- [ ] Confidentiality notice on every slide
- [ ] Consistent spacing (160px margins everywhere)
- [ ] Fonts embedded (Inter + Inter Display)
- [ ] Accessible contrast ratios maintained
