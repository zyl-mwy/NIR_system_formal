find_package(Qt6 REQUIRED COMPONENTS Core)

add_library(add_plugin MODULE add_plugin.cpp)
add_library(sub_plugin MODULE sub_plugin.cpp)
add_library(mul_plugin MODULE mul_plugin.cpp)
# add_library(div_plugin MODULE div_plugin.cpp)

foreach(target add_plugin sub_plugin mul_plugin) # div_plugin
  target_link_libraries(${target} PRIVATE Qt6::Core)
  target_include_directories(${target} PRIVATE ${CMAKE_SOURCE_DIR}/src)
  set_target_properties(${target} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/plugins
    PREFIX ""  # 生成名称如 add_plugin.so，便于加载
  )
endforeach()

