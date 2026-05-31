#pragma once

#define FREEGEN_VERSION_MAJOR 0
#define FREEGEN_VERSION_MINOR 1
#define FREEGEN_VERSION_PATCH 0

#define FREEGEN_VERSION_STRING "0.1.0"

namespace freegen {
inline constexpr int kVersionMajor = FREEGEN_VERSION_MAJOR;
inline constexpr int kVersionMinor = FREEGEN_VERSION_MINOR;
inline constexpr int kVersionPatch = FREEGEN_VERSION_PATCH;
inline constexpr const char* kVersionString = FREEGEN_VERSION_STRING;
inline constexpr const char* kAppName = "FreeGen";
} // namespace freegen
