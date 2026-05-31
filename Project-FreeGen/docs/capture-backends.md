# Capture Backends

FreeGen supports multiple capture backends for different platforms.

## Linux: PipeWire / XDG Desktop Portal

The Linux capture backend uses PipeWire for low-latency screen capture with XDG Desktop Portal for user permission flow.

### Architecture

```
FreeGen
  │
  ├─ PortalHandler
  │     │
  │     ├─ D-Bus → org.freedesktop.portal.Desktop
  │     │          → CreateSession()
  │     │          → SelectSources()
  │     │          → Start()
  │     │
  │     └─ Returns PipeWire Node ID
  │
  └─ PipeWireHandler
        │
        ├─ pw_stream (capture direction)
        ├─ MemFd mapping (mmap)
        ├─ DMA-BUF import (zero-copy path)
        └─ FrameCallback → FreeGen pipeline
```

### Capture Modes

| Mode | Description | Performance |
|------|-------------|-------------|
| MemFd (CPU) | Frame data mapped via file descriptor | 1-2ms copy overhead |
| DMA-BUF (GPU) | Direct GPU buffer import (zero-copy) | ~0ms overhead |

### Frame Format

PipeWire negotiates RGBA (32-bit) as the primary format, with BGRA fallback. Frames are delivered as:

```cpp
struct CaptureFrame {
    const void* data;      // Pixel data (CPU pointer or DMA-BUF handle)
    uint32_t width;        // Frame width
    uint32_t height;       // Frame height
    uint32_t stride;       // Bytes per row
    uint64_t timestamp;    // Microsecond timestamp
    bool isDmaBuf;         // True if zero-copy DMA-BUF path
};
```

## Windows: DXGI Desktop Duplication

The Windows backend uses IDXGIOutputDuplication for desktop capture.

### Architecture

```
FreeGen
  │
  └─ DXGICaptureBackend
        │
        ├─ IDXGIOutputDuplication
        │     → AcquireNextFrame()
        │     → GetFrameDirtyRects()
        │     → ReleaseFrame()
        │
        └─ FrameCallback → FreeGen pipeline
```

### Capture Performance

| Method | Latency | CPU Usage |
|--------|---------|-----------|
| Desktop Duplication | 1-2 frames | 2-5% |
| BitBlt (fallback) | 1-3 frames | 5-10% |

## Adding a New Capture Backend

Implement the `ICaptureBackend` interface:

```cpp
class MyCaptureBackend : public ICaptureBackend {
    bool initialize() override;    // Setup resources
    bool start() override;         // Begin capture
    void stop() override;          // Stop capture
    std::string name() const override;
    void setFrameCallback(FrameCallback cb) override;
    std::vector<std::string> listSources() const override;
    bool selectSource(const std::string& id) override;
};
```
