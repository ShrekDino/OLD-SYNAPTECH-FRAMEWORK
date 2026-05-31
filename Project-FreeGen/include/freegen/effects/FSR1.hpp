#pragma once

#include "freegen/effects/IEffect.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/render/ComputePipeline.hpp"
#include "freegen/core/ShaderModule.hpp"
#include <memory>

namespace freegen {

class FSR1 : public IEffect {
public:
    FSR1() = default;
    ~FSR1() override = default;

    std::string_view name() const override { return "FSR 1.0"; }
    std::string_view description() const override { return "AMD FidelityFX Super Resolution 1.0 (EASU + RCAS)"; }
    EffectCategory category() const override { return EffectCategory::Upscale; }

    void init(const EffectInitInfo& info) override;
    void shutdown() override;

    void process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) override;

    std::span<EffectParam> parameters() override { return m_params; }
    void setParameter(std::string_view name, float value) override;
    float getParameter(std::string_view name) const override;

    void drawSettingsUI() override;

private:
    struct PushConstants {
        float inputWidth;
        float inputHeight;
        float outputWidth;
        float outputHeight;
        float sharpness;
    };

    std::unique_ptr<ComputePipeline> m_easuPipeline;
    std::unique_ptr<ComputePipeline> m_rcasPipeline;
    std::unique_ptr<ShaderModule> m_easuShader;
    std::unique_ptr<ShaderModule> m_rcasShader;

    vk::DescriptorSetLayout m_descriptorSetLayout;
    vk::DescriptorSet m_descriptorSet;

    const Device* m_device = nullptr;
    std::vector<EffectParam> m_params;

    bool m_initialized = false;
};

} // namespace freegen
