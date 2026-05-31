if(FREEGEN_BUILD_SHADERS)
    add_shader_target(freegen_shaders "${CMAKE_SOURCE_DIR}/shaders" "${CMAKE_BINARY_DIR}/shaders")
endif()

add_executable(freegen main.cpp)

target_link_libraries(freegen PRIVATE freegen)

target_compile_definitions(freegen PRIVATE
    FREEGEN_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    FREEGEN_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    FREEGEN_VERSION_PATCH=${PROJECT_VERSION_PATCH}
)

if(FREEGEN_BUILD_SHADERS)
    add_dependencies(freegen freegen_shaders)
endif()

set_project_warnings(freegen)
enable_sanitizers(freegen)

install(TARGETS freegen RUNTIME DESTINATION bin)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include)
