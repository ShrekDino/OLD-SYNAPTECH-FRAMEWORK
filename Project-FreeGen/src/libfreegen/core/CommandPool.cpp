#include "freegen/core/CommandPool.hpp"
#include "freegen/core/Device.hpp"

namespace freegen {

CommandPool::CommandPool(const Device& device, uint32_t queueFamilyIndex)
    : m_device(&device) {
    m_pool = device.logical().createCommandPoolUnique(vk::CommandPoolCreateInfo{
        .flags = vk::CommandPoolCreateFlagBits::eResetCommandBuffer,
        .queueFamilyIndex = queueFamilyIndex
    });
}

CommandPool::~CommandPool() = default;

vk::CommandBuffer CommandPool::allocateBuffer(vk::CommandBufferLevel level) const {
    return m_device->logical().allocateCommandBuffers(vk::CommandBufferAllocateInfo{
        .commandPool = m_pool.get(),
        .level = level,
        .commandBufferCount = 1
    })[0];
}

std::vector<vk::CommandBuffer> CommandPool::allocateBuffers(uint32_t count, vk::CommandBufferLevel level) const {
    return m_device->logical().allocateCommandBuffers(vk::CommandBufferAllocateInfo{
        .commandPool = m_pool.get(),
        .level = level,
        .commandBufferCount = count
    });
}

void CommandPool::freeBuffer(vk::CommandBuffer buffer) const {
    m_device->logical().freeCommandBuffers(m_pool.get(), buffer);
}

void CommandPool::reset() const {
    m_device->logical().resetCommandPool(m_pool.get());
}

} // namespace freegen
