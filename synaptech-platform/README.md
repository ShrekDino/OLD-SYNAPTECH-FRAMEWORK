# synaptech-platform

**Monorepo for the SynapTechBio ecosystem** — from connectome to computation.

| Package | Source | What It Does |
|---|---|---|
| `packages/idre` | [synaptech-idre](https://github.com/ShrekDino/synaptech-idre) | GPU-accelerated sparse graph engine executing the 139k-neuron Drosophila connectome in real-time |
| `packages/flywire-lsm` | [Flywirellm](https://github.com/ShrekDino/Flywirellm) | Two-region hierarchical Liquid State Machine, >95% next-token prediction |
| `packages/flywire-realtime` | [flywire-realtime-engine](https://github.com/ShrekDino/flywire-realtime-engine) | 60 Hz closed-loop whole-brain simulation with body physics and sensory feedback |
| `packages/csdf` | [uploaded-consciousness-framework](https://github.com/ShrekDino/uploaded-consciousness-framework) | Formal testbed for failure modes in synthetic consciousness architectures |
| `packages/eve` | [EVE](https://github.com/ShrekDino/EVE) | Self-aware knowledge entity using active inference and local LLMs |
| `packages/cosmos` | *New* | NVIDIA Cosmos integration layer — world model bridge for Physical AI |

See [MONOREPO_MAP.md](MONOREPO_MAP.md) for the full cross-reference to original repositories.

## Architecture

```
External world (NVIDIA Cosmos)
    │
    │  Cosmos-Predict2.5 (visual world generation)
    │  Cosmos-Reason2 (spatial-temporal reasoning)
    │  Cosmos-Tokenizer (video↔latent encoding)
    │
    ▼
┌──────────────────────────────────────┐
│  packages/cosmos                     │
│  ┌────────────┐ ┌──────────────────┐ │
│  │ worldgen/  │ │ reason/          │ │
│  │ Predict2.5 │ │ Reason2 adapter  │ │
│  │ client     │ │ VLM reasoning    │ │
│  └─────┬──────┘ └────────┬─────────┘ │
│  ┌─────┴──────────────────┴─────────┐ │
│  │ bridge/ — NIM client, tokenizer  │ │
│  └──────────────────────────────────┘ │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴───────────────────┐
    ▼                              ▼
┌─────────────────┐   ┌───────────────────────┐
│ flywire-realtime│   │ csdf                  │
│ ┌─────────────┐ │   │ ┌─────────────────┐   │
│ │CosmosVisual │ │   │ │CosmosEnvironment│   │
│ │Stimulus     │◄┼───┼►│agent world model│   │
│ └─────────────┘ │   │ └─────────────────┘   │
│ ┌─────────────┐ │   │ ┌─────────────────┐   │
│ │Body physics │ │   │ │GWFR merge /     │   │
│ │78-neuropil  │◄┼───┼►│thermostat /     │   │
│ │closed loop  │ │   │ │DQFR cycling     │   │
│ └──────┬──────┘ │   │ └─────────────────┘   │
└─────────┼───────┘   └───────────────────────┘
          │
┌─────────▼────────┐
│ idre             │
│ ┌──────────────┐ │
│ │CSCEngine     │ │
│ │130k×130k     │◄┼── Loihi bridge
│ │spMV ~1.2ms   │ │
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │FlyWire LSM   │ │
│ │500-neuron    │◄┼── Reservoir computing
│ │reservoir     │ │
│ └──────────────┘ │
└──────────────────┘
```

## Quick Start

```bash
# Launch everything
python tools/run_all.py

# Or individual packages
cd packages/idre && python run.py all
cd packages/flywire-lsm && python -m flywire_lsm.server
cd packages/flywire-realtime && python flybrain_activity.py --closed-loop --realtime
cd packages/csdf && python scripts/run.py --single --cosmos
cd packages/eve && python eve_suite_pyside6.py
```

## License

MIT — see individual package licenses for details.

## Contact

Sami Torres — SamiT2825@synaptechbio.org
