#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <vector>

namespace freegen {

class Device;
class Swapchain;
class CommandPool;
class TextureManager;
class GraphicsPipeline;
class ShaderModule;
class IEffect;

class Compositor {
public:
    Compositor(const Device& device,
               Swapchain& swapchain,
               const CommandPool& commandPool,
               TextureManager& textureManager);
    ~Compositor();

    Compositor(const Compositor&) = delete;
    Compositor& operator=(const Compositor&) = delete;
    Compositor(Compositor&&) = default;
    Compositor& operator=(Compositor&&) = default;

    struct FrameResources {
        vk::UniqueSemaphore imageAvailable;
        vk::UniqueSemaphore renderFinished;
        vk::UniqueFence inFlight;
        vk::CommandBuffer commandBuffer;
    };

    void init();
    void shutdown();

    vk::CommandBuffer beginFrame();
    void endFrame(vk::CommandBuffer cmd);

    bool present();

    void setEffects(std::span<IEffect*> effects);
    void setInputTexture(vk::ImageView view, vk::Extent2D extent);

    void recreateSwapchain();

    FrameResources& currentFrame() { return m_frames[m_currentFrame]; }
    uint32_t currentFrameIndex() const { return m_currentFrame; }

private:
    void createSyncObjects();
    void recordCommandBuffer(uint32_t imageIndex);

    const Device* m_device;
    Swapchain* m_swapchain;
    const CommandPool* m_commandPool;
    TextureManager* m_textureManager;

    std::vector<FrameResources> m_frames;
    uint32_t m_currentFrame = 0;

    vk::UniqueDescriptorSetLayout m_descriptorSetLayout;
    vk::UniqueDescriptorPool m_descriptorPool;
    vk::UniqueDescriptorSet m_descriptorSet;

    std::unique_ptr<GraphicsPipeline> m_graphicsPipeline;
    std::unique_ptr<ShaderModule> m_vertShader;
    std::unique_ptr<ShaderModule> m_fragShader;

    std::vector<IEffect*> m_effects;
    vk::ImageView m_inputView;
    vk::Extent2D m_inputExtent{};
    bool m_hasInput = false;
};

} // namespace freegen
