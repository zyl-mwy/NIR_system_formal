# 预测器训练模块

## 文件夹结构

```
predictor_train/
├── rf_predictor/              # 随机森林预测器（固定 1024 输入）
│   ├── spectrum_predictor.py  # 训练和导出 ONNX 模型（随机森林算法）
│   ├── onnx_predictor.py      # Python 预测程序
│   ├── onnx_example.cpp       # C++ 预测程序
│   ├── CMakeLists.txt         # C++ 编译配置
│   ├── requirements.txt       # Python 依赖
│   ├── README.md              # 使用说明
│   └── spectrum_model.onnx    # 训练好的模型文件
│
└── svm_predictor/             # 支持向量机预测器（动态检测输入）
    ├── spectrum_predictor.py  # 训练和导出 ONNX 模型（SVM 算法）
    ├── onnx_predictor.py      # Python 预测程序
    ├── onnx_example.cpp       # C++ 预测程序
    ├── CMakeLists.txt         # C++ 编译配置
    ├── requirements.txt       # Python 依赖
    ├── README.md              # 使用说明
    └── spectrum_model.onnx    # 训练好的模型文件
```

## 对应关系

### 预测器插件 ↔ 训练文件夹

| 预测器插件 | 训练文件夹 | 算法 | 输入维度 |
|-----------|-----------|------|---------|
| `plugins/predictor/rf_predictor_plugin.cpp` | `predictor_train/rf_predictor/` | 随机森林 (Random Forest) | 固定 1024 |
| `plugins/predictor/svm_predictor_plugin.cpp` | `predictor_train/svm_predictor/` | 支持向量机 (SVM) | 动态检测 |

## 工作流程

### 1. 训练模型

**随机森林模型：**
```bash
cd predictor_train/rf_predictor
python3 spectrum_predictor.py
# 生成 spectrum_model.onnx
```

**支持向量机模型：**
```bash
cd predictor_train/svm_predictor
python3 spectrum_predictor.py
# 生成 spectrum_model.onnx
```

### 2. 使用模型进行预测

**方式1：使用 Python 程序**
```bash
# 随机森林预测器
cd predictor_train/rf_predictor
python3 onnx_predictor.py spectrum_model.onnx

# 支持向量机预测器
cd predictor_train/svm_predictor
python3 onnx_predictor.py spectrum_model.onnx
```

**方式2：使用 C++ 程序**
```bash
# 随机森林预测器
cd predictor_train/rf_predictor
mkdir -p build && cd build
cmake ..
make -j4
./onnx_example ../spectrum_model.onnx

# 支持向量机预测器
cd predictor_train/svm_predictor
mkdir -p build && cd build
cmake ..
make -j4
./onnx_example ../spectrum_model.onnx
```

**方式3：在主程序中使用（推荐）**
1. 启动主程序
2. 在界面中选择预测算法（随机森林或支持向量机）
3. 输入模型文件路径（例如：`predictor_train/rf_predictor/spectrum_model.onnx`）
4. 点击"加载模型"
5. 点击"启用预测"
6. 开始 UDP 接收，预测结果会自动显示

## 各文件夹说明

### `rf_predictor/`
- **功能**: 随机森林预测器的训练和预测程序
- **算法**: Random Forest Regressor
- **输入维度**: 固定 1024
- **特点**: 集成学习，训练速度快

### `svm_predictor/`
- **功能**: 支持向量机预测器的训练和预测程序
- **算法**: Support Vector Regression (SVR)
- **输入维度**: 动态检测
- **特点**: 核函数方法，适合高维数据

## 依赖安装

```bash
# 安装 Python 依赖
cd predictor_train/rf_predictor  # 或 svm_predictor
pip install -r requirements.txt

# C++ 程序需要 ONNX Runtime（已在 CMakeLists.txt 中配置）
```

## 快速开始

```bash
# 1. 训练随机森林模型
cd predictor_train/rf_predictor
python3 spectrum_predictor.py

# 2. 训练支持向量机模型
cd predictor_train/svm_predictor
python3 spectrum_predictor.py

# 3. 在主程序中使用
# 启动主程序后，在界面中选择对应的预测算法并加载模型
```

## 注意事项

1. **模型文件格式**: 必须使用 ONNX 格式
2. **输入维度匹配**: 
   - RF 预测器：必须使用 1024 输入的模型
   - SVM 预测器：可以适配不同输入维度的模型
3. **模型训练**: 每个文件夹中的 `spectrum_predictor.py` 使用不同的算法训练模型
4. **插件对应**: 确保使用正确的模型文件对应正确的预测器插件


