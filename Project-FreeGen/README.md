<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img src="docs/assets/logo-light.svg" width="200" alt="FreeGen Logo">
  </picture>
</p>

<h1 align="center">FreeGen</h1>

<h3 align="center">Open-Source Screen Capture → Upscaling → Frame Generation</h3>

<p align="center">
  <a href="https://github.com/ShrekDino/Project-FreeGen/actions/workflows/build.yml">
    <img src="https://github.com/ShrekDino/Project-FreeGen/actions/workflows/build.yml/badge.svg" alt="Build">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/ShrekDino/Project-FreeGen" alt="License">
  </a>
  <a href="https://github.com/ShrekDino/Project-FreeGen/releases">
    <img src="https://img.shields.io/github/v/release/ShrekDino/Project-FreeGen" alt="Release">
  </a>
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
  </a>
  <a href="https://github.com/ShrekDino/Project-FreeGen/issues">
    <img src="https://img.shields.io/github/issues/ShrekDino/Project-FreeGen" alt="Issues">
  </a>
</p>

---

**FreeGen** is a high-performance, open-source alternative to proprietary upscaling and frame generation solutions like **Lossless Scaling**, **NVIDIA DLSS**, and **AMD FSR**. It captures your screen, applies any combination of upscaling and frame generation, and outputs to a fullscreen overlay.

Built for the **handheld gaming community** (Steam Deck, ROG Ally, Legion Go) and any gamer who wants full transparency about what their GPU is doing.

> **Glass box, not black box.** Every shader is open source. Every algorithm is documented. Every frame is yours.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎮 Screen Capture
- **Linux**: PipeWire + XDG Desktop Portal (DMA-BUF zero-copy capable)
- **Windows**: DXGI Desktop Duplication
- Fullscreen or per-window capture

</td>
<td width="50%">

### 🔍 Upscaling
- **FSR 1.0** — AMD FidelityFX Super Resolution (EASU + RCAS)
- **Integer Scaling** — Nearest-neighbor pixel replication
- **Passthrough** — No upscaling
- Easy to add more (Anime4K, NIS, Lanczos, etc.)

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Frame Generation
- **Motion-adaptive interpolation** between captured frames
- Doubles perceived framerate (e.g., 30 → 60, 60 → 120)
- Extensible architecture for AI-based models

</td>
<td width="50%">

### 🎛️ Control
- Real-time ImGui overlay (press **Tab**)
- Per-game profiles with auto-detection
- JSON config file + CLI arguments
- FPS limiter, HUD display

</td>
</tr>
</table>

---

## 🚀 Quick Start

```bash
# Install dependencies
sudo apt install libvulkan-dev libsdl2-dev libpipewire-0.3-dev libdbus-1-dev

# Build & run
git clone https://github.com/ShrekDino/Project-FreeGen.git
cd Project-FreeGen
cmake --preset release
cmake --build build/release -j$(nproc)
./build/release/src/freegen
```

Or use the Docker dev environment:

```bash
docker compose up build
```

---

## 📖 Documentation

| Topic | Link |
|-------|------|
| Architecture & Pipeline | [docs/architecture.md](docs/architecture.md) |
| Build from Source | [docs/build.md](docs/build.md) |
| Effect System | [docs/effects.md](docs/effects.md) |
| Capture Backends | [docs/capture-backends.md](docs/capture-backends.md) |
| Configuration & CLI | [docs/configuration.md](docs/configuration.md) |
| Packaging | [docs/packaging.md](docs/packaging.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## 🏗️ Architecture

```
[Game/App] ──► [Capture Backend] ──► [Effect Chain] ──► [Display Output]
                     │                      │
                PipeWire/DXGI         Upscale + FrameGen
```

The core is a modular pipeline where each stage is an independent, replaceable component. Effects are registered via a simple C++ interface — adding a new upscaler requires only a GLSL shader and ~100 lines of C++.

[Full architecture documentation →](docs/architecture.md)

---

## 🗺️ Roadmap

- [x] Vulkan rendering pipeline with swapchain resize
- [x] FSR 1.0 upscaling (EASU + RCAS compute shaders)
- [x] Integer scaling
- [x] Frame interpolation (motion-adaptive blend)
- [x] ImGui overlay with settings panel
- [x] JSON config persistence
- [x] CLI argument parsing
- [x] Per-game profiles
- [ ] Full DMA-BUF zero-copy capture
- [ ] FSR 2.0/3.0 upscaling
- [ ] AI-based frame generation (ONNX runtime)
- [ ] Wayland layer shell overlay
- [ ] Anime4K, NIS, Lanczos effects
- [ ] Hardware cursor capture
- [ ] Localization (i18n)
- [ ] Gamepad navigation

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Linux (PipeWire) or Windows 10+ | — |
| GPU | Vulkan 1.3 (integrated) | Vulkan 1.3 (discrete) |
| RAM | 2 GB | 4 GB+ |
| Capture | PipeWire 0.3+ / DXGI | DMA-BUF capable GPU |

---

## 🤝 Contributing

We welcome all contributions — bug fixes, new effects, documentation, or testing.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Format: `./scripts/manage.sh format`
5. Test: `./scripts/manage.sh test`
6. Push and open a PR

[Full contributing guide →](CONTRIBUTING.md)

---

## 📄 License

FreeGen is licensed under **Apache 2.0**. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ❤️ for the handheld gaming community.</sub>
  <br>
  <sub>Inspired by <a href="https://github.com/Blinue/Magpie">Magpie</a>, <a href="https://www.losslessscaling.com/">Lossless Scaling</a>, and AMD FidelityFX.</sub>
</p>
