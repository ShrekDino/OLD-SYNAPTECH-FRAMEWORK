#include "freegen/capture/LinuxCaptureBackend.hpp"
#include <spdlog/spdlog.h>

namespace freegen {

LinuxCaptureBackend::LinuxCaptureBackend() = default;

LinuxCaptureBackend::~LinuxCaptureBackend() {
    stop();
}

bool LinuxCaptureBackend::initialize() {
    spdlog::info("Initializing Linux Capture Backend");
    return true;
}

bool LinuxCaptureBackend::start() {
    if (m_running) return false;

    m_running = true;
    m_thread = std::thread(&LinuxCaptureBackend::captureThread, this);
    spdlog::info("Linux capture backend started");
    return true;
}

void LinuxCaptureBackend::stop() {
    if (!m_running) return;
    m_running = false;
    if (m_thread.joinable()) {
        m_thread.join();
    }
    spdlog::info("Linux capture backend stopped");
}

std::vector<std::string> LinuxCaptureBackend::listSources() const {
    return {"Desktop (Fullscreen)", "Active Window"};
}

bool LinuxCaptureBackend::selectSource(const std::string& sourceId) {
    m_sourceId = sourceId;
    return true;
}

void LinuxCaptureBackend::captureThread() {
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
