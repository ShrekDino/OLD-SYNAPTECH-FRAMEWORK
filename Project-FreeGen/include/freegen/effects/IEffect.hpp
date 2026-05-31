#pragma once

#include <vulkan/vulkan.hpp>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace freegen {

enum class EffectCategory {
    Upscale,
    FrameGen,
    Filter,
    PreProcess
};

enum class EffectParamType {
    Float,
    Int,
    Bool,
    FloatRange,
    IntRange,
    Enum
};

struct EffectParam {
    std::string name;
    std::string description;
    EffectParamType type = EffectParamType::Float;
    float minValue = 0.0f;
    float maxValue = 1.0f;
    float defaultValue = 0.0f;
    float currentValue = 0.0f;
    std::vector<std::string> enumValues;
};

struct EffectInput {
    vk::ImageView inputImage;
    vk::Extent2D inputExtent;
    vk::Format format = vk::Format::eR8G8B8A8Unorm;
    uint32_t frameCount = 0;
    vk::ImageView previousFrame = VK_NULL_HANDLE;

    // For compute effects: output image
    vk::ImageView outputImage = VK_NULL_HANDLE;
    vk::Extent2D outputExtent{};
};

struct EffectOutput {
    vk::ImageView outputImage;
    vk::Extent2D outputExtent;
    bool modified = false;
};

struct EffectInitInfo {
    const class Device* device;
    vk::DescriptorPool descriptorPool;
    vk::DescriptorSetLayout descriptorSetLayout;
    uint32_t maxFramesInFlight = 3;
};

class IEffect {
public:
    virtual ~IEffect() = default;

    virtual std::string_view name() const = 0;
    virtual std::string_view description() const = 0;
    virtual EffectCategory category() const = 0;

    virtual bool supportsInputFormat(vk::Format format) const { return format == vk::Format::eR8G8B8A8Unorm; }

    virtual void init(const EffectInitInfo& info) = 0;
    virtual void shutdown() = 0;

    virtual void process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) = 0;

    virtual std::span<EffectParam> parameters() { return {}; }
    virtual void setParameter(std::string_view name, float value) {}
    virtual float getParameter(std::string_view name) const { return 0.0f; }

    virtual void drawSettingsUI() {}
};

} // namespace freegen
