#pragma once

#include <memory>
#include <string>
#include <filesystem>
#include <vector>

namespace freegen {

struct AppConfig {
    std::string captureMode = "auto";
    std::string captureSource;
    std::string upscaler = "Off";
    std::string frameGen = "Off";
    float sharpness = 0.5f;
    float scaleFactor = 2.0f;
    bool vsync = true;
    bool showFps = true;
    bool showOverlay = true;
    uint32_t maxFps = 0;

    std::string activeProfile = "Default";
};

class ConfigManager {
public:
    ConfigManager();
    ~ConfigManager() = default;

    void setConfigPath(const std::filesystem::path& path);

    AppConfig load();
    void save(const AppConfig& config);

    AppConfig loadProfile(const std::string& name);
    void saveProfile(const std::string& name, const AppConfig& config);
    std::vector<std::string> listProfiles() const;

    std::filesystem::path defaultConfigPath() const;

private:
    std::filesystem::path m_configPath;
};

} // namespace freegen
