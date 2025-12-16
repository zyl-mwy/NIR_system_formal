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


