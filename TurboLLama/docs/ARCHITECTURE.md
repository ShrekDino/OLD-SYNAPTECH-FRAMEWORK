# TurboLLama Architecture

## Overview

TurboLLama is a fork of [Ollama](https://github.com/ollama/ollama) that replaces its embedded llama.cpp backend with [TurboQuant](https://github.com/TheTom/llama-cpp-turboquant). The result: an Ollama-compatible server with ~4.6x KV cache compression, MoE expert caching, and MTP speculative decoding.

```
┌─────────────────────────────────────────────────┐
│                 ollama serve                      │
│  ┌─────────────────────────────────────────────┐ │
│  │          Go HTTP API (/api/*, /v1/*)         │ │
│  │  ┌───────┐ ┌───────┐ ┌──────┐ ┌─────────┐  │ │
│  │  │ chat  │ │ gen   │ │ tags │ │ embed   │  │ │
│  │  └───┬───┘ └───┬───┘ └──────┘ └─────────┘  │ │
│  └──────┼──────────┼───────────────────────────┘ │
│         │          │                              │
│  ┌──────▼──────────▼───────────────────────────┐ │
│  │       llama.cpp (TurboQuant fork)            │ │
│  │  ┌─────────────────────────────────────────┐ │ │
│  │  │  KV Cache: turbo3/turbo4 (WHT + L-M)   │ │ │
│  │  │  MoE: LRU expert cache in VRAM          │ │ │
│  │  │  MTP: speculative decoding              │ │ │
│  │  │  Attention: TriAttention scoring        │ │ │
│  │  │  Flash Attn: 236 TBQ template instances │ │ │
│  │  └─────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Key components

### 1. TurboQuant types (22 new ggml types)

| Type | Block | Head dim | Bits | Use case |
|---|---|---|---|---|
| TBQ3_0 | 256 | 256 | ~3 | Wide models |
| TBQ3_1 | 128 | 128 | ~3 | LLaMA, Mistral, Qwen3 |
| TBQ3_2 | 64 | 64 | ~3 | Narrow heads |
| TBQ4_0 | 256 | 256 | ~4 | Higher quality |
| TBQ4_1 | 128 | 128 | ~4 | Default quality mode |
| AMX3_1 | 128 | 128 | ~6.75 | TriAttention (AMX) |

### 2. Head_dim auto-mapping

When you specify `tbq3` or `turbo3`, the system auto-selects the right block size variant based on your model's head dimension. No need to remember which variant your model needs.

### 3. MoE Expert Cache

An LRU cache in VRAM for MoE expert weights. Experts used recently stay hot in VRAM. Cold experts fall back to the existing CPU transfer path. Controlled by `OLLAMA_EXPERT_CACHE_SIZE` (MB).

### 4. MTP Speculative Decoding

Models with MTP heads (like Qwen3.6-35B-A3B) can use the MTP head as a draft model for speculative decoding. Requires a model GGUF with MTP tensors and `--spec-type draft-mtp` flag.

## Build pipeline

```
Source repos:
  ollama/ollama ────┐
  TheTom/llama-     │
  cpp-turboquant    ├──> cmake build ──> libggml-cuda.so
       │            │       (CUDA)
  8 patches ────────┘
                            │
                     go build (CGo)
                            │
                     ollama binary (82 MB)
```

## File structure

| Ollama path | Modification |
|---|---|
| `ml/backend/ggml/ggml/include/ggml.h` | +22 TBQ/AMX type enums |
| `ml/backend/ggml/ggml/src/ggml-common.h` | +20 TBQ block structs |
| `ml/backend/ggml/ggml/src/ggml.c` | +22 type trait entries |
| `llama/llama.cpp/src/llama-context.cpp` | +head_dim auto-mapping |
| `llama/llama.cpp/src/llama-kv-cache.cpp` | +attn_rot_k, n_embd_head tracking |
| `llama/llama.cpp/src/llama-kv-cache.h` | +tria_score_maybe, type_k/v API |
| `llama/llama.cpp/src/llama-kv-cache.cpp` | +ExpertCache integration |
| `llama/llama.cpp/src/models/qwen35moe.cpp` | +MTP auto-detect + HF alias |
| `llm/server.go` | +FA bypass for turbo3/turbo4 |
| `llama/llama.go` | +turbo3/turbo4 type mapping |
| `fs/ggml/ggml.go` | +turbo3/turbo4 validation |
