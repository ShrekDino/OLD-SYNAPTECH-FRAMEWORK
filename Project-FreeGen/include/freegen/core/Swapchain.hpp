#pragma once

#include <vulkan/vulkan.hpp>
#include <memory>
#include <vector>

namespace freegen {

class Device;

struct SwapchainConfig {
    vk::Extent2D extent{1280, 720};
    bool vsync = true;
    uint32_t imageCount = 3;
};

class Swapchain {
public:
    Swapchain(const Device& device, vk::SurfaceKHR surface, SwapchainConfig config);
    ~Swapchain();

    Swapchain(const Swapchain&) = delete;
    Swapchain& operator=(const Swapchain&) = delete;
    Swapchain(Swapchain&& other) noexcept;
    Swapchain& operator=(Swapchain&& other) noexcept;

    void recreate(vk::SurfaceKHR surface, SwapchainConfig config);
    vk::Result acquireNextImage(vk::Semaphore semaphore, uint32_t* imageIndex) const;

    vk::SwapchainKHR handle() const { return *m_swapchain; }
    const std::vector<vk::Image>& images() const { return m_images; }
    const std::vector<vk::UniqueImageView>& imageViews() const { return m_imageViews; }
    const std::vector<vk::UniqueFramebuffer>& framebuffers() const { return m_framebuffers; }
    vk::Extent2D extent() const { return m_config.extent; }
    vk::Format format() const { return m_surfaceFormat.format; }
    vk::RenderPass renderPass() const { return *m_renderPass; }
    const SwapchainConfig& config() const { return m_config; }
    size_t imageCount() const { return m_images.size(); }

private:
    void createSwapchain(vk::SurfaceKHR surface);
    void createImageViews();
    void createRenderPass();
    void createFramebuffers();
    void destroy();

    vk::SurfaceFormatKHR chooseFormat(const std::vector<vk::SurfaceFormatKHR>& formats) const;
    vk::PresentModeKHR choosePresentMode(const std::vector<vk::PresentModeKHR>& modes) const;
    vk::Extent2D chooseExtent(const vk::SurfaceCapabilitiesKHR& caps) const;

    const Device* m_device;
    SwapchainConfig m_config;
    vk::UniqueSwapchainKHR m_swapchain;
    vk::UniqueRenderPass m_renderPass;
    std::vector<vk::Image> m_images;
    std::vector<vk::UniqueImageView> m_imageViews;
    std::vector<vk::UniqueFramebuffer> m_framebuffers;
    vk::SurfaceFormatKHR m_surfaceFormat;
};

} // namespace freegen
