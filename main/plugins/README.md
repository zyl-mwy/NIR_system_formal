# 插件目录说明

## 目录结构

```
plugins/
├── CMakeLists.txt          # 主 CMakeLists，包含子目录
├── calc/                   # 计算插件目录
│   ├── CMakeLists.txt     # 计算插件编译配置
│   ├── add_plugin.cpp      # 加法插件
│   ├── sub_plugin.cpp      # 减法插件
│   ├── mul_plugin.cpp      # 乘法插件
│   └── div_plugin.cpp      # 除法插件（可选）
└── predictor/             # 预测插件目录
    ├── CMakeLists.txt     # 预测插件编译配置
    ├── rf_predictor_plugin.cpp    # 随机森林预测插件（固定1024输入）
    └── svm_predictor_plugin.cpp    # 支持向量机预测插件（动态检测输入）
```

## 插件分类

### calc/ - 计算插件
- **功能**: 基本的数学运算（加、减、乘、除）
- **接口**: `CalcPlugin` (`src/plugin_interface.h`)
- **管理器**: `PluginManager` (`src/plugin_manager.h/cpp`)
- **特点**: 简单的双参数计算

### predictor/ - 预测插件
- **功能**: 光谱数据机器学习预测
- **接口**: `SpectrumPredictorPlugin` (`src/spectrum_predictor_interface.h`)
- **管理器**: `SpectrumPredictorManager` (`src/spectrum_predictor_manager.h/cpp`)
- **特点**: 
  - 使用 ONNX Runtime 进行推理
  - 支持两种算法：随机森林（RF）和支持向量机（SVM）
  - 需要加载 ONNX 模型文件

## 编译说明

### 主 CMakeLists.txt
`plugins/CMakeLists.txt` 通过 `add_subdirectory()` 包含两个子目录：
```cmake
add_subdirectory(calc)
add_subdirectory(predictor)
```

### 计算插件编译
- 依赖: Qt6 Core
- 输出: `build/plugins/add_plugin.so`, `sub_plugin.so`, `mul_plugin.so`

### 预测插件编译
- 依赖: Qt6 Core, ONNX Runtime
- 输出: `build/plugins/rf_predictor_plugin.so`, `svm_predictor_plugin.so`
- ONNX Runtime 路径配置在 `predictor/CMakeLists.txt` 中

## 插件加载

### 计算插件
- 由 `PluginManager` 自动从 `build/plugins/` 目录加载
- 通过 `qobject_cast<CalcPlugin *>` 识别

### 预测插件
- 由 `SpectrumPredictorManager` 自动从 `build/plugins/` 目录加载
- 通过文件名包含 `predictor_plugin` 识别
- 通过 `qobject_cast<SpectrumPredictorPlugin *>` 识别

## 添加新插件

### 添加新的计算插件
1. 在 `calc/` 目录创建新的 `.cpp` 文件
2. 实现 `CalcPlugin` 接口
3. 在 `calc/CMakeLists.txt` 中添加编译配置

### 添加新的预测插件
1. 在 `predictor/` 目录创建新的 `.cpp` 文件
2. 实现 `SpectrumPredictorPlugin` 接口
3. 在 `predictor/CMakeLists.txt` 中添加编译配置
4. 确保文件名包含 `predictor_plugin`

## 注意事项

1. **输出目录**: 所有插件都输出到 `build/plugins/` 目录（统一管理）
2. **命名规范**: 
   - 计算插件: `*_plugin.cpp`
   - 预测插件: `*_predictor_plugin.cpp`
3. **依赖管理**: 
   - 计算插件只需要 Qt6 Core
   - 预测插件需要 Qt6 Core 和 ONNX Runtime
4. **路径引用**: 子目录的 CMakeLists.txt 使用 `${CMAKE_SOURCE_DIR}` 引用项目根目录


