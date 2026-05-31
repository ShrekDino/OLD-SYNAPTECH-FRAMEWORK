#include "freegen/render/TextureManager.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/core/CommandPool.hpp"
#include <cstring>
#include <spdlog/spdlog.h>

namespace freegen {

TextureManager::TextureManager(const Device& device, const CommandPool& commandPool)
    : m_device(&device), m_commandPool(&commandPool) {}

TextureManager::~TextureManager() = default;

TextureManager::Texture TextureManager::createTexture(const TextureInfo& info) {
    Texture tex;
    tex.info = info;

    vk::ImageCreateInfo imageInfo{
        .imageType = vk::ImageType::e2D,
        .format = info.format,
        .extent = {info.extent.width, info.extent.height, 1},
        .mipLevels = 1,
        .arrayLayers = 1,
        .samples = vk::SampleCountFlagBits::e1,
        .tiling = vk::ImageTiling::eOptimal,
        .usage = info.usage,
        .initialLayout = info.initialLayout
    };

    tex.image = m_device->logical().createImageUnique(imageInfo);

    auto memRequirements = m_device->logical().getImageMemoryRequirements(tex.image.get());
    uint32_t memoryType = m_device->findMemoryType(memRequirements.memoryTypeBits, info.memoryProps);

    tex.memory = m_device->logical().allocateMemoryUnique(vk::MemoryAllocateInfo{
        .allocationSize = memRequirements.size,
        .memoryTypeIndex = memoryType
    });

    m_device->logical().bindImageMemory(tex.image.get(), tex.memory.get(), 0);

    tex.view = m_device->logical().createImageViewUnique(vk::ImageViewCreateInfo{
        .image = tex.image.get(),
        .viewType = vk::ImageViewType::e2D,
        .format = info.format,
        .subresourceRange = {
            .aspectMask = vk::ImageAspectFlagBits::eColor,
            .baseMipLevel = 0,
            .levelCount = 1,
            .baseArrayLayer = 0,
            .layerCount = 1
        }
    });

    tex.sampler = createSampler(*m_device);

    return tex;
}

void TextureManager::destroyTexture(Texture& texture) {
    if (texture.image) {
        m_device->logical().waitIdle();
    }
    texture.sampler.reset();
    texture.view.reset();
    texture.memory.reset();
    texture.image.reset();
}

StagingBuffer TextureManager::createStagingBuffer(vk::DeviceSize size) {
    StagingBuffer staging;
    staging.size = size;

    staging.buffer = m_device->logical().createBufferUnique(vk::BufferCreateInfo{
        .size = size,
        .usage = vk::BufferUsageFlagBits::eTransferSrc,
        .sharingMode = vk::SharingMode::eExclusive
    });

    auto memRequirements = m_device->logical().getBufferMemoryRequirements(staging.buffer.get());
    uint32_t memoryType = m_device->findMemoryType(
        memRequirements.memoryTypeBits,
        vk::MemoryPropertyFlagBits::eHostVisible |
        vk::MemoryPropertyFlagBits::eHostCoherent);

    staging.memory = m_device->logical().allocateMemoryUnique(vk::MemoryAllocateInfo{
        .allocationSize = memRequirements.size,
        .memoryTypeIndex = memoryType
    });

    m_device->logical().bindBufferMemory(staging.buffer.get(), staging.memory.get(), 0);
    staging.mappedData = m_device->logical().mapMemory(staging.memory.get(), 0, size);

    return staging;
}

void TextureManager::destroyStagingBuffer(StagingBuffer& buffer) {
    if (buffer.mappedData) {
        m_device->logical().unmapMemory(buffer.memory.get());
    }
    buffer.memory.reset();
    buffer.buffer.reset();
    buffer.mappedData = nullptr;
}

void TextureManager::uploadToTexture(vk::CommandBuffer cmd, Texture& texture,
                                     const StagingBuffer& staging, vk::Extent2D extent) {
    transitionLayout(cmd, texture.image.get(),
                     vk::ImageLayout::eUndefined,
                     vk::ImageLayout::eTransferDstOptimal);
    copyBufferToImage(cmd, staging.buffer.get(), texture.image.get(), extent);
    transitionLayout(cmd, texture.image.get(),
                     vk::ImageLayout::eTransferDstOptimal,
                     vk::ImageLayout::eShaderReadOnlyOptimal);
}

void TextureManager::transitionLayout(vk::CommandBuffer cmd, vk::Image image,
                                      vk::ImageLayout oldLayout, vk::ImageLayout newLayout,
                                      vk::ImageAspectFlags aspect) {
    vk::ImageMemoryBarrier barrier{
        .oldLayout = oldLayout,
        .newLayout = newLayout,
        .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .image = image,
        .subresourceRange = {aspect, 0, 1, 0, 1}
    };

    vk::PipelineStageFlags srcStage;
    vk::PipelineStageFlags dstStage;

    if (oldLayout == vk::ImageLayout::eUndefined &&
        newLayout == vk::ImageLayout::eTransferDstOptimal) {
        barrier.srcAccessMask = vk::AccessFlagBits::eNone;
        barrier.dstAccessMask = vk::AccessFlagBits::eTransferWrite;
        srcStage = vk::PipelineStageFlagBits::eTopOfPipe;
        dstStage = vk::PipelineStageFlagBits::eTransfer;
    } else if (oldLayout == vk::ImageLayout::eTransferDstOptimal &&
               newLayout == vk::ImageLayout::eShaderReadOnlyOptimal) {
        barrier.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
        barrier.dstAccessMask = vk::AccessFlagBits::eShaderRead;
        srcStage = vk::PipelineStageFlagBits::eTransfer;
        dstStage = vk::PipelineStageFlagBits::eFragmentShader;
    } else if (oldLayout == vk::ImageLayout::eUndefined &&
               newLayout == vk::ImageLayout::eGeneral) {
        barrier.srcAccessMask = vk::AccessFlagBits::eNone;
        barrier.dstAccessMask = vk::AccessFlagBits::eShaderWrite;
        srcStage = vk::PipelineStageFlagBits::eTopOfPipe;
        dstStage = vk::PipelineStageFlagBits::eComputeShader;
    } else if (oldLayout == vk::ImageLayout::eGeneral &&
               newLayout == vk::ImageLayout::eShaderReadOnlyOptimal) {
        barrier.srcAccessMask = vk::AccessFlagBits::eShaderWrite;
        barrier.dstAccessMask = vk::AccessFlagBits::eShaderRead;
        srcStage = vk::PipelineStageFlagBits::eComputeShader;
        dstStage = vk::PipelineStageFlagBits::eFragmentShader;
    } else {
        barrier.srcAccessMask = vk::AccessFlagBits::eNone;
        barrier.dstAccessMask = vk::AccessFlagBits::eNone;
        srcStage = vk::PipelineStageFlagBits::eAllCommands;
        dstStage = vk::PipelineStageFlagBits::eAllCommands;
    }

    cmd.pipelineBarrier(srcStage, dstStage, vk::DependencyFlags{}, {}, {}, barrier);
}

void TextureManager::copyBufferToImage(vk::CommandBuffer cmd, vk::Buffer buffer,
                                       vk::Image image, vk::Extent2D extent) {
    cmd.copyBufferToImage(buffer, image, vk::ImageLayout::eTransferDstOptimal,
                          vk::BufferImageCopy{
                              .bufferOffset = 0,
                              .bufferRowLength = 0,
                              .bufferImageHeight = 0,
                              .imageSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
                              .imageOffset = {0, 0, 0},
                              .imageExtent = {extent.width, extent.height, 1}
                          });
}

vk::UniqueSampler TextureManager::createSampler(const Device& device,
                                                 vk::Filter magFilter,
                                                 vk::SamplerAddressMode addressMode) {
    auto props = device.physical().getProperties();
    return device.logical().createSamplerUnique(vk::SamplerCreateInfo{
        .magFilter = magFilter,
        .minFilter = magFilter,
        .mipmapMode = vk::SamplerMipmapMode::eLinear,
        .addressModeU = addressMode,
        .addressModeV = addressMode,
        .addressModeW = addressMode,
        .anisotropyEnable = VK_TRUE,
        .maxAnisotropy = props.limits.maxSamplerAnisotropy,
        .compareEnable = VK_FALSE,
        .compareOp = vk::CompareOp::eAlways,
        .borderColor = vk::BorderColor::eIntOpaqueBlack
    });
}

void TextureManager::uploadCapturedFrame(const void* data, uint32_t width, uint32_t height, uint32_t bytesPerPixel) {
    vk::Extent2D extent{width, height};
    m_inputExtent = extent;

    TextureInfo info{
        .extent = extent,
        .format = bytesPerPixel == 4 ? vk::Format::eR8G8B8A8Unorm : vk::Format::eR8G8B8A8Srgb,
        .usage = vk::ImageUsageFlagBits::eSampled | vk::ImageUsageFlagBits::eTransferDst,
    };

    auto staging = createStagingBuffer(static_cast<vk::DeviceSize>(width) * height * bytesPerPixel);
    if (staging.mappedData) {
        std::memcpy(staging.mappedData, data, staging.size);
    }

    auto cmd = m_commandPool->allocateBuffer();
    cmd.begin(vk::CommandBufferBeginInfo{.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit});

    if (!m_inputTexture) {
        m_inputTexture = createTexture(info);
    }

    transitionLayout(cmd, m_inputTexture->image.get(),
                     vk::ImageLayout::eUndefined,
                     vk::ImageLayout::eTransferDstOptimal);
    copyBufferToImage(cmd, staging.buffer.get(), m_inputTexture->image.get(), extent);
    transitionLayout(cmd, m_inputTexture->image.get(),
                     vk::ImageLayout::eTransferDstOptimal,
                     vk::ImageLayout::eShaderReadOnlyOptimal);

    cmd.end();

    vk::SubmitInfo submit{
        .commandBufferCount = 1,
        .pCommandBuffers = &cmd,
    };
    m_device->graphicsQueue().submit(submit, {});
    m_device->logical().waitIdle();
    m_commandPool->freeBuffer(cmd);

    destroyStagingBuffer(staging);
}

} // namespace freegen
