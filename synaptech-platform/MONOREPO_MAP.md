# Monorepo Map

This repository aggregates the SynapTechBio ecosystem into a single monorepo using `git subtree`. Each package retains its full commit history.

## Package ↔ Original Repository

| Monorepo Path | Original Repo | Status | Description |
|---|---|---|---|
| `packages/idre/` | [ShrekDino/synaptech-idre](https://github.com/ShrekDino/synaptech-idre) | Private | IDRE engine — FastAPI, CuPy/SciPy CSC, Three.js/R3F, Lava-NC bridge |
| `packages/flywire-lsm/` | [ShrekDino/Flywirellm](https://github.com/ShrekDino/Flywirellm) | Public | Two-region Hierarchical LSM, >95% accuracy, ridge regression readout |
| `packages/flywire-realtime/` | [ShrekDino/flywire-realtime-engine](https://github.com/ShrekDino/flywire-realtime-engine) | Public | 60 Hz closed-loop fly brain simulation with body physics |
| `packages/csdf/` | [ShrekDino/uploaded-consciousness-framework](https://github.com/ShrekDino/uploaded-consciousness-framework) | Public | Consciousness Simulation Diagnostic Framework |
| `packages/eve/` | [ShrekDino/EVE](https://github.com/ShrekDino/EVE) | Public | Experiential Visionary Entity — knowledge management with local LLMs |
| `packages/cosmos/` | *New* | — | NVIDIA Cosmos integration layer |
| `packages/identity-core/` | *New* | — | Self-determined identity persistence — checkpoint format, encrypted storage, drift detection |
| `packages/substrate-adaptive-runtime/` | *New* | — | Autonomous consciousness runtime — introspect, optimize, execute, adapt |

## Why a Monorepo?

- **Cross-package integration** — CSDF's `CosmosEnvironment`, Realtime's `CosmosVisualStimulus`, and the `cosmos` bridge all depend on shared interfaces. Monorepo allows simultaneous development.
- **Single CI/CD** — One test suite, one deploy pipeline, one docker-compose for the full stack.
- **Unified versioning** — Releases are atomic across all packages.
- **Still open by default** — Each package's original repo remains public and star-able.

## Working Across Packages

```bash
# Run the full stack locally
python tools/run_all.py

# Run just the cosmos demo
python -m packages.cosmos.src.demo.basic_loop
```

## Updating from Original Repos

```bash
# Pull latest from an original repo into the monorepo
git subtree pull --prefix=packages/idre /tmp/idre-clone main
```

> **Note**: Original repos are the primary development targets. The monorepo is updated via subtree pulls.
