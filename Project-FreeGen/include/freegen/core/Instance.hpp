#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <span>
#include <string>
#include <vector>

namespace freegen {

struct InstanceConfig {
    std::string appName = "FreeGen";
    uint32_t appVersion = VK_MAKE_API_VERSION(0, 0, 1, 0);
    bool enableValidation = true;
    std::vector<const char*> extraExtensions;
};

class Instance {
public:
    explicit Instance(const InstanceConfig& config);
    ~Instance();

    Instance(const Instance&) = delete;
    Instance& operator=(const Instance&) = delete;
    Instance(Instance&&) = delete;
    Instance& operator=(Instance&&) = delete;

    vk::Instance handle() const { return *m_instance; }
    vk::DebugUtilsMessengerEXT debugMessenger() const { return *m_debugMessenger; }
    const InstanceConfig& config() const { return m_config; }

    static std::vector<const char*> RequiredExtensions();
    static bool HasValidationSupport();

private:
    void SetupDebugMessenger();
    std::vector<const char*> GetValidationLayers() const;

    InstanceConfig m_config;
    vk::UniqueInstance m_instance;
    vk::UniqueDebugUtilsMessengerEXT m_debugMessenger;

    static VKAPI_ATTR VkBool32 VKAPI_CALL
    DebugCallback(VkDebugUtilsMessageSeverityFlagBitsEXT severity,
                  VkDebugUtilsMessageTypeFlagsEXT type,
                  const VkDebugUtilsMessengerCallbackDataEXT* data,
                  void* userData);
};

} // namespace freegen
