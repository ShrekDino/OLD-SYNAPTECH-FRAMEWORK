#include "freegen/render/GraphicsPipeline.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/core/ShaderModule.hpp"
#include "freegen/core/Swapchain.hpp"

namespace freegen {

GraphicsPipeline::GraphicsPipeline(const Device& device,
                                   const Swapchain& swapchain,
                                   const ShaderModule& vertShader,
                                   const ShaderModule& fragShader,
                                   vk::DescriptorSetLayout layout)
    : m_device(&device) {
    auto vertStage = vertShader.stageCreateInfo(vk::ShaderStageFlagBits::eVertex);
    auto fragStage = fragShader.stageCreateInfo(vk::ShaderStageFlagBits::eFragment);

    vk::PipelineShaderStageCreateInfo stages[] = {vertStage, fragStage};

    vk::PipelineVertexInputStateCreateInfo vertexInput{
        .vertexBindingDescriptionCount = 0,
        .vertexAttributeDescriptionCount = 0
    };

    vk::PipelineInputAssemblyStateCreateInfo inputAssembly{
        .topology = vk::PrimitiveTopology::eTriangleStrip,
        .primitiveRestartEnable = VK_FALSE
    };

    vk::Viewport viewport{
        .x = 0.0f, .y = 0.0f,
        .width = static_cast<float>(swapchain.extent().width),
        .height = static_cast<float>(swapchain.extent().height),
        .minDepth = 0.0f, .maxDepth = 1.0f
    };

    vk::Rect2D scissor{
        .offset = {0, 0},
        .extent = swapchain.extent()
    };

    vk::PipelineViewportStateCreateInfo viewportState{
        .viewportCount = 1, .pViewports = &viewport,
        .scissorCount = 1, .pScissors = &scissor
    };

    vk::PipelineRasterizationStateCreateInfo rasterizer{
        .depthClampEnable = VK_FALSE,
        .rasterizerDiscardEnable = VK_FALSE,
        .polygonMode = vk::PolygonMode::eFill,
        .cullMode = vk::CullModeFlagBits::eNone,
        .frontFace = vk::FrontFace::eCounterClockwise,
        .depthBiasEnable = VK_FALSE,
        .lineWidth = 1.0f
    };

    vk::PipelineMultisampleStateCreateInfo multisampling{
        .rasterizationSamples = vk::SampleCountFlagBits::e1,
        .sampleShadingEnable = VK_FALSE
    };

    vk::PipelineColorBlendAttachmentState colorBlendAttachment{
        .blendEnable = VK_FALSE,
        .colorWriteMask = vk::ColorComponentFlagBits::eR |
                          vk::ColorComponentFlagBits::eG |
                          vk::ColorComponentFlagBits::eB |
                          vk::ColorComponentFlagBits::eA
    };

    vk::PipelineColorBlendStateCreateInfo colorBlending{
        .logicOpEnable = VK_FALSE,
        .logicOp = vk::LogicOp::eCopy,
        .attachmentCount = 1,
        .pAttachments = &colorBlendAttachment,
        .blendConstants = {0.0f, 0.0f, 0.0f, 0.0f}
    };

    vk::PipelineLayoutCreateInfo layoutInfo{
        .setLayoutCount = layout ? 1u : 0u,
        .pSetLayouts = layout ? &layout : nullptr
    };

    if (layout) {
        m_pipelineLayout = device.logical().createPipelineLayoutUnique(layoutInfo);
    } else {
        m_pipelineLayout = device.logical().createPipelineLayoutUnique(layoutInfo);
    }

    vk::GraphicsPipelineCreateInfo pipelineInfo{
        .stageCount = 2,
        .pStages = stages,
        .pVertexInputState = &vertexInput,
        .pInputAssemblyState = &inputAssembly,
        .pViewportState = &viewportState,
        .pRasterizationState = &rasterizer,
        .pMultisampleState = &multisampling,
        .pDepthStencilState = nullptr,
        .pColorBlendState = &colorBlending,
        .pDynamicState = nullptr,
        .layout = m_pipelineLayout.get(),
        .renderPass = swapchain.renderPass(),
        .subpass = 0
    };

    m_pipeline = device.logical().createGraphicsPipelineUnique(nullptr, pipelineInfo).value;
}

GraphicsPipeline::~GraphicsPipeline() = default;

void GraphicsPipeline::bind(vk::CommandBuffer cmd) const {
    cmd.bindPipeline(vk::PipelineBindPoint::eGraphics, m_pipeline.get());
}

void GraphicsPipeline::drawFullscreenQuad(vk::CommandBuffer cmd) const {
    cmd.draw(4, 1, 0, 0);
}

} // namespace freegen
