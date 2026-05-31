#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <functional>

struct SDL_Window;

namespace freegen {

class ImGuiHandler {
public:
    ImGuiHandler();
    ~ImGuiHandler();

    ImGuiHandler(const ImGuiHandler&) = delete;
    ImGuiHandler& operator=(const ImGuiHandler&) = delete;
    ImGuiHandler(ImGuiHandler&&) = delete;
    ImGuiHandler& operator=(ImGuiHandler&&) = delete;

    struct Config {
        SDL_Window* window = nullptr;
        vk::Instance instance;
        vk::PhysicalDevice physicalDevice;
        vk::Device device;
        uint32_t queueFamilyIndex = 0;
        vk::Queue queue;
        vk::RenderPass renderPass;
        uint32_t minImageCount = 3;
        vk::Extent2D imageExtent{};
    };

    void init(const Config& config);
    void shutdown();

    void newFrame();
    void render(vk::CommandBuffer cmd);

    bool isVisible() const { return m_visible; }
    void setVisible(bool visible) { m_visible = visible; }
    void toggle() { m_visible = !m_visible; }

    using SettingsCallback = std::function<void()>;
    void setSettingsCallback(SettingsCallback callback) { m_settingsCallback = std::move(callback); }

    void setStats(float fps, float frameTime, uint32_t inputW, uint32_t inputH,
                  uint32_t outputW, uint32_t outputH, std::string_view effectName);

private:
    bool m_initialized = false;
    bool m_visible = true;
    SettingsCallback m_settingsCallback;

    struct Stats {
        float fps = 0;
        float frameTime = 0;
        uint32_t inputW = 0;
        uint32_t inputH = 0;
        uint32_t outputW = 0;
        uint32_t outputH = 0;
        std::string effectName;
    } m_stats;

    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace freegen
