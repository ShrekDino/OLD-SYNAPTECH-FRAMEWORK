# Architecture

The SynapTechBio platform bridges biological connectomes, sparse neuromorphic computation, consciousness diagnostics, and physical world simulation into a single stack.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    COSMOS INTEGRATION LAYER                      │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Predict2.5       │  │ Reason2         │  │ Tokenizer        │  │
│  │ Visual world gen │  │ Spatial-temporal│  │ Video ↔ latent   │  │
│  │ Text2World       │  │ Physical common │  │ Continuous/discrete│ │
│  │ Video2World      │  │ sense, CoT      │  │ Causal video      │  │
│  └────────┬────────┘  └───────┬────────┘  └────────┬─────────┘  │
│           │                   │                     │            │
│  ┌────────┴───────────────────┴─────────────────────┴──────────┐ │
│  │ bridge/ — Async NIM HTTP client, cloud API fallback         │ │
│  │ Supports: local Docker NIM, NVIDIA cloud API, CPU fallback  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ FLYWIRE REALTIME │  │ CSDF              │  │ IDRE                 │
│ ┌─────────────┐  │  │ ┌──────────────┐  │  │ ┌────────────────┐  │
│ │CosmosVisual │  │  │ │CosmosEnv     │  │  │ │ CSCEngine      │  │
│ │Stimulus     │  │  │ │(replaces     │  │  │ │ 130k×130k      │  │
│ │(generates   │  │  │ │EmbeddingEnv) │  │  │ │ spMV ~1.2ms    │  │
│ │visual scenes│  │  │ └──────────────┘  │  │ │ CuPy/SciPy     │  │
│ │from mot cmds)│  │  │ ┌──────────────┐  │  │ └────────────────┘  │
│ └─────────────┘  │  │ │Agent         │  │  │ ┌────────────────┐  │
│ ┌─────────────┐  │  │ │VAE world mdl │  │  │ │ Lava-NC Bridge │  │
│ │DetailedFly  │  │  │ │Markov blanket│  │  │ │ Intel Loihi    │  │
│ │Body physics │  │  │ │DQFR cycling  │  │  │ │ compile/run    │  │
│ │3-DOF, legs  │  │  │ │GWFR merge    │  │  │ └────────────────┘  │
│ │gait cycle   │  │  │ │Thermostat    │  │  │ ┌────────────────┐  │
│ └─────────────┘  │  │ └──────────────┘  │  │ │ FlyWire LSM    │  │
│ ┌─────────────┐  │  │ ┌──────────────┐  │  │ │ 500-neuron     │  │
│ │MotorDecoder │  │  │ │Dashboard     │  │  │ │ Hierarchical   │  │
│ │12-channel   │  │  │ │Rich TUI      │  │  │ │ Ridge regress  │  │
│ └─────────────┘  │  │ │live display  │  │  │ └────────────────┘  │
│ ┌─────────────┐  │  │ └──────────────┘  │  │ ┌────────────────┐  │
│ │SensoryFeedback│  │  ┌──────────────┐  │  │ │ SSE Streamer   │  │
│ │78-neuropil  │  │  │ │Language     │  │  │ │ 1000-pulse     │  │
│ │closed-loop  │  │  │ │module       │  │  │ │ batches @8ms   │  │
│ └─────────────┘  │  │ │GPT-2 blocks │  │  │ └────────────────┘  │
│ ┌─────────────┐  │  │ └──────────────┘  │  └──────────────────────┘
│ │Visualizer   │  │  └──────────────────┘
│ │UDP bridge   │  │
│ └─────────────┘  │
└─────────────────┘                           ┌──────────────────────┐
                                                │ EVE                  │
                                                │ ┌────────────────┐  │
                                                │ │ Knowledge Vault│  │
                                                │ │ WikiLinks      │  │
                                                │ │ Ollama LLMs    │  │
                                                │ │ Active inference│ │
                                                │ │ LoRA training  │  │
                                                │ └────────────────┘  │
                                                └──────────────────────┘
```

## Data Flow

### Short loop (Real-time behavior)
```
Connectome (IDRE CSC spMV) → 78-neuropil activation → MotorDecoder
→ DetailedFlyBody physics → SensoryFeedback (closed-loop) → Connectome
```

### World loop (Cosmos-augmented)
```
Motor commands → CosmosVisualStimulus → Cosmos-Predict2.5 → Visual world prediction
→ Cosmos-Tokenizer encode → latent tokens → CSDF Agent world model
→ Cosmos-Reason2 → spatial-temporal reasoning → behavior modulation
```

### Diagnostic loop (CSDF)
```
Agent internal state (mu) → VAE world model → Free energy F
→ Thermostat (dS_int/dt) → DQFR duty cycling → GWFR multi-node merge
→ Failure mode classification → Dashboard visualization
```

## Key Interfaces

| Interface | Provider | Consumer | Format |
|---|---|---|---|
| Connectome activation | IDRE `POST /activate` | Realtime Engine, LSM | JSON: `{input_vector, output_vector, spike_count, latency_ms}` |
| SSE neural pulses | IDRE `GET /stream/pulses` | Frontend, CSDF | SSE: `{neuron_ids, voltages, spikes, ts}` |
| World state | Cosmos-Predict2.5 | `CosmosVisualStimulus` | Video frames (RGB) |
| Token embeddings | Cosmos-Tokenizer | CSDF `CosmosEnvironment` | Continuous/discrete latent tensors |
| Spatial reasoning | Cosmos-Reason2 | CSDF Agent, EVE | Text + chain-of-thought |
| Body state | `DetailedFlyBody` | `SensoryFeedback`, `CosmosVisualStimulus` | Dict: `{position, velocity, leg_contacts, heading}` |
| Motor commands | `MotorDecoder` | `DetailedFlyBody`, `CosmosVisualStimulus` | 12-float array |
| Agent state | CSDF `Agent` | CSDF `Dashboard`, `GWFRMerger` | Dict: `{mu, F, S_gen, z, blanket}` |
| Knowledge | EVE `Knowledge Vault` | EVE `Librarian` | Markdown + embeddings |

## Deployment

```bash
# Development — one command per package
python tools/run_all.py

# Production — all services via Docker
docker-compose -f tools/docker-compose.yml up
```

See each package's README for individual startup instructions.
