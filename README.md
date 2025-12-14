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
