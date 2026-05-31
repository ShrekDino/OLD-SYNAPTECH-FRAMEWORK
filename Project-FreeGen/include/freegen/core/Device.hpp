#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace freegen {

struct QueueFamilyIndices {
    std::optional<uint32_t> graphics;
    std::optional<uint32_t> present;
    std::optional<uint32_t> compute;
    std::optional<uint32_t> transfer;

    bool IsComplete() const {
        return graphics.has_value() && present.has_value();
    }
};

struct SwapchainSupport {
    vk::SurfaceCapabilitiesKHR capabilities;
    std::vector<vk::SurfaceFormatKHR> formats;
    std::vector<vk::PresentModeKHR> presentModes;
    bool IsComplete() const {
        return !formats.empty() && !presentModes.empty();
    }
};

class Device {
public:
    Device(vk::Instance instance, vk::SurfaceKHR surface);
    ~Device();

    Device(const Device&) = delete;
    Device& operator=(const Device&) = delete;
    Device(Device&&) = delete;
    Device& operator=(Device&&) = delete;

    vk::PhysicalDevice physical() const { return m_physical; }
    vk::Device logical() const { return *m_device; }
    vk::Queue graphicsQueue() const { return m_graphicsQueue; }
    vk::Queue presentQueue() const { return m_presentQueue; }
    vk::Queue computeQueue() const { return m_computeQueue; }
    const QueueFamilyIndices& queueFamilyIndices() const { return m_queueIndices; }
    SwapchainSupport swapchainSupport(vk::SurfaceKHR surface) const;
    uint32_t findMemoryType(uint32_t filter, vk::MemoryPropertyFlags props) const;
    vk::FormatProperties getFormatProperties(vk::Format format) const;

    vk::UniqueShaderModule createShaderModule(std::span<const uint32_t> code) const;

private:
    void pickPhysicalDevice(vk::Instance instance, vk::SurfaceKHR surface);
    void createLogicalDevice(vk::SurfaceKHR surface);
    bool isDeviceSuitable(vk::PhysicalDevice device, vk::SurfaceKHR surface) const;
    bool checkExtensionSupport(vk::PhysicalDevice device) const;
    QueueFamilyIndices findQueueFamilies(vk::PhysicalDevice device, vk::SurfaceKHR surface) const;
    int rateDeviceSuitability(vk::PhysicalDevice device, vk::SurfaceKHR surface) const;

    static constexpr std::array<const char*, 1> kDeviceExtensions = {
        VK_KHR_SWAPCHAIN_EXTENSION_NAME
    };

    vk::PhysicalDevice m_physical;
    vk::UniqueDevice m_device;
    QueueFamilyIndices m_queueIndices;
    vk::Queue m_graphicsQueue;
    vk::Queue m_presentQueue;
    vk::Queue m_computeQueue;
};

} // namespace freegen
