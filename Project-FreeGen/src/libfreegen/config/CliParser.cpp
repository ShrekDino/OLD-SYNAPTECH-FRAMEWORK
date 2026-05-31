#include "freegen/config/CliParser.hpp"
#include <CLI/CLI.hpp>
#include <spdlog/spdlog.h>
#include <iostream>

namespace freegen {

struct CliParser::Impl {
    CLI::App app;
};

CliParser::CliParser() : m_impl(std::make_unique<Impl>()) {
    m_impl->app.name("freegen");
    m_impl->app.description("Open-source screen capture upscaling and frame generation tool");
}

CliOptions CliParser::parse(int argc, char** argv) {
    CliOptions opts;

    m_impl->app.add_flag("--version", opts.version, "Print version information");
    m_impl->app.add_option("-c,--config", opts.config, "Path to config file");
    m_impl->app.add_option("-p,--profile", opts.profile, "Profile name");
    m_impl->app.add_option("--capture-source", opts.captureSource, "Capture source (monitor, window, etc.)");
    m_impl->app.add_option("--upscaler", opts.upscaler, "Upscaler to use (Off, FSR 1.0, Integer, etc.)");
    m_impl->app.add_option("--frame-gen", opts.frameGen, "Frame generation mode (Off, Interpolate)");
    m_impl->app.add_option("--sharpness", opts.sharpness, "Sharpness for applicable upscalers (0.0-2.0)");
    m_impl->app.add_option("--scale", opts.scaleFactor, "Scale factor for integer scaling (1-6)");
    m_impl->app.add_flag("--no-vsync", opts.vsync, "Disable vsync")->set_default_str("false");
    m_impl->app.add_flag("--no-overlay", opts.noOverlay, "Hide the overlay UI");
    m_impl->app.add_flag("--list-sources", opts.listSources, "List available capture sources");
    m_impl->app.add_flag("--list-effects", opts.listEffects, "List available effects");
    m_impl->app.add_option("--width", opts.width, "Output width");
    m_impl->app.add_option("--height", opts.height, "Output height");
    m_impl->app.add_option("--fps", opts.fps, "Target FPS");

    try {
        m_impl->app.parse(argc, argv);
    } catch (const CLI::ParseError& e) {
        if (opts.version) {
            printVersion();
            exit(0);
        }
        m_impl->app.exit(e);
        exit(e.get_exit_code());
    }

    return opts;
}

void CliParser::printHelp() const {
    std::cout << m_impl->app.help() << std::endl;
}

void CliParser::printVersion() const {
    std::cout << "FreeGen v" << FREEGEN_VERSION_MAJOR << "."
              << FREEGEN_VERSION_MINOR << "."
              << FREEGEN_VERSION_PATCH << std::endl;
}

} // namespace freegen
