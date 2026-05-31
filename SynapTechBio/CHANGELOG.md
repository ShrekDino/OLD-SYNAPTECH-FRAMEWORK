# Changelog — SynapTechBio Pitch Deck & Strategy Materials

> **Purpose:** Every material change to the SynapTechBio project materials, documented in plain language. Anyone reading the repo can see exactly what changed, why, and when.
>
> **Format:** Each entry lists the file changed, the original claim/position, the corrected position, and the rationale.

---

## 2026-05-25 — Architectural Overhaul (Option B Pivot)

### Summary

All materials underwent a strategic pivot from "DeepTech Capital Vehicle" (institutional sales, hired team, Valve governance) to "Lean Sovereign Lab" (solo founder, free sandbox, deferred governance, STTR grants). Every file in the `Workfolder/` was rewritten or significantly modified.

### Files Changed

---

#### `00_MANIFEST.md` — Rewritten

| Aspect | Original | Corrected |
|--------|----------|-----------|
| One-line thesis | "Valve Corporation of Austin" | "Solo founder translating connectome into consumer-hardware engine" |
| Organizational model | Single super-organism model | Two-phase: Phase 1 (solo) / Phase 2 (post-seed) |
| Go-to-market | Implicit institutional sales | Explicit: free sandbox → STTR grants → enterprise inbound |
| The Ask | "Investment in a new kind of organization" | "Investment in a solo founder with a surgical allocation plan" |
| Governance bodies | Present as current state | Marked as "Phase 2 (deferred)" |

---

#### `01_TEAM_DESIGN.md` — Unchanged

Brand palette, typography, grid system, and animation specs remain valid. No changes needed.

---

#### `02_TEAM_NARRATIVE.md` — Rewritten

| Slide | Original | Corrected |
|-------|----------|-----------|
| 3 — Vision | "The Valve of Austin" — pyramid vs web comparison diagram | "From Connectome to Computation" — connectome metric boxes |
| 8 — Business | RPaaS pricing story with $300k ACV | Sandbox story: "Free URL. Hit rate limit. Email me." |
| 10 — Organization | "Super Organism" speech with governance bodies | "Solo founder. No managers. No governance overhead." |
| 12 — Funds | "53% goes to salaries" | "Zero dollars for salaries. Every dollar buys compute, patents, proof." |
| Valve/Super-organism themes | Recurring references in Slides 3, 9, 10 | Single mention in Slide 3, clearly labeled as future vision |
| Revenue projections | Present in narrative for Slide 8 | Removed entirely |

---

#### `03_TEAM_DATA.md` — Rewritten

| Chart | Original | Corrected |
|-------|----------|-----------|
| Chart 1 | Use of Funds: $80k Engineering / $30k GPU / $15k Loihi / $10k Legal / $10k Infra / $5k Marketing | Use of Funds: $50k GPU / $35k Legal / $35k Loihi / $15k Infra / $15k Marketing / $0 Salaries |
| Chart 2 (Roadmap) | P0: Multi-Tenant Auth → P6: Scale & Benchmark ($150k total, $20k phases) | P0: Public Sandbox Deploy → P6: Fundraise Trigger ($150k total, $5k-$20k phases) |
| Chart 5 (Revenue) | 5-year projection: $1.5M → $450M ARR | **Removed entirely.** No revenue projections. |
| Chart 6 (Revenue removed) | Market sizing TAM/SAM/SOM bars | **Removed from pitch deck.** Retained in reference only. |
| Key Metrics | Year 1-5 hub counts, ARR, cumulative revenue | Sandbox DAU, STTR LOIs, patents filed, no revenue targets |

---

#### `04_TEAM_TECHNICAL.md` — Expanded

| Section | Change |
|---------|--------|
| Section 7 (New) | Added complete Public Sandbox Architecture: rate limits, deployment topology, monthly costs, opt-in telemetry model, rationale for skipping DCSL on free tier |

---

#### `05_TEAM_BUSINESS.md` — Rewritten

| Aspect | Original | Corrected |
|--------|----------|-----------|
| Business model name | RPaaS (Research-Platform-as-a-Service) | "Bottom-Up Sandbox → Enterprise Upsell" |
| Pricing tiers | Free / Institutional ($300k ACV) / Enterprise | Free Sandbox (rate-limited) / Enterprise (custom, inbound only) |
| Year 1 revenue target | $1.5M ARR (5 hubs) | $0 (pre-revenue. No targets.) |
| Revenue projections | 5-year table showing $450M ARR | Removed. Revenue is trailing indicator. |
| Unit economics | CAC $50k/hub, 70% gross margin, LTV $3M | Server cost per sandbox user/day (~$0.03). CAC $0. |
| STTR position | Section 5 (footnote) | Section 2 (primary go-to-market channel) |
| LOIs | Not mentioned | Central milestone (3 LOIs by Week 6) |
| Cap table | Published as active | Clean SAFE, no board seats, no observed rights |
| Compensation | Published pay bands | Deferred until Series A ("No salaries until Series A") |
| Engineering headcount | 2 FTE × 6 months at $80k total | $0. Solo founder. No hires. |
| Financial assumptions | Gross margin 70%, 5% churn, etc | Burn rate $8.3k/month, founder salary $0, 18-month runway |

---

#### `06_TEAM_ORGANIZATION.md` — Rewritten

| Element | Original | Corrected |
|---------|----------|-----------|
| Current structure | 3 teams (Research/Engineering/Community) with 7-person org chart | Solo founder. No teams. No org chart. |
| Decision-making | "Decisions by person doing the work. Steward resolves conflicts." | "Founder makes all operational and strategic decisions." |
| Governance | Community Council + Ethical Review Board + RFC Process (all active) | Ad-hoc external advisors as needed. Formal bodies deferred to 6+ FTE. |
| Compensation | Full pay bands published, equity plan, 20% profit sharing | "No salaries until Series A. Deferred." Pay bands moved to Future Reference. |
| Valve model adaptation | Presented as active | Marked as "Phase 2 (deferred until 6+ FTE)" |
| Austin recruitment tables | Active strategy | Moved to "Future Reference" section |
| Culture principles | 8 principles | 5 principles (removed "No heroes" and "No secrets" as premature) |

---

#### `07_TEAM_PRODUCTION.md` — Slides 3, 8, 10, 11, 12 Replaced

| Slide | Element | Original | Corrected |
|-------|---------|----------|-----------|
| 3 | Headline | "The Valve of Austin" | "From Connectome to Computation" |
| 3 | Visual | Pyramid vs Web comparison diagram | Connectome metric boxes (139k neurons / 50M synapses / CC BY 4.0) |
| 3 | Subhead | "Flat hierarchy. Self-organizing teams..." | "The most efficient intelligence system runs on 20W..." |
| 3 | Quote | "\"I'm not building a company. I'm building a super organism.\"" | Removed |
| 8 | Headline | "RPaaS — Research-Platform-as-a-Service" | "Go-to-Market: The Sandbox" |
| 8 | Content | 3 pricing cards + TAM/SAM/SOM bars | Full-bleed browser mockup of ActivationSandbox.tsx + URL |
| 8 | Footer data | Market sizing | "Free. No auth. 100 activations/day. Same engine. 1.2ms spMV." |
| 10 | Headline | "A Super Organism, Not a Corporation" | "The Organization" |
| 10 | Subhead | "Flat Hierarchy \| Equity for All \| Community Governance" | "Solo Founder. Full Stack. Full Time." |
| 10 | Diagram | Flat org web diagram (7 positions) | None — text-only slide |
| 10 | Bullets | 6 governance principles | 3 simple statements: decision-making, governance, ethics |
| 11 | Subhead | "26 Weeks to Series A Ready" | "Solo-achievable milestones. No team dependencies." |
| 11 | Phases | P0: Multi-Tenant Auth / P1: DCSL / P2: LSM Demo / P3: Open Portal / P4: Alignment / P5: Loihi Farm / P6: Benchmark | P0: Sandbox / P1: STTR Outreach / P2: Patents / P3: Sandbox Iteration / P4: STTR Submission / P5: Loihi Benchmark / P6: Fundraise Trigger |
| 11 | Phase costs | $15k-$25k each | $5k-$20k each |
| 12 | Subhead | (none) | "Zero dollars for salaries. Every dollar buys compute, patents, proof." |
| 12 | Table | Eng $80k / GPU $30k / Loihi $15k / Legal $10k / Infra $10k / Mktg $5k | GPU $50k / Legal $35k / Loihi $35k / Infra $15k / Mktg $15k / Salaries $0 |
| 12 | Callout | "$0 executive comp \| $0 office \| 100% mission" | "$0 salaries \| $0 office \| $0 management \| 100% infra+IP" |

---

#### `08_TEAM_SCRIPT.md` — Slides 3, 8, 10, 11, 12 Replaced

| Slide | Original Script Reference | Corrected Script Reference |
|-------|--------------------------|---------------------------|
| 3 | "Valve proved a flat organization can produce billion-dollar value..." | "The most efficient intelligence system runs on 20W. Its wiring diagram belongs to everyone." |
| 8 | "Research-Platform-as-a-Service. Free for community researchers — because the moat grows..." | "There are two ways to sell enterprise software. Hire a sales team... or publish a working product to the web." |
| 10 | "Currently: it's me. A solo founder with a working prototype... Here's what happens when we fund..." | "Currently: it's me. No employees. No managers. No governance overhead." |
| 11 | "The next 26 weeks are about three things: lock down four provisional patents..." | "The next 26 weeks are about four things: deploy the sandbox, secure STTR partnerships, file patents, prove adoption." |
| 12 | "53% goes to salaries... 20% goes to compute..." | "33% goes to reserved GPU compute... 23% to patent protection... Zero dollars for salaries." |
| Runtime | ~7:40 | ~7:45 |

---

#### `build_deck.py` — Slides 3, 8, 10, 11, 12 Replaced

| Slide | Code Change |
|-------|-------------|
| 3 | Removed Valve comparison diagram, quote, and 4 governance bullets. Added 3 metric boxes (139k/50M/CC BY 4.0) and updated headline/subhead. |
| 8 | Removed pricing card loop (3 cards × 7 code lines each). Added sandbox mockup ASCII art, URL display, value propositions. |
| 10 | Removed org chart section. Replaced with centered founder text ("SAMI TORRES — Solo Founder") and 3 simple bullets. |
| 11 | Replaced all 7 phase tuples with new phases. Changed subhead. Updated total callout text. |
| 12 | Replaced funds list with new allocation. Added subhead. Changed callout text. |

---

#### `BUILD_INSTRUCTIONS.md` — Unchanged

Build pipeline still valid. The corrected deck is assembled the same way.

---

#### `01_TEAM_DESIGN.md` — Unchanged

Brand palette, typography, animations all remain valid for the corrected slides.

---

### Files Created

#### `SYNAPTECHBIO_CRITIQUE_AND_CORRECTIONS.md` — 457 lines

Complete audit trail document containing:
- The Architect's 4-point critique (phantom S3 moat, salary math failure, RPaaS cash-flow illusion, hardware dependency)
- The Unorthodox Advantage (what was correct all along)
- Detailed before/after for all four blueprint items
- Section-by-section original vs corrected matrix
- All file-change annotations

#### `SYNAPTECHBIO_COMPLETE_REFERENCE.md` — 2,005 lines (Updated)

Original comprehensive reference document with:
- Corrections header noting all 4 material changes
- Section 32: Corrections Log (5 documented corrections with original vs corrected tables)
- Many inline section updates

#### `CHANGELOG.md` — This file

### Key Decisions Documented Throughout

| Decision | Status | Location |
|----------|--------|----------|
| Strategic posture | Option B — Lean Sovereign Lab | `00_MANIFEST.md`, `05_TEAM_BUSINESS.md`, `SYNAPTECHBIO_CRITIQUE_AND_CORRECTIONS.md` |
| Ask remains $150k | Confirmed | All financial sections |
| Zero headcount | Locked | `05_TEAM_BUSINESS.md`, `06_TEAM_ORGANIZATION.md` |
| Sandbox-first go-to-market | Locked | `02_TEAM_NARRATIVE.md` Slide 8, `07_TEAM_PRODUCTION.md` Slide 8, `08_TEAM_SCRIPT.md` Slide 8 |
| STTR as primary channel | Locked | `05_TEAM_BUSINESS.md` Section 2, `03_TEAM_DATA.md` Roadmap P1/P4 |
| Governance deferred to 6+ FTE | Locked | `06_TEAM_ORGANIZATION.md`, `07_TEAM_PRODUCTION.md` Slide 10 |
| No revenue projections | Locked | `03_TEAM_DATA.md`, `05_TEAM_BUSINESS.md` |
| DCSL marked as partially implemented | Locked | `04_TEAM_TECHNICAL.md` Sandbox section, `SECURITY.md` (in GitHub repo) |
| 20× energy savings marked as estimate | Locked | `04_TEAM_TECHNICAL.md` Section 1, `03_TEAM_DATA.md` Chart 3 |

---

*For the full forensic breakdown including the Architect's original critique text, see `SYNAPTECHBIO_CRITIQUE_AND_CORRECTIONS.md`.*
