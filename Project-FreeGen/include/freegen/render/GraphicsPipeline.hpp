#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <vector>

namespace freegen {

class Device;
class ShaderModule;
class Swapchain;

class GraphicsPipeline {
public:
    GraphicsPipeline(const Device& device,
                     const Swapchain& swapchain,
                     const ShaderModule& vertShader,
                     const ShaderModule& fragShader,
                     vk::DescriptorSetLayout layout = VK_NULL_HANDLE);
    ~GraphicsPipeline();

    GraphicsPipeline(const GraphicsPipeline&) = delete;
    GraphicsPipeline& operator=(const GraphicsPipeline&) = delete;
    GraphicsPipeline(GraphicsPipeline&&) = default;
    GraphicsPipeline& operator=(GraphicsPipeline&&) = default;

    vk::Pipeline handle() const { return *m_pipeline; }
    vk::PipelineLayout layout() const { return *m_pipelineLayout; }

    void bind(vk::CommandBuffer cmd) const;
    void drawFullscreenQuad(vk::CommandBuffer cmd) const;

private:
    const Device* m_device;
    vk::UniquePipelineLayout m_pipelineLayout;
    vk::UniquePipeline m_pipeline;
};

} // namespace freegen
