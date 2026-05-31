cmake_minimum_required(VERSION 3.24)
project(FreeGen VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(cmake/CompilerWarnings.cmake)
include(cmake/Sanitizers.cmake)
include(cmake/ShaderCompilation.cmake)

option(FREEGEN_ENABLE_TESTS "Enable tests" ON)
option(FREEGEN_BUILD_SHADERS "Build GLSL shaders at compile time" ON)

find_package(Vulkan REQUIRED)
find_package(fmt CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)
find_package(CLI11 CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(glm CONFIG REQUIRED)
find_package(SDL2 CONFIG REQUIRED)

find_package(PkgConfig REQUIRED)
if(UNIX AND NOT APPLE)
    pkg_check_modules(PIPEWIRE REQUIRED libpipewire-0.3)
    pkg_check_modules(DBUS REQUIRED dbus-1)
endif()

add_subdirectory(src/libfreegen)
add_subdirectory(src)

if(FREEGEN_ENABLE_TESTS)
    enable_testing()
    add_subdirectory(src/tests)
endif()
