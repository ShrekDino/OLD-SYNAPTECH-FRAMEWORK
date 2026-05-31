# FreeGen

**FreeGen** is an open-source alternative to proprietary upscaling and frame generation solutions (like Lossless Scaling, NVIDIA DLSS/FSR), built for the handheld gaming community and power users who want full transparency.

## Features

- **Screen Capture** via PipeWire (Linux) and DXGI Desktop Duplication (Windows)
- **Upscaling** with FSR 1.0, integer scaling, and extensible plugin system
- **Frame Generation** via motion-adaptive interpolation (extensible for AI models)
- **Cross-Platform** — Linux (X11/Wayland) and Windows (DXGI)
- **Plugin Architecture** — easy to add new upscalers and frame gen models
- **ImGui Overlay** — real-time settings, FPS display, HUD
- **Per-Game Profiles** — save and load configurations by game
- **Config Persistence** — JSON config files, CLI arguments

## Quick Start

### From Source

```bash
git clone https://github.com/ShrekDino/Project-FreeGen.git
cd Project-FreeGen
./scripts/manage.sh install        # Install dependencies
./scripts/manage.sh build release  # Build in release mode
./scripts/manage.sh run            # Launch FreeGen
```

### Flatpak

```bash
./scripts/build-flatpak.sh
flatpak install freegen.flatpak
```

### AppImage

```bash
./scripts/build-appimage.sh
./freegen-x86_64.AppImage
```

## Key Bindings

| Key | Action |
|-----|--------|
| Tab | Toggle settings overlay |
| Escape | Quit FreeGen |

## System Requirements

| Component | Minimum |
|-----------|---------|
| OS | Linux (with PipeWire) or Windows 10+ |
| GPU | Vulkan 1.3 capable (integrated or discrete) |
| RAM | 2 GB |
| Disk | 50 MB |

## Architecture Overview

```
[Game/App Window] → [Capture Backend] → [Effect Chain] → [Display Output]
                        │                      │
                   PipeWire/DXGI         Upscale + FrameGen
```

See the [Architecture](architecture.md) page for a detailed breakdown.

## Project Status

FreeGen is in active development. Current capabilities:

- [x] Vulkan rendering pipeline with swapchain resize
- [x] FSR 1.0 upscaling (EASU + RCAS)
- [x] Integer scaling
- [x] Linux PipeWire capture (stub — full DMA-BUF pending)
- [x] Windows DXGI capture (stub — full implementation pending)
- [x] ImGui overlay with settings panel
- [x] Config persistence and CLI parsing
- [x] Per-game profiles
- [x] Frame interpolation (basic)
- [ ] Full DMA-BUF zero-copy capture
- [ ] FSR 2.0 / FSR 3.0 upscaling
- [ ] AI-based frame generation
- [ ] Wayland layer shell overlay
- [ ] Hardware cursor capture
