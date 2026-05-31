#pragma once

#include <vulkan/vulkan.hpp>
#include <cstdint>
#include <memory>
#include <optional>
#include <vector>

namespace freegen {

class Device;
class CommandPool;

struct TextureInfo {
    vk::Extent2D extent;
    vk::Format format = vk::Format::eR8G8B8A8Unorm;
    vk::ImageUsageFlags usage = vk::ImageUsageFlagBits::eSampled |
                                vk::ImageUsageFlagBits::eStorage |
                                vk::ImageUsageFlagBits::eTransferDst;
    vk::ImageLayout initialLayout = vk::ImageLayout::eUndefined;
    vk::MemoryPropertyFlags memoryProps = vk::MemoryPropertyFlagBits::eDeviceLocal;
};

struct StagingBuffer {
    vk::UniqueBuffer buffer;
    vk::UniqueDeviceMemory memory;
    void* mappedData = nullptr;
    vk::DeviceSize size = 0;
};

class TextureManager {
public:
    TextureManager(const Device& device, const CommandPool& commandPool);
    ~TextureManager();

    TextureManager(const TextureManager&) = delete;
    TextureManager& operator=(const TextureManager&) = delete;
    TextureManager(TextureManager&&) = default;
    TextureManager& operator=(TextureManager&&) = default;

    struct Texture {
        vk::UniqueImage image;
        vk::UniqueDeviceMemory memory;
        vk::UniqueImageView view;
        vk::UniqueSampler sampler;
        TextureInfo info;
    };

    Texture createTexture(const TextureInfo& info);
    void destroyTexture(Texture& texture);

    StagingBuffer createStagingBuffer(vk::DeviceSize size);
    void destroyStagingBuffer(StagingBuffer& buffer);

    void uploadToTexture(vk::CommandBuffer cmd, Texture& texture,
                         const StagingBuffer& staging,
                         vk::Extent2D extent);

    void transitionLayout(vk::CommandBuffer cmd, vk::Image image,
                          vk::ImageLayout oldLayout, vk::ImageLayout newLayout,
                          vk::ImageAspectFlags aspect = vk::ImageAspectFlagBits::eColor);

    void copyBufferToImage(vk::CommandBuffer cmd, vk::Buffer buffer,
                           vk::Image image, vk::Extent2D extent);

    const Device& device() const { return *m_device; }

    static vk::UniqueSampler createSampler(const Device& device,
                                            vk::Filter magFilter = vk::Filter::eLinear,
                                            vk::SamplerAddressMode addressMode = vk::SamplerAddressMode::eClampToEdge);

    void uploadCapturedFrame(const void* data, uint32_t width, uint32_t height, uint32_t bytesPerPixel);
    vk::ImageView inputView() const { return m_inputTexture ? m_inputTexture->view.get() : VK_NULL_HANDLE; }
    vk::Extent2D inputExtent() const { return m_inputExtent; }
    bool hasInput() const { return m_inputTexture.has_value(); }

private:
    const Device* m_device;
    const CommandPool* m_commandPool;

    std::optional<Texture> m_inputTexture;
    vk::Extent2D m_inputExtent{};
};

} // namespace freegen
