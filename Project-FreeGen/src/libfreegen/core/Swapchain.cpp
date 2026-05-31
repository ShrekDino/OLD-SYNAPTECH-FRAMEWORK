#include "freegen/core/Swapchain.hpp"
#include "freegen/core/Device.hpp"
#include <algorithm>
#include <limits>
#include <spdlog/spdlog.h>

namespace freegen {

Swapchain::Swapchain(const Device& device, vk::SurfaceKHR surface, SwapchainConfig config)
    : m_device(&device), m_config(std::move(config)) {
    createSwapchain(surface);
    createImageViews();
    createRenderPass();
    createFramebuffers();
}

Swapchain::~Swapchain() {
    destroy();
}

Swapchain::Swapchain(Swapchain&& other) noexcept
    : m_device(other.m_device),
      m_config(other.m_config),
      m_swapchain(std::move(other.m_swapchain)),
      m_renderPass(std::move(other.m_renderPass)),
      m_images(std::move(other.m_images)),
      m_imageViews(std::move(other.m_imageViews)),
      m_framebuffers(std::move(other.m_framebuffers)),
      m_surfaceFormat(other.m_surfaceFormat) {}

Swapchain& Swapchain::operator=(Swapchain&& other) noexcept {
    if (this != &other) {
        destroy();
        m_device = other.m_device;
        m_config = other.m_config;
        m_swapchain = std::move(other.m_swapchain);
        m_renderPass = std::move(other.m_renderPass);
        m_images = std::move(other.m_images);
        m_imageViews = std::move(other.m_imageViews);
        m_framebuffers = std::move(other.m_framebuffers);
        m_surfaceFormat = other.m_surfaceFormat;
    }
    return *this;
}

void Swapchain::recreate(vk::SurfaceKHR surface, SwapchainConfig config) {
    m_device->logical().waitIdle();
    m_config = std::move(config);
    destroy();
    createSwapchain(surface);
    createImageViews();
    createRenderPass();
    createFramebuffers();
    spdlog::info("Swapchain recreated: {}x{}", m_config.extent.width, m_config.extent.height);
}

void Swapchain::destroy() {
    m_framebuffers.clear();
    m_imageViews.clear();
    m_renderPass.reset();
    m_swapchain.reset();
    m_images.clear();
}

void Swapchain::createSwapchain(vk::SurfaceKHR surface) {
    auto support = m_device->swapchainSupport(surface);
    m_surfaceFormat = chooseFormat(support.formats);
    auto presentMode = choosePresentMode(support.presentModes);
    auto extent = chooseExtent(support.capabilities);

    uint32_t imageCount = std::clamp(
        m_config.imageCount,
        support.capabilities.minImageCount,
        support.capabilities.maxImageCount > 0
            ? support.capabilities.maxImageCount
            : std::numeric_limits<uint32_t>::max());

    vk::SwapchainCreateInfoKHR createInfo{
        .surface = surface,
        .minImageCount = imageCount,
        .imageFormat = m_surfaceFormat.format,
        .imageColorSpace = m_surfaceFormat.colorSpace,
        .imageExtent = extent,
        .imageArrayLayers = 1,
        .imageUsage = vk::ImageUsageFlagBits::eColorAttachment |
                      vk::ImageUsageFlagBits::eTransferDst,
        .preTransform = support.capabilities.currentTransform,
        .compositeAlpha = vk::CompositeAlphaFlagBitsKHR::eOpaque,
        .presentMode = presentMode,
        .clipped = VK_TRUE,
        .oldSwapchain = m_swapchain ? m_swapchain.get() : nullptr
    };

    auto indices = m_device->queueFamilyIndices();
    if (indices.graphics != indices.present) {
        uint32_t queueFamilyIndices[] = {indices.graphics.value(), indices.present.value()};
        createInfo.imageSharingMode = vk::SharingMode::eConcurrent;
        createInfo.queueFamilyIndexCount = 2;
        createInfo.pQueueFamilyIndices = queueFamilyIndices;
    }

    m_swapchain = m_device->logical().createSwapchainKHRUnique(createInfo);
    m_images = m_device->logical().getSwapchainImagesKHR(m_swapchain.get());
    m_config.extent = extent;

    spdlog::info("Swapchain created: {}x{} ({} images, format: {})",
                 extent.width, extent.height, imageCount,
                 vk::to_string(m_surfaceFormat.format));
}

void Swapchain::createImageViews() {
    m_imageViews.clear();
    m_imageViews.reserve(m_images.size());

    for (const auto& image : m_images) {
        vk::ImageViewCreateInfo createInfo{
            .image = image,
            .viewType = vk::ImageViewType::e2D,
            .format = m_surfaceFormat.format,
            .subresourceRange = {
                .aspectMask = vk::ImageAspectFlagBits::eColor,
                .baseMipLevel = 0,
                .levelCount = 1,
                .baseArrayLayer = 0,
                .layerCount = 1
            }
        };
        m_imageViews.push_back(m_device->logical().createImageViewUnique(createInfo));
    }
}

void Swapchain::createRenderPass() {
    vk::AttachmentDescription colorAttachment{
        .format = m_surfaceFormat.format,
        .samples = vk::SampleCountFlagBits::e1,
        .loadOp = vk::AttachmentLoadOp::eClear,
        .storeOp = vk::AttachmentStoreOp::eStore,
        .stencilLoadOp = vk::AttachmentLoadOp::eDontCare,
        .stencilStoreOp = vk::AttachmentStoreOp::eDontCare,
        .initialLayout = vk::ImageLayout::eUndefined,
        .finalLayout = vk::ImageLayout::ePresentSrcKHR
    };

    vk::AttachmentReference colorAttachmentRef{
        .attachment = 0,
        .layout = vk::ImageLayout::eColorAttachmentOptimal
    };

    vk::SubpassDescription subpass{
        .pipelineBindPoint = vk::PipelineBindPoint::eGraphics,
        .colorAttachmentCount = 1,
        .pColorAttachments = &colorAttachmentRef
    };

    vk::SubpassDependency dependency{
        .srcSubpass = VK_SUBPASS_EXTERNAL,
        .dstSubpass = 0,
        .srcStageMask = vk::PipelineStageFlagBits::eColorAttachmentOutput,
        .dstStageMask = vk::PipelineStageFlagBits::eColorAttachmentOutput,
        .srcAccessMask = vk::AccessFlagBits::eNone,
        .dstAccessMask = vk::AccessFlagBits::eColorAttachmentWrite
    };

    m_renderPass = m_device->logical().createRenderPassUnique(vk::RenderPassCreateInfo{
        .attachmentCount = 1,
        .pAttachments = &colorAttachment,
        .subpassCount = 1,
        .pSubpasses = &subpass,
        .dependencyCount = 1,
        .pDependencies = &dependency
    });
}

void Swapchain::createFramebuffers() {
    m_framebuffers.clear();
    m_framebuffers.reserve(m_imageViews.size());

    for (const auto& view : m_imageViews) {
        m_framebuffers.push_back(m_device->logical().createFramebufferUnique(
            vk::FramebufferCreateInfo{
                .renderPass = m_renderPass.get(),
                .attachmentCount = 1,
                .pAttachments = &view.get(),
                .width = m_config.extent.width,
                .height = m_config.extent.height,
                .layers = 1
            }));
    }
}

vk::Result Swapchain::acquireNextImage(vk::Semaphore semaphore, uint32_t* imageIndex) const {
    auto result = m_device->logical().acquireNextImageKHR(
        m_swapchain.get(), std::numeric_limits<uint64_t>::max(), semaphore, nullptr, imageIndex);
    return result;
}

vk::SurfaceFormatKHR Swapchain::chooseFormat(const std::vector<vk::SurfaceFormatKHR>& formats) const {
    if (formats.size() == 1 && formats[0].format == vk::Format::eUndefined) {
        return {vk::Format::eB8G8R8A8Unorm, vk::ColorSpaceKHR::eSrgbNonlinear};
    }

    for (const auto& fmt : formats) {
        if (fmt.format == vk::Format::eB8G8R8A8Unorm &&
            fmt.colorSpace == vk::ColorSpaceKHR::eSrgbNonlinear) {
            return fmt;
        }
    }

    return formats[0];
}

vk::PresentModeKHR Swapchain::choosePresentMode(const std::vector<vk::PresentModeKHR>& modes) const {
    if (m_config.vsync) {
        if (std::ranges::find(modes, vk::PresentModeKHR::eMailbox) != modes.end()) {
            return vk::PresentModeKHR::eMailbox;
        }
        return vk::PresentModeKHR::eFifo;
    }

    if (std::ranges::find(modes, vk::PresentModeKHR::eImmediate) != modes.end()) {
        return vk::PresentModeKHR::eImmediate;
    }
    return vk::PresentModeKHR::eFifo;
}

vk::Extent2D Swapchain::chooseExtent(const vk::SurfaceCapabilitiesKHR& caps) const {
    if (caps.currentExtent.width != std::numeric_limits<uint32_t>::max()) {
        return caps.currentExtent;
    }
    return {
        std::clamp(m_config.extent.width, caps.minImageExtent.width, caps.maxImageExtent.width),
        std::clamp(m_config.extent.height, caps.minImageExtent.height, caps.maxImageExtent.height)
    };
}

} // namespace freegen
