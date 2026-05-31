#include "freegen/render/ComputePipeline.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/core/ShaderModule.hpp"

namespace freegen {

ComputePipeline::ComputePipeline(const Device& device,
                                 const ShaderModule& compShader,
                                 std::span<const vk::DescriptorSetLayout> layouts)
    : m_device(&device) {
    auto compStage = compShader.stageCreateInfo(vk::ShaderStageFlagBits::eCompute);

    vk::PipelineLayoutCreateInfo layoutInfo{
        .setLayoutCount = static_cast<uint32_t>(layouts.size()),
        .pSetLayouts = layouts.data()
    };

    m_pipelineLayout = device.logical().createPipelineLayoutUnique(layoutInfo);

    vk::ComputePipelineCreateInfo pipelineInfo{
        .stage = compStage,
        .layout = m_pipelineLayout.get()
    };

    m_pipeline = device.logical().createComputePipelineUnique(nullptr, pipelineInfo).value;
}

ComputePipeline::~ComputePipeline() = default;

void ComputePipeline::bind(vk::CommandBuffer cmd) const {
    cmd.bindPipeline(vk::PipelineBindPoint::eCompute, m_pipeline.get());
}

void ComputePipeline::dispatch(vk::CommandBuffer cmd, const ComputeDispatchConfig& config) const {
    cmd.dispatch(config.groupCountX, config.groupCountY, config.groupCountZ);
}

} // namespace freegen
