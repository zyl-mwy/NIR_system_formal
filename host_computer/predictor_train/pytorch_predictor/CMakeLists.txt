cmake_minimum_required(VERSION 3.15)
project(jit_spectrum_predictor)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# libtorch 路径
set(LIBTORCH_ROOT 
    "/media/linxi-ice-2/CCCOMA_X64FRE_ZH-CN_DV9/test1/c_libtorch_test/libtorch"
)

# 设置 libtorch 包含目录和库目录
set(LIBTORCH_INCLUDE_DIRS "${LIBTORCH_ROOT}/include")
set(LIBTORCH_INCLUDE_DIRS_TORCH "${LIBTORCH_ROOT}/include/torch/csrc/api/include")
set(LIBTORCH_LIB_DIR "${LIBTORCH_ROOT}/lib")

# 检查路径是否存在
if(NOT EXISTS "${LIBTORCH_INCLUDE_DIRS}")
    message(WARNING "libtorch 头文件目录不存在: ${LIBTORCH_INCLUDE_DIRS}")
    message(WARNING "请修改 CMakeLists.txt 中的 LIBTORCH_ROOT 为实际的 libtorch 路径")
    message(FATAL_ERROR "无法继续编译")
endif()

if(NOT EXISTS "${LIBTORCH_LIB_DIR}")
    message(WARNING "libtorch 库目录不存在: ${LIBTORCH_LIB_DIR}")
    message(WARNING "请修改 CMakeLists.txt 中的 LIBTORCH_ROOT 为实际的 libtorch 路径")
    message(FATAL_ERROR "无法继续编译")
endif()

# 查找 libtorch 库文件
find_library(TORCH_LIBRARY
    NAMES torch
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
)

# 查找其他依赖库（可选）
find_library(TORCH_CUDA_LIBRARY
    NAMES torch_cuda
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
)

find_library(C10_LIBRARY
    NAMES c10
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
)

find_library(TORCH_CPU_LIBRARY
    NAMES torch_cpu
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
)

find_library(TORCH_GLOBAL_DEPS_LIBRARY
    NAMES torch_global_deps
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
)

# 输出配置信息
message(STATUS "==========================================")
message(STATUS "libtorch 配置:")
message(STATUS "  根目录: ${LIBTORCH_ROOT}")
message(STATUS "  包含目录: ${LIBTORCH_INCLUDE_DIRS}")
message(STATUS "  库目录: ${LIBTORCH_LIB_DIR}")
message(STATUS "  主库: ${TORCH_LIBRARY}")
if(TORCH_CUDA_LIBRARY)
    message(STATUS "  CUDA 库: ${TORCH_CUDA_LIBRARY}")
endif()
if(C10_LIBRARY)
    message(STATUS "  C10 库: ${C10_LIBRARY}")
endif()
if(TORCH_CPU_LIBRARY)
    message(STATUS "  CPU 库: ${TORCH_CPU_LIBRARY}")
endif()
if(TORCH_GLOBAL_DEPS_LIBRARY)
    message(STATUS "  Global Deps 库: ${TORCH_GLOBAL_DEPS_LIBRARY}")
endif()
message(STATUS "==========================================")

# 添加可执行文件
add_executable(jit_example jit_example.cpp)

# 包含目录
target_include_directories(jit_example PRIVATE 
    ${LIBTORCH_INCLUDE_DIRS}
    ${LIBTORCH_INCLUDE_DIRS_TORCH}
)

# 链接库（按依赖顺序）
# 先链接基础库
if(C10_LIBRARY)
    target_link_libraries(jit_example PRIVATE ${C10_LIBRARY})
endif()

if(TORCH_GLOBAL_DEPS_LIBRARY)
    target_link_libraries(jit_example PRIVATE ${TORCH_GLOBAL_DEPS_LIBRARY})
endif()

# 然后链接 CPU 库
if(TORCH_CPU_LIBRARY)
    target_link_libraries(jit_example PRIVATE ${TORCH_CPU_LIBRARY})
endif()

# 最后链接主库
target_link_libraries(jit_example PRIVATE ${TORCH_LIBRARY})

# CUDA 库（如果存在）
if(TORCH_CUDA_LIBRARY)
    target_link_libraries(jit_example PRIVATE ${TORCH_CUDA_LIBRARY})
endif()

# 编译选项
# 抑制 libtorch 库本身的警告（未使用参数等）
target_compile_options(jit_example PRIVATE 
    -Wall 
    -Wextra
    -Wno-unused-parameter          # 抑制未使用参数警告
    -Wno-sign-compare              # 抑制符号比较警告（已在代码中修复，但保留此选项以防万一）
    -Wno-unused-variable          # 抑制未使用变量警告
    -Wno-unused-function          # 抑制未使用函数警告
    -Wno-deprecated-declarations  # 抑制已弃用声明警告
)

# 设置运行时库路径（RPATH），这样运行时就不需要设置 LD_LIBRARY_PATH
set_target_properties(jit_example PROPERTIES
    INSTALL_RPATH "${LIBTORCH_LIB_DIR}"
    BUILD_WITH_INSTALL_RPATH TRUE
    INSTALL_RPATH_USE_LINK_PATH TRUE
)

# 设置构建时的 RPATH（用于直接运行 build 目录中的可执行文件）
set_target_properties(jit_example PROPERTIES
    BUILD_RPATH "${LIBTORCH_LIB_DIR}"
)

# 安装规则（可选）
install(TARGETS jit_example
    RUNTIME DESTINATION bin
)

# 打印使用说明
message(STATUS "")
message(STATUS "编译完成后，运行程序:")
message(STATUS "  LD_LIBRARY_PATH=${LIBTORCH_LIB_DIR}:\$LD_LIBRARY_PATH ./jit_example <model_path>")
message(STATUS "  或:")
message(STATUS "  ./jit_example <model_path> [input_data_file]")
message(STATUS "")
message(STATUS "示例:")
message(STATUS "  ./jit_example ../spectrum_model.jit")
message(STATUS "  ./jit_example ../spectrum_model.jit input_data.txt")
message(STATUS "")

