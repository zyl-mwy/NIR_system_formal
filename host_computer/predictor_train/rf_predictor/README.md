# 随机森林预测器 (Random Forest Predictor)

## 说明

此文件夹包含随机森林预测器的训练和预测程序。

**对应关系：**
- **预测器插件**: `plugins/predictor/rf_predictor_plugin.cpp`
- **算法**: Random Forest Regressor
- **输入维度**: 固定 1024

## 工作流程

### 1. 训练模型

```bash
cd spectrum_training
python3 spectrum_predictor.py
# 生成 spectrum_model.onnx
```

### 2. 使用模型进行预测

**方式1：使用光谱专用程序**
```bash
cd spectrum_onnx
python3 onnx_predictor.py ../spectrum_model.onnx
```

**方式2：使用通用程序**
```bash
cd new_onnx_inference
python3 onnx_data_predictor.py ../spectrum_model.onnx
```

## 各文件夹说明

### `spectrum_training/`
- **功能**: 训练机器学习模型并导出为 ONNX 格式
- **输入**: 自动生成训练数据
- **输出**: ONNX 模型文件（`spectrum_model.onnx`）

### `spectrum_onnx/`
- **功能**: 使用 ONNX 模型进行光谱数据预测
- **特点**: 固定输入维度（1024 个数据点）
- **语言**: Python + C++

### `new_onnx_inference/`
- **功能**: 通用的 ONNX 模型预测程序
- **特点**: 自动检测模型输入输出维度
- **语言**: Python + C++

## 依赖安装

```bash
# 安装 Python 依赖
cd spectrum_training
pip install -r requirements.txt

# C++ 程序需要 ONNX Runtime（已在 CMakeLists.txt 中配置）
```

## 快速开始

```bash
# 1. 训练并导出模型
cd spectrum_training
python3 spectrum_predictor.py

# 2. 使用 Python 进行预测
cd ../spectrum_onnx
python3 onnx_predictor.py ../spectrum_model.onnx

# 3. 编译并运行 C++ 版本
cd ../spectrum_onnx
mkdir -p build && cd build
cmake ..
make -j4
LD_LIBRARY_PATH=/path/to/onnxruntime/lib:$LD_LIBRARY_PATH ./onnx_example ../spectrum_model.onnx
```
