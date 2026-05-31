#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <vector>

namespace freegen {

class Device;
class ShaderModule;

struct ComputeDispatchConfig {
    uint32_t groupCountX = 1;
    uint32_t groupCountY = 1;
    uint32_t groupCountZ = 1;
};

class ComputePipeline {
public:
    ComputePipeline(const Device& device,
                    const ShaderModule& compShader,
                    std::span<const vk::DescriptorSetLayout> layouts = {});
    ~ComputePipeline();

    ComputePipeline(const ComputePipeline&) = delete;
    ComputePipeline& operator=(const ComputePipeline&) = delete;
    ComputePipeline(ComputePipeline&&) = default;
    ComputePipeline& operator=(ComputePipeline&&) = default;

    vk::Pipeline handle() const { return *m_pipeline; }
    vk::PipelineLayout layout() const { return *m_pipelineLayout; }

    void bind(vk::CommandBuffer cmd) const;
    void dispatch(vk::CommandBuffer cmd, const ComputeDispatchConfig& config) const;

private:
    const Device* m_device;
    vk::UniquePipelineLayout m_pipelineLayout;
    vk::UniquePipeline m_pipeline;
};

} // namespace freegen
