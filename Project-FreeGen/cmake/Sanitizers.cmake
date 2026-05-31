function(enable_sanitizers project_name)
    option(FREEGEN_ENABLE_SANITIZERS "Enable sanitizers" OFF)

    if(NOT FREEGEN_ENABLE_SANITIZERS)
        return()
    endif()

    if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
        message(WARNING "Sanitizers not supported on MSVC")
        return()
    endif()

    set(SANITIZERS
        -fsanitize=address
        -fsanitize=undefined
        -fno-sanitize-recover=all
        -fno-omit-frame-pointer
    )

    target_compile_options(${project_name} PRIVATE ${SANITIZERS})
    target_link_options(${project_name} PRIVATE ${SANITIZERS})
endfunction()
