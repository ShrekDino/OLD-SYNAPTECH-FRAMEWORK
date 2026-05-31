# Architecture

FreeGen is designed as a modular pipeline with clear separation of concerns. Each stage of the pipeline is an independent component with a well-defined interface.

## Pipeline

```
┌──────────────────┐
│   SDL2 Window    │  ← User interacts with this
│  (Vulkan Surface)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  Capture Backend │────▶│  Frame Buffer    │
│ (PipeWire/DXGI)  │     │  (DMA-BUF/CPU)   │
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────┐
│           Compositor                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Pre-Proc │ │ Upscale  │ │Frame Gen │ │
│  │ Effects  │ │ Effects  │ │ Effects  │ │
│  └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────────────────────────────────┐│
│  │         ImGui Overlay               ││
│  └──────────────────────────────────────┘│
└──────────────────┬──────────────────────┘
                   │
                   ▼
           ┌──────────────┐
           │  Swapchain   │
           │  Present     │
           └──────────────┘
```

## Component Design

### Core (`src/libfreegen/core/`)

| Class | Responsibility |
|-------|---------------|
| `Instance` | Vulkan instance creation, debug messenger, extension management |
| `Device` | Physical device selection (with scoring), logical device, queue creation |
| `Swapchain` | Swapchain creation/recreation, render pass, framebuffers, surface format selection |
| `CommandPool` | Command pool management, buffer allocation/reset |
| `ShaderModule` | SPIR-V loading from `.spv` files at runtime, shader stage creation |

### Render (`src/libfreegen/render/`)

| Class | Responsibility |
|-------|---------------|
| `TextureManager` | GPU image allocation, staging buffers, layout transitions, sampler creation |
| `GraphicsPipeline` | Fullscreen quad graphics pipeline for final output |
| `ComputePipeline` | Generic compute pipeline wrapper (shader + layout + dispatch) |
| `Compositor` | Frame lifecycle management, sync objects, effect chain orchestration |

### Capture (`src/libfreegen/capture/`)

| Class | Responsibility |
|-------|---------------|
| `ICaptureBackend` | Abstract interface for all capture backends |
| `LinuxCaptureBackend` | PipeWire + XDG Desktop Portal screen capture |
| `DXGICaptureBackend` | Windows DXGI Desktop Duplication capture |

### Effects (`src/libfreegen/effects/`)

| Class | Responsibility |
|-------|---------------|
| `IEffect` | Abstract interface for all effects (init, process, UI, params) |
| `EffectManager` | Registry of all registered effects, chain builder |
| `FSR1` | FidelityFX Super Resolution 1.0 (EASU upscale + RCAS sharpen) |
| `IntegerScale` | Nearest-neighbor integer pixel replication |
| `FrameGenInterpolate` | Motion-adaptive frame interpolation |

### UI (`src/libfreegen/ui/`)

| Class | Responsibility |
|-------|---------------|
| `ImGuiHandler` | Dear ImGui lifecycle (init, frame, render, Vulkan integration) |
| `SettingsWindow` | Full settings panel with capture/upscale/framegen/display sections |

### Config (`src/libfreegen/config/`)

| Class | Responsibility |
|-------|---------------|
| `ConfigManager` | JSON config load/save, profile management |
| `CliParser` | CLI11-based argument parsing |
| `ProfileManager` | Per-game profile auto-detection and management |

## Threading Model

```
Main Thread                          Capture Thread
───────────                          ──────────────
SDL Event Loop                       PipeWire Loop
  │                                     │
  ├─ ImGui::NewFrame()                  ├─ pw_buffer callback
  ├─ Compositor::beginFrame()           ├─ mmap/DMA-BUF copy
  ├─ ImGui::Render()                    └─ FrameCallback()
  ├─ Compositor::endFrame()
  └─ Compositor::present()
```

The capture thread runs independently and delivers frames via a callback. The main thread processes frames in the render loop using the most recently captured frame.

## Key Design Decisions

1. **Vulkan Compute for effects**: All upscaling and frame generation runs as compute shaders, enabling cross-platform GPU acceleration without vendor lock-in.

2. **Plugin architecture**: Effects implement `IEffect` and can be registered at startup. Community effects require no core changes.

3. **GLSL with build-time compilation**: Shaders are written in portable GLSL and compiled to SPIR-V at build time via `glslc`.

4. **Config over convention**: Settings persist to `~/.config/freegen/config.json` with per-game profile overrides.
