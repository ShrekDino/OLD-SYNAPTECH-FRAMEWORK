#include "freegen/config/ConfigManager.hpp"
#include <fstream>
#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>

namespace freegen {

ConfigManager::ConfigManager() {
    m_configPath = defaultConfigPath();
}

void ConfigManager::setConfigPath(const std::filesystem::path& path) {
    m_configPath = path;
}

std::filesystem::path ConfigManager::defaultConfigPath() const {
    const char* xdgConfig = std::getenv("XDG_CONFIG_HOME");
    std::filesystem::path base;
    if (xdgConfig) {
        base = xdgConfig;
    } else {
        base = std::filesystem::path(std::getenv("HOME")) / ".config";
    }
    return base / "freegen" / "config.json";
}

AppConfig ConfigManager::load() {
    AppConfig config;

    if (!std::filesystem::exists(m_configPath)) {
        spdlog::info("No config found at {}, using defaults", m_configPath.string());
        return config;
    }

    try {
        std::ifstream file(m_configPath);
        auto json = nlohmann::json::parse(file);

        config.captureMode = json.value("capture_mode", config.captureMode);
        config.captureSource = json.value("capture_source", config.captureSource);
        config.upscaler = json.value("upscaler", config.upscaler);
        config.frameGen = json.value("frame_gen", config.frameGen);
        config.sharpness = json.value("sharpness", config.sharpness);
        config.scaleFactor = json.value("scale_factor", config.scaleFactor);
        config.vsync = json.value("vsync", config.vsync);
        config.showFps = json.value("show_fps", config.showFps);
        config.showOverlay = json.value("show_overlay", config.showOverlay);
        config.maxFps = json.value("max_fps", config.maxFps);
        config.activeProfile = json.value("active_profile", config.activeProfile);

        spdlog::info("Loaded config from {}", m_configPath.string());
    } catch (const std::exception& e) {
        spdlog::warn("Failed to load config: {}", e.what());
    }

    return config;
}

void ConfigManager::save(const AppConfig& config) {
    try {
        std::filesystem::create_directories(m_configPath.parent_path());

        nlohmann::json json;
        json["capture_mode"] = config.captureMode;
        json["capture_source"] = config.captureSource;
        json["upscaler"] = config.upscaler;
        json["frame_gen"] = config.frameGen;
        json["sharpness"] = config.sharpness;
        json["scale_factor"] = config.scaleFactor;
        json["vsync"] = config.vsync;
        json["show_fps"] = config.showFps;
        json["show_overlay"] = config.showOverlay;
        json["max_fps"] = config.maxFps;
        json["active_profile"] = config.activeProfile;

        std::ofstream file(m_configPath);
        if (!file) {
            throw std::runtime_error("Failed to open config file for writing: " + m_configPath.string());
        }
        file << json.dump(4);
        spdlog::info("Saved config to {}", m_configPath.string());
    } catch (const std::exception& e) {
        spdlog::error("Failed to save config: {}", e.what());
    }
}

AppConfig ConfigManager::loadProfile(const std::string& name) {
    auto profilePath = m_configPath.parent_path() / "profiles" / (name + ".json");
    AppConfig config;

    if (!std::filesystem::exists(profilePath)) return config;

    try {
        std::ifstream file(profilePath);
        auto json = nlohmann::json::parse(file);

        config.captureMode = json.value("capture_mode", config.captureMode);
        config.upscaler = json.value("upscaler", config.upscaler);
        config.frameGen = json.value("frame_gen", config.frameGen);
        config.sharpness = json.value("sharpness", config.sharpness);
        config.scaleFactor = json.value("scale_factor", config.scaleFactor);
        config.vsync = json.value("vsync", config.vsync);
    } catch (const std::exception& e) {
        spdlog::warn("Failed to load profile '{}': {}", name, e.what());
    }

    return config;
}

void ConfigManager::saveProfile(const std::string& name, const AppConfig& config) {
    auto profileDir = m_configPath.parent_path() / "profiles";
    std::filesystem::create_directories(profileDir);

    nlohmann::json json;
    json["capture_mode"] = config.captureMode;
    json["upscaler"] = config.upscaler;
    json["frame_gen"] = config.frameGen;
    json["sharpness"] = config.sharpness;
    json["scale_factor"] = config.scaleFactor;
    json["vsync"] = config.vsync;

    std::ofstream file(profileDir / (name + ".json"));
    if (!file) {
        spdlog::error("Failed to open profile for writing: {}", name);
        return;
    }
    file << json.dump(4);
}

std::vector<std::string> ConfigManager::listProfiles() const {
    std::vector<std::string> profiles;
    auto profileDir = m_configPath.parent_path() / "profiles";

    if (!std::filesystem::exists(profileDir)) return profiles;

    for (const auto& entry : std::filesystem::directory_iterator(profileDir)) {
        if (entry.path().extension() == ".json") {
            profiles.push_back(entry.path().stem().string());
        }
    }

    return profiles;
}

} // namespace freegen
