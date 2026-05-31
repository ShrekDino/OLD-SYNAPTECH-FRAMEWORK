#pragma once

#include "freegen/effects/IEffect.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/render/ComputePipeline.hpp"
#include "freegen/core/ShaderModule.hpp"
#include <memory>

namespace freegen {

class IntegerScale : public IEffect {
public:
    IntegerScale() = default;
    ~IntegerScale() override = default;

    std::string_view name() const override { return "Integer Scale"; }
    std::string_view description() const override { return "Nearest-neighbor integer scaling"; }
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
        float scaleFactor;
        float inputWidth;
        float inputHeight;
    };

    std::unique_ptr<ComputePipeline> m_pipeline;
    std::unique_ptr<ShaderModule> m_shader;
    vk::DescriptorSetLayout m_descriptorSetLayout;

    const Device* m_device = nullptr;
    std::vector<EffectParam> m_params;
    bool m_initialized = false;
};

} // namespace freegen
