# NIR_system_formal
近红外光谱检测上位机软件

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
下载 https://www.anaconda.com/download 对应x86/amd65 linux版本
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
