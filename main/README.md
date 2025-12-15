# Qt6 QML 近红外光谱检测上位机

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

```bash
# 配置
mkdir build
cd build
cmake ..

# 编译
make

./calc_app
```

