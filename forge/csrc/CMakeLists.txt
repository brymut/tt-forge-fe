set(PYTHON_SITE_PACKAGES_DIR ${TTFORGE_VENV_DIR}/lib/${TTFORGE_PYTHON_VERSION}/site-packages)

set(CMAKE_PREFIX_PATH
    ${PYTHON_SITE_PACKAGES_DIR}/torch
    ${CMAKE_PREFIX_PATH})

find_package(Python3 COMPONENTS Development REQUIRED)
find_package(Torch REQUIRED)

set(TT_MLIR_ROOT_DIR ${CMAKE_SOURCE_DIR}/third_party/tt-mlir)
set(TTMLIR_INCLUDE_DIRS
    ${TT_MLIR_ROOT_DIR}/include
    ${TT_MLIR_ROOT_DIR}/build/include
    ${TT_MLIR_ROOT_DIR}/tools/ttnn-standalone
)

set(TTFORGE_CSRC_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/third_party
    ${CMAKE_SOURCE_DIR}/third_party/fmt/include
    ${CMAKE_SOURCE_DIR}/third_party/pybind11/include
    ${CMAKE_SOURCE_DIR}/third_party/json/single_include
    ${CMAKE_SOURCE_DIR}/third_party/pybind11_json/include
    ${CMAKE_SOURCE_DIR}/third_party/tt-mlir/build/include
    ${CMAKE_SOURCE_DIR}/third_party/tt-mlir/runtime/include
    ${CMAKE_SOURCE_DIR}/third_party/tt-mlir/include
    ${TTMLIR_TOOLCHAIN_DIR}/include
    ${Python3_INCLUDE_DIRS}
    ${TTMLIR_INCLUDE_DIRS}
)

include_directories(${TTFORGE_CSRC_INCLUDES})
# This is workaround for utils/assert.hpp using ##__VA_ARGS__ which is not supported by clang
include_directories(SYSTEM ${CMAKE_SOURCE_DIR})
include_directories(SYSTEM ${TORCH_INCLUDE_DIRS})

add_subdirectory(graph_lib)
add_subdirectory(autograd)
add_subdirectory(shared_utils)
add_subdirectory(backend_api)
add_subdirectory(reportify)
add_subdirectory(runtime)
add_subdirectory(test)
add_subdirectory(verif)
add_subdirectory(ops)

### ttforge_csrc_objs ###

file(GLOB CPP_FILES
    "forge_bindings.cpp"
    "forge_passes.cpp"
    "passes/*.cpp"
    "lower_to_forge/common.cpp"
)

add_library(ttforge_csrc_objs OBJECT ${CPP_FILES})
target_compile_options(ttforge_csrc_objs PRIVATE ${STATIC_LIB_FLAGS} ${TTFORGE_CSRC_CFLAGS})
add_dependencies(ttforge_csrc_objs tt-mlir)

### End of ttforge_csrc_objs ###

######## ttforge_csrc ########

set(TTMLIR_LIB_DIR "${CMAKE_SOURCE_DIR}/third_party/tt-mlir/build/install/lib")
set(TORCH_LIB_DIR "${TTFORGE_VENV_DIR}/lib/${TTFORGE_PYTHON_VERSION}/site-packages/torch/lib")

add_library(ttforge_csrc SHARED)

set(METAL_LIB_DIR "${CMAKE_SOURCE_DIR}/third_party/tt-mlir/third_party/tt-metal/src/tt-metal/build/lib")

# Because _ttnn library doesn't have lib prefix, this is workaround to make linking work
add_library(ttnn SHARED IMPORTED)
set_property(TARGET ttnn PROPERTY IMPORTED_LOCATION "${METAL_LIB_DIR}/_ttnn.so")

target_link_libraries(ttforge_csrc PRIVATE
    graph
    autograd
    shared_utils
    backend_api
    reportify
    runtime
    runtime_testutils
    ttforge_csrc_objs
    verif
    ops

    TTMLIRCompiler
    TTMLIRRuntime
    TTNNCompileSo

    xml2
    curses
    z
    m
    torch_python
    c10
    ${TTFORGE_PYTHON_VERSION}
    ${TORCH_LIBRARIES}
)

target_link_libraries(ttforge_csrc PUBLIC coverage_config)

target_compile_options(ttforge_csrc PRIVATE
    ${TTFORGE_CSRC_CFLAGS}
    ${CXXFLAGS}
    ${SHARED_LIB_FLAGS}
)

target_link_directories(ttforge_csrc PRIVATE
    ${TTMLIR_TOOLCHAIN_DIR}/lib
    ${TTMLIR_LIB_DIR}
    ${TORCH_LIB_DIR})

# Change the output name (the part after 'lib' and before '.so')
set_target_properties(ttforge_csrc PROPERTIES
    OUTPUT_NAME "_C" # Rename to _C instead of ttforge_csrc, so that it can be imported in python as `import forge._C`
    PREFIX "" # Remove the 'lib' prefix
    SUFFIX ".so"
    INSTALL_RPATH "$ORIGIN:$ORIGIN/lib"
)

### End of ttforge_csrc ###

#### Copy python module extension to ttforge directory ####

add_custom_target(run_after_ttforge_csrc ALL
    COMMAND mkdir -p ${TTFORGE_VENV_DIR}/lib/${TTFORGE_PYTHON_VERSION}/site-packages/forge
    COMMAND cp $<TARGET_FILE:ttforge_csrc> ${TTFORGE_VENV_DIR}/lib/${TTFORGE_PYTHON_VERSION}/site-packages/forge/_C.so
    COMMAND touch -r $<TARGET_FILE:ttforge_csrc> ${TTFORGE_VENV_DIR}/lib/${TTFORGE_PYTHON_VERSION}/site-packages/forge/_C.so
    COMMAND ln -sf ${TTFORGE_VENV_DIR}/lib/${TTFORGE_PYTHON_VERSION}/site-packages/forge/_C.so ${CMAKE_SOURCE_DIR}/forge/forge/_C.so
    COMMENT "Running run_after_ttforge_csrc to copy the python module extension to forge directory"
    USES_TERMINAL
)

add_dependencies(run_after_ttforge_csrc ttforge_csrc)
