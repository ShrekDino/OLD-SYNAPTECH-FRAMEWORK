#pragma once

#include "freegen/capture/ICaptureBackend.hpp"
#include <atomic>
#include <memory>
#include <thread>

namespace freegen {

struct PortalHandler;
struct PipeWireHandler;

class LinuxCaptureBackend : public ICaptureBackend {
public:
    LinuxCaptureBackend();
    ~LinuxCaptureBackend() override;

    LinuxCaptureBackend(const LinuxCaptureBackend&) = delete;
    LinuxCaptureBackend& operator=(const LinuxCaptureBackend&) = delete;
    LinuxCaptureBackend(LinuxCaptureBackend&&) = delete;
    LinuxCaptureBackend& operator=(LinuxCaptureBackend&&) = delete;

    bool initialize() override;
    bool start() override;
    void stop() override;
    bool isRunning() const override { return m_running; }
    std::string name() const override { return "Linux PipeWire"; }

    void setFrameCallback(FrameCallback callback) override { m_callback = std::move(callback); }

    std::vector<std::string> listSources() const override;
    bool selectSource(const std::string& sourceId) override;

    uint32_t captureWidth() const override { return m_width; }
    uint32_t captureHeight() const override { return m_height; }

private:
    void captureThread();

    std::unique_ptr<PortalHandler> m_portal;
    std::unique_ptr<PipeWireHandler> m_pipewire;
    std::thread m_thread;
    std::atomic<bool> m_running{false};
    FrameCallback m_callback;
    uint32_t m_width = 0;
    uint32_t m_height = 0;
    std::string m_sourceId;
};

} // namespace freegen
