#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace freegen {

struct CaptureFrame {
    const void* data = nullptr;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t stride = 0;
    uint32_t bytesPerPixel = 4;
    uint64_t timestamp = 0;
    int64_t modifier = 0; // DMA-BUF modifier, -1 for CPU buffer
    bool isDmaBuf = false;
};

class ICaptureBackend {
public:
    using FrameCallback = std::function<void(const CaptureFrame&)>;

    virtual ~ICaptureBackend() = default;

    virtual bool initialize() = 0;
    virtual bool start() = 0;
    virtual void stop() = 0;
    virtual bool isRunning() const = 0;
    virtual std::string name() const = 0;

    virtual void setFrameCallback(FrameCallback callback) = 0;

    virtual std::vector<std::string> listSources() const = 0;
    virtual bool selectSource(const std::string& sourceId) = 0;

    virtual uint32_t captureWidth() const = 0;
    virtual uint32_t captureHeight() const = 0;
};

} // namespace freegen
