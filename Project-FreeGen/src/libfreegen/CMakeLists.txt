file(GLOB_RECURSE FREEGEN_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
)

add_library(freegen STATIC ${FREEGEN_SOURCES})

target_include_directories(freegen PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${Vulkan_INCLUDE_DIRS}
)

target_link_libraries(freegen PUBLIC
    Vulkan::Vulkan
    fmt::fmt
    spdlog::spdlog
    CLI11::CLI11
    nlohmann_json::nlohmann_json
    glm::glm
    SDL2::SDL2
)

if(UNIX AND NOT APPLE)
    target_compile_definitions(freegen PRIVATE FREEGEN_LINUX_CAPTURE)
    target_include_directories(freegen PRIVATE ${PIPEWIRE_INCLUDE_DIRS} ${DBUS_INCLUDE_DIRS})
    target_link_libraries(freegen PRIVATE ${PIPEWIRE_LIBRARIES} ${DBUS_LIBRARIES})
endif()

if(WIN32)
    target_compile_definitions(freegen PRIVATE FREEGEN_WINDOWS_CAPTURE)
endif()

set_project_warnings(freegen)
enable_sanitizers(freegen)
