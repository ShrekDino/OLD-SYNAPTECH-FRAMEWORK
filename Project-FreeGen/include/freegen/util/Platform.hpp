#pragma once

#include <string>
#include <vector>

namespace freegen {

class Platform {
public:
    static std::string osName();
    static std::string osVersion();
    static std::string hostname();
    static std::string userName();

    static uint64_t totalMemoryBytes();
    static uint64_t availableMemoryBytes();

    static int cpuCoreCount();
    static std::string cpuName();

    static std::string gpuName();

    static std::string configDir();
    static std::string dataDir();

    static std::vector<std::string> runningProcesses();
    static std::string currentProcessName();
    static uint32_t currentProcessId();
};

} // namespace freegen
