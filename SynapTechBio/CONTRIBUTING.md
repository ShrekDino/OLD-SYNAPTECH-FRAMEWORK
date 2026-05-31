# Contributing to SynapTechBio

> *Thank you for wanting to build the Neuromorphic Commons with us.*
>
> **First read:** [MANIFEST.md](MANIFEST.md) — our founding vision
> **Then:** [CURRENT_STATE.md](CURRENT_STATE.md) — what exists vs what doesn't
> **Then:** [HOW_YOU_CAN_HELP.md](HOW_YOU_CAN_HELP.md) — concrete ways to contribute

---

## Who Can Contribute

**Everyone.** Whether you're a neuroscientist, a software engineer, a student, a cybersecurity researcher, or someone who just thinks fly brains are cool — there's a place for you here.

### Ways to Contribute

| Role | Contribution Path |
|------|-------------------|
| **Researcher** | Use the platform, provide feedback, propose collaborations |
| **Developer** | Code contributions to IDRE, LSM, visualization tools |
| **Scientist** | Validate benchmarks, propose new connectome datasets |
| **Designer** | Improve the 3D visualization, UI/UX of the portal |
| **Writer** | Improve documentation, write tutorials, share case studies |
| **Security** | Audit DCSL, propose threat models, report vulnerabilities |
| **Community** | Answer questions, onboard new contributors, moderate discussions |

---

## Getting Started

1. **Read the manifesto**: [MANIFEST.md](MANIFEST.md) — understand our vision and values
2. **Check the status**: [CURRENT_STATE.md](CURRENT_STATE.md) — know where we are right now
3. **Find your role**: [HOW_YOU_CAN_HELP.md](HOW_YOU_CAN_HELP.md) — concrete ways to contribute
4. **Read the vision**: [COMPANY_OVERVIEW.md](COMPANY_OVERVIEW.md) and [GOALS_AND_ROADMAP.md](GOALS_AND_ROADMAP.md)
5. **Explore the code**: Check out the technology submodules (`technology/idre/`, `technology/flywire-lsm/`)
6. **Find something to work on**: Look for issues tagged `good-first-issue` or `help-wanted`
7. **Join the conversation**: Open a discussion or comment on an RFC

---

## Code Contributions

For technical contributions to IDRE, FlyWire LSM, or related projects:

### Development Workflow

1. **Fork the relevant repository**
2. **Create a branch**: `git checkout -b feat/your-feature` or `fix/your-bug`
3. **Make your changes** following our code standards
4. **Write or update tests**
5. **Run checks**:
   - Backend: `ruff check src/ && python -m pytest tests/`
   - Frontend: `npx tsc --noEmit && npm run lint`
6. **Submit a pull request** with a clear description

### Code Standards

- **Python**: Type hints on all public functions, line length 120, ruff formatting
- **TypeScript**: Strict mode enabled, functional components with hooks
- **GLSL**: Separate `.glsl` files imported as raw strings
- **Commits**: Descriptive, conventional commit format preferred

---

## Non-Code Contributions

### Research Collaborations
Open an issue tagged `research-proposal` with:
- Your research question
- How IDRE/LSM could help
- Potential collaboration model

### Bug Reports
Open an issue using the bug report template, including:
- Steps to reproduce
- Expected vs actual behavior
- Environment details

### Feature Requests
Open an issue using the feature request template, including:
- Use case and motivation
- Proposed solution
- Alternatives considered

---

## Recognition

Every contributor is recognized:
- **All contributors** listed in our Hall of Fame
- **Significant contributions** acknowledged in release notes
- **Research collaborations** co-authored on publications
- **Community leaders** eligible for Community Council nomination

---

## Code of Conduct

All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and inclusive. We have zero tolerance for harassment.

---

## Questions?

Open a discussion, comment on an issue, or reach out directly:
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and brainstorming
- **Email**: SamiT2825@synaptechbio.org
