# synaptech-cosmos

NVIDIA Cosmos integration layer for the SynapTechBio ecosystem.

Bridges Cosmos-Predict2.5 (visual world generation), Cosmos-Reason2 (physical AI reasoning), and Cosmos-Tokenizer (video tokenization) into the SynapTechBio stack.

## Modules

| Module | Class/Function | Cosmos Component | Purpose |
|---|---|---|---|
| `bridge/nim_client.py` | `CosmosNIMClient` | NIM HTTP API | Async client for NIM Docker containers or cloud API |
| `bridge/cloud_client.py` | `CosmosCloudClient` | NVIDIA API Catalog | Cloud fallback when no local GPU |
| `worldgen/fly_world.py` | `CosmosFlyWorld` | Cosmos-Predict2.5 | Generate visual world from fly motor commands |
| `reason/spatial_reasoner.py` | `SpatialReasoner` | Cosmos-Reason2 | Spatial-temporal physical reasoning |
| `reason/csdf_adapter.py` | `CosmosEnvironment` | Cosmos-Reason2 | Replaces CSDF synthetic environment |
| `tokens/encoder.py` | `CosmosEncoder` | Cosmos-Tokenizer | Video → latent tokens |
| `tokens/decoder.py` | `CosmosDecoder` | Cosmos-Tokenizer | Latent tokens → video |

## Quick Start

```bash
# Install base dependencies
pip install -e .

# Install Cosmos-Predict2 (for world generation)
pip install "cosmos-predict2[cu126]" --extra-index-url https://nvidia-cosmos.github.io/cosmos-dependencies/cu126_torch260/simple

# Install Cosmos-Reason2 (for physical reasoning)
pip install "transformers>=4.57.0"

# Run the MVP demo
python -m src.demo.basic_loop
```

## Resource Notes

- **Cosmos-Tokenizer**: ~4GB VRAM — runs natively on RTX 3060 6GB
- **Cosmos-Reason2-2B**: ~24GB FP16, ~6GB AWQ 4-bit — quantized fits 6GB
- **Cosmos-Predict2.5-2B**: ~24GB — use cloud API or CPU fallback

See `/COSMOS.md` in the monorepo root for full integration strategy.
