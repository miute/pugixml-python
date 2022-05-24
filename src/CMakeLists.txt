cmake_minimum_required(VERSION 3.12)

cmake_policy(SET CMP0074 NEW)

project(pugi LANGUAGES CXX)

set(DESTDIR ${PROJECT_SOURCE_DIR}/pugixml)

add_compile_definitions(PUGIXML_NO_EXCEPTIONS)

add_subdirectory(third_party/pybind11)
add_subdirectory(third_party/pugixml EXCLUDE_FROM_ALL)

pybind11_add_module(
    ${PROJECT_NAME}
    main.cpp
)

target_compile_features(
    ${PROJECT_NAME}
    PRIVATE
    cxx_std_17
)

target_compile_definitions(
    ${PROJECT_NAME}
    PRIVATE
    MODULE_NAME=${PROJECT_NAME}
)

target_link_libraries(
    ${PROJECT_NAME}
    PRIVATE
    pugixml
)

set_target_properties(
    pugixml-static
    PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)

set_target_properties(
    ${PROJECT_NAME}
    PROPERTIES
    INTERPROCEDURAL_OPTIMIZATION ON
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)

pybind11_extension(${PROJECT_NAME})

install(
    TARGETS
    ${PROJECT_NAME}
    LIBRARY
    DESTINATION ${DESTDIR}
)
