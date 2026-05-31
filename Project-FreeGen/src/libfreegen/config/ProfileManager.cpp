#include "freegen/config/ProfileManager.hpp"
#include <algorithm>
#include <fstream>
#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>

namespace freegen {

ProfileManager::ProfileManager() = default;

void ProfileManager::init(const std::filesystem::path& configDir) {
    m_profilesDir = configDir / "profiles";
    std::filesystem::create_directories(m_profilesDir);

    m_autoDetect = {
        {"steam", "Steam Game"},
        {"gamescope", "Gamescope Session"},
        {"wine", "Wine/Proton Game"},
    };
}

std::vector<std::string> ProfileManager::listProfiles() const {
    std::vector<std::string> profiles;
    if (!std::filesystem::exists(m_profilesDir)) return profiles;

    for (const auto& entry : std::filesystem::directory_iterator(m_profilesDir)) {
        if (entry.path().extension() == ".json") {
            profiles.push_back(entry.path().stem().string());
        }
    }
    return profiles;
}

AppConfig ProfileManager::loadProfile(const std::string& name) {
    auto path = m_profilesDir / (name + ".json");
    AppConfig config;

    if (!std::filesystem::exists(path)) return config;

    try {
        std::ifstream file(path);
        auto json = nlohmann::json::parse(file);
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

void ProfileManager::saveProfile(const std::string& name, const AppConfig& config) {
    std::filesystem::create_directories(m_profilesDir);

    nlohmann::json json;
    json["upscaler"] = config.upscaler;
    json["frame_gen"] = config.frameGen;
    json["sharpness"] = config.sharpness;
    json["scale_factor"] = config.scaleFactor;
    json["vsync"] = config.vsync;

    std::ofstream file(m_profilesDir / (name + ".json"));
    if (!file) {
        spdlog::error("Failed to open profile for writing: {}", name);
        return;
    }
    file << json.dump(4);
    spdlog::info("Saved profile '{}'", name);
}

void ProfileManager::deleteProfile(const std::string& name) {
    auto path = m_profilesDir / (name + ".json");
    if (std::filesystem::remove(path)) {
        spdlog::info("Deleted profile '{}'", name);
    }
}

void ProfileManager::setActiveProfile(const std::string& name) {
    m_activeProfile = name;
}

AppConfig ProfileManager::loadActive() {
    return loadProfile(m_activeProfile);
}

void ProfileManager::saveActive(const AppConfig& config) {
    saveProfile(m_activeProfile, config);
}

AppConfig ProfileManager::detectProfileForProcess(const std::string& processName) {
    auto it = std::find_if(m_autoDetect.begin(), m_autoDetect.end(),
        [&](const auto& pair) {
            return processName.find(pair.first) != std::string::npos;
        });

    if (it != m_autoDetect.end()) {
        spdlog::info("Auto-detected profile for '{}': {}", processName, it->second);
        auto config = loadProfile(it->second);
        if (!config.upscaler.empty()) {
            return config;
        }
    }

    return AppConfig{};
}

} // namespace freegen
