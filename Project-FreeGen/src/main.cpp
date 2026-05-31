#include <SDL.h>
#include <SDL_vulkan.h>
#include <spdlog/spdlog.h>

#include "freegen/core/Instance.hpp"
#include "freegen/core/Device.hpp"
#include "freegen/core/Swapchain.hpp"
#include "freegen/core/CommandPool.hpp"
#include "freegen/render/TextureManager.hpp"
#include "freegen/render/Compositor.hpp"
#include "freegen/capture/ICaptureBackend.hpp"
#include "freegen/effects/EffectManager.hpp"
#include "freegen/effects/FSR1.hpp"
#include "freegen/effects/IntegerScale.hpp"
#include "freegen/effects/FrameGenInterpolate.hpp"
#include "freegen/ui/ImGuiHandler.hpp"
#include "freegen/ui/SettingsWindow.hpp"
#include "freegen/config/ConfigManager.hpp"
#include "freegen/config/CliParser.hpp"
#include "freegen/config/ProfileManager.hpp"
#include "freegen/util/Logger.hpp"
#include "freegen/util/Platform.hpp"

#include <chrono>
#include <memory>

namespace {

constexpr uint32_t kDefaultWidth = 1280;
constexpr uint32_t kDefaultHeight = 720;

struct SDLDeleter {
    void operator()(SDL_Window* w) const { SDL_DestroyWindow(w); }
};

std::unique_ptr<SDL_Window, SDLDeleter> createWindow(uint32_t width, uint32_t height) {
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) < 0) {
        throw std::runtime_error(std::string("SDL init failed: ") + SDL_GetError());
    }

    SDL_Window* window = SDL_CreateWindow(
        "FreeGen",
        SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
        static_cast<int>(width), static_cast<int>(height),
        SDL_WINDOW_VULKAN | SDL_WINDOW_RESIZABLE | SDL_WINDOW_ALLOW_HIGHDPI);

    if (!window) {
        throw std::runtime_error(std::string("SDL window creation failed: ") + SDL_GetError());
    }

    return std::unique_ptr<SDL_Window, SDLDeleter>(window);
}

vk::SurfaceKHR createSurface(vk::Instance instance, SDL_Window* window) {
    VkSurfaceKHR surface;
    if (!SDL_Vulkan_CreateSurface(window, instance, &surface)) {
        throw std::runtime_error(std::string("Failed to create Vulkan surface: ") + SDL_GetError());
    }
    return surface;
}

} // anonymous namespace

int main(int argc, char* argv[]) {
    freegen::Logger::init(freegen::Logger::Level::Info);

    try {
        freegen::CliParser cli;
        auto opts = cli.parse(argc, argv);

        spdlog::info("FreeGen v{}.{}.{} starting on {}",
                     FREEGEN_VERSION_MAJOR, FREEGEN_VERSION_MINOR, FREEGEN_VERSION_PATCH,
                     freegen::Platform::osName());

        freegen::ConfigManager configManager;
        freegen::ProfileManager profileManager;

        auto appConfig = configManager.load();
        if (!opts.profile.empty()) {
            appConfig = profileManager.loadProfile(opts.profile);
        }

        auto window = createWindow(kDefaultWidth, kDefaultHeight);

        freegen::InstanceConfig instConfig;
        instConfig.appName = "FreeGen";
        instConfig.enableValidation = true;

        std::vector<const char*> sdlExts;
        unsigned int sdlExtCount;
        SDL_Vulkan_GetInstanceExtensions(window.get(), &sdlExtCount, nullptr);
        sdlExts.resize(sdlExtCount);
        SDL_Vulkan_GetInstanceExtensions(window.get(), &sdlExtCount, sdlExts.data());
        for (const auto* ext : sdlExts) {
            instConfig.extraExtensions.push_back(ext);
        }

        auto instance = std::make_unique<freegen::Instance>(instConfig);

        vk::SurfaceKHR surface = createSurface(instance->handle(), window.get());

        auto device = std::make_unique<freegen::Device>(instance->handle(), surface);

        auto queueIndices = device->queueFamilyIndices();
        auto graphicsPool = std::make_unique<freegen::CommandPool>(
            *device, queueIndices.graphics.value());

        freegen::SwapchainConfig swapConfig{
            .extent = {kDefaultWidth, kDefaultHeight},
            .vsync = appConfig.vsync
        };
        auto swapchain = std::make_unique<freegen::Swapchain>(
            *device, surface, swapConfig);

        auto textureManager = std::make_unique<freegen::TextureManager>(*device, *graphicsPool);

        auto compositor = std::make_unique<freegen::Compositor>(
            *device, *swapchain, *graphicsPool, *textureManager);
        compositor->init();

        auto effectManager = std::make_unique<freegen::EffectManager>();
        effectManager->registerEffect(std::make_unique<freegen::FSR1>());
        effectManager->registerEffect(std::make_unique<freegen::IntegerScale>());
        effectManager->registerEffect(std::make_unique<freegen::FrameGenInterpolate>());

        freegen::EffectInitInfo effectInfo{
            .device = device.get(),
            .descriptorPool = VK_NULL_HANDLE,
            .descriptorSetLayout = VK_NULL_HANDLE,
            .maxFramesInFlight = 3
        };
        effectManager->initAll(effectInfo);

        auto imguiHandler = std::make_unique<freegen::ImGuiHandler>();
        freegen::ImGuiHandler::Config imguiConfig{
            .window = window.get(),
            .instance = instance->handle(),
            .physicalDevice = device->physical(),
            .device = device->logical(),
            .queueFamilyIndex = queueIndices.graphics.value(),
            .queue = device->graphicsQueue(),
            .renderPass = swapchain->renderPass(),
            .minImageCount = 3,
            .imageExtent = {kDefaultWidth, kDefaultHeight}
        };
        imguiHandler->init(imguiConfig);

        auto settingsWindow = std::make_unique<freegen::SettingsWindow>();
        settingsWindow->setEffectManager(effectManager.get());

        imguiHandler->setSettingsCallback([&]() {
            settingsWindow->draw();
        });

        std::unique_ptr<freegen::ICaptureBackend> captureBackend;
#ifdef FREEGEN_LINUX_CAPTURE
        captureBackend = std::make_unique<freegen::LinuxCaptureBackend>();
#elif FREEGEN_WINDOWS_CAPTURE
        captureBackend = std::make_unique<freegen::DXGICaptureBackend>();
#endif

        if (captureBackend) {
            captureBackend->initialize();
            captureBackend->start();
            captureBackend->setFrameCallback([&](const freegen::CaptureFrame& frame) {
                if (frame.data && frame.width > 0 && frame.height > 0) {
                    textureManager->uploadCapturedFrame(frame.data, frame.width, frame.height, frame.bytesPerPixel);
                    compositor->setInputTexture(textureManager->inputView(), textureManager->inputExtent());
                }
            });
        }

        auto lastTime = std::chrono::high_resolution_clock::now();
        uint64_t frameCount = 0;
        float fps = 0.0f;
        bool running = true;

        while (running) {
            SDL_Event event;
            while (SDL_PollEvent(&event)) {
                ImGui_ImplSDL2_ProcessEvent(&event);
                if (event.type == SDL_QUIT) {
                    running = false;
                } else if (event.type == SDL_KEYDOWN) {
                    if (event.key.keysym.sym == SDLK_TAB) {
                        imguiHandler->toggle();
                    } else if (event.key.keysym.sym == SDLK_ESCAPE) {
                        running = false;
                    }
                } else if (event.type == SDL_WINDOWEVENT) {
                    if (event.window.event == SDL_WINDOWEVENT_RESIZED) {
                        int w, h;
                        SDL_GetWindowSize(window.get(), &w, &h);
                        if (w > 0 && h > 0) {
                            swapConfig.extent = {static_cast<uint32_t>(w), static_cast<uint32_t>(h)};
                            swapchain->recreate(surface, swapConfig);
                            compositor->recreateSwapchain();
                        }
                    }
                }
            }

            imguiHandler->newFrame();

            auto cmd = compositor->beginFrame();
            if (!cmd) {
                swapchain->recreate(surface, swapConfig);
                compositor->recreateSwapchain();
                continue;
            }

            auto currentTime = std::chrono::high_resolution_clock::now();
            auto delta = std::chrono::duration<float, std::milli>(currentTime - lastTime).count();
            lastTime = currentTime;
            ++frameCount;

            if (frameCount % 60 == 0 && delta > 0.0f) {
                fps = 60000.0f / delta;
            }

            std::string activeEffect = settingsWindow->upscale().mode;
            if (settingsWindow->frameGen().enabled) {
                activeEffect += " + FrameGen";
            }

            imguiHandler->setStats(fps, delta,
                                   settingsWindow->upscale().mode == "Off" ? 0 : kDefaultWidth,
                                   settingsWindow->upscale().mode == "Off" ? 0 : kDefaultHeight,
                                   kDefaultWidth, kDefaultHeight,
                                   activeEffect);

            imguiHandler->render(cmd);

            compositor->endFrame(cmd);
            if (!compositor->present()) {
                swapchain->recreate(surface, swapConfig);
                compositor->recreateSwapchain();
            }
        }

        device->logical().waitIdle();
        instance->handle().destroySurfaceKHR(surface);
        effectManager->shutdownAll();
        imguiHandler->shutdown();
        if (captureBackend) captureBackend->stop();
        spdlog::info("FreeGen shutdown complete");

    } catch (const std::exception& e) {
        spdlog::error("Fatal error: {}", e.what());
        return 1;
    }

    return 0;
}
