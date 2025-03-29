cmake_minimum_required(VERSION 3.15...3.30)

cmake_policy(SET CMP0074 NEW)

project(pugi LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
set(DESTDIR pugixml CACHE STRING "The directory where the binaries will be written. (e.g., path/to/pugixml/src/pugixml)")
message(STATUS "DESTDIR: ${DESTDIR}")
add_compile_definitions(PUGIXML_NO_EXCEPTIONS)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
add_subdirectory(src/third_party/pybind11)
add_subdirectory(src/third_party/pugixml EXCLUDE_FROM_ALL)

python_add_library(
    ${PROJECT_NAME}
    MODULE
    src/main.cpp
    WITH_SOABI
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

target_include_directories(
    ${PROJECT_NAME}
    PRIVATE
    ${Python3_INCLUDE_DIRS}
    src/third_party/pybind11/include
)

target_link_libraries(
    ${PROJECT_NAME}
    PRIVATE
    pybind11::headers
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

install(
    TARGETS
    ${PROJECT_NAME}
    LIBRARY
    DESTINATION ${DESTDIR}
)
