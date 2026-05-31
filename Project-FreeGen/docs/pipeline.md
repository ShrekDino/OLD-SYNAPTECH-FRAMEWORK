# Frame Pipeline

Understanding how a single frame flows through FreeGen's pipeline.

## Step-by-Step Flow

### 1. Capture

The capture backend (PipeWire on Linux, DXGI on Windows) delivers a raw frame:

```
CaptureFrame {
    data:       void*       → pointer to pixel data (RGBA8 or DMA-BUF)
    width:      uint32_t    → source width in pixels
    height:     uint32_t    → source height in pixels
    stride:     uint32_t    → bytes per row
    timestamp:  uint64_t    → capture timestamp (μs)
    isDmaBuf:   bool        → true if zero-copy DMA-BUF path
}
```

### 2. Staging Buffer

The CPU-side data is copied into a Vulkan host-visible staging buffer:

```
StagingBuffer (CPU visible)
    ↓ vkCmdCopyBufferToImage
Texture (GPU device-local, optimal tiling)
    ↓ layout transition
Texture in VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL
```

### 3. Effect Chain

Effects are processed in order:

1. **Pre-process** (optional): deband, denoise
2. **Upscale** (optional): FSR 1.0, Integer, Passthrough
3. **Frame Gen** (optional): interpolation between current and previous frame
4. **Post-process** (optional): sharpen, color adjust

Each effect reads from an input image and writes to an output image, using Vulkan compute shaders.

### 4. Graphics Pipeline

The final (possibly upscaled/interpolated) texture is sampled by a fullscreen quad:

```
Vertex Shader:  4 vertices (triangle strip), passes UV coordinates
Fragment Shader: samples texture, outputs to swapchain image
```

### 5. ImGui Overlay

The ImGui overlay is rendered on top of the frame:

```
- Settings window (if visible)
- HUD display (FPS, frame time, input/output resolution, active effect)
```

### 6. Present

The completed swapchain image is presented to the display:

```
vkQueuePresentKHR → monitor refresh
```

## Performance Considerations

- **Capture → GPU transfer**: The staging buffer copy is the primary bottleneck. DMA-BUF zero-copy eliminates this.
- **Compute shader dispatch**: FSR 1.0 dispatches 8x8 workgroups. Larger workgroups improve occupancy.
- **Frame gen**: Interpolation requires both current and previous frame in GPU memory — double the VRAM usage.
- **Triple buffering**: The swapchain uses 3 images for smooth frame pacing.

## Latency

```
Capture → Copy → Effects → Present
   │       │       │         │
  16μs    1ms     2ms      16μs  (target at 60fps)
```

Total pipeline latency targets < 1 frame (< 16ms at 60fps).
