# TurboLLama Benchmarks

Hardware: RTX 2080 SUPER (8 GB) · Ryzen 7 5800X · 46 GB RAM  
Model: Qwen3.6-35B-A3B (Q4_K_XL, 17.6 GB)  
Context: 192K tokens

## KV Cache VRAM usage

| Cache type | VRAM @192K | Compression | Quality impact |
|---|---|---|---|
| f16 (vanilla) | ~3.7 GB | 1x | Reference |
| q8_0 | ~1.8 GB | ~2x | Negligible |
| q4_0 | ~0.9 GB | ~4x | Minor |
| **turbo3** | **~0.8 GB** | **~4.6x** | **Minimal (WHT)** |
| **turbo4** | **~1.0 GB** | **~3.8x** | **Near-lossless (WHT)** |

## Inference speed (tok/s)

| Setup | tok/s | Notes |
|---|---|---|
| Vanilla llama.cpp (q8_0, 192K) | OOM | Doesn't fit in 8 GB |
| TurboLLama (turbo3, FA off, 192K) | ~12-15 | Stable, all experts on CPU |
| TurboLLama (turbo3, FA on\*, 192K) | ~25-35 | With TBQ FA templates compiled |
| TurboLLama (turbo3, 4K context) | ~37 | Small context, minimal KV |
| TurboLLama + MTP (draft=5, 4K) | ~12 | Draft overhead > benefit on 8GB |

\*FA with TBQ requires compiling 236 template instances (~30 min).

## MoE Expert Cache

| Cache size | Hit rate (est.) | VRAM saved |
|---|---|---|
| 256 MB (4 experts) | ~40% | Minimal |
| 512 MB (8 experts) | ~65% | Noticeable |
| 1024 MB (16 experts) | ~85% | Good |
| 2048 MB (32 experts) | ~95% | Near-optimal |

## Model compatibility

| Architecture | TurboQuant | MTP | MoE cache |
|---|---|---|---|
| Qwen3.6-35B-A3B | ✅ | ✅ | ✅ |
| Qwen3.5-27B | ✅ | ❌ | ❌ (dense) |
| LLaMA 3.x | ✅ | ❌ | ❌ (dense) |
| Mixtral 8x7B | ✅ | ❌ | ✅ |
| DeepSeek V2/V3 | ✅ | ❌ | ✅ |
| Gemma 2/3 | ✅ | ❌ | ❌ (dense) |
| GLM-4.7-Flash | ✅ (MLA) | ✅ | ✅ |
