#include "freegen/render/Compositor.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/core/Swapchain.hpp"
#include "freegen/core/CommandPool.hpp"
#include "freegen/core/ShaderModule.hpp"
#include "freegen/render/TextureManager.hpp"
#include "freegen/render/GraphicsPipeline.hpp"
#include "freegen/effects/IEffect.hpp"
#include <spdlog/spdlog.h>

namespace freegen {

Compositor::Compositor(const Device& device,
                       Swapchain& swapchain,
                       const CommandPool& commandPool,
                       TextureManager& textureManager)
    : m_device(&device),
      m_swapchain(&swapchain),
      m_commandPool(&commandPool),
      m_textureManager(&textureManager) {}

Compositor::~Compositor() {
    shutdown();
}

void Compositor::init() {
    auto shaderBase = std::filesystem::path("shaders");
    m_vertShader = std::make_unique<ShaderModule>(
        *m_device, shaderBase / "fullscreen.vert.spv");
    m_fragShader = std::make_unique<ShaderModule>(
        *m_device, shaderBase / "texture.frag.spv");

    vk::DescriptorSetLayoutBinding samplerBinding{
        .binding = 0,
        .descriptorType = vk::DescriptorType::eCombinedImageSampler,
        .descriptorCount = 1,
        .stageFlags = vk::ShaderStageFlagBits::eFragment
    };

    m_descriptorSetLayout = m_device->logical().createDescriptorSetLayoutUnique(
        vk::DescriptorSetLayoutCreateInfo{
            .bindingCount = 1,
            .pBindings = &samplerBinding
        });

    m_descriptorPool = m_device->logical().createDescriptorPoolUnique(
        vk::DescriptorPoolCreateInfo{
            .poolSizeCount = 1,
            .pPoolSizes = &vk::DescriptorPoolSize{
                vk::DescriptorType::eCombinedImageSampler, 1
            },
            .maxSets = 1
        });

    auto descriptorSets = m_device->logical().allocateDescriptorSetsUnique(
        vk::DescriptorSetAllocateInfo{
            .descriptorPool = m_descriptorPool.get(),
            .descriptorSetLayoutCount = 1,
            .pSetLayouts = &m_descriptorSetLayout.get()
        });
    m_descriptorSet = std::move(descriptorSets[0]);

    m_graphicsPipeline = std::make_unique<GraphicsPipeline>(
        *m_device, *m_swapchain, *m_vertShader, *m_fragShader,
        m_descriptorSetLayout.get());

    createSyncObjects();
}

void Compositor::shutdown() {
    if (m_device) {
        m_device->logical().waitIdle();
    }
    m_frames.clear();
    m_graphicsPipeline.reset();
    m_fragShader.reset();
    m_vertShader.reset();
}

void Compositor::createSyncObjects() {
    uint32_t imageCount = m_swapchain->imageCount();
    m_frames.resize(imageCount);

    for (auto& frame : m_frames) {
        frame.imageAvailable = m_device->logical().createSemaphoreUnique(
            vk::SemaphoreCreateInfo{});
        frame.renderFinished = m_device->logical().createSemaphoreUnique(
            vk::SemaphoreCreateInfo{});
        frame.inFlight = m_device->logical().createFenceUnique(
            vk::FenceCreateInfo{.flags = vk::FenceCreateFlagBits::eSignaled});
        frame.commandBuffer = m_commandPool->allocateBuffer();
    }
}

void Compositor::setEffects(std::span<IEffect*> effects) {
    m_effects.assign(effects.begin(), effects.end());
}

void Compositor::setInputTexture(vk::ImageView view, vk::Extent2D extent) {
    m_inputView = view;
    m_inputExtent = extent;
    m_hasInput = true;
}

void Compositor::recreateSwapchain() {
    m_device->logical().waitIdle();
    m_frames.clear();
    m_graphicsPipeline.reset();
    m_graphicsPipeline = std::make_unique<GraphicsPipeline>(
        *m_device, *m_swapchain, *m_vertShader, *m_fragShader,
        m_descriptorSetLayout.get());
    createSyncObjects();
}

vk::CommandBuffer Compositor::beginFrame() {
    auto& frame = m_frames[m_currentFrame];
    m_device->logical().waitForFences(frame.inFlight.get(), VK_TRUE, UINT64_MAX);

    auto result = m_swapchain->acquireNextImage(
        frame.imageAvailable.get(), &m_currentFrame);

    if (result == vk::Result::eErrorOutOfDateKHR) {
        return nullptr;
    }

    m_device->logical().resetFences(frame.inFlight.get());

    frame.commandBuffer.reset();
    frame.commandBuffer.begin(vk::CommandBufferBeginInfo{
        .flags = vk::CommandBufferUsageFlagBits::eSimultaneousUse
    });

    return frame.commandBuffer;
}

void Compositor::endFrame(vk::CommandBuffer cmd) {
    auto& frame = m_frames[m_currentFrame];
    recordCommandBuffer(m_currentFrame);
    cmd.end();

    vk::PipelineStageFlags waitStage = vk::PipelineStageFlagBits::eColorAttachmentOutput;
    vk::SubmitInfo submit{
        .waitSemaphoreCount = 1,
        .pWaitSemaphores = &frame.imageAvailable.get(),
        .pWaitDstStageMask = &waitStage,
        .commandBufferCount = 1,
        .pCommandBuffers = &cmd,
        .signalSemaphoreCount = 1,
        .pSignalSemaphores = &frame.renderFinished.get()
    };

    m_device->graphicsQueue().submit(submit, frame.inFlight.get());
}

bool Compositor::present() {
    auto& frame = m_frames[m_currentFrame];
    vk::PresentInfoKHR presentInfo{
        .waitSemaphoreCount = 1,
        .pWaitSemaphores = &frame.renderFinished.get(),
        .swapchainCount = 1,
        .pSwapchains = &m_swapchain->handle(),
        .pImageIndices = &m_currentFrame
    };

    auto result = m_device->presentQueue().presentKHR(presentInfo);
    if (result == vk::Result::eErrorOutOfDateKHR ||
        result == vk::Result::eSuboptimalKHR) {
        return false;
    }

    m_currentFrame = (m_currentFrame + 1) % m_swapchain->imageCount();
    return true;
}

void Compositor::recordCommandBuffer(uint32_t imageIndex) {
    auto& frame = m_frames[imageIndex];
    auto cmd = frame.commandBuffer;

    cmd.beginRenderPass(vk::RenderPassBeginInfo{
        .renderPass = m_swapchain->renderPass(),
        .framebuffer = m_swapchain->framebuffers()[imageIndex].get(),
        .renderArea = {{0, 0}, m_swapchain->extent()},
        .clearValueCount = 1,
        .pClearValues = &vk::ClearValue{
            .color = vk::ClearColorValue{0.0f, 0.0f, 0.0f, 1.0f}
        }
    }, vk::SubpassContents::eInline);

    if (m_hasInput) {
        vk::DescriptorImageInfo imageInfo{
            .sampler = nullptr,
            .imageView = m_inputView,
            .imageLayout = vk::ImageLayout::eShaderReadOnlyOptimal
        };

        vk::WriteDescriptorSet descriptorWrite{
            .dstSet = m_descriptorSet.get(),
            .dstBinding = 0,
            .descriptorCount = 1,
            .descriptorType = vk::DescriptorType::eCombinedImageSampler,
            .pImageInfo = &imageInfo
        };

        m_device->logical().updateDescriptorSets(descriptorWrite, {});
        cmd.bindDescriptorSets(vk::PipelineBindPoint::eGraphics,
                                m_graphicsPipeline->layout(), 0,
                                m_descriptorSet.get(), {});

        m_graphicsPipeline->bind(cmd);
        m_graphicsPipeline->drawFullscreenQuad(cmd);
    }

    cmd.endRenderPass();
}

} // namespace freegen
