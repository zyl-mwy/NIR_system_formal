import socket
import struct
import numpy as np
import matplotlib.pyplot as plt

# UDP配置
UDP_IP = "192.168.1.102"  # 本机IP地址
UDP_PORT = 1234
BUFFER_SIZE = 1024

# 图像配置
IMAGE_WIDTH = 512
PIXELS_IN_ROW = 512  # 每行的像素数量
UPDATE_INTERVAL = 100  # 每1行更新一次图形

# 初始化Matplotlib图形
plt.ion()  # 启用交互模式
fig, ax = plt.subplots(figsize=(8, 6))
x = np.arange(IMAGE_WIDTH)  # X轴：像素坐标 (0到1023)
line, = ax.plot(x, np.zeros(IMAGE_WIDTH), 'b-')  # 初始化折线图
ax.set_xlabel('Pixel Position')
ax.set_ylabel('16-bit Grayscale')
ax.set_title('Real-time Row Data Plot')
ax.set_xlim(0, IMAGE_WIDTH - 1)
ax.set_ylim(0, 65535)
ax.grid(True)

# UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# 初始化数据数组
row_data = np.zeros((1, IMAGE_WIDTH), dtype=np.uint16)

# 退出标志
exit_flag = False

# 键盘事件处理函数
def on_key_press(event):
    global exit_flag
    if event.key == 'q':
        exit_flag = True

# 绑定键盘事件
fig.canvas.mpl_connect('key_press_event', on_key_press)

try:
    row_count = 0
    while not exit_flag:
        # 接收一行数据
        data, addr = sock.recvfrom(BUFFER_SIZE)

        # 计算应该解包的像素数量
        pixels_to_unpack = min(PIXELS_IN_ROW, len(data) // 2)
        # 解析图像数据
        pixel_data = struct.unpack('!{}H'.format(pixels_to_unpack), data)
        # print(len(pixel_data))
        print(pixel_data[0])
        # 将图像数据转换为NumPy数组
        img_array_row = np.array(pixel_data, dtype=np.uint16)
        img_array_row = img_array_row[:IMAGE_WIDTH]

        # 更新数据数组
        row_data[0, :len(img_array_row)] = img_array_row

        # 每UPDATE_INTERVAL行更新一次图形
        row_count += 1
        if row_count % UPDATE_INTERVAL == 0:
            line.set_ydata(row_data[0])
            fig.canvas.draw()
            fig.canvas.flush_events()

except KeyboardInterrupt:
    print("接收数据过程中断")
