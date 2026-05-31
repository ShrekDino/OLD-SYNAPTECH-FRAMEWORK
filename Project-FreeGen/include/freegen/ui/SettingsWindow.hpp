#pragma once

#include <memory>
#include <string>
#include <vector>

namespace freegen {

class EffectManager;
struct AppConfig;

class SettingsWindow {
public:
    struct UpscaleSettings {
        std::string mode = "Off";
        float sharpness = 0.5f;
        float scaleFactor = 2.0f;
        bool integerScaling = false;
    };

    struct FrameGenSettings {
        bool enabled = false;
        float quality = 0.5f;
        bool vsync = true;
    };

    struct CaptureSettings {
        std::string source;
        uint32_t fps = 60;
    };

    struct DisplaySettings {
        float fps = 60.0f;
        bool showFps = true;
        bool showOverlay = true;
    };

    SettingsWindow();
    ~SettingsWindow() = default;

    void setEffectManager(EffectManager* manager) { m_effectManager = manager; }
    void setAppConfig(AppConfig* config) { m_appConfig = config; }

    void draw();

    UpscaleSettings& upscale() { return m_upscale; }
    FrameGenSettings& frameGen() { return m_frameGen; }
    CaptureSettings& capture() { return m_capture; }
    DisplaySettings& display() { return m_display; }

    const UpscaleSettings& upscale() const { return m_upscale; }
    const FrameGenSettings& frameGen() const { return m_frameGen; }
    const CaptureSettings& capture() const { return m_capture; }
    const DisplaySettings& display() const { return m_display; }

private:
    void drawUpscaleSection();
    void drawFrameGenSection();
    void drawCaptureSection();
    void drawDisplaySection();
    void drawEffectsBrowser();

    EffectManager* m_effectManager = nullptr;
    AppConfig* m_appConfig = nullptr;
    UpscaleSettings m_upscale;
    FrameGenSettings m_frameGen;
    CaptureSettings m_capture;
    DisplaySettings m_display;
};

} // namespace freegen
