#include "freegen/capture/DXGICaptureBackend.hpp"
#include <spdlog/spdlog.h>

namespace freegen {

struct DXGICaptureBackend::Impl {};

DXGICaptureBackend::DXGICaptureBackend()
    : m_impl(std::make_unique<Impl>()) {}

DXGICaptureBackend::~DXGICaptureBackend() {
    stop();
}

bool DXGICaptureBackend::initialize() {
    spdlog::info("Initializing Windows DXGI Capture Backend");
    return true;
}

bool DXGICaptureBackend::start() {
    if (m_running) return false;
    m_running = true;
    m_thread = std::thread(&DXGICaptureBackend::captureThread, this);
    spdlog::info("DXGI capture backend started");
    return true;
}

void DXGICaptureBackend::stop() {
    if (!m_running) return;
    m_running = false;
    if (m_thread.joinable()) {
        m_thread.join();
    }
    spdlog::info("DXGI capture backend stopped");
}

std::vector<std::string> DXGICaptureBackend::listSources() const {
    return {"Primary Monitor", "Active Window"};
}

bool DXGICaptureBackend::selectSource(const std::string& sourceId) {
    m_sourceId = sourceId;
    return true;
}

void DXGICaptureBackend::captureThread() {
    while (m_running) {
        if (m_callback) {
            CaptureFrame frame{
                .data = nullptr,
                .width = 1920,
                .height = 1080,
                .timestamp = static_cast<uint64_t>(
                    std::chrono::duration_cast<std::chrono::microseconds>(
                        std::chrono::steady_clock::now().time_since_epoch()).count())
            };
            m_callback(frame);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(16));
    }
}

} // namespace freegen
