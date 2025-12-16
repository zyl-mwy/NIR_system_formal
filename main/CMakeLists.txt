cmake_minimum_required(VERSION 3.10)
project(test_split_algo_qml6 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# 自动查找用户目录下的Qt6
if(NOT DEFINED CMAKE_PREFIX_PATH)
    file(GLOB QT6_PATHS "$ENV{HOME}/Qt/6.*/gcc_*")
    if(QT6_PATHS)
        list(GET QT6_PATHS 0 QT6_PATH)
        set(CMAKE_PREFIX_PATH ${QT6_PATH} ${CMAKE_PREFIX_PATH})
        message(STATUS "Found Qt6 at: ${QT6_PATH}")
    endif()
endif()

find_package(Qt6 REQUIRED COMPONENTS Quick Qml Network)

add_subdirectory(plugins)

add_executable(calc_app
  src/main.cpp
  src/plugin_manager.cpp
  src/plugin_manager.h
  src/plugin_interface.h
  src/serial_communicator.cpp
  src/serial_communicator.h
  src/udp_receiver.cpp
  src/udp_receiver.h
  src/udp_communicator.cpp
  src/udp_communicator.h
  src/spectrum_processor.cpp
  src/spectrum_processor.h
  src/reference_processor.cpp
  src/reference_processor.h
  src/spectrum_predictor_manager.cpp
  src/spectrum_predictor_manager.h
  src/spectrum_predictor_interface.h
  resources/qml.qrc
)

target_link_libraries(calc_app PRIVATE Qt6::Quick Qt6::Qml Qt6::Network)
target_include_directories(calc_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# 添加插件依赖（PyTorch 插件可选，如果 libtorch 路径不存在则跳过）
set(PLUGIN_DEPENDENCIES add_plugin sub_plugin mul_plugin rf_predictor_plugin svm_predictor_plugin)
if(TARGET pytorch_predictor_plugin)
    list(APPEND PLUGIN_DEPENDENCIES pytorch_predictor_plugin)
endif()
add_dependencies(calc_app ${PLUGIN_DEPENDENCIES})

