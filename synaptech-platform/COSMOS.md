# NVIDIA Cosmos Integration

## Why Cosmos?

NVIDIA Cosmos provides the **external world** half of the mind-environment loop. The SynapTechBio ecosystem simulates the internal neural substrate (connectome, LSM, consciousness diagnostics). Cosmos supplies the physics, visual world, and spatial-temporal reasoning that an embodied or uploaded mind needs to interact with.

| SynapTechBio component | Cosmos counterpart | What the integration provides |
|---|---|---|
| FlyWire Realtime Engine (body physics + closed-loop stimulus) | Cosmos-Predict2.5 | Visual world generation from motor commands — the fly agent *sees* what its actions produce |
| CSDF (VAE world model, agent embedding environment) | Cosmos-Reason2 | Physically-grounded spatial-temporal reasoning replaces synthetic embedding sequences |
| IDRE (connectome visualization, SSE stream) | Cosmos-Tokenizer | Tokenize 3D brain visualization into discrete/continuous latent space for multimodal analysis |

## Cosmos Models

| Model | Size | VRAM | Use in SynapTechBio | Local on RTX 3060 6GB? |
|---|---|---|---|---|
| **Cosmos-Predict2.5-2B** (Text2World / Video2World) | 2B params | ~24GB | Generate visual world from fly motor commands | CPU fallback or cloud NIM |
| **Cosmos-Reason2-2B** (Physical AI VLM) | 2B params | ~24GB (FP16), ~6GB (AWQ 4-bit) | Spatial-temporal reasoning for CSDF agent | ✅ AWQ quantized fits |
| **Cosmos-Tokenizer** (CV8x8x8 / DV8x16x16) | ~300M | ~4GB | Encode/decode video ↔ latent tokens | ✅ Runs locally |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   packages/cosmos                    │
│                                                      │
│  bridge/          — NIM HTTP client + cloud fallback │
│  ├─ nim_client.py   · Async REST client for NIM API  │
│  └─ cloud_client.py · NVIDIA cloud API when no GPU   │
│                                                      │
│  worldgen/        — Cosmos-Predict2.5 adapter        │
│  ├─ fly_world.py    · Motor command → world state    │
│  └─ scene_encoder.py · Frame → continuous latent     │
│                                                      │
│  reason/          — Cosmos-Reason2 adapter           │
│  ├─ csdf_adapter.py · Agent state → physical context │
│  └─ spatial_reasoner.py · Video → CoT reasoning      │
│                                                      │
│  tokens/          — Cosmos-Tokenizer wrapper         │
│  ├─ encoder.py       · Video → discrete/continuous   │
│  └─ decoder.py       · Latent → video reconstruction │
│                                                      │
│  demo/            — MVP integration scripts          │
│  └─ basic_loop.py    · One full cycle               │
└─────────────────────────────────────────────────────┘
```

## Integration Points

### 1. FlyWire Realtime Engine → Cosmos-Predict2.5

**File**: `packages/cosmos/src/worldgen/fly_world.py`
**Class**: `CosmosFlyWorld`

Takes the Realtime Engine's 12-channel motor commands + 78-neuropil activity → generates a visual world frame via Cosmos-Predict2.5 → feeds back as sensory stimulus.

```python
class CosmosFlyWorld:
    def predict_world(self, motor_commands, neuropil_state):
        prompt = self._build_prompt(motor_commands, neuropil_state)
        video = self.nim_client.text2world(prompt)
        return video  # RGB frames for stimulus injection
```

### 2. CSDF → Cosmos-Reason2

**File**: `packages/cosmos/src/reason/csdf_adapter.py`
**Class**: `CosmosEnvironment`

Replaces CSDF's synthetic `EmbeddingEnvironment` with Cosmos-Reason2 spatiotemporal grounding. The agent's internal state `mu` is conditioned on physically-grounded reasoning about the world.

```python
class CosmosEnvironment(EmbeddingEnvironment):
    def __init__(self, reasoner: CosmosReasoner, tokenizer: CosmosTokenizer):
        self.reasoner = reasoner
        self.tokenizer = tokenizer

    def step(self):
        world_context = self.reasoner.reason(self.agent_state)
        mu = self._embed(world_context)
        return mu, self._entropy(mu)
```

### 3. CSDF Agent → Cosmos-Reason2 (spatial-temporal)

**File**: `packages/cosmos/src/reason/spatial_reasoner.py`
**Class**: `SpatialReasoner`

Takes a video frame or token sequence from the agent's world model → reasons about spatial relationships, physical causality, and future states → returns structured reasoning as agent context.

## Resource Strategy (RTX 3060 6GB)

| Model | Strategy | How |
|---|---|---|
| **Predict2.5** | Cloud NIM API | NVIDIA API catalog, Docker NIM on cloud instance, or CPU with `device_map="cpu"` in `diffusers` |
| **Reason2** | 4-bit AWQ quantization | Fits in ~6GB. Use `transformers` + `autoawq` or `vllm` with quantization |
| **Tokenizer** | Native local | Runs directly on available VRAM. Highest priority for local development |

## MVP Demo

```bash
cd packages/cosmos
python -m src.demo.basic_loop
```

This script:
1. Loads the Cosmos-Tokenizer (local if VRAM available, else CPU)
2. Starts a minimal CSDF agent with `CosmosEnvironment`
3. Generates a sample world frame via text prompt (Predict2.5 via cloud or CPU)
4. Runs Reason2 on the output (AWQ quantized if available)
5. Displays the full diagnostic output (F, S_gen, Omega_coherence, failure modes)

## Dependencies

```bash
# Cosmos-Predict2 (pip)
pip install "cosmos-predict2[cu126]" --extra-index-url https://nvidia-cosmos.github.io/cosmos-dependencies/cu126_torch260/simple

# Cosmos-Reason2 (transformers)
pip install "transformers>=4.57.0"

# Cosmos-Tokenizer
pip install torch numpy

# Quantization (for Reason2 on 6GB)
pip install autoawq
```

Or use the NIM Docker containers:
```bash
docker run --gpus all -p 8000:8000 \
  -e NGC_API_KEY=$NGC_API_KEY \
  nvidia/cosmos-predict2.5
```
