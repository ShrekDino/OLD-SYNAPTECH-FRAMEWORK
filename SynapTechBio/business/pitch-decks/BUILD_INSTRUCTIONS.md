# BUILD INSTRUCTIONS: Assembling the Ultimate Pitch Deck

> *How to turn the 8 team documents into a finished 13-slide presentation.*

---

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.11+ | Chart generation + PPTX build | `brew install python` / `apt install python3` |
| python-pptx | PowerPoint generation | `pip install python-pptx` |
| matplotlib | Chart images | `pip install matplotlib seaborn` |
| Inter Font | Brand typography | [fonts.google.com/specimen/Inter](https://fonts.google.com/specimen/Inter) |
| PowerPoint or Keynote | Final touch-ups | — |
| Adobe Illustrator (optional) | Diagram polish | — |

---

## Build Steps

### Step 1: Generate Charts

Using `build_charts.py` (or adapt from `SynapTechBio/PitchDeck/generate_charts.py`):

```bash
mkdir -p assets/charts
python3 build_charts.py
```

This generates 7 chart PNGs in `assets/charts/`:
- `market-sizing.png`
- `competitive-matrix.png`
- `accuracy-benchmark.png`
- `use-of-funds.png`
- `roadmap-gantt.png`
- `performance-benchmarks.png`
- `austin-talent-cost.png`

### Step 2: Prepare Assets

| Asset | Source | Format |
|-------|--------|--------|
| Logo | `assets/logo/synaptechbio-logo.svg` | SVG + white variant |
| 3D Brain Render | Screenshot from IDRE frontend | 1920×1080 PNG |
| FlyWire Connectome | Nature 2024 paper cover | High-res JPEG |
| Austin Skyline | Stock photo or illustration | Silhouette PNG |
| Ecosystem Icons | Noun Project or custom | Line-style SVG |
| Network Diagrams | Illustrator or Excalidraw | SVG or PNG |

### Step 3: Build Presentation

Option A — Automated (Python):

```bash
python3 build_deck.py
```

This uses `python-pptx` to assemble the deck following specs in `07_TEAM_PRODUCTION.md`.

Option B — Manual (PowerPoint/Keynote):

1. Create 16:9 presentation (1920×1080)
2. Apply brand theme (colors, fonts from `01_TEAM_DESIGN.md`)
3. Build each slide following `07_TEAM_PRODUCTION.md` layout specs
4. Insert charts from Step 1
5. Add animations per spec
6. Add speaker notes from `08_TEAM_SCRIPT.md`

### Step 4: Review Against Designer Checklist

From `01_TEAM_DESIGN.md`:

- [ ] All 13 slides follow typography hierarchy exactly
- [ ] Brand colors are hex-perfect
- [ ] Logo in top-left on every slide
- [ ] Footer bar on every slide (except title and close)
- [ ] No image pixelation at 1920×1080
- [ ] All text readable against backgrounds
- [ ] Animations are subtle, not distracting
- [ ] Slide numbers sequential
- [ ] Confidentiality notice on every slide
- [ ] Consistent 160px margins
- [ ] Fonts embedded (Inter + Inter Display)
- [ ] Accessible contrast ratios maintained

### Step 5: Practice the Script

From `08_TEAM_SCRIPT.md`:

1. Time yourself — target 7 minutes total
2. Record video and review pacing
3. Practice the close until it feels natural
4. Prepare Q&A answers (last section of script)

### Step 6: Export

```bash
# Export to PDF
python3 export_pdf.py  # or manual export from PowerPoint

# Export individual slides as PNG
python3 export_slides.py
```

---

## File Reference

| Document | What It Covers |
|----------|---------------|
| `00_MANIFEST.md` | Unified vision, core thesis, repo ecosystem |
| `01_TEAM_DESIGN.md` | Colors, typography, layout grid, slide templates |
| `02_TEAM_NARRATIVE.md` | Emotional arc, slide-by-slide story, key phrases |
| `03_TEAM_DATA.md` | Chart specs, data points, sources |
| `04_TEAM_TECHNICAL.md` | Architecture diagrams, validation data, ecosystem map |
| `05_TEAM_BUSINESS.md` | RPaaS model, financial projections, market analysis |
| `06_TEAM_ORGANIZATION.md` | Valve model, Austin strategy, compensation philosophy |
| `07_TEAM_PRODUCTION.md` | Slide-by-slide build specs, animations, export |
| `08_TEAM_SCRIPT.md` | Full read-aloud script, Q&A prep |

---

## Build Script Template

```python
# build_deck.py — minimal starter

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Brand colors
DARK_TEAL = RGBColor(0x0A, 0x1F, 0x2E)
TEAL = RGBColor(0x0D, 0x73, 0x77)
GOLD = RGBColor(0xFF, 0xD1, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xB0, 0xBE, 0xC5)

prs = Presentation()
prs.slide_width = Inches(13.333)  # 1920px
prs.slide_height = Inches(7.5)    # 1080px

# --- Slide 1: Title ---
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
# Set background color
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = DARK_TEAL

# Add title
title = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(10), Inches(1.5))
tf = title.text_frame
p = tf.paragraphs[0]
p.text = "SYNAPTECHBIO"
p.font.size = Pt(48)
p.font.color.rgb = WHITE
p.font.bold = True
p.alignment = PP_ALIGN.CENTER

# Add subtitle
subtitle = slide.shapes.add_textbox(Inches(1.5), Inches(4.0), Inches(10), Inches(1))
tf = subtitle.text_frame
p = tf.paragraphs[0]
p.text = "The Decentralized Intelligence Foundry"
p.font.size = Pt(22)
p.font.color.rgb = LIGHT_GRAY
p.font.bold = False
p.alignment = PP_ALIGN.CENTER

prs.save("SynapTechBio_Ultimate_Pitch_Deck.pptx")
print("Deck saved!")
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install python-pptx matplotlib seaborn

# 2. Copy this build script
# 3. Run it
python3 build_deck.py

# 4. Open the generated PPTX
# 5. Polish manually in PowerPoint
# 6. Export to PDF
```

---

## Estimated Production Time

| Task | Time |
|------|------|
| Generate charts (automated) | 5 minutes |
| Design background assets | 2-4 hours |
| Build slides (manual) | 4-6 hours |
| Apply animations | 1-2 hours |
| Add speaker notes | 30 minutes |
| Review and polish | 1-2 hours |
| **Total** | **~10-15 hours** |

---

## Contact for Design Questions

**Design Lead:** Sami Torres (serving as steward until design hire)  
**Email:** SamiT2825@synaptechbio.org  
**Reference Repo:** github.com/ShrekDino/SynapTechBio
