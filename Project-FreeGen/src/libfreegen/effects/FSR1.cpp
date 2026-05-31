#include "freegen/effects/FSR1.hpp"
#include <spdlog/spdlog.h>
#include <imgui.h>

namespace freegen {

void FSR1::init(const EffectInitInfo& info) {
    m_device = static_cast<const Device*>(info.device);
    m_descriptorSetLayout = info.descriptorSetLayout;

    auto shaderBase = std::filesystem::path("shaders");

    try {
        m_easuShader = std::make_unique<ShaderModule>(*m_device, shaderBase / "fsr_easu.comp.spv");
        m_easuPipeline = std::make_unique<ComputePipeline>(*m_device, *m_easuShader,
            std::vector{info.descriptorSetLayout});

        m_rcasShader = std::make_unique<ShaderModule>(*m_device, shaderBase / "fsr_rcas.comp.spv");
        m_rcasPipeline = std::make_unique<ComputePipeline>(*m_device, *m_rcasShader,
            std::vector{info.descriptorSetLayout});

        m_params = {
            {"Sharpness", "RCAS sharpening strength", EffectParamType::FloatRange, 0.0f, 2.0f, 0.5f, 0.5f}
        };

        m_initialized = true;
        spdlog::info("FSR 1.0 initialized");
    } catch (const std::exception& e) {
        spdlog::error("Failed to initialize FSR 1.0: {}", e.what());
        m_initialized = false;
    }
}

void FSR1::shutdown() {
    m_easuPipeline.reset();
    m_rcasPipeline.reset();
    m_easuShader.reset();
    m_rcasShader.reset();
    m_initialized = false;
}

void FSR1::process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) {
    if (!m_initialized) {
        output = {input.inputImage, input.inputExtent, false};
        return;
    }

    PushConstants easuPC{
        .inputWidth = static_cast<float>(input.inputExtent.width),
        .inputHeight = static_cast<float>(input.inputExtent.height),
        .outputWidth = static_cast<float>(input.outputExtent.width),
        .outputHeight = static_cast<float>(input.outputExtent.height),
        .sharpness = m_params[0].currentValue
    };

    m_easuPipeline->bind(cmd);
    cmd.pushConstants(m_easuPipeline->layout(),
                      vk::ShaderStageFlagBits::eCompute, 0,
                      sizeof(PushConstants), &easuPC);

    uint32_t groupX = (input.outputExtent.width + 15) / 16;
    uint32_t groupY = (input.outputExtent.height + 15) / 16;
    m_easuPipeline->dispatch(cmd, {groupX, groupY, 1});

    if (m_params[0].currentValue > 0.0f) {
        PushConstants rcasPC{
            .inputWidth = static_cast<float>(input.outputExtent.width),
            .inputHeight = static_cast<float>(input.outputExtent.height),
            .outputWidth = static_cast<float>(input.outputExtent.width),
            .outputHeight = static_cast<float>(input.outputExtent.height),
            .sharpness = m_params[0].currentValue
        };

        m_rcasPipeline->bind(cmd);
        cmd.pushConstants(m_rcasPipeline->layout(),
                          vk::ShaderStageFlagBits::eCompute, 0,
                          sizeof(PushConstants), &rcasPC);
        m_rcasPipeline->dispatch(cmd, {groupX, groupY, 1});
    }

    output = {input.outputImage, input.outputExtent, true};
}

void FSR1::setParameter(std::string_view name, float value) {
    for (auto& param : m_params) {
        if (param.name == name) {
            param.currentValue = std::clamp(value, param.minValue, param.maxValue);
            return;
        }
    }
}

float FSR1::getParameter(std::string_view name) const {
    for (const auto& param : m_params) {
        if (param.name == name) return param.currentValue;
    }
    return 0.0f;
}

void FSR1::drawSettingsUI() {
    if (!m_initialized) {
        ImGui::TextDisabled("FSR 1.0 failed to initialize");
        return;
    }

    ImGui::SliderFloat("Sharpness", &m_params[0].currentValue,
                       m_params[0].minValue, m_params[0].maxValue,
                       "%.2f");
    ImGui::TextDisabled("EASU + RCAS compute upscaling");
}

} // namespace freegen
