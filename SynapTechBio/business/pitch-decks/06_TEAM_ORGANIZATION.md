# 06 — TEAM ORGANIZATION: Current State & Future Vision

> *This document is split into two phases. Phase 1 describes the pre-seed solo-founder reality. Phase 2 describes the target organizational model — deferred until the team reaches 6+ FTE.*

---

## Phase 1: Pre-Seed (Current)

### Structure

```
Sami Torres — Founder & Solo Operator
  │
  ├── Builds the platform (IDRE, sandbox, DCSL)
  ├── Files patents (working with outside counsel)
  ├── Secures STTR partnerships (research lab outreach)
  ├── Manages infrastructure (reserved GPU, Loihi)
  └── Handles community (GitHub, email, sandbox users)
```

- **Decision-making:** Founder makes all operational and strategic decisions.
- **Ethical review:** Ad-hoc external advisors consulted as needed. No formal board.
- **Community input:** GitHub issues, Discord, and email — founder reads everything but makes final calls.
- **Compensation:** No salaries. Founder takes minimum draw from savings. Contributors receive recognition, co-authorship, and priority equity grants when a priced round closes.
- **Headcount:** 1. No hires until the sandbox demonstrates sustained adoption (100+ DAU) or an STTR grant funds a specific research engineering role.

### Why No Governance Structure

Pre-seed governance overhead (Community Council, Ethical Review Board, rotating leads, RFC processes) burns cognitive bandwidth that a solo founder cannot afford. Every hour spent on governance process is an hour not spent on:

- Optimizing the CSC sparse engine
- Filing patent claims
- Deploying the sandbox
- Converting a PI at Stanford into an STTR partner

**The Valve model is the North Star, not the starting line.** Valve had a shipping product and 30+ employees before it went flat. SynapTechBio will adopt the model when it has a team worth organizing.

---

## Phase 2: Post-Seed (Target — Deferred Until 6+ FTE)

### Structure

```
                       ┌────────────────────────┐
                       │  COMMUNITY COUNCIL      │
                       │  (Elected — advisory)  │
                       └──────────┬─────────────┘
                                  │
┌──────────────────────────────────┼──────────────────────────────────┐
│                         Founder (Sami)                              │
│                  Steward — not CEO. Holds the vision.               │
└──────────────────────────────────┼──────────────────────────────────┘
                                  │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  RESEARCH TEAM   │   │ ENGINEERING TEAM │   │  COMMUNITY TEAM  │
│  • Neuroscience  │   │ • Backend (IDRE) │   │ • Documentation  │
│  • Connectomics  │   │ • Frontend (3D)  │   │ • Support        │
│  • LSM validation│   │ • Infrastructure │   │ • Events         │
│  • STTR partners │   │ • Security/DCSL  │   │ • Onboarding     │
│                   │   │ • AI alignment  │   │ • Moderation     │
└──────────────────┘   └──────────────────┘   └──────────────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                  │
                      ┌────────────────────────┐
                      │  ETHICAL REVIEW BOARD  │
                      │  (Independent — veto)  │
                      └────────────────────────┘
```

### Valve Model Adaptation (Post-Seed)

| Valve Feature | SynapTechBio Adaptation | Effective |
|--------------|------------------------|-----------|
| No managers | Self-organizing teams around functional areas | At 6+ FTE |
| Project self-selection | Team members choose projects based on interest + skill | At 6+ FTE |
| Open allocation | 80% core platform, 20% exploration time | At 6+ FTE |
| Peer review compensation | Transparent pay bands (no negotiation) | At 3+ FTE |
| Profit sharing | 20% of platform revenue distributed to contributors | At revenue stage |
| Flat hierarchy | Flat, with functional leads (rotating) | At 6+ FTE |

### Team Formation Principles (Future)

1. Teams form around problems, not departments
2. No permanent team assignments — members can rotate every quarter
3. Functional leads rotate every 6 months — no permanent managers
4. Decisions are made by the person doing the work; steward resolves conflicts

### Governance Bodies (Future)

| Body | Members | Authority | Effective |
|------|---------|-----------|-----------|
| Community Council | 5-7 elected from community | Advisory — roadmap input | Post-Seed |
| Ethical Review Board | 5: neuroscientist, ethicist, community rep, legal, security | Binding veto on ethical concerns | Post-Seed |
| RFC Process | Open participation | Consensus-based decision making | Post-Seed |

---

## Compensation Philosophy (Deferred)

No salaries until Series A. No pay bands. No equity distribution.

**Pre-Seed policy:** Contributors receive recognition, co-authorship on publications, and priority equity grants when a priced round closes. The founder takes no salary.

**Post-Seed target:** Transparent pay bands, equity for all 6+ month contributors, 20% profit sharing. These are designed and ready to implement — they are not abandoned, merely deferred.

### Target Pay Bands (For Reference — Not Active)

| Role Level | Base Salary (Austin) | Equity Grant (4yr vest) |
|-----------|---------------------|----------------------|
| Senior Engineer | $130k - $160k | 1% - 2% |
| Mid Engineer | $100k - $130k | 0.5% - 1% |
| Junior / New Grad | $70k - $90k | 0.25% - 0.5% |
| Research Scientist | $120k - $150k | 1% - 2% |
| Community Manager | $60k - $80k | 0.25% - 0.5% |

---

## Austin Talent Strategy (Context for Future)

### Why Austin (When We Hire)

| Factor | Austin | San Francisco | Seattle | New York |
|--------|--------|---------------|---------|----------|
| Cost of Living Index | 162 | 269 | 219 | 239 |
| State Income Tax | 0% | 12.3% (top) | 0% | 10.9% (top) |
| 1BR Rent (avg) | $1,600 | $3,200 | $2,100 | $3,800 |
| University Pipeline | UT Austin | Stanford/Berkeley | UW | NYU/Columbia |
| Tech HQ Migration | Tesla, Apple, Google, Oracle | — | — | — |

### Recruitment Channels (Future)

| Channel | Target | Message |
|---------|--------|---------|
| UT Austin | CS/Neuroscience graduates | "Build the future of intelligence. Stay in Austin." |
| GitHub | Open-source contributors | "Your code literally advances neuroscience." |
| Neurotech conferences | Researchers | "Free Loihi access. Open platform. Keep your IP." |

---

## Culture Principles (Non-Negotiable — Apply Now, Solo or Not)

1. **No assholes.** Zero tolerance for ego, politics, or credentialism.
2. **Build in the open.** Code, plans, and problems are public by default.
3. **Safety first.** Open source does not mean unprotected.
4. **Rest is work.** Burnout is a design flaw, not a badge of honor.
5. **Criticize ideas, not people.** Every suggestion is a gift.
