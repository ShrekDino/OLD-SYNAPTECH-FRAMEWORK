#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <vector>

namespace freegen {

class Device;

class CommandPool {
public:
    CommandPool(const Device& device, uint32_t queueFamilyIndex);
    ~CommandPool();

    CommandPool(const CommandPool&) = delete;
    CommandPool& operator=(const CommandPool&) = delete;
    CommandPool(CommandPool&&) = default;
    CommandPool& operator=(CommandPool&&) = default;

    vk::CommandPool handle() const { return *m_pool; }
    vk::CommandBuffer allocateBuffer(vk::CommandBufferLevel level = vk::CommandBufferLevel::ePrimary) const;
    std::vector<vk::CommandBuffer> allocateBuffers(uint32_t count, vk::CommandBufferLevel level = vk::CommandBufferLevel::ePrimary) const;
    void freeBuffer(vk::CommandBuffer buffer) const;
    void reset() const;

private:
    const Device* m_device;
    vk::UniqueCommandPool m_pool;
};

} // namespace freegen
