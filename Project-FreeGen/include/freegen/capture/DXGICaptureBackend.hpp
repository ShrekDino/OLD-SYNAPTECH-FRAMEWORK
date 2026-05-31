#pragma once

#include "freegen/capture/ICaptureBackend.hpp"
#include <atomic>
#include <memory>
#include <thread>

namespace freegen {

class DXGICaptureBackend : public ICaptureBackend {
public:
    DXGICaptureBackend();
    ~DXGICaptureBackend() override;

    DXGICaptureBackend(const DXGICaptureBackend&) = delete;
    DXGICaptureBackend& operator=(const DXGICaptureBackend&) = delete;

    bool initialize() override;
    bool start() override;
    void stop() override;
    bool isRunning() const override { return m_running; }
    std::string name() const override { return "Windows DXGI"; }

    void setFrameCallback(FrameCallback callback) override { m_callback = std::move(callback); }

    std::vector<std::string> listSources() const override;
    bool selectSource(const std::string& sourceId) override;

    uint32_t captureWidth() const override { return m_width; }
    uint32_t captureHeight() const override { return m_height; }

private:
    void captureThread();

    std::thread m_thread;
    std::atomic<bool> m_running{false};
    FrameCallback m_callback;
    uint32_t m_width = 0;
    uint32_t m_height = 0;
    std::string m_sourceId;

    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace freegen
