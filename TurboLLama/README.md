# TurboLLama

**Ollama-compatible, TurboQuant-powered. Same `ollama run`. More VRAM.**

TurboLLama is Ollama with a slightly opinionated fork of llama.cpp — the one with TurboQuant KV cache compression, sleeping MoE expert offloading, and MTP speculative decoding. Your 8GB GPU runs 35B models at 192K context. Your 24GB runs 397B models. No config wrestling. No magic incantations.

```bash
curl -fsSL https://raw.githubusercontent.com/ShrekDino/TurboLLama/main/scripts/install.sh | sh
OLLAMA_KV_CACHE_TYPE=turbo3 ollama run qwen3.6:35b-a3b
```

## Why?

Vanilla Ollama is great. But if you've ever tried running a 35B MoE model on an 8GB card, you know the pain: OOM at 8K context, swapping galore, and that sinking feeling when `nvidia-smi` shows 7.9 GiB at idle. TurboLLama fixes that at the engine level — not with config hacks, but with better math.

## What's different

| | Vanilla Ollama | TurboLLama |
|---|---|---|
| KV cache @192K on 8GB | OOM | ✅ ~0.8 GB (turbo3, ~4.6x compression) |
| KV cache @192K on 8GB (quality) | OOM | ✅ ~1.0 GB (turbo4, ~3.8x compression) |
| MoE expert caching | Static (all CPU or all GPU) | ✅ LRU hot cache in VRAM |
| MTP speculative decode | ❌ | ✅ Native MTP head support |
| Head_dim auto-mapping | ❌ | ✅ Auto-maps cache block size |
| 35B model on 8GB | 😰 | 😌 |

## Quick start

```bash
# One-command install (builds from source, 20-45 min):
curl -fsSL https://raw.githubusercontent.com/ShrekDino/TurboLLama/main/scripts/install.sh | sh

# Or manual:
git clone https://github.com/ShrekDino/TurboLLama
cd TurboLLama
bash scripts/install.sh

# Use it like you always do:
export OLLAMA_KV_CACHE_TYPE=turbo3
ollama run qwen3.6:35b-a3b
```

## How it works

```
ollama run                    ollama serve
    │                             │
    ▼                             ▼
TurboLLama fork ◄────────── llama.cpp (TurboQuant)
  ├─ 22 new ggml types            ├─ turbo3 / turbo4 KV cache
  ├─ /v1/chat/completions         ├─ WHT-based rotation
  ├─ /api/generate                ├─ TriAttention scoring
  └─ /api/chat                    └─ MoE expert LRU cache
```

The Go server is 99.9% Ollama. The llama.cpp backend is where the magic happens: 22 new quantization types, Walsh-Hadamard rotated KV cache, AMX3 polar scoring for attention pruning, and an LRU cache that keeps your MoE experts hot in VRAM.

## Environment variables

| Var | Values | Default | What |
|---|---|---|---|
| `OLLAMA_KV_CACHE_TYPE` | `turbo3`, `turbo4`, `q8_0`, `f16` | `f16` | KV cache quantization |
| `OLLAMA_FLASH_ATTENTION` | `0`, `1` | `0` | Flash attention (set `1` for speed, `0` for compatibility) |
| `OLLAMA_EXPERT_CACHE_SIZE` | MB | `1024` | VRAM budget for MoE expert cache |
| `OLLAMA_MTP_ENABLED` | `0`, `1` | `0` | MTP speculative decoding (requires MTP model) |

## Build from source (manual)

```bash
# Prerequisites
sudo apt install golang-go cmake build-essential cuda  # or pacman -S go cmake base-devel cuda

# Clone
git clone https://github.com/ShrekDino/TurboLLama
cd TurboLLama
bash scripts/install.sh
```

The installer:
1. Clones `ollama/ollama` and `TheTom/llama-cpp-turboquant`
2. Applies 8 optimization patches
3. Builds ggml-cuda with 236 TurboQuant template instances
4. Builds the Go binary with CGo
5. Installs to `/usr/local/bin/ollama`
6. Creates a systemd service with optimal defaults

## Project structure

```
TurboLLama/
├── scripts/
│   ├── install.sh           # Full build-from-source pipeline
│   ├── build-llama.sh       # TurboQuant llama.cpp CUDA build
│   └── build-ollama.sh      # Ollama Go fork build
├── patches/
│   ├── 001-*.patch → 008-*.patch  # All modifications
├── config/
│   ├── .env.example
│   ├── ollama-turboquant.service
│   └── hermes-config.yaml
└── docs/
    ├── ARCHITECTURE.md
    └── BENCHMARKS.md
```

## Credits

- [Ollama](https://github.com/ollama/ollama) — the amazing Go server we fork
- [TheTom/llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant) — TurboQuant KV cache engine
- [AmesianX/TurboQuant](https://github.com/AmesianX/TurboQuant) — upstream TurboQuant research
