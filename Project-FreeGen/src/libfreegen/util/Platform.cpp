#include "freegen/util/Platform.hpp"

#ifdef _WIN32
#include <windows.h>
#include <versionhelpers.h>
#else
#include <unistd.h>
#include <sys/utsname.h>
#include <algorithm>
#include <fstream>
#include <cstring>
#endif

namespace freegen {

std::string Platform::osName() {
#ifdef _WIN32
    return "Windows";
#elif __APPLE__
    return "macOS";
#elif __linux__
    return "Linux";
#else
    return "Unknown";
#endif
}

std::string Platform::osVersion() {
#ifdef _WIN32
    return "Windows 10+";
#elif __linux__
    struct utsname buf;
    uname(&buf);
    return buf.release;
#else
    return "Unknown";
#endif
}

std::string Platform::hostname() {
    char buf[256] = {0};
#ifdef _WIN32
    DWORD size = sizeof(buf);
    GetComputerNameA(buf, &size);
#else
    gethostname(buf, sizeof(buf));
#endif
    return buf;
}

std::string Platform::userName() {
    const char* user = std::getenv("USER");
    if (!user) user = std::getenv("USERNAME");
    if (!user) user = "unknown";
    return user;
}

uint64_t Platform::totalMemoryBytes() {
#ifdef _WIN32
    MEMORYSTATUSEX status = {sizeof(MEMORYSTATUSEX)};
    GlobalMemoryStatusEx(&status);
    return status.ullTotalPhys;
#elif __linux__
    long pages = sysconf(_SC_PHYS_PAGES);
    long pageSize = sysconf(_SC_PAGE_SIZE);
    return static_cast<uint64_t>(pages) * static_cast<uint64_t>(pageSize);
#else
    return 0;
#endif
}

uint64_t Platform::availableMemoryBytes() {
#ifdef _WIN32
    MEMORYSTATUSEX status = {sizeof(MEMORYSTATUSEX)};
    GlobalMemoryStatusEx(&status);
    return status.ullAvailPhys;
#elif __linux__
    long pages = sysconf(_SC_AVPHYS_PAGES);
    long pageSize = sysconf(_SC_PAGE_SIZE);
    return static_cast<uint64_t>(pages) * static_cast<uint64_t>(pageSize);
#else
    return 0;
#endif
}

int Platform::cpuCoreCount() {
#ifdef _WIN32
    SYSTEM_INFO sysinfo;
    GetSystemInfo(&sysinfo);
    return sysinfo.dwNumberOfProcessors;
#else
    return static_cast<int>(sysconf(_SC_NPROCESSORS_ONLN));
#endif
}

std::string Platform::cpuName() {
#ifdef __linux__
    std::ifstream cpuinfo("/proc/cpuinfo");
    std::string line;
    while (std::getline(cpuinfo, line)) {
        if (line.find("model name") != std::string::npos) {
            auto pos = line.find(':');
            if (pos != std::string::npos) {
                return line.substr(pos + 2);
            }
        }
    }
#endif
    return "Unknown";
}

std::string Platform::gpuName() {
    return "Unknown (query via Vulkan)";
}

std::string Platform::configDir() {
    const char* xdg = std::getenv("XDG_CONFIG_HOME");
    if (xdg) return std::string(xdg) + "/freegen";
    const char* home = std::getenv("HOME");
    if (home) return std::string(home) + "/.config/freegen";
    return "./config";
}

std::string Platform::dataDir() {
    const char* xdg = std::getenv("XDG_DATA_HOME");
    if (xdg) return std::string(xdg) + "/freegen";
    const char* home = std::getenv("HOME");
    if (home) return std::string(home) + "/.local/share/freegen";
    return "./data";
}

std::vector<std::string> Platform::runningProcesses() {
    std::vector<std::string> processes;
#ifdef __linux__
    for (const auto& entry : std::filesystem::directory_iterator("/proc")) {
        if (entry.is_directory()) {
            std::string name = entry.path().filename().string();
            if (!name.empty() && std::all_of(name.begin(), name.end(), ::isdigit)) {
                std::ifstream cmdline(entry.path() / "comm");
                std::string comm;
                if (std::getline(cmdline, comm)) {
                    processes.push_back(comm);
                }
            }
        }
    }
#endif
    return processes;
}

std::string Platform::currentProcessName() {
#ifdef __linux__
    std::ifstream cmdline("/proc/self/comm");
    std::string name;
    if (std::getline(cmdline, name)) return name;
#endif
    return "freegen";
}

uint32_t Platform::currentProcessId() {
#ifdef _WIN32
    return static_cast<uint32_t>(GetCurrentProcessId());
#else
    return static_cast<uint32_t>(getpid());
#endif
}

} // namespace freegen
