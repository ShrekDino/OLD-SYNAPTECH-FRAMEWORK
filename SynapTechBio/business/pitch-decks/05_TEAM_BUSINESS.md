# 05 — TEAM BUSINESS: Model & Financials

> *This document reflects the corrected business model under Option B: solo founder, bottom-up adoption via public sandbox, and STTR grants as primary go-to-market. All numbers are honest assessments grounded in current reality.*

---

## 1. Business Model: Bottom-Up Sandbox → Enterprise Upsell

SynapTechBio does not have a sales team. It has a working connectome simulator deployed to the public web. The go-to-market is: publish a tool that solves a real researcher bottleneck, let organic adoption drive discovery, upsell only when a user outgrows the free tier.

### Pricing Tiers

| Tier | Price | What You Get | Who It's For |
|------|-------|-------------|--------------|
| **Sandbox (Free)** | $0 | Rate-limited spMV (100 activations/day), basic 3D visualization, community support, opt-in telemetry | Students, hobbyists, curious neuroscientists |
| **Enterprise** | Custom | Uncapped spMV, DCSL IP protection, Loihi compile, dedicated support, SLA | Pharma, biotech, defense, large institutions |

### Why No Institutional Tier

The original $300k ACV Institutional tier was untestable fantasy. Academic procurement cycles run 9-12 months. SynapTechBio's current runway is 18 months with no sales headcount. Enterprise deals are pursued only when an inbound lead explicitly requests dedicated infrastructure — and priced per-deal, not per-tier.

### Unit Economics (Observed, Not Projected)

| Metric | Sandbox (Free) | Enterprise |
|--------|---------------|------------|
| Server cost per user/day | ~$0.03 (at current CSC engine efficiency) | $0 (dedicated infra, passthrough pricing) |
| Customer Acquisition Cost | $0 (organic) | $0 (inbound only) |
| Gross Margin | 0% | 70-80% |

No ARR targets. No revenue projections. Revenue is a trailing indicator of sandbox adoption, not a leading target.

---

## 2. Go-to-Market: The STTR Pipeline

STTR grants are not a footnote — they are the primary initial revenue channel. A solo founder cannot cold-call into biotech procurement. But a solo founder can partner with a university lab on a federal grant application.

### Why STTR Fits a Solo Operator

| Requirement | SynapTechBio Status |
|-------------|-------------------|
| Small business (<500 employees) | ✅ 1 employee |
| Research institution partner | ✅ Targeting Stanford/MIT/UCSD |
| PI can be from business | ✅ Founder qualifies |
| >40% work by small business | ✅ Platform development |
| >30% work by research institution | ✅ Neuroscience validation |
| No sales team required | ✅ Grant replaces sales cycle |

### Target Pipeline

| Topic | Agency | Amount | Target Partner | LOI Status |
|-------|--------|--------|----------------|------------|
| GPU-Accelerated Connectome Simulation for Neuromorphic Architecture | NSF SBIR | $275k | UCSD (Swanson Lab) | Conversation active |
| Drosophila-Inspired LSM for Real-Time Neural Signal Analysis | NIH STTR | $250k | Stanford (Deisseroth Lab) | Conversation active |
| Democratized Connectome Simulation Platform | NSF Cyberinfrastructure | $300k | MIT (McGovern Institute) | Target |

### LOI Strategy (90-Day)

1. Send personalized demo links to individual PIs using the sandbox
2. Offer co-authorship on any publication using the platform
3. Secure non-binding Letters of Intent expressing intent to collaborate on STTR applications
4. Present LOIs to investors as pipeline validation, not signed contracts

**Current reality:** No LOIs secured. Conversations are active. The working sandbox is the conversion tool.

---

## 3. Use of Funds: $150,000 Pre-Seed (Option B)

Allocation rewritten for solo-founder execution. Zero headcount. Maximum infrastructure and legal protection.

| Category | Amount | % | Specifics |
|----------|--------|---|-----------|
| **Cloud GPU (Reserved)** | $50,000 | 33% | 2× A100 80GB reserved instances, 12 months (Lambda Labs / runpod.io). No on-demand. No rate risk. |
| **Legal / IP** | $35,000 | 23% | 6 provisional → utility patent filings ($4k-6k each via experienced counsel), DCSL framework legal review, C-Corp incorporation, IP assignment documentation |
| **INRC / Loihi Access** | $35,000 | 23% | Intel Neuromorphic Research Cloud membership + reserved cloud Loihi 2 time, 12 months |
| **Infrastructure** | $15,000 | 10% | Pinecone vector DB, S3 storage, Hugging Face hosting, domain, email, CI/CD |
| **Marketing / Travel** | $15,000 | 10% | Conference registration (SF, Stanford, MIT), demo materials, prototype hardware for demos |
| **Engineering Salaries** | $0 | 0% | Founder takes minimum draw from savings. No hires until sandbox proves traction. |
| **Total** | **$150,000** | **100%** | **18-month runway at ~$8.3k/month burn** |

### Why This Allocation

- **No engineering salaries:** Hiring 2 engineers at $80k total over 6 months would pay ~$6.7k/month each — below Austin junior market rate and in direct contradiction of the "equal pay" philosophy. A solo founder preserves velocity and avoids management overhead that would slow the actual critical path: scientific validation, patent protection, and sandbox deployment.
- **Reserved compute:** On-demand GPU pricing carries 40-60% premium over reserved. Locking in reserved instances avoids Lambda Labs capacity crunches and ensures predictable infrastructure for sandbox uptime.
- **Patents first:** The DCSL cryptographic split-layer architecture and the closed-form Ridge Regression readout mechanics are the two most defensible IP assets. Filing utility patents before any public sandbox launch prevents prior-art complications.

---

## 4. Financial Assumptions

| Assumption | Value | Rationale |
|-----------|-------|-----------|
| Founder salary | $0 | Living expenses from personal savings. Minimum draw deferred. |
| Office | $0 | Remote-first, co-working as needed. |
| Runway | 18 months | $150k / ~$8.3k monthly burn. Allows 3 quarters of sandbox operation before fundraise pressure. |
| Revenue | $0 until STTR | No revenue model. STTR Phase I (~$250k non-dilutive) is the first financial validation target. |
| Fundraising trigger | 3 signed LOIs + sandbox with 100+ DAU | Before raising a larger round. Not before. |

### Cash Flow Reality

```
Month  0: $150k raised  →  $35k legal/IP  →  $115k remaining
Month  1: $50k GPU reserved (12mo upfront or monthly)  →  $65k remaining
Month  2: $35k Loihi reserved  →  $30k remaining
Month  3-18: ~$8.3k/month for infra + travel + living
```

At month 12, if no STTR grant or revenue has materialized, the remaining ~$50k funds 6 more months of minimal compute. The sandbox must demonstrate traction by month 9 to open the next round or STTR window.

---

## 5. Cap Table & Entity Structure

| Detail | Status |
|--------|--------|
| Jurisdiction | Delaware |
| Type | C-Corporation |
| Status | Pre-incorporated via registered agent |
| Instrument | Post-money SAFE |
| Authorized Shares | 10,000,000 |
| Founder Equity | 100% (no dilution until priced round) |
| Option Pool | 15% (reserved, unallocated) |
| IP Assignment | All IP assigned to entity upon incorporation |

**No investor board seats. No observed rights. No pro-rata.** The SAFE is clean. The founder retains full decision-making authority until a priced round.

---

## 6. Key Business Risks (Revised for Option B)

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| **No funding raised** | Medium | Sandbox is free to deploy. Community contributions sustain the vision even without compute budget. |
| **STTR grants not awarded** | Medium | Multiple agency submissions (NSF, NIH). Apply to 3+ programs in parallel. Each application is also a relationship-builder with the partner lab. |
| **Sandbox fails to attract users** | Medium | Target niche neuroscience community directly (FlyWire mailing list, neurotwitter, lab cold-emails). 100 DAU is achievable with targeted outreach to ~500 researchers. |
| **Founder burnout** | Medium | Solo founder risk is real. Mitigated by low burn rate (no rent stress), clear 18-month timeline, and community contributors who can absorb specific tasks. |
| **Large competitor enters space** | Low-Medium | DCSL patent + open community are the durable moats. No competitor can replicate the sandbox's organic lead-gen advantage once the telemetry flywheel spins up. |
| **Intel shifts INRC protocols** | Low | Loihi is a benchmark target, not a dependency. The CSC engine runs on any GPU/CPU. Loihi access is for validation and marketing, not core functionality. |

---

## 7. Compensation Philosophy (Deferred)

No salaries until Series A. No pay bands. No equity distribution.

**Current policy:** Contributors receive recognition, co-authorship on publications, and priority equity grants when a priced round closes. The founder takes no salary. Full compensation framework will be designed and published when the team reaches 3+ FTE.

This is not a contradiction of the "equal pay" philosophy. It is a honest reflection of pre-revenue reality. Promising $130k salaries to engineers on a $150k budget was the contradiction. Correcting it is integrity.
