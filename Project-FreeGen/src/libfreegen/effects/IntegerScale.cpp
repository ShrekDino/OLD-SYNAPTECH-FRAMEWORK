#include "freegen/effects/IntegerScale.hpp"
#include <spdlog/spdlog.h>
#include <imgui.h>

namespace freegen {

void IntegerScale::init(const EffectInitInfo& info) {
    m_device = static_cast<const Device*>(info.device);
    m_descriptorSetLayout = info.descriptorSetLayout;

    auto shaderBase = std::filesystem::path("shaders");

    try {
        m_shader = std::make_unique<ShaderModule>(*m_device, shaderBase / "integer_scale.comp.spv");
        m_pipeline = std::make_unique<ComputePipeline>(*m_device, *m_shader,
            std::vector{info.descriptorSetLayout});

        m_params = {
            {"Scale", "Integer scale factor", EffectParamType::IntRange, 1.0f, 6.0f, 2.0f, 2.0f}
        };

        m_initialized = true;
        spdlog::info("IntegerScale initialized");
    } catch (const std::exception& e) {
        spdlog::error("Failed to initialize IntegerScale: {}", e.what());
        m_initialized = false;
    }
}

void IntegerScale::shutdown() {
    m_pipeline.reset();
    m_shader.reset();
    m_initialized = false;
}

void IntegerScale::process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) {
    if (!m_initialized) {
        output = {input.inputImage, input.inputExtent, false};
        return;
    }

    PushConstants pc{
        .scaleFactor = m_params[0].currentValue,
        .inputWidth = static_cast<float>(input.inputExtent.width),
        .inputHeight = static_cast<float>(input.inputExtent.height)
    };

    m_pipeline->bind(cmd);
    cmd.pushConstants(m_pipeline->layout(),
                      vk::ShaderStageFlagBits::eCompute, 0,
                      sizeof(PushConstants), &pc);

    uint32_t groupX = (input.outputExtent.width + 15) / 16;
    uint32_t groupY = (input.outputExtent.height + 15) / 16;
    m_pipeline->dispatch(cmd, {groupX, groupY, 1});

    output = {input.outputImage, input.outputExtent, true};
}

void IntegerScale::setParameter(std::string_view name, float value) {
    for (auto& param : m_params) {
        if (param.name == name) {
            param.currentValue = std::clamp(value, param.minValue, param.maxValue);
            return;
        }
    }
}

float IntegerScale::getParameter(std::string_view name) const {
    for (const auto& param : m_params) {
        if (param.name == name) return param.currentValue;
    }
    return 0.0f;
}

void IntegerScale::drawSettingsUI() {
    if (!m_initialized) {
        ImGui::TextDisabled("Integer Scale failed to initialize");
        return;
    }

    int scale = static_cast<int>(m_params[0].currentValue);
    if (ImGui::SliderInt("Scale Factor", &scale, 1, 6)) {
        m_params[0].currentValue = static_cast<float>(scale);
    }
    ImGui::TextDisabled("Nearest-neighbor integer scaling");
}

} // namespace freegen
