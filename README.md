# NIR_system_formal
近红外光谱水分检测系统
* 作者：Linxi
* 微信：19966438400
* QQ：1909992592
* 加好友询问问题记得备注NIR_system_formal

## 硬件准备
1. 树莓派5套件
    * 树莓派5开发板
    * 树莓派5电源
    * 树莓派散热器
    * 64GB 内存卡
    * 读卡器
    * USB数据线
    * 千兆网线
2. 笔记本——最好有英伟达独立显卡
3. 近红外光谱相机

## 软件准备
### 树莓派
安装任何ubuntu软件之前，务必先
```
sudo apt update
sudo apt upgrade
```
1. Ubuntu 24.04 Sever + lubuntu-desktop
```
sudo apt install lubuntu-desktop
```
2. xrdp
```
sudo apt install xrdp
```
3. gnome-disk-utility
```
sudo apt install gnome-disk-utility
```
4. cursor
```
# 添加 Cursor 的 GPG 密钥
curl -fsSL https://downloads.cursor.com/keys/anysphere.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/cursor.gpg > /dev/null

# 添加 Cursor 软件源
echo "deb [arch=amd64,arm64 signed-by=/etc/apt/keyrings/cursor.gpg] https://downloads.cursor.com/aptrepo stable main" | sudo tee /etc/apt/sources.list.d/cursor.list > /dev/null

# 更新并安装
sudo apt update
sudo apt install cursor
```
5. clash-verge
```
下载 https://clash-verge.org/zh-CN/download 对应的linux-arm64版本的
sudo apt install *.deb
```
6. Qt6
```
下载 https://www.qt.io/zh-cn/ 对应的开源版本
sudo chmod +x *.run
./*.run
sudo apt install libxcb-cursor0 libxcb-cursor-dev
```
### 电脑
1. ubuntu 24.04 桌面版
```
https://cn.ubuntu.com/download
怎么安装百度或者上b站
```
2. Raspberry Pi Imager
```
https://www.raspberrypi.com/software/
怎么安装百度或者上b站
```
3. timeshift
```
sudo apt install timeshift
```
4. clash-verge
```
下载 https://clash-verge.org/zh-CN/download 对应的linux-x86/amd64版本的
sudo apt install *.deb
```
5. cursor
```
# 添加 Cursor 的 GPG 密钥
curl -fsSL https://downloads.cursor.com/keys/anysphere.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/cursor.gpg > /dev/null

# 添加 Cursor 软件源
echo "deb [arch=amd64,arm64 signed-by=/etc/apt/keyrings/cursor.gpg] https://downloads.cursor.com/aptrepo stable main" | sudo tee /etc/apt/sources.list.d/cursor.list > /dev/null

# 更新并安装
sudo apt update
sudo apt install cursor
```
6. Qt6
```
下载 https://www.qt.io/zh-cn/ 对应的开源版本
sudo chmod +x *.run
./*.run
sudo apt install libxcb-cursor0 libxcb-cursor-dev
```
7. anaconda
```
下载 https://www.anaconda.com/download 对应x86/amd64 linux版本
chmod +x *.sh
./*.sh
之后跟着引导走
安装完成后
vim ~/.bashrc
结尾加上
export  PATH=$PATH:/home/USERNAME/anaconda3/bin
source ~/anaconda3/bin/activate
之后
source ~/.bashrc
source activate
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
pip config set install.trusted-host mirrors.aliyun.com
sudo apt-get install nvidia-driver-535
sudo reboot
sudo apt install nvidia-cuda-toolkit
nvcc -V
```
## 常见问题
1. ubuntu用什么软件连接树莓派
   ```
   remmina
      ssh连接: 选择ssh选项先输入对应的ip地址后回车，后面输入账号密码
      rdp连接: 一定要用+号新建连接，基本设置里面色深选择增强色（16位），保存为默认值之后，在主界面选择rdp选项，输入ip地址进入，后面输入账号密码
   ```
2. 树莓派如何固定ip并设置MTU
   * sudo nano /etc/netplan/50-cloud-init.yaml
   ```
   network:
     version: 2
     ethernets:
       eth0:
         addresses: [192.168.10.2/24]  # 同时设置静态IP
         mtu: 2500
         
     wifis:
       wlan0:
         optional: true
         dhcp4: true
         dhcp4-overrides:
           route-metric: 200  # WiFi优先级较低
         regulatory-domain: "CN"
         access-points:
           "linxi":
             hidden: true
             auth:
               key-management: "psk"
               password: "489da4c177223ab9c12b8141c739f3836e114525dd712b0ad0cae53224865e70"
   ```
   * sudo netplan try/apply
   * sudo reboot 
   * ip addr
3. 程序没写出来之前，不知道下位机有没有收到数据包
   * sudo tcpdump -vvv
4. 网线口在闪烁，但是上一步还是看不到任何包
   * watch -n 1 'ethtool -S enp2s0'
   * watch -n 1 'ethtool -S eth0 | grep -E "(rx_mtu_err|rx_jabber|rx_good_pkts)"'
   * ip -s link show eth0
5. 如何看自己的网卡相关信息
   * ifconfig
   * ip link show
   * ip addr
6. 笔记本和电脑之间传数据
   * scp XXX.doc nvidia@172.23.100.201:~
7. 上述传数据命令出现问题
   * 从电脑到树莓派
   ```
   ssh-keygen -f "/home/linxi-ice/.ssh/known_hosts" -R "192.168.10.2"
   ```
   * 从树莓派到电脑
   ```
   sudo apt install openssh-server # 如果未安装
   sudo systemctl start ssh
   sudo systemctl enable ssh
   sudo systemctl status ssh
   sudo netstat -tlnp | grep ssh
   ```
8. 想用qt5，对应的环境怎么装
   * sudo apt install qtbase5-dev
   * sudo apt install libqt5charts5-dev
   * sudo apt install libopenblas0
9. 如何编译c++程序
   建议cmake 和 g++ 组合
   * sudo apt install cmake
   * sudo apt install g++
10. 如何查看自己新插入的串口设备的名字
    * sudo dmesg | grep tty
11. ubuntu 磁盘莫名其妙满了
    * sudo apt install baobab
    * baobab
12. 想要知道python某个包的具体安装位置
    * pip show xxx

## 使用这个系统的完整流程
1. 给你的树莓派装上 ubuntu24.04 系统
   1. 在你的电脑上（最好是ubuntu，windows也可以），安装好Raspberry Pi Imager
   2. 将树莓派的内存卡取出，通过读卡器插到电脑上
   3. 在引导中找到 ubuntu24.04 server，切记不是桌面版
   4. 按照安装流程烧录镜像，记得一定要配置 ssh 和 wifi
2. 连接树莓派
   1. 把烧录好镜像的内存卡插回到树莓派
   2. 连接方式确认
      1. 如果你的树莓派可以外接屏幕，为了避免麻烦，直接外接屏幕就好，不需要远程连接，直接跳到步骤6，并且略过步骤7、8
      2. 如果你用的是windows系统，请下载putty这个软件并安装好
      3. 如果你用的是ubuntu系统，找到remmina这个自带的软件
   3. 找到树莓派当前内网ip地址
      1. 如果你之前安装树莓派镜像填写的wifi是你的手机热点，那么请打开你的手机，找到热点管理界面，就能找到
      2. 如果你之前安装树莓派镜像填写的wifi是你家里或者单位的wifi，那么你需要打开这个路由器的管理界面（这个得有权限才行），就能找到
   4. 确保你的电脑和树莓派连接的是同一个wifi
   5. 通过ssh连接到树莓派
   6. 给树莓派安装桌面环境
   ```
   sudo apt update
   sudo apt upgrade
   sudo apt install lubuntu-desktop
   ```
   7. 给树莓派安装远程桌面连接工具
   ```
   sudo apt install xrdp
   ```
   8. 远程连接树莓派
      1. 如果你使用windows，请打开 远程桌面连接 这个软件，并连接到树莓派
      2. 如果你使用ubuntu，请打开 remmina 这个软件，选择rdp选项并连接到树莓派
3. 将树莓派与摄像头相连
   1. 通过网线连接 树莓派的网口 与 摄像头的网口
   2. 通过usb转type-c线 连接树莓派的usb口 与 摄像头的type-c口
4. 电脑预训练模型权重文件
   1. 电脑上配置python环境
   2. 通过git下载源代码
   3. 切换到predictor_train文件夹，训练文件夹下面的几个模型，得到权重文件
5. 树莓派编译运行该程序
   1. 树莓派安装开源qt6
   2. 树莓派通过git下载源代码
   3. 树莓派预编译libtorch
   4. 树莓派预编译onnxruntime
   5. 更改源代码中相应的cmake配置文件，以适应前面的qt6、libtorch以及onnxruntime库
   6. 编译源代码
   7. 将电脑上预训练得到的权重文件，拷贝到树莓派上的相同位置
   8. 双击运行
## 其他开源项目
### 最值得先看的：整链条比较完整的项目
#### 最全
* https://hub.hamamatsu.com/us/en/technical-notes/image-sensors/ingaas-linear-sensor-reference-circuit-design-section-1.html
#### drmcnelson / TCD1304-Sensor-Device-with-Linear-Response-and-16-Bit-Differential-ADC
* https://github.com/drmcnelson/TCD1304-Sensor-Device-with-Linear-Response-and-16-Bit-Differential-ADC.git
* 基于 TCD1304 线性 CCD 的完整项目，仓库明确写了包含 gerbers、BOM、firmware、library 和 user app，也就是硬件、电路、固件、用户端软件基本都给了。虽然不是 InGaAs，也不是 FPGA，而是 Teensy/Arduino 体系
#### drmcnelson / Linear-CCD-with-LTSpice-KiCAD-Firmware-and-Python-Library
* https://github.com/drmcnelson/Linear-CCD-with-LTSpice-KiCAD-Firmware-and-Python-Library.git
* 上面那个项目的前代/相关项目，仓库说明非常明确：包含 电路设计、固件、Python 库，面向 linear CCD + Teensy 4，并且带 trigger / gate / sync。
#### drmcnelson / S11639-01-Linear-CCD-PCB-and-Code
* https://github.com/drmcnelson/S11639-01-Linear-CCD-PCB-and-Code.git
* Hamamatsu S11639-01 线性 CCD，仓库说明写得很直接：提供 electronics, firmware and host software；控制器和主机通过 USB 交互，命令接口是 human-readable ASCII，数据可选 ASCII 或 binary。
### 和“光谱仪成品/原型”更接近的项目
#### leobrowning92 / arduino-lineCCD-spectrometer
* https://github.com/leobrowning92/arduino-lineCCD-spectrometer.git
* 基于 TCD1304AP line CCD 做光谱仪，仓库说明明确说“数据由 Arduino 读出，再通过 serial USB 发到电脑”。
#### SmokyMountainScientific / Teensy-Spectrometer-Firmware
* https://github.com/SmokyMountainScientific/Teensy-Spectrometer-Firmware.git
* 基于 Teensy 4.0 + TCD1304 CCD 的光谱仪固件项目，说明里提到配套还有 校准界面、3D 打印结构件 和其他硬件资源
#### astuder / epc901
* https://github.com/astuder/epc901.git
* 比较完整的 1024×1 线阵 CCD 传感器 项目。仓库 README 明确写了包含 hardware、software、firmware、capture logic、trigger logic、transfer format、Python 脚本
### 不是线阵 CCD，但对上位机和通信很有借鉴意义
#### uutzinger / C12880MA
* https://github.com/uutzinger/C12880MA.git
* 基于 Hamamatsu C12880MA 微型光谱芯片 的项目，仓库说明写得很清楚：利用光谱芯片给出的 ADC trigger signal，在 Teensy 上通过 DMA 读数据。它不是 C-T + 外置线阵，而是集成微型光谱器件
#### icfaust / c12880maPi
* https://github.com/icfaust/c12880maPi.git
* Raspberry Pi + C12880MA + ADC 板 的接口软件，仓库明确说有 C++ 通信代码，也有 CLI 和 GUI。
#### eulerlab / spectral-scanner
* https://github.com/eulerlab/spectral-scanner.git
* 基于 C12880MA 的低成本 spectral scanner，仓库说明提到有 notebook，并采用 MicroPython-ESP32。
### 坚持要往 FPGA 方向靠，哪些项目能补上“控制器”这一块
#### KoroB14 / DECA_USB3_Cam
* https://github.com/KoroB14/DECA_USB3_Cam.git
* MAX10 FPGA + CYUSB3014 + Python client 的视频流传输项目，虽然对象是相机而不是光谱仪，但仓库明确提供了 USB 3.0 streaming 和 Python-based client。
#### amsheth / Object-Tracking-with-FPGA
* https://github.com/amsheth/Object-Tracking-with-FPGA.git
* 使用 Opal Kelly XEM7310 FPGA，并通过其数据传输模块把 FPGA 数据送到 PC 端 Python kernel。
#### Basil
* https://github.com/SiLab-Bonn/basil.git
* 一个 Python + Verilog 的模块化 DAQ 框架，说明里明确写了提供 FPGA firmware modules 和通用采集系统设计支持。
### 线性ccd+单片机
* https://oshwhub.com/qiuzhihhq/tcd1304-linear-camera-image-sens
* https://oshwhub.com/mr_258876/project_prism
### 纯fpga开发板
#### 明德扬fpga
* https://alidocs.dingtalk.com/i/nodes/QOG9lyrgJPjaX5ZvfLRDXqjQWzN67Mw4?doc_type=wiki_doc&utm_scene=team_space
* 最新802网盘资料 链接：https://pan.baidu.com/s/1OjWfXyjlDIc3JnBLPjN6JQ 提取码：0y5l
* https://gitcode.com/Open-source-documentation-tutorial/af1b1/?utm_source=document_gitcode&index=top&type=card&
* https://www.bilibili.com/video/BV14K4y1u7kH/?spm_id_from=333.1387.favlist.content.click
* https://blog.csdn.net/weixin_44212493/article/details/104334510
#### 老师给的板子
* https://www.manualslib.com/manual/2380620/Alinx-Av6150.html
* https://www.bilibili.com/video/BV1E5tnzrEAn/?spm_id_from=333.1007.top_right_bar_window_custom_collection.content.click&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.st.com/en/development-tools/stm32cubeprog.html
#### 正点原子
* http://47.111.11.73/docs/boards/fpga/index.html
#### 野火
* https://doc.embedfire.com/fpga/altera/ep4ce10_pro/zh/latest/code/foreword.html
#### ise安装
https://www.bilibili.com/video/BV1E5tnzrEAn/?spm_id_from=333.337.search-card.all.click&vd_source=ee200f7e09eb8dbc8631c991d8917853
### pcb
* https://www.bilibili.com/video/BV1bj4bzEEQQ?spm_id_from=333.788.videopod.sections&vd_source=ee200f7e09eb8dbc8631c991d8917853&p=6
* https://www.bilibili.com/video/BV1At421h7Ui?spm_id_from=333.788.player.switch&vd_source=ee200f7e09eb8dbc8631c991d8917853&p=2
* https://www.bilibili.com/video/BV1Ah4y1i7iJ/?spm_id_from=333.337.search-card.all.click&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.bilibili.com/video/BV18h4y1i7gu?spm_id_from=333.788.recommend_more_video.-1&trackid=web_related_0.router-related-2479604-5tzfh.1775315001814.68&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.bilibili.com/video/BV1Zc411o7zb?spm_id_from=333.788.recommend_more_video.-1&trackid=web_related_0.router-related-2479604-97qjn.1775376358521.727&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.bilibili.com/video/BV1fUrSYmE7d/?spm_id_from=333.337.search-card.all.click&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.bilibili.com/video/BV1MTP1e6Euo?spm_id_from=333.788.videopod.sections&vd_source=ee200f7e09eb8dbc8631c991d8917853&p=15
* https://blog.csdn.net/d111111111d/article/details/153389924
* https://oshwhub.com/li-chuang-kai-fa-ban/li-chuang-luo-ji-pai-g1-kai-fa-ban
* https://www.bilibili.com/video/BV1p3gVzUErT/?spm_id_from=333.337.search-card.all.click&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.bilibili.com/video/BV1L2eaehEfc?spm_id_from=333.788.videopod.sections&vd_source=ee200f7e09eb8dbc8631c991d8917853
* https://www.bilibili.com/video/BV1j5myBBEwy?spm_id_from=333.788.videopod.sections&vd_source=ee200f7e09eb8dbc8631c991d8917853
### 装配
* https://github.com/EdavisAPU/Education-Optics
* https://osnadocs.ub.uni-osnabrueck.de/bitstream/ds-202304188661/1/Osterheider_etal_Phys_Educ_2022.pdf
* https://github.com/zyl-mwy/NIR_system_formal/blob/main/README.md
* https://2018.igem.org/Team%3AAachen/Hardware?utm_source=chatgpt.com
