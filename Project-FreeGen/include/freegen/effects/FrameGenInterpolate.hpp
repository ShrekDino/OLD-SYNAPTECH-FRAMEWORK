#pragma once

#include "freegen/effects/IEffect.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/render/ComputePipeline.hpp"
#include "freegen/core/ShaderModule.hpp"
#include "freegen/render/TextureManager.hpp"
#include <memory>

namespace freegen {

class FrameGenInterpolate : public IEffect {
public:
    FrameGenInterpolate() = default;
    ~FrameGenInterpolate() override = default;

    std::string_view name() const override { return "Frame Interpolation"; }
    std::string_view description() const override { return "Simple motion-adaptive frame interpolation between consecutive frames"; }
    EffectCategory category() const override { return EffectCategory::FrameGen; }

    void init(const EffectInitInfo& info) override;
    void shutdown() override;

    void process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) override;

    std::span<EffectParam> parameters() override { return m_params; }
    void setParameter(std::string_view name, float value) override;
    float getParameter(std::string_view name) const override;

    void drawSettingsUI() override;

private:
    struct PushConstants {
        uint32_t inputWidth;
        uint32_t inputHeight;
        float blendFactor;
        uint32_t frameIndex;
    };

    std::unique_ptr<ComputePipeline> m_pipeline;
    std::unique_ptr<ShaderModule> m_shader;
    vk::DescriptorSetLayout m_descriptorSetLayout;

    struct FrameBuffer {
        TextureManager::Texture texture;
        bool valid = false;
    };

    std::array<FrameBuffer, 2> m_frameHistory;
    uint32_t m_frameIndex = 0;

    const Device* m_device = nullptr;
    std::vector<EffectParam> m_params;
    bool m_initialized = false;
    TextureManager* m_textureManager = nullptr;
};

} // namespace freegen
