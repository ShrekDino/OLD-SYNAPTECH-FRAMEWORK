#include "freegen/core/Device.hpp"
#include <algorithm>
#include <map>
#include <ranges>
#include <set>
#include <spdlog/spdlog.h>

namespace freegen {

Device::Device(vk::Instance instance, vk::SurfaceKHR surface) {
    pickPhysicalDevice(instance, surface);
    createLogicalDevice(surface);
}

Device::~Device() {
    if (m_device) {
        m_device->waitIdle();
    }
}

void Device::pickPhysicalDevice(vk::Instance instance, vk::SurfaceKHR surface) {
    auto devices = instance.enumeratePhysicalDevices();
    if (devices.empty()) {
        throw std::runtime_error("No Vulkan-capable GPUs found");
    }

    std::multimap<int, vk::PhysicalDevice> candidates;
    for (const auto& device : devices) {
        int score = rateDeviceSuitability(device, surface);
        candidates.emplace(score, device);
    }

    if (candidates.rbegin()->first <= 0) {
        throw std::runtime_error("Failed to find a suitable GPU");
    }

    m_physical = candidates.rbegin()->second;

    auto props = m_physical.getProperties();
    spdlog::info("Selected GPU: {} (type: {})",
                 props.deviceName,
                 vk::to_string(props.deviceType));
}

void Device::createLogicalDevice(vk::SurfaceKHR surface) {
    m_queueIndices = findQueueFamilies(m_physical, surface);

    std::vector<vk::DeviceQueueCreateInfo> queueCreateInfos;
    std::set<uint32_t> uniqueQueueFamilies = {
        m_queueIndices.graphics.value(),
        m_queueIndices.present.value()
    };

    float queuePriority = 1.0f;
    for (uint32_t family : uniqueQueueFamilies) {
        queueCreateInfos.push_back(vk::DeviceQueueCreateInfo{
            .queueFamilyIndex = family,
            .queueCount = 1,
            .pQueuePriorities = &queuePriority
        });
    }

    vk::PhysicalDeviceFeatures deviceFeatures{
        .samplerAnisotropy = VK_TRUE,
        .shaderInt64 = VK_TRUE
    };

    vk::DeviceCreateInfo createInfo{
        .queueCreateInfoCount = static_cast<uint32_t>(queueCreateInfos.size()),
        .pQueueCreateInfos = queueCreateInfos.data(),
        .enabledExtensionCount = static_cast<uint32_t>(kDeviceExtensions.size()),
        .ppEnabledExtensionNames = kDeviceExtensions.data(),
        .pEnabledFeatures = &deviceFeatures
    };

    m_device = m_physical.createDeviceUnique(createInfo);

    m_graphicsQueue = m_device->getQueue(m_queueIndices.graphics.value(), 0);
    m_presentQueue = m_device->getQueue(m_queueIndices.present.value(), 0);

    if (m_queueIndices.compute.has_value()) {
        m_computeQueue = m_device->getQueue(m_queueIndices.compute.value(), 0);
    } else {
        m_computeQueue = m_graphicsQueue;
    }

    spdlog::info("Logical device created");
}

bool Device::isDeviceSuitable(vk::PhysicalDevice device, vk::SurfaceKHR surface) const {
    auto indices = findQueueFamilies(device, surface);
    bool extensionsSupported = checkExtensionSupport(device);
    bool swapchainAdequate = false;
    if (extensionsSupported) {
        auto support = swapchainSupport(surface);
        swapchainAdequate = !support.formats.empty() && !support.presentModes.empty();
    }
    return indices.IsComplete() && extensionsSupported && swapchainAdequate;
}

bool Device::checkExtensionSupport(vk::PhysicalDevice device) const {
    auto availableExtensions = device.enumerateDeviceExtensionProperties();
    std::set<std::string> required(kDeviceExtensions.begin(), kDeviceExtensions.end());
    for (const auto& ext : availableExtensions) {
        required.erase(ext.extensionName);
    }
    return required.empty();
}

QueueFamilyIndices Device::findQueueFamilies(vk::PhysicalDevice device, vk::SurfaceKHR surface) const {
    QueueFamilyIndices indices;
    auto families = device.getQueueFamilyProperties();

    for (uint32_t i = 0; const auto& family : families) {
        if (family.queueFlags & vk::QueueFlagBits::eGraphics) {
            indices.graphics = i;
        }
        if (surface && device.getSurfaceSupportKHR(i, surface)) {
            indices.present = i;
        }
        if (family.queueFlags & vk::QueueFlagBits::eCompute) {
            indices.compute = i;
        }
        if (family.queueFlags & vk::QueueFlagBits::eTransfer) {
            indices.transfer = i;
        }
        if (indices.IsComplete() && indices.compute.has_value()) {
            break;
        }
        ++i;
    }

    if (!indices.present.has_value()) {
        indices.present = indices.graphics;
    }
    if (!indices.compute.has_value()) {
        indices.compute = indices.graphics;
    }

    return indices;
}

int Device::rateDeviceSuitability(vk::PhysicalDevice device, vk::SurfaceKHR surface) const {
    if (!isDeviceSuitable(device, surface)) {
        return 0;
    }

    auto props = device.getProperties();
    auto features = device.getFeatures();

    int score = 0;
    if (props.deviceType == vk::PhysicalDeviceType::eDiscreteGpu) {
        score += 1000;
    } else if (props.deviceType == vk::PhysicalDeviceType::eIntegratedGpu) {
        score += 500;
    }

    score += static_cast<int>(props.limits.maxImageDimension2D);
    if (!features.samplerAnisotropy) {
        score -= 500;
    }

    return score;
}

SwapchainSupport Device::swapchainSupport(vk::SurfaceKHR surface) const {
    SwapchainSupport support;
    support.capabilities = m_physical.getSurfaceCapabilitiesKHR(surface);
    support.formats = m_physical.getSurfaceFormatsKHR(surface);
    support.presentModes = m_physical.getSurfacePresentModesKHR(surface);
    return support;
}

uint32_t Device::findMemoryType(uint32_t filter, vk::MemoryPropertyFlags props) const {
    auto memProperties = m_physical.getMemoryProperties();
    for (uint32_t i = 0; i < memProperties.memoryTypeCount; ++i) {
        if ((filter & (1 << i)) &&
            (memProperties.memoryTypes[i].propertyFlags & props) == props) {
            return i;
        }
    }
    throw std::runtime_error("Failed to find suitable memory type");
}

vk::FormatProperties Device::getFormatProperties(vk::Format format) const {
    return m_physical.getFormatProperties(format);
}

vk::UniqueShaderModule Device::createShaderModule(std::span<const uint32_t> code) const {
    return m_device->createShaderModuleUnique(vk::ShaderModuleCreateInfo{
        .codeSize = code.size() * sizeof(uint32_t),
        .pCode = code.data()
    });
}

} // namespace freegen
