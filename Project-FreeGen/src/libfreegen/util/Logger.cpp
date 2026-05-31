#include "freegen/util/Logger.hpp"
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>

namespace freegen {

Logger::Level Logger::s_level = Logger::Level::Info;

void Logger::init(Level level) {
    s_level = level;

    auto sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    sink->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%^%l%$] %v");

    auto logger = std::make_shared<spdlog::logger>("freegen", sink);
    spdlog::set_default_logger(logger);

    switch (level) {
    case Level::Trace:    spdlog::set_level(spdlog::level::trace); break;
    case Level::Debug:    spdlog::set_level(spdlog::level::debug); break;
    case Level::Info:     spdlog::set_level(spdlog::level::info); break;
    case Level::Warn:     spdlog::set_level(spdlog::level::warn); break;
    case Level::Error:    spdlog::set_level(spdlog::level::err); break;
    case Level::Critical: spdlog::set_level(spdlog::level::critical); break;
    case Level::Off:      spdlog::set_level(spdlog::level::off); break;
    }

    spdlog::info("Logger initialized (level: {})", levelToString(level));
}

void Logger::setLevel(Level level) {
    s_level = level;
    switch (level) {
    case Level::Trace:    spdlog::set_level(spdlog::level::trace); break;
    case Level::Debug:    spdlog::set_level(spdlog::level::debug); break;
    case Level::Info:     spdlog::set_level(spdlog::level::info); break;
    case Level::Warn:     spdlog::set_level(spdlog::level::warn); break;
    case Level::Error:    spdlog::set_level(spdlog::level::err); break;
    case Level::Critical: spdlog::set_level(spdlog::level::critical); break;
    case Level::Off:      spdlog::set_level(spdlog::level::off); break;
    }
}

void Logger::trace(const std::string& msg) { spdlog::trace(msg); }
void Logger::debug(const std::string& msg) { spdlog::debug(msg); }
void Logger::info(const std::string& msg) { spdlog::info(msg); }
void Logger::warn(const std::string& msg) { spdlog::warn(msg); }
void Logger::error(const std::string& msg) { spdlog::error(msg); }
void Logger::critical(const std::string& msg) { spdlog::critical(msg); }

Logger::Level Logger::levelFromString(const std::string& str) {
    if (str == "trace") return Level::Trace;
    if (str == "debug") return Level::Debug;
    if (str == "info") return Level::Info;
    if (str == "warn") return Level::Warn;
    if (str == "error") return Level::Error;
    if (str == "critical") return Level::Critical;
    if (str == "off") return Level::Off;
    return Level::Info;
}

std::string Logger::levelToString(Level level) {
    switch (level) {
    case Level::Trace:    return "trace";
    case Level::Debug:    return "debug";
    case Level::Info:     return "info";
    case Level::Warn:     return "warn";
    case Level::Error:    return "error";
    case Level::Critical: return "critical";
    case Level::Off:      return "off";
    }
    return "unknown";
}

} // namespace freegen
