function(set_project_warnings project_name)
    option(FREEGEN_WARNINGS_AS_ERRORS "Treat compiler warnings as errors" OFF)

    set(MSVC_WARNINGS
        /W4
        /w14242 /w14254 /w14263 /w14265 /w14287 /w14296
        /w14311 /w14545 /w14546 /w14547 /w14549 /w14555 /w16064
        /w16082 /w16061
    )

    set(CLANG_WARNINGS
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
        -Wsign-conversion
        -Wshadow
        -Wnon-virtual-dtor
        -Wold-style-cast
        -Wcast-align
        -Wunused
        -Woverloaded-virtual
        -Wdouble-promotion
        -Wformat=2
        -Wnull-dereference
        -Wimplicit-fallthrough
    )

    set(GCC_WARNINGS
        ${CLANG_WARNINGS}
        -Wmisleading-indentation
        -Wduplicated-cond
        -Wduplicated-branches
        -Wlogical-op
        -Wuseless-cast
    )

    if(FREEGEN_WARNINGS_AS_ERRORS)
        set(CLANG_WARNINGS ${CLANG_WARNINGS} -Werror)
        set(GCC_WARNINGS ${GCC_WARNINGS} -Werror)
        set(MSVC_WARNINGS ${MSVC_WARNINGS} /WX)
    endif()

    if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
        target_compile_options(${project_name} PRIVATE ${MSVC_WARNINGS})
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(${project_name} PRIVATE ${CLANG_WARNINGS})
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
        target_compile_options(${project_name} PRIVATE ${GCC_WARNINGS})
    endif()
endfunction()
