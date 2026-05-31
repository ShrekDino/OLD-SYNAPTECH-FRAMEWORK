#pragma once

#include "freegen/config/ConfigManager.hpp"
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace freegen {

class ProfileManager {
public:
    ProfileManager();
    ~ProfileManager() = default;

    void init(const std::filesystem::path& configDir);

    std::vector<std::string> listProfiles() const;
    AppConfig loadProfile(const std::string& name);
    void saveProfile(const std::string& name, const AppConfig& config);
    void deleteProfile(const std::string& name);

    std::string activeProfile() const { return m_activeProfile; }
    void setActiveProfile(const std::string& name);

    AppConfig loadActive();
    void saveActive(const AppConfig& config);

    AppConfig detectProfileForProcess(const std::string& processName);

private:
    std::string m_activeProfile = "Default";
    std::filesystem::path m_profilesDir;
    std::unordered_map<std::string, std::string> m_autoDetect;
};

} // namespace freegen
