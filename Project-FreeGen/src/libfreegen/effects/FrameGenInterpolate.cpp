#include "freegen/effects/FrameGenInterpolate.hpp"
#include <spdlog/spdlog.h>
#include <imgui.h>

namespace freegen {

void FrameGenInterpolate::init(const EffectInitInfo& info) {
    m_device = static_cast<const Device*>(info.device);
    m_descriptorSetLayout = info.descriptorSetLayout;

    auto shaderBase = std::filesystem::path("shaders");

    try {
        m_shader = std::make_unique<ShaderModule>(*m_device, shaderBase / "frame_interpolate.comp.spv");
        m_pipeline = std::make_unique<ComputePipeline>(*m_device, *m_shader,
            std::vector{info.descriptorSetLayout});

        m_params = {
            {"Quality", "Interpolation quality / blend factor", EffectParamType::FloatRange, 0.0f, 1.0f, 0.5f, 0.5f}
        };

        m_initialized = true;
        spdlog::info("FrameGenInterpolate initialized");
    } catch (const std::exception& e) {
        spdlog::error("Failed to initialize FrameGenInterpolate: {}", e.what());
        m_initialized = false;
    }
}

void FrameGenInterpolate::shutdown() {
    m_pipeline.reset();
    m_shader.reset();
    m_initialized = false;
}

void FrameGenInterpolate::process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) {
    if (!m_initialized) {
        output = {input.inputImage, input.inputExtent, false};
        return;
    }

    PushConstants pc{
        .inputWidth = input.inputExtent.width,
        .inputHeight = input.inputExtent.height,
        .blendFactor = m_params[0].currentValue,
        .frameIndex = m_frameIndex++
    };

    m_pipeline->bind(cmd);
    cmd.pushConstants(m_pipeline->layout(),
                      vk::ShaderStageFlagBits::eCompute, 0,
                      sizeof(PushConstants), &pc);

    auto groupX = (input.outputExtent.width + 15) / 16;
    auto groupY = (input.outputExtent.height + 15) / 16;
    m_pipeline->dispatch(cmd, {groupX, groupY, 1});

    output = {input.outputImage, input.outputExtent, true};
}

void FrameGenInterpolate::setParameter(std::string_view name, float value) {
    for (auto& param : m_params) {
        if (param.name == name) {
            param.currentValue = std::clamp(value, param.minValue, param.maxValue);
            return;
        }
    }
}

float FrameGenInterpolate::getParameter(std::string_view name) const {
    for (const auto& param : m_params) {
        if (param.name == name) return param.currentValue;
    }
    return 0.0f;
}

void FrameGenInterpolate::drawSettingsUI() {
    if (!m_initialized) {
        ImGui::TextDisabled("Frame Interpolation failed to initialize");
        return;
    }

    ImGui::SliderFloat("Blend Factor", &m_params[0].currentValue, 0.0f, 1.0f, "%.2f");
    ImGui::TextDisabled("Generates interpolated frames between captures");
}

} // namespace freegen
