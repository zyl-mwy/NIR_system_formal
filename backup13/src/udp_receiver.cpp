#include "udp_receiver.h"

#include <QDebug>
#include <QVariant>
#include <QtEndian>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <cstring>
#include <cerrno>

const int NUM_COUNT = 1024;  // 每个数据包最多包含1024个数字
const int BUFFER_SIZE = 2100;  // 接收缓冲区大小（1024*2+4+余量）

UdpReceiverThread::UdpReceiverThread(QObject *parent)
    : QThread(parent), running_(false), port_(1234), socket_fd_(-1), stop_pipe_{-1, -1} {
}

UdpReceiverThread::~UdpReceiverThread() {
  stopReceiving();
}

bool UdpReceiverThread::startReceiving(int port, const QString &bindAddress) {
  if (running_) {
    emit statusChanged(QStringLiteral("UDP接收已在运行"));
    return false;
  }

  port_ = port;
  bindAddress_ = bindAddress;
  running_ = true;
  start();
  return true;
}

void UdpReceiverThread::stopReceiving() {
  if (running_) {
    running_ = false;
    // 向管道写入数据，立即唤醒select()
    if (stop_pipe_[1] >= 0) {
      char dummy = 1;
      write(stop_pipe_[1], &dummy, 1);
    }
    // 关闭socket
    if (socket_fd_ >= 0) {
      close(socket_fd_);
      socket_fd_ = -1;
    }
    // 等待线程退出
    if (!wait(1000)) {
      // 如果1秒内还没退出，强制终止
      terminate();
      wait(500);
    }
    // 关闭管道
    if (stop_pipe_[0] >= 0) {
      close(stop_pipe_[0]);
      stop_pipe_[0] = -1;
    }
    if (stop_pipe_[1] >= 0) {
      close(stop_pipe_[1]);
      stop_pipe_[1] = -1;
    }
  }
}

void UdpReceiverThread::run() {
  // 创建管道，用于立即唤醒select()
  if (pipe(stop_pipe_) < 0) {
    QString error = QStringLiteral("无法创建管道: ") + QString::fromLocal8Bit(strerror(errno));
    emit errorOccurred(error);
    return;
  }
  
  // 设置管道为非阻塞模式
  int flags = fcntl(stop_pipe_[0], F_GETFL, 0);
  fcntl(stop_pipe_[0], F_SETFL, flags | O_NONBLOCK);
  
  // 创建UDP socket
  socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
  if (socket_fd_ < 0) {
    QString error = QStringLiteral("无法创建socket: ") + QString::fromLocal8Bit(strerror(errno));
    emit errorOccurred(error);
    close(stop_pipe_[0]);
    close(stop_pipe_[1]);
    stop_pipe_[0] = stop_pipe_[1] = -1;
    return;
  }

  // 设置socket选项：重用地址
  int reuse = 1;
  if (setsockopt(socket_fd_, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
    QString error = QStringLiteral("设置SO_REUSEADDR失败: ") + QString::fromLocal8Bit(strerror(errno));
    emit errorOccurred(error);
    close(socket_fd_);
    socket_fd_ = -1;
    close(stop_pipe_[0]);
    close(stop_pipe_[1]);
    stop_pipe_[0] = stop_pipe_[1] = -1;
    return;
  }

  // 增加接收缓冲区
  int recvBufSize = 4 * 1024 * 1024;
  setsockopt(socket_fd_, SOL_SOCKET, SO_RCVBUF, &recvBufSize, sizeof(recvBufSize));

  // 绑定地址和端口
  struct sockaddr_in serverAddr;
  memset(&serverAddr, 0, sizeof(serverAddr));
  serverAddr.sin_family = AF_INET;
  serverAddr.sin_port = htons(port_);
  
  if (bindAddress_.isEmpty()) {
    serverAddr.sin_addr.s_addr = INADDR_ANY;
  } else {
    QByteArray addrBytes = bindAddress_.toLocal8Bit();
    if (inet_aton(addrBytes.constData(), &serverAddr.sin_addr) == 0) {
      QString error = QStringLiteral("无效的绑定地址: ") + bindAddress_;
      emit errorOccurred(error);
      close(socket_fd_);
      socket_fd_ = -1;
      close(stop_pipe_[0]);
      close(stop_pipe_[1]);
      stop_pipe_[0] = stop_pipe_[1] = -1;
      return;
    }
  }

  if (bind(socket_fd_, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
    QString error = QStringLiteral("无法绑定UDP端口 ") + QString::number(port_) + 
                     QStringLiteral(": ") + QString::fromLocal8Bit(strerror(errno));
    emit errorOccurred(error);
    close(socket_fd_);
    socket_fd_ = -1;
    close(stop_pipe_[0]);
    close(stop_pipe_[1]);
    stop_pipe_[0] = stop_pipe_[1] = -1;
    return;
  }

  emit statusChanged(QStringLiteral("✓ UDP接收已启动，端口: ") + QString::number(port_));

  unsigned char buffer[BUFFER_SIZE];
  struct sockaddr_in clientAddr;
  socklen_t clientLen = sizeof(clientAddr);

  while (running_) {
    fd_set readFds;
    FD_ZERO(&readFds);
    FD_SET(socket_fd_, &readFds);
    FD_SET(stop_pipe_[0], &readFds);  // 同时监听停止管道
    
    int maxFd = (socket_fd_ > stop_pipe_[0] ? socket_fd_ : stop_pipe_[0]) + 1;
    
    // 使用NULL超时，select()会一直阻塞直到有数据或管道有数据
    // 当stopReceiving()向管道写入数据时，select()会立即返回
    int selectResult = select(maxFd, &readFds, nullptr, nullptr, nullptr);
    
    if (selectResult < 0) {
      if (errno == EINTR) {
        continue;  // 被信号中断，继续
      }
      if (errno == EBADF) {
        // socket或管道已被关闭，退出循环
        break;
      }
      QString error = QStringLiteral("select错误: ") + QString::fromLocal8Bit(strerror(errno));
      emit errorOccurred(error);
      break;
    }
    
    // 检查停止管道，如果有数据说明需要停止
    if (FD_ISSET(stop_pipe_[0], &readFds)) {
      char dummy;
      read(stop_pipe_[0], &dummy, 1);  // 读取数据，清空管道
      break;  // 立即退出
    }
    
    // 检查running_标志
    if (!running_) {
      break;
    }
    
    // 检查UDP socket是否有数据
    if (!FD_ISSET(socket_fd_, &readFds)) {
      continue;  // 没有UDP数据，继续循环
    }

    // 接收数据
    ssize_t receivedBytes = recvfrom(socket_fd_, 
                                      buffer, 
                                      BUFFER_SIZE, 
                                      0,
                                      (struct sockaddr*)&clientAddr, 
                                      &clientLen);

    if (receivedBytes < 2) {  // 至少需要2字节（1个uint16_t）
      continue;
    }

    // 解析数据包：直接处理为原始光谱数据（1024个uint16_t）
    const uint16_t *dataPtr = reinterpret_cast<const uint16_t *>(buffer);
    size_t totalUint16Count = receivedBytes / sizeof(uint16_t);
    
    // 计算实际接收到的数据数量（最多1024个数字）
    size_t actualDataCount = (totalUint16Count < static_cast<size_t>(NUM_COUNT)) ? totalUint16Count : static_cast<size_t>(NUM_COUNT);

    // 转换字节序并转换为QVariantList（在接收线程中完成，避免阻塞主线程）
    QVariantList variantData;
    variantData.reserve(static_cast<int>(actualDataCount));
    
    for (size_t i = 0; i < actualDataCount; ++i) {
      uint16_t value = qFromBigEndian<quint16>(dataPtr[i]);  // 网络字节序转主机字节序
      variantData.append(QVariant::fromValue(value));
    }

    // 发送信号到主线程（数据已转换完成）
    emit packetReceived(variantData);
  }

  if (socket_fd_ >= 0) {
    close(socket_fd_);
    socket_fd_ = -1;
  }
  
  // 关闭管道
  if (stop_pipe_[0] >= 0) {
    close(stop_pipe_[0]);
    stop_pipe_[0] = -1;
  }
  if (stop_pipe_[1] >= 0) {
    close(stop_pipe_[1]);
    stop_pipe_[1] = -1;
  }

  emit statusChanged(QStringLiteral("UDP接收已停止"));
}

