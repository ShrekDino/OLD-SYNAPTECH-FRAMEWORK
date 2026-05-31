#include "freegen/core/Instance.hpp"
#include <algorithm>
#include <cstring>
#include <ranges>
#include <set>
#include <spdlog/spdlog.h>

namespace freegen {

namespace {

constexpr std::array kValidationLayers = {
    "VK_LAYER_KHRONOS_validation"
};

#ifdef NDEBUG
constexpr bool kEnableValidation = false;
#else
constexpr bool kEnableValidation = true;
#endif

} // anonymous namespace

bool Instance::HasValidationSupport() {
    auto layers = vk::enumerateInstanceLayerProperties();
    return std::ranges::any_of(kValidationLayers, [&](const char* name) {
        return std::ranges::any_of(layers, [name](const auto& prop) {
            return std::strcmp(prop.layerName, name) == 0;
        });
    });
}

std::vector<const char*> Instance::RequiredExtensions() {
    std::vector<const char*> extensions = {
        VK_KHR_SURFACE_EXTENSION_NAME
    };

#ifdef VK_USE_PLATFORM_WIN32_KHR
    extensions.push_back(VK_KHR_WIN32_SURFACE_EXTENSION_NAME);
#elif defined(VK_USE_PLATFORM_XLIB_KHR)
    extensions.push_back(VK_KHR_XLIB_SURFACE_EXTENSION_NAME);
#elif defined(VK_USE_PLATFORM_WAYLAND_KHR)
    extensions.push_back(VK_KHR_WAYLAND_SURFACE_EXTENSION_NAME);
#endif

    if (kEnableValidation) {
        extensions.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
    }

    return extensions;
}

Instance::Instance(const InstanceConfig& config) : m_config(config) {
    spdlog::info("Creating Vulkan instance: {}", config.appName);

    auto extensions = RequiredExtensions();
    for (const auto& ext : config.extraExtensions) {
        extensions.push_back(ext);
    }

    vk::ApplicationInfo appInfo{
        .pApplicationName = config.appName.c_str(),
        .applicationVersion = config.appVersion,
        .pEngineName = "FreeGen",
        .engineVersion = VK_MAKE_API_VERSION(0, 0, 1, 0),
        .apiVersion = VK_API_VERSION_1_3
    };

    vk::InstanceCreateInfo createInfo{
        .pApplicationInfo = &appInfo,
        .enabledExtensionCount = static_cast<uint32_t>(extensions.size()),
        .ppEnabledExtensionNames = extensions.data()
    };

    auto validationLayers = GetValidationLayers();
    if (!validationLayers.empty()) {
        createInfo.enabledLayerCount = static_cast<uint32_t>(validationLayers.size());
        createInfo.ppEnabledLayerNames = validationLayers.data();
    }

    vk::DebugUtilsMessengerCreateInfoEXT debugCreateInfo;
    if (!validationLayers.empty()) {
        debugCreateInfo = vk::DebugUtilsMessengerCreateInfoEXT{
            .messageSeverity = vk::DebugUtilsMessageSeverityFlagBitsEXT::eWarning |
                               vk::DebugUtilsMessageSeverityFlagBitsEXT::eError,
            .messageType = vk::DebugUtilsMessageTypeFlagBitsEXT::eGeneral |
                           vk::DebugUtilsMessageTypeFlagBitsEXT::eValidation |
                           vk::DebugUtilsMessageTypeFlagBitsEXT::ePerformance,
            .pfnUserCallback = &DebugCallback,
            .pUserData = this
        };
        createInfo.pNext = &debugCreateInfo;
    }

    m_instance = vk::createInstanceUnique(createInfo);

    if (!validationLayers.empty()) {
        SetupDebugMessenger();
    }

    spdlog::info("Vulkan instance created successfully");
}

Instance::~Instance() {
    spdlog::info("Destroying Vulkan instance");
}

void Instance::SetupDebugMessenger() {
    vk::DebugUtilsMessengerCreateInfoEXT createInfo{
        .messageSeverity = vk::DebugUtilsMessageSeverityFlagBitsEXT::eWarning |
                           vk::DebugUtilsMessageSeverityFlagBitsEXT::eError,
        .messageType = vk::DebugUtilsMessageTypeFlagBitsEXT::eGeneral |
                       vk::DebugUtilsMessageTypeFlagBitsEXT::eValidation |
                       vk::DebugUtilsMessageTypeFlagBitsEXT::ePerformance,
        .pfnUserCallback = &DebugCallback,
        .pUserData = this
    };

    m_debugMessenger = m_instance->createDebugUtilsMessengerEXTUnique(createInfo);
}

std::vector<const char*> Instance::GetValidationLayers() const {
    if (!m_config.enableValidation || !kEnableValidation) {
        return {};
    }
    if (!HasValidationSupport()) {
        spdlog::warn("Validation layers requested but not available");
        return {};
    }
    return {kValidationLayers.begin(), kValidationLayers.end()};
}

VKAPI_ATTR VkBool32 VKAPI_CALL
Instance::DebugCallback(VkDebugUtilsMessageSeverityFlagBitsEXT severity,
                        VkDebugUtilsMessageTypeFlagsEXT /*type*/,
                        const VkDebugUtilsMessengerCallbackDataEXT* data,
                        void* /*userData*/) {
    auto sev = spdlog::level::info;
    if (severity >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT) {
        sev = spdlog::level::err;
    } else if (severity >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT) {
        sev = spdlog::level::warn;
    }

    spdlog::log(sev, "[Vulkan] {}", data->pMessage);
    return VK_FALSE;
}

} // namespace freegen
