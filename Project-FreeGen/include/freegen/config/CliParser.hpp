#pragma once

#include <memory>
#include <string>
#include <vector>

namespace freegen {

struct CliOptions {
    bool help = false;
    bool version = false;
    std::string config;
    std::string profile;
    std::string captureSource;
    std::string upscaler = "FSR 1.0";
    std::string frameGen = "Off";
    float sharpness = 0.5f;
    float scaleFactor = 2.0f;
    bool vsync = true;
    bool noOverlay = false;
    bool listSources = false;
    bool listEffects = false;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t fps = 0;
};

class CliParser {
public:
    CliParser();
    ~CliParser() = default;

    CliOptions parse(int argc, char** argv);
    void printHelp() const;
    void printVersion() const;

private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace freegen
