function(add_shader_target target_name shader_dir output_dir)
    file(GLOB_RECURSE SHADER_SOURCES "${shader_dir}/*.vert" "${shader_dir}/*.frag" "${shader_dir}/*.comp")

    foreach(shader ${SHADER_SOURCES})
        file(RELATIVE_PATH rel_path "${shader_dir}" "${shader}")
        set(spv_output "${output_dir}/${rel_path}.spv")

        get_filename_component(shader_stage "${shader}" LAST_EXT)
        if(shader_stage STREQUAL ".vert")
            set(stage_flag "vert")
        elseif(shader_stage STREQUAL ".frag")
            set(stage_flag "frag")
        elseif(shader_stage STREQUAL ".comp")
            set(stage_flag "comp")
        else()
            continue()
        endif()

        add_custom_command(
            OUTPUT "${spv_output}"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${output_dir}/${rel_path}/.."
            COMMAND glslc -fshader-stage=${stage_flag} "${shader}" -o "${spv_output}"
            DEPENDS "${shader}"
            COMMENT "Compiling ${rel_path} -> ${rel_path}.spv"
        )
        list(APPEND SPV_OUTPUTS "${spv_output}")
    endforeach()

    add_custom_target(${target_name} ALL DEPENDS ${SPV_OUTPUTS})
endfunction()
