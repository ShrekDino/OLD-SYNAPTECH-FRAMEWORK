#pragma once

#include <memory>
#include <string>

namespace freegen {

class Logger {
public:
    enum class Level {
        Trace,
        Debug,
        Info,
        Warn,
        Error,
        Critical,
        Off
    };

    static void init(Level level = Level::Info);
    static void setLevel(Level level);

    static void trace(const std::string& msg);
    static void debug(const std::string& msg);
    static void info(const std::string& msg);
    static void warn(const std::string& msg);
    static void error(const std::string& msg);
    static void critical(const std::string& msg);

    static Level levelFromString(const std::string& str);
    static std::string levelToString(Level level);

private:
    static Level s_level;
};

} // namespace freegen
