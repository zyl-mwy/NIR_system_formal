# Qt6 QML 计算器应用

这是一个基于Qt6和QML的插件化计算器应用。

## 依赖要求

### 系统依赖
- Qt6 (已自动检测用户目录 `~/Qt/6.*/gcc_*`)
- **libxcb-cursor0** (必需，用于Qt6 xcb平台插件)

### 安装系统依赖

```bash
sudo apt-get update
sudo apt-get install libxcb-cursor0
```

## 编译和运行

### 方法1: 使用自动化脚本（推荐）

**编译并运行:**
```bash
./build.sh
```

**仅运行（需要先编译）:**
```bash
./run.sh
```

### 方法2: 手动编译

```bash
# 配置
mkdir -p build
cd build
cmake ..

# 编译
make

# 运行（需要设置环境变量）
export LD_LIBRARY_PATH=~/Qt/6.10.1/gcc_arm64/lib:$LD_LIBRARY_PATH
export QT_PLUGIN_PATH=~/Qt/6.10.1/gcc_arm64/plugins:$QT_PLUGIN_PATH
export QML2_IMPORT_PATH=~/Qt/6.10.1/gcc_arm64/qml:$QML2_IMPORT_PATH
./calc_app
```

## 项目结构

- `main.cpp` - 主程序入口
- `plugin_manager.cpp/h` - 插件管理器
- `plugin_interface.h` - 插件接口定义
- `plugins/` - 插件目录
  - `add_plugin.cpp` - 加法插件
  - `sub_plugin.cpp` - 减法插件
  - `mul_plugin.cpp` - 乘法插件
- `Main.qml` - QML主界面
- `qml.qrc` - QML资源文件

## 故障排除

### 问题: "Could not load the Qt platform plugin 'xcb'"

**原因:** 缺少 `libxcb-cursor0` 库

**解决方案:**
```bash
sudo apt-get install libxcb-cursor0
```

### 问题: CMake找不到Qt6

**原因:** Qt6未安装在标准位置

**解决方案:** 
- CMakeLists.txt已自动检测 `~/Qt/6.*/gcc_*` 路径
- 如果Qt6在其他位置，可以手动设置:
  ```bash
  cmake -DCMAKE_PREFIX_PATH=/path/to/qt6 ..
  ```

## 脚本说明

- `build.sh` - 自动编译并运行程序，包含依赖检查
- `run.sh` - 仅运行程序，自动检查依赖和环境变量


