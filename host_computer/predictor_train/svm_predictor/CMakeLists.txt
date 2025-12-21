cmake_minimum_required(VERSION 3.15)
project(onnx_spectrum_predictor)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ONNX Runtime 路径（用户指定的路径）
set(ONNXRUNTIME_ROOT 
    "/media/linxi-ice-2/CCCOMA_X64FRE_ZH-CN_DV9/test1/c_sklearn_test/c++_run_module/pretrain_onnxruntime/onnxruntime"
)

# 设置 ONNX Runtime 包含目录和库目录
set(ONNXRUNTIME_INCLUDE_DIRS "${ONNXRUNTIME_ROOT}/include")
set(ONNXRUNTIME_LIB_DIR "${ONNXRUNTIME_ROOT}/lib")

# 检查路径是否存在
if(NOT EXISTS "${ONNXRUNTIME_INCLUDE_DIRS}")
    message(FATAL_ERROR "ONNX Runtime 头文件目录不存在: ${ONNXRUNTIME_INCLUDE_DIRS}")
endif()

if(NOT EXISTS "${ONNXRUNTIME_LIB_DIR}")
    message(FATAL_ERROR "ONNX Runtime 库目录不存在: ${ONNXRUNTIME_LIB_DIR}")
endif()

# 查找 ONNX Runtime 库文件
find_library(ONNXRUNTIME_LIBRARY
    NAMES onnxruntime
    PATHS ${ONNXRUNTIME_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
)

find_library(ONNXRUNTIME_PROVIDERS_SHARED_LIBRARY
    NAMES onnxruntime_providers_shared
    PATHS ${ONNXRUNTIME_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
)

if(ONNXRUNTIME_LIBRARY AND ONNXRUNTIME_PROVIDERS_SHARED_LIBRARY)
    message(STATUS "==========================================")
    message(STATUS "ONNX Runtime 配置:")
    message(STATUS "  根目录: ${ONNXRUNTIME_ROOT}")
    message(STATUS "  包含目录: ${ONNXRUNTIME_INCLUDE_DIRS}")
    message(STATUS "  库目录: ${ONNXRUNTIME_LIB_DIR}")
    message(STATUS "  主库: ${ONNXRUNTIME_LIBRARY}")
    message(STATUS "  提供者库: ${ONNXRUNTIME_PROVIDERS_SHARED_LIBRARY}")
    message(STATUS "==========================================")
else()
    message(FATAL_ERROR "未找到 ONNX Runtime 库文件，请检查路径和库名称")
endif()

# 添加可执行文件
add_executable(onnx_example onnx_example.cpp)

# 包含目录
target_include_directories(onnx_example PRIVATE ${ONNXRUNTIME_INCLUDE_DIRS})

# 链接库
target_link_libraries(onnx_example PRIVATE ${ONNXRUNTIME_LIBRARY})
if(ONNXRUNTIME_PROVIDERS_SHARED)
    target_link_libraries(onnx_example PRIVATE ${ONNXRUNTIME_PROVIDERS_SHARED})
endif()

# 编译选项
target_compile_options(onnx_example PRIVATE -Wall -Wextra)

# 设置运行时库路径（RPATH），这样运行时就不需要设置 LD_LIBRARY_PATH
set_target_properties(onnx_example PROPERTIES
    INSTALL_RPATH "${ONNXRUNTIME_LIB_DIR}"
    BUILD_WITH_INSTALL_RPATH TRUE
    INSTALL_RPATH_USE_LINK_PATH TRUE
)

# 设置构建时的 RPATH（用于直接运行 build 目录中的可执行文件）
set_target_properties(onnx_example PROPERTIES
    BUILD_RPATH "${ONNXRUNTIME_LIB_DIR}"
)

# 安装规则（可选）
install(TARGETS onnx_example
    RUNTIME DESTINATION bin
)

# 打印使用说明
message(STATUS "")
message(STATUS "编译完成后，运行程序:")
message(STATUS "  LD_LIBRARY_PATH=${ONNXRUNTIME_LIB_DIR}:\$LD_LIBRARY_PATH ./onnx_example <model_path>")
message(STATUS "")

