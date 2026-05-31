#include <gtest/gtest.h>
#include "freegen/config/ConfigManager.hpp"
#include "freegen/config/ProfileManager.hpp"
#include <filesystem>
#include <fstream>

namespace freegen {

class ConfigTest : public ::testing::Test {
protected:
    void SetUp() override {
        tmpDir = std::filesystem::temp_directory_path() / "freegen_test";
        std::filesystem::create_directories(tmpDir);
    }

    void TearDown() override {
        std::filesystem::remove_all(tmpDir);
    }

    std::filesystem::path tmpDir;
};

TEST_F(ConfigTest, DefaultConfigValues) {
    AppConfig config;
    EXPECT_EQ(config.upscaler, "Off");
    EXPECT_EQ(config.frameGen, "Off");
    EXPECT_FLOAT_EQ(config.sharpness, 0.5f);
    EXPECT_FLOAT_EQ(config.scaleFactor, 2.0f);
    EXPECT_TRUE(config.vsync);
    EXPECT_TRUE(config.showFps);
    EXPECT_TRUE(config.showOverlay);
}

TEST_F(ConfigTest, SaveAndLoadConfig) {
    ConfigManager configManager;
    auto configPath = tmpDir / "config.json";
    configManager.setConfigPath(configPath);

    AppConfig config;
    config.upscaler = "FSR 1.0";
    config.frameGen = "Interpolate";
    config.sharpness = 0.8f;
    config.scaleFactor = 3.0f;
    config.vsync = false;

    configManager.save(config);

    AppConfig loaded = configManager.load();
    EXPECT_EQ(loaded.upscaler, "FSR 1.0");
    EXPECT_EQ(loaded.frameGen, "Interpolate");
    EXPECT_FLOAT_EQ(loaded.sharpness, 0.8f);
    EXPECT_FLOAT_EQ(loaded.scaleFactor, 3.0f);
    EXPECT_FALSE(loaded.vsync);
}

TEST_F(ConfigTest, SaveAndLoadProfile) {
    ProfileManager profileManager;
    auto configPath = tmpDir / "config.json";
    profileManager.init(configPath.parent_path());

    AppConfig config;
    config.upscaler = "Integer";
    config.sharpness = 0.0f;

    profileManager.saveProfile("TestGame", config);

    AppConfig loaded = profileManager.loadProfile("TestGame");
    EXPECT_EQ(loaded.upscaler, "Integer");
    EXPECT_FLOAT_EQ(loaded.sharpness, 0.0f);
}

TEST_F(ConfigTest, ListProfiles) {
    ProfileManager profileManager;
    profileManager.init(tmpDir);

    profileManager.saveProfile("Profile1", AppConfig{});
    profileManager.saveProfile("Profile2", AppConfig{});

    auto profiles = profileManager.listProfiles();
    EXPECT_EQ(profiles.size(), 2);
    EXPECT_NE(std::find(profiles.begin(), profiles.end(), "Profile1"), profiles.end());
    EXPECT_NE(std::find(profiles.begin(), profiles.end(), "Profile2"), profiles.end());
}

TEST_F(ConfigTest, DeleteProfile) {
    ProfileManager profileManager;
    profileManager.init(tmpDir);

    profileManager.saveProfile("TempProfile", AppConfig{});
    EXPECT_EQ(profileManager.listProfiles().size(), 1);

    profileManager.deleteProfile("TempProfile");
    EXPECT_EQ(profileManager.listProfiles().size(), 0);
}

} // namespace freegen
