# PyTorch 预测器

基于 PyTorch 神经网络的光谱数据预测器，使用 JIT 格式模型文件。

## 文件夹结构

```
pytorch_predictor/
├── spectrum_predictor.py  # 训练和导出 JIT 模型（PyTorch）
├── jit_predictor.py       # Python 预测程序
├── jit_example.cpp        # C++ 验证程序（用于验证预测结果）
├── CMakeLists.txt         # C++ 编译配置
├── requirements.txt       # Python 依赖
├── README.md             # 使用说明
└── spectrum_model.jit    # 训练好的模型文件（JIT 格式）
```

## 对应关系

| 预测器插件 | 训练文件夹 | 算法 | 输入维度 | 模型格式 |
|-----------|-----------|------|---------|---------|
| `plugins/predictor/pytorch_predictor_plugin.cpp` | `predictor_train/pytorch_predictor/` | PyTorch 神经网络 | 固定 1024 | .jit |

## 工作流程

### 1. 训练模型

```bash
cd predictor_train/pytorch_predictor
pip install -r requirements.txt
python3 spectrum_predictor.py
# 生成 spectrum_model.jit
```

训练参数：
- `--input-size`: 输入维度（默认 1024）
- `--epochs`: 训练轮数（默认 100）
- `--batch-size`: 批次大小（默认 32）
- `--lr`: 学习率（默认 0.001）
- `--n-samples`: 训练样本数（默认 10000）
- `--output`: 输出模型文件名（默认 spectrum_model.jit）

### 2. 使用模型进行预测

**方式1：使用 Python 程序**
```bash
cd predictor_train/pytorch_predictor
python3 jit_predictor.py spectrum_model.jit
```

**方式2：使用 C++ 验证程序（验证预测结果）**
```bash
cd predictor_train/pytorch_predictor
mkdir -p build && cd build
cmake ..  # 需要先配置 CMakeLists.txt 中的 libtorch 路径
make -j4
./jit_example ../spectrum_model.jit
# 或使用自定义输入数据文件
./jit_example ../spectrum_model.jit ../input_data.txt
```

**方式3：使用 C++ 插件（推荐，在主程序中使用）**
在主程序中使用：
1. 启动主程序
2. 在界面中选择预测算法（PyTorch 预测器）
3. 模型会自动从 `predictor_train/pytorch_predictor/spectrum_model.jit` 加载
4. 点击"启用预测"
5. 开始 UDP 接收，预测结果会自动显示

## 模型架构

- **输入层**: 1024 个特征
- **隐藏层**: 512 -> 256 -> 128（带 Dropout）
- **输出层**: 1 个值（回归预测）
- **激活函数**: ReLU
- **优化器**: Adam
- **损失函数**: MSE

## 依赖安装

### Python 依赖
```bash
cd predictor_train/pytorch_predictor
pip install -r requirements.txt
```

### C++ 依赖（libtorch）
需要在 CMakeLists.txt 中配置 libtorch 路径。

## 注意事项

1. **模型文件格式**: 必须使用 PyTorch JIT 格式（.jit）
2. **输入维度**: 固定为 1024
3. **数据预处理**: 模型内部使用 StandardScaler 进行标准化
4. **设备支持**: 训练时自动检测 CUDA，推理时使用 CPU（libtorch 默认）

## 快速开始

```bash
# 1. 训练模型
cd predictor_train/pytorch_predictor
python3 spectrum_predictor.py

# 2. 验证预测结果（可选）
# 使用 Python 版本
python3 jit_predictor.py spectrum_model.jit

# 使用 C++ 版本（需要先配置 libtorch 路径）
mkdir -p build && cd build
cmake ..  # 修改 CMakeLists.txt 中的 LIBTORCH_ROOT
make -j4
./jit_example ../spectrum_model.jit

# 对比两个版本的预测结果，应该相同

# 3. 在主程序中使用
# 启动主程序后，在界面中选择 PyTorch 预测算法并加载模型
```

## 验证预测结果一致性

C++ 验证程序 (`jit_example.cpp`) 和 Python 预测程序 (`jit_predictor.py`) 使用相同的输入数据时，应该产生相同的预测结果。

**验证步骤：**
1. 使用 Python 版本预测：
   ```bash
   python3 jit_predictor.py spectrum_model.jit
   ```

2. 使用 C++ 版本预测（使用相同的随机种子）：
   ```bash
   ./jit_example ../spectrum_model.jit
   ```

3. 对比两个程序的输出，预测值应该相同（或非常接近，允许浮点误差）

**注意：** C++ 程序默认使用固定种子（42）生成测试数据，与 Python 版本保持一致，便于对比结果。

