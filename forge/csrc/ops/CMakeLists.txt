add_library(ops
    STATIC
    op.cpp
    op_common.cpp
    op_abs.cpp
    op_add.cpp
    op_concatenate.cpp
    op_constant.cpp
    op_cosine.cpp
    op_divide.cpp
    op_multiply.cpp
    op_sine.cpp
    op_transpose.cpp
    op_reshape.cpp
    op_subtract.cpp
    python_bindings.cpp)

target_link_libraries(ops PUBLIC coverage_config)

target_compile_options(ops PRIVATE ${STATIC_LIB_FLAGS} ${TTFORGE_CSRC_CFLAGS})
