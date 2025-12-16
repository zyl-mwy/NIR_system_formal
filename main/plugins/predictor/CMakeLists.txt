find_package(Qt6 REQUIRED COMPONENTS Core)

# ONNX Runtime 路径
set(ONNXRUNTIME_ROOT 
    "/media/linxi-ice-2/CCCOMA_X64FRE_ZH-CN_DV9/test1/c_sklearn_test/c++_run_module/pretrain_onnxruntime/onnxruntime"
)
set(ONNXRUNTIME_INCLUDE_DIRS "${ONNXRUNTIME_ROOT}/include")
set(ONNXRUNTIME_LIB_DIR "${ONNXRUNTIME_ROOT}/lib")

# 预测插件（随机森林 - 固定1024输入）
add_library(rf_predictor_plugin MODULE rf_predictor_plugin.cpp)

# 预测插件（支持向量机 - 动态检测输入）
add_library(svm_predictor_plugin MODULE svm_predictor_plugin.cpp)

# PyTorch (libtorch) 路径
set(LIBTORCH_ROOT 
    "/media/linxi-ice-2/CCCOMA_X64FRE_ZH-CN_DV9/test1/c_libtorch_test/libtorch"
)
set(LIBTORCH_INCLUDE_DIRS "${LIBTORCH_ROOT}/include")
set(LIBTORCH_LIB_DIR "${LIBTORCH_ROOT}/lib")

# 预测插件（PyTorch - 固定1024输入，使用 JIT 格式）
add_library(pytorch_predictor_plugin MODULE pytorch_predictor_plugin.cpp)

# PyTorch 插件配置
if(EXISTS "${LIBTORCH_ROOT}")
  target_link_libraries(pytorch_predictor_plugin PRIVATE Qt6::Core)
  target_include_directories(pytorch_predictor_plugin PRIVATE 
    ${CMAKE_SOURCE_DIR}/src
    ${LIBTORCH_INCLUDE_DIRS}
    ${LIBTORCH_INCLUDE_DIRS}/torch/csrc/api/include
  )
  
  # 查找所有必要的 libtorch 库
  find_library(TORCH_LIBRARY
    NAMES torch
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
  )
  
  find_library(C10_LIBRARY
    NAMES c10
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
  )
  
  find_library(TORCH_CPU_LIBRARY
    NAMES torch_cpu
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
  )
  
  find_library(TORCH_GLOBAL_DEPS_LIBRARY
    NAMES torch_global_deps
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED
  )
  
  find_library(TORCH_CUDA_LIBRARY
    NAMES torch_cuda
    PATHS ${LIBTORCH_LIB_DIR}
    NO_DEFAULT_PATH
  )
  
  # 按依赖顺序链接库
  target_link_libraries(pytorch_predictor_plugin PRIVATE 
    ${C10_LIBRARY}
    ${TORCH_GLOBAL_DEPS_LIBRARY}
    ${TORCH_CPU_LIBRARY}
    ${TORCH_LIBRARY}
  )
  
  if(TORCH_CUDA_LIBRARY)
    target_link_libraries(pytorch_predictor_plugin PRIVATE ${TORCH_CUDA_LIBRARY})
  endif()
  
  # 获取 Qt6 库路径
  get_target_property(QT6_CORE_LOCATION Qt6::Core LOCATION)
  get_filename_component(QT6_LIB_DIR ${QT6_CORE_LOCATION} DIRECTORY)
  
  # 设置运行时库路径（包括 Qt6 和 libtorch）
  set_target_properties(pytorch_predictor_plugin PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/plugins
    PREFIX ""
    BUILD_RPATH "${LIBTORCH_LIB_DIR}:${QT6_LIB_DIR}"
    INSTALL_RPATH "${LIBTORCH_LIB_DIR}:${QT6_LIB_DIR}"
    BUILD_WITH_INSTALL_RPATH TRUE
  )
  
  message(STATUS "PyTorch 插件配置成功")
  message(STATUS "  Qt6 库目录: ${QT6_LIB_DIR}")
  message(STATUS "  libtorch 库目录: ${LIBTORCH_LIB_DIR}")
else()
  message(WARNING "libtorch 路径不存在: ${LIBTORCH_ROOT}，PyTorch 插件将被跳过")
endif()

foreach(target rf_predictor_plugin svm_predictor_plugin)
  target_link_libraries(${target} PRIVATE Qt6::Core)
  target_include_directories(${target} PRIVATE 
    ${CMAKE_SOURCE_DIR}/src
    ${ONNXRUNTIME_INCLUDE_DIRS}
  )
  
  # 链接 ONNX Runtime 库
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
  
  target_link_libraries(${target} PRIVATE 
    ${ONNXRUNTIME_LIBRARY} 
    ${ONNXRUNTIME_PROVIDERS_SHARED_LIBRARY}
  )
  
  # 设置运行时库路径
  set_target_properties(${target} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/plugins
    PREFIX ""  # 生成名称如 rf_predictor_plugin.so
    BUILD_RPATH "${ONNXRUNTIME_LIB_DIR}"
    INSTALL_RPATH "${ONNXRUNTIME_LIB_DIR}"
    BUILD_WITH_INSTALL_RPATH TRUE
  )
endforeach()


