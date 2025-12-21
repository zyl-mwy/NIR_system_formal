# 近红外水分检测上位机使用说明（树莓派）

> 工程目录：`NIR_system_formal/main`  
> 可执行程序：`build/calc_app`

---

## 一、系统概述

本程序是近红外水分检测仪的上位机，运行在树莓派等 Linux 设备上，通过串口 / UDP 接收光谱数据，完成：

- 光谱采集与显示（支持实时平均）
- 黑/白参考修正与光谱预处理
- 水分预测与异常监控
- 预测结果记录（含对应光谱）与 CSV 导出
- 系统资源监控（CPU/内存/磁盘/CPU 温度）
- CPU 温度保护（超温自动停采 + 恢复后自动重启采集）
- 光谱异常自检（基于信噪比 SNR）
- 单条光谱采集与记录（用于标样 / 建模）
- 全局日志记录与查看（同时写入 `build/log/app.log`）

---

## 二、启动与基本运行

### 2.1 编译与运行

```bash
cd NIR_system_formal/main
mkdir -p build && cd build
cmake ..
make -j4
./calc_app
```

如需开机自启，可在系统中通过 `systemd` 或桌面自启动配置 `build/calc_app`。

### 2.2 主界面结构（`qml/Main.qml`）

- 左上：串口 / UDP 通信配置与“开始/停止获取光谱”按钮  
- 中间：光谱显示区域（含平均光谱）  
- 右侧：预测结果、状态提示  
- 底部：通信状态、采集速率等信息  
- 顶部菜单：日志查看、系统监控、预测结果记录、光谱异常自检、单条光谱采集等

---

## 三、光谱采集（串口 & UDP）

### 3.1 串口采集

1. 在主界面“串口配置”中输入串口号，例如 `/dev/ttyUSB0`。  
2. 点击“开始获取光谱”按钮：  
   - 程序调用 `serialComm.toggleCommand(port)` 打开串口采集；  
   - 再次点击则发送停止命令并关闭串口。  
3. 串口状态标签会显示成功 / 失败信息，并在日志中记录。

### 3.2 UDP 采集

1. 在“UDP 配置”中设置：  
   - 地址：设备监听地址（留空为任意地址）；  
   - 端口：例如 `1234`。  
2. 点击“开始获取光谱”时，程序会同时调用  
   `udpComm.startReceiving(bindAddress, port)` 开始接收。  
3. 点击“停止获取光谱”时，调用 `udpComm.stopReceiving()` 停止接收。

备注：UDP 侧会统计有效 / 无效数据包并在界面显示。

---

## 四、黑/白参考与光谱处理（简要）

> 具体实现位于 `reference_processor.*` 与 `spectrum_processor.*` 等文件，这里只给使用建议。

典型使用流程：

1. 在暗场或遮光状态下采集 **黑参考光谱**。  
2. 在标准白板或参考板上采集 **白参考光谱**。  
3. 正常测量样品时，程序使用黑/白参考将原始电压光谱转换为反射率 / 透过率，再做后续预测。

建议每天或每班次重新采集一次黑/白参考，以减小环境漂移。

---

## 五、预测与异常监控

### 5.1 预测结果显示

当后端预测器输出结果时，主界面会：

- 更新预测值文本（例如 “水分：0.2450”）；  
- 更新预测结果趋势曲线；  
- 根据异常监控配置改变颜色（正常/异常）。

预测器管理逻辑在 `spectrum_predictor_manager.*` 与插件目录 `plugins/predictor/` 中。

### 5.2 预测值异常监控（上下限）

**入口：** 菜单栏 → 工具 → **预测结果记录**（窗口上半部分）。

- 参数：  
  - `predictionMonitorEnabled`：启用异常监控（勾选框）；  
  - `predictionLowerLimit`：下限；  
  - `predictionUpperLimit`：上限。  
- 行为：  
  - 预测值 ∈ [下限, 上限] ⇒ 状态“正常”，文本为正常颜色；  
  - 超出范围 ⇒ 状态“异常”，文本变红，并在预测曲线上绘制上下限虚线；  
  - 所有状态变化会记入日志与预测结果记录。  
- 安全细节：  
  - 一旦点击下限或上限输入框，系统会**自动取消勾选**“启用异常监控”，防止修改阈值时旧设置仍在生效；  
  - 修改完成后，如需继续监控，需重新勾选。

---

## 六、预测结果记录与 CSV 导出

### 6.1 预测结果记录窗口

**入口：** 工具 → **预测结果记录**

窗口包含两部分：

1. **预测值异常监控设置**（见 5.2）；  
2. **预测结果记录表**：  
   - 列：时间、预测器、预测值、时间间隔、上下限、状态；  
   - 支持自适应列宽和窗口大小；  
   - “清空记录”按钮清空内存中的记录列表。

### 6.2 `log/result.csv`

后端通过 `LogManager::logPredictionResult()` 把每次预测写入 `build/log/result.csv`，格式大致为：

```text
timestamp,predictorIndex,value,status,monitorEnabled,lowerLimit,upperLimit,1000.00,1000.59,...,1600.00
```

其中后 1024 列为当前样品对应的光谱值，列名为波长（单位 nm，保留 2 位小数）。

用途：

- 建模 / 重训：可直接导入 Python、Matlab 等进行建模；  
- 质量追溯：每条预测结果都能回溯到当时的光谱和阈值设置。

---

## 七、日志系统

### 7.1 日志源与输出

- 所有 Qt 日志（`qDebug/qInfo/qWarning/qCritical`）通过 `LogManager` 全局捕获；  
- QML 与 C++ 业务代码可以调用 `logManager.logInfo(source, message)` 写入自定义日志；  
- 日志同时写入：  
  - 内存（用于界面显示）；  
  - `build/log/app.log` 文件（长期保存）。

常记录的事件包括：

- 串口 / UDP 通信状态变化；  
- “开始/停止获取光谱”按钮点击；  
- 预测结果及其正常/异常判定；  
- CPU 温度保护触发 / 恢复；  
- 光谱 SNR 自检告警；  
- 各种菜单按钮、窗口操作等。

### 7.2 日志查看窗口

**入口：** 工具 → **查看日志**

特性：

- 按时间显示：时间戳 + 级别 + 消息；  
- 不同级别用彩色标签区分；  
- 每条日志下有分隔线，便于阅读；  
- 新日志到达时自动滚动到底部；  
- “清空”按钮清空内存中的列表（不影响磁盘文件）。

---

## 八、系统监控与 CPU 温度保护

### 8.1 系统监控窗口

**入口：** 工具 → **系统监控**

显示内容：

- CPU 占用：百分比 + 彩色进度条；  
- CPU 温度：当前温度（℃）+ 0–100 区间进度条；  
- 内存使用 / 总量 + 进度条；  
- 磁盘使用 / 总量 + 进度条。

布局使用 `ColumnLayout` + `RowLayout`，随窗口大小自动调整。

### 8.2 CPU 温度保护逻辑

**控制项：**

- 勾选框：**启用 CPU 温度保护**（`cpuTempProtectEnabled`）；  
- 数字输入：**温度上限**（`cpuTempProtectLimit`，默认约 80℃，建议 70–85℃）。

**行为：**

1. **超温时自动停止采集**  
   - 当保护启用且 `temp > cpuTempProtectLimit`：  
     - 置 `cpuTempProtectTriggered = true`；  
     - 调用与主界面“停止获取光谱”相同的逻辑：  
       - 停止串口采集（`serialComm.toggleCommand(port)`）；  
       - 停止 UDP 接收（`udpComm.stopReceiving()`）；  
     - 记录日志：“CPU 温度超限(...)，已自动停止采集”。

2. **温度恢复后自动继续采集**  
   - 若之前已触发保护，且 `temp < cpuTempProtectLimit - 5`：  
     - 清除 `cpuTempProtectTriggered`；  
     - 若此时：  
       - 保护仍然启用；  
       - 串口和 UDP 均处于未采集状态；  
       ⇒ 自动执行与主界面“开始获取光谱”一致的逻辑：  
         - 启动串口：`serialComm.toggleCommand(port)`；  
         - 启动 UDP：`udpComm.startReceiving(...)`；  
     - 记录日志：“CPU 温度已恢复正常(...)，已自动重新开始获取光谱”。

3. **修改上限时的安全处理**  
   - 点击“温度上限”输入框获得焦点时：  
     - 自动将 `cpuTempProtectEnabled` 设为 `false`，并取消勾选；  
   - 修改完成后需手动重新勾选，新的上限才会生效。

---

## 九、光谱异常自检（基于 SNR）

### 9.1 配置窗口

**入口：** 工具 → **光谱异常自检**

参数：

- `spectrumSnrMonitorEnabled`：启用自检（勾选框）；  
- `spectrumSnrThreshold`：SNR 阈值（例如 20–50）。

**交互细节：**

- 点击 SNR 阈值输入框时，会自动取消勾选启用自检，防止旧阈值在修改过程中继续使用；  
- 修改完成后，需要重新勾选启用。

### 9.2 行为说明

- 对当前平均光谱计算信噪比 SNR；  
- 若 `SNR < 阈值` 且监控已启用：  
  - 在主界面光谱图上用醒目方式提示“光谱信噪比过低”；  
  - 记录日志（含当前 SNR 和阈值）；  
- 该功能只报警，不自动停采。

---

## 十、单条光谱采集与记录

### 10.1 单次采集窗口

**入口：**（根据实际菜单名称）工具 → **单条光谱采集**（或类似条目）

功能：

- 用于采集单条光谱及对应的**真实水分值**，便于建模和标样管理；  
- **不执行预测**，只做采集和记录。

主要控件：

- “光谱标签”输入：例如“样品1 / 玉米A”；  
- “水分含量”输入：实测水分值（数字）；  
- “采集一条新的光谱”按钮；  
- 单次窗口中的“开始/停止获取光谱”快捷按钮（行为与主界面一致）。

记录区：

- ListView 显示每条单光谱记录：  
  - 标签（可编辑）；  
  - 采集时间；  
  - 光谱长度、最小值、最大值；  
  - 水分值（可编辑）；  
- 所有输入框与主界面风格统一，并随窗口大小自动调整宽度。

---

## 十一、预测插件训练（在有 CUDA 显卡的机器上）

本项目将“**模型训练**”与“**在线预测**”解耦：

- 树莓派 / 上位机：**只负责加载模型文件做推理**；  
- 带 CUDA 显卡的开发机：**负责训练模型并导出文件**，再拷回上位机使用。

### 11.1 目录结构

- 上位机工程根目录：`NIR_system_formal/main`  
- 预测插件运行位置：`plugins/predictor/`（C++ 插件，加载模型文件）  
- 训练脚本与模型文件：`predictor_train/` 下各子目录：
  - `pytorch_predictor/`：深度学习模型，使用 PyTorch（可利用 GPU）；  
  - `rf_predictor/`：随机森林等传统模型，导出 ONNX；  
  - `svm_predictor/`：SVM 等传统模型，导出 ONNX。

> **说明：预测器采用“插件 + 外部模型文件”形式存在**  
> - 只要在 `plugins/predictor/` 下新增/修改对应的 C++ 预测插件（以及相关 CMake 配置），  
> - 并在 `predictor_train/` 中编写好相应的 Python 训练脚本，  
> - 就可以方便地加入新的预测算法。  
> - **传统机器学习路径**：在 Python 中使用 **scikit-learn** 进行训练，将模型导出为 **ONNX 格式权重文件**，在上位机 C++ 侧使用 **ONNX Runtime** 读取 ONNX 模型并完成推理；  
> - **深度学习路径**：在 Python 中使用 **PyTorch** 训练网络，将模型导出为 **JIT（TorchScript）格式权重文件**，在上位机 C++ 侧使用 **libtorch** 加载该 JIT 模型并完成推理。

### 11.2 在有 GPU 的机器上训练

以 PyTorch 预测器为例：

1. 将 `NIR_system_formal/main/predictor_train/` 拷贝到一台带 CUDA 的开发机。  
2. 在该机器上进入：

   ```bash
   cd predictor_train/pytorch_predictor
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 按你的数据/脚本约定，运行训练脚本（示例）：

   ```bash
   python spectrum_predictor.py     # 或 jit_predictor.py
   ```

4. 训练完成后，会生成或覆盖 `spectrum_model.jit`（JIT 模型文件）。

对于 `rf_predictor/`、`svm_predictor/`，流程类似，只是使用的是 sklearn/ONNX，导出的通常是 `spectrum_model.onnx` 等文件。

### 11.3 将模型拷回树莓派

训练完成后，将新的模型文件拷回上位机工程中：

- 方式一：覆盖原有训练目录中的模型：

  ```text
  predictor_train/pytorch_predictor/spectrum_model.jit
  predictor_train/rf_predictor/spectrum_model.onnx
  predictor_train/svm_predictor/spectrum_model.onnx
  ```

- 方式二：直接拷到运行目录下（视插件加载逻辑而定，例如 `build/plugins/predictor/` 读取固定路径的模型文件）。

确保模型文件路径与 `plugins/predictor/` 中对应 C++ 插件的加载逻辑一致。

### 11.4 在上位机中使用新模型

1. 在树莓派上重新启动上位机程序 `build/calc_app`。  
2. 在主界面中，选择对应的预测插件（例如下拉框选择 `pytorch_predictor` / `rf_predictor` / `svm_predictor`）。  
3. 之后的预测都将使用你刚刚训练并拷回的最新模型文件。

> 建议：在模型文件旁边维护一个简单的版本描述（例如 `model_info.txt`），写明：
> - 模型类型（pytorch/rf/svm …）  
> - 训练日期与数据集说明  
> - 适用原料/水分范围  
> 方便以后回溯“当前上位机正在用哪个模型”。

---

## 十二、常见使用流程（简要）

1. **启动程序**，检查系统监控（CPU 温度、内存、磁盘）。  
2. 按需启用 CPU 温度保护并设定温度上限。  
3. 配置串口与 UDP，点击“开始获取光谱”。  
4. 在需要时采集黑/白参考。  
5. 在“预测结果记录”中设置预测上下限并启用异常监控；  
6. 如需监控光谱质量，在“光谱异常自检”中设定 SNR 阈值并启用；  
7. 运行过程中通过主界面、系统监控、日志查看综合观察系统状态；  
8. 根据需要，通过 `log/result.csv` 或单条光谱采集窗口导出数据，用于建模和质量分析。

