#include "freegen/ui/ImGuiHandler.hpp"
#include <SDL.h>
#include <imgui.h>
#include <imgui_impl_sdl2.h>
#include <imgui_impl_vulkan.h>
#include <spdlog/spdlog.h>

namespace freegen {

struct ImGuiHandler::Impl {
    vk::DescriptorPool descriptorPool;
};

ImGuiHandler::ImGuiHandler() : m_impl(std::make_unique<Impl>()) {}

ImGuiHandler::~ImGuiHandler() {
    shutdown();
}

void ImGuiHandler::init(const Config& config) {
    if (m_initialized) return;

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();

    ImGuiIO& io = ImGui::GetIO();
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    io.IniFilename = nullptr;

    ImGui::StyleColorsDark();

    ImGui_ImplSDL2_InitForVulkan(config.window);

    vk::DescriptorPoolSize poolSizes[] = {
        {vk::DescriptorType::eCombinedImageSampler, 100},
        {vk::DescriptorType::eUniformBuffer, 100},
        {vk::DescriptorType::eStorageBuffer, 100}
    };

    m_impl->descriptorPool = config.device.createDescriptorPoolUnique(
        vk::DescriptorPoolCreateInfo{
            .flags = vk::DescriptorPoolCreateFlagBits::eFreeDescriptorSet,
            .maxSets = 100,
            .poolSizeCount = static_cast<uint32_t>(std::size(poolSizes)),
            .pPoolSizes = poolSizes
        });

    ImGui_ImplVulkan_InitInfo vulkanInfo{
        .Instance = config.instance,
        .PhysicalDevice = config.physicalDevice,
        .Device = config.device,
        .QueueFamily = config.queueFamilyIndex,
        .Queue = config.queue,
        .DescriptorPool = m_impl->descriptorPool,
        .RenderPass = config.renderPass,
        .MinImageCount = config.minImageCount,
        .ImageCount = config.minImageCount,
        .MSAASamples = VK_SAMPLE_COUNT_1_BIT,
    };

    ImGui_ImplVulkan_Init(&vulkanInfo);

    m_initialized = true;
    spdlog::info("ImGui initialized");
}

void ImGuiHandler::shutdown() {
    if (!m_initialized) return;

    ImGui_ImplVulkan_Shutdown();
    ImGui_ImplSDL2_Shutdown();
    ImGui::DestroyContext();

    if (m_impl->descriptorPool) {
        m_impl->descriptorPool.reset();
    }

    m_initialized = false;
    spdlog::info("ImGui shutdown");
}

void ImGuiHandler::newFrame() {
    ImGui_ImplVulkan_NewFrame();
    ImGui_ImplSDL2_NewFrame();
    ImGui::NewFrame();
}

void ImGuiHandler::render(vk::CommandBuffer cmd) {
    if (!m_visible) return;

    if (m_settingsCallback) {
        ImGui::Begin("FreeGen Settings", &m_visible, ImGuiWindowFlags_AlwaysAutoResize);
        m_settingsCallback();
        ImGui::End();
    }

    if (m_stats.fps > 0) {
        ImGui::Begin("FreeGen HUD", nullptr,
                     ImGuiWindowFlags_NoDecoration |
                     ImGuiWindowFlags_AlwaysAutoResize |
                     ImGuiWindowFlags_NoBackground |
                     ImGuiWindowFlags_NoNav |
                     ImGuiWindowFlags_NoMove);

        ImGui::TextColored(ImVec4(0.0f, 1.0f, 0.0f, 1.0f),
                           "FPS: %.1f", m_stats.fps);
        ImGui::SameLine();
        ImGui::TextColored(ImVec4(0.5f, 0.8f, 1.0f, 1.0f),
                           "| Frame: %.1f ms", m_stats.frameTime);

        ImGui::TextColored(ImVec4(0.8f, 0.8f, 0.8f, 1.0f),
                           "Input: %ux%u | Output: %ux%u",
                           m_stats.inputW, m_stats.inputH,
                           m_stats.outputW, m_stats.outputH);

        ImGui::TextColored(ImVec4(1.0f, 0.8f, 0.2f, 1.0f),
                           "Effect: %s", m_stats.effectName.c_str());

        ImGui::End();
    }

    ImGui::Render();
    ImGui_ImplVulkan_RenderDrawData(ImGui::GetDrawData(), cmd);
}

void ImGuiHandler::setStats(float fps, float frameTime, uint32_t inputW, uint32_t inputH,
                            uint32_t outputW, uint32_t outputH, std::string_view effectName) {
    m_stats.fps = fps;
    m_stats.frameTime = frameTime;
    m_stats.inputW = inputW;
    m_stats.inputH = inputH;
    m_stats.outputW = outputW;
    m_stats.outputH = outputH;
    m_stats.effectName = effectName;
}

} // namespace freegen
