#include "freegen/ui/SettingsWindow.hpp"
#include "freegen/effects/EffectManager.hpp"
#include "freegen/config/ConfigManager.hpp"
#include <imgui.h>

namespace freegen {

SettingsWindow::SettingsWindow() = default;

void SettingsWindow::draw() {
    ImGui::Begin("FreeGen Settings", nullptr, ImGuiWindowFlags_AlwaysAutoResize);

    if (ImGui::CollapsingHeader("Capture", ImGuiTreeNodeFlags_DefaultOpen)) {
        drawCaptureSection();
    }
    if (ImGui::CollapsingHeader("Upscaling", ImGuiTreeNodeFlags_DefaultOpen)) {
        drawUpscaleSection();
    }
    if (ImGui::CollapsingHeader("Frame Generation", ImGuiTreeNodeFlags_DefaultOpen)) {
        drawFrameGenSection();
    }
    if (ImGui::CollapsingHeader("Display", ImGuiTreeNodeFlags_DefaultOpen)) {
        drawDisplaySection();
    }
    if (ImGui::CollapsingHeader("Effects Browser")) {
        drawEffectsBrowser();
    }

    ImGui::End();
}

void SettingsWindow::drawCaptureSection() {
    const char* modes[] = {"Auto", "Desktop", "Window"};
    static int currentMode = 0;
    ImGui::Combo("Capture Mode", &currentMode, modes, IM_ARRAYSIZE(modes));

    static char sourceBuf[256] = "";
    ImGui::InputText("Source", sourceBuf, sizeof(sourceBuf));

    int fps = static_cast<int>(m_capture.fps);
    if (ImGui::SliderInt("Capture FPS", &fps, 15, 240)) {
        m_capture.fps = static_cast<uint32_t>(fps);
    }
}

void SettingsWindow::drawUpscaleSection() {
    const char* upscalers[] = {"Off", "FSR 1.0", "Integer Scale", "Passthrough"};
    int current = 0;
    if (m_upscale.mode == "FSR 1.0") current = 1;
    else if (m_upscale.mode == "Integer") current = 2;
    else if (m_upscale.mode == "Passthrough") current = 3;

    if (ImGui::Combo("Mode", &current, upscalers, IM_ARRAYSIZE(upscalers))) {
        switch (current) {
        case 0: m_upscale.mode = "Off"; break;
        case 1: m_upscale.mode = "FSR 1.0"; break;
        case 2: m_upscale.mode = "Integer"; break;
        case 3: m_upscale.mode = "Passthrough"; break;
        }
    }

    if (m_upscale.mode == "FSR 1.0") {
        ImGui::SliderFloat("Sharpness", &m_upscale.sharpness, 0.0f, 2.0f, "%.2f");
    } else if (m_upscale.mode == "Integer") {
        float scale = m_upscale.scaleFactor;
        if (ImGui::SliderFloat("Scale", &scale, 1.0f, 6.0f, "%.0fx")) {
            m_upscale.scaleFactor = scale;
        }
    }
}

void SettingsWindow::drawFrameGenSection() {
    ImGui::Checkbox("Enable Frame Generation", &m_frameGen.enabled);

    if (m_frameGen.enabled) {
        ImGui::SliderFloat("Quality", &m_frameGen.quality, 0.0f, 1.0f, "%.2f");
        ImGui::TextDisabled("Generates interpolated frames to boost perceived FPS");
    }
}

void SettingsWindow::drawDisplaySection() {
    float fps = m_display.fps;
    if (ImGui::SliderFloat("Target FPS", &fps, 15.0f, 360.0f, "%.0f")) {
        m_display.fps = fps;
    }

    ImGui::Checkbox("Show FPS", &m_display.showFps);
    ImGui::Checkbox("Show Overlay", &m_display.showOverlay);
}

void SettingsWindow::drawEffectsBrowser() {
    if (!m_effectManager) {
        ImGui::TextDisabled("No effect manager available");
        return;
    }

    auto effects = m_effectManager->allEffects();
    for (auto* effect : effects) {
        if (ImGui::TreeNode(effect->name().data())) {
            ImGui::TextDisabled("%s", effect->description().data());

            std::string_view cat;
            switch (effect->category()) {
            case EffectCategory::Upscale: cat = "Upscale"; break;
            case EffectCategory::FrameGen: cat = "FrameGen"; break;
            case EffectCategory::Filter: cat = "Filter"; break;
            case EffectCategory::PreProcess: cat = "PreProcess"; break;
            }
            ImGui::Text("Category: %s", cat.data());

            effect->drawSettingsUI();
            ImGui::TreePop();
        }
    }
}

} // namespace freegen
