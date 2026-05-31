find_package(GTest CONFIG REQUIRED)

enable_testing()

function(add_freegen_test test_name test_source)
    add_executable(${test_name} ${test_source})
    target_link_libraries(${test_name} PRIVATE
        freegen
        GTest::GTest
        GTest::Main
    )
    add_test(NAME ${test_name} COMMAND ${test_name})
endfunction()

add_freegen_test(test_config test_config.cpp)
add_freegen_test(test_effects test_effects.cpp)
add_freegen_test(test_compute test_compute_pipeline.cpp)
