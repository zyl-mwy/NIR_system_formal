#include "serial_communicator.h"

#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <errno.h>
#include <cstring>
#include <QtMath>

SerialCommunicator::SerialCommunicator(QObject *parent) : QObject(parent), isStarted_(false) {
}

bool SerialCommunicator::sendStartCommand(const QString &portName) {
  // 启动命令: [0x08, 0x6B, 0x00, 0x00, 0x00, 0x3E, 0x09, 0xD7]
  unsigned char startCmd[] = {0x08, 0x6B, 0x00, 0x00, 0x00, 0x3E, 0x09, 0xD7};
  bool success = sendCommand(portName, startCmd, sizeof(startCmd), QStringLiteral("启动"));
  if (success) {
    isStarted_ = true;
    emit stateChanged(true);
  }
  return success;
}

bool SerialCommunicator::sendStopCommand(const QString &portName) {
  // 停止命令: 使用相同的命令（根据用户说明，启动和停止是同一个命令）
  unsigned char stopCmd[] = {0x08, 0x6B, 0x00, 0x00, 0x00, 0x3E, 0x09, 0xD7};
  bool success = sendCommand(portName, stopCmd, sizeof(stopCmd), QStringLiteral("停止"));
  if (success) {
    isStarted_ = false;
    emit stateChanged(false);
  }
  return success;
}

bool SerialCommunicator::toggleCommand(const QString &portName) {
  if (isStarted_) {
    return sendStopCommand(portName);
  } else {
    return sendStartCommand(portName);
  }
}

bool SerialCommunicator::setExposureTimeUs(double exposureTimeUs,
                                            const QString &portName) {
  if (exposureTimeUs <= 0.0) {
    emit statusChanged(QStringLiteral("✗ 曝光时间必须为正数"));
    return false;
  }

  // 根据芯片使用说明，0xA4 命令每 LSB 约 186 ns
  // N_expo ≈ exposureTimeUs(µs) / 0.186
  const double stepNs = 186.0;
  qint64 ticks = qRound64(exposureTimeUs * 1000.0 / stepNs);
  if (ticks < 0) ticks = 0;
  if (ticks > 0xFFFFFF) ticks = 0xFFFFFF;

  unsigned char cmd[] = {
      0x08,
      0xA4,
      static_cast<unsigned char>((ticks >> 16) & 0xFF),
      static_cast<unsigned char>((ticks >> 8) & 0xFF),
      static_cast<unsigned char>(ticks & 0xFF),
      0x3E,
      0x09,
      0xD7};

  return sendCommand(portName, cmd, sizeof(cmd),
                     QStringLiteral("设置曝光时间(约 %1 µs)")
                         .arg(exposureTimeUs, 0, 'f', 2));
}

bool SerialCommunicator::setReadoutTimeUs(double readoutTimeUs,
                                           const QString &portName) {
  if (readoutTimeUs <= 0.0) {
    emit statusChanged(QStringLiteral("✗ 读出时间必须为正数"));
    return false;
  }

  // 使用说明中 0xA5 命令每 LSB 约 1488 ns
  // N_read ≈ readoutTimeUs(µs) / 1.488
  const double stepNs = 1488.0;
  qint64 ticks = qRound64(readoutTimeUs * 1000.0 / stepNs);
  if (ticks < 0) ticks = 0;
  if (ticks > 0xFFFFFF) ticks = 0xFFFFFF;

  unsigned char cmd[] = {
      0x08,
      0xA5,
      static_cast<unsigned char>((ticks >> 16) & 0xFF),
      static_cast<unsigned char>((ticks >> 8) & 0xFF),
      static_cast<unsigned char>(ticks & 0xFF),
      0x3E,
      0x09,
      0xD7};

  return sendCommand(portName, cmd, sizeof(cmd),
                     QStringLiteral("设置读出时间(约 %1 µs)")
                         .arg(readoutTimeUs, 0, 'f', 2));
}

bool SerialCommunicator::sendCommand(const QString &portName, const unsigned char *cmd, int cmdSize, const QString &cmdName) {
  // 打开串口
  QByteArray portBytes = portName.toLocal8Bit();
  int fd = open(portBytes.constData(), O_WRONLY | O_NOCTTY | O_NONBLOCK);
  
  if (fd < 0) {
    QString errorMsg = QStringLiteral("✗ 无法打开串口: ") + QString::fromLocal8Bit(strerror(errno));
    emit statusChanged(errorMsg);
    return false;
  }
  
  // 配置串口参数
  struct termios tty;
  if (tcgetattr(fd, &tty) != 0) {
    QString errorMsg = QStringLiteral("✗ 获取串口属性失败: ") + QString::fromLocal8Bit(strerror(errno));
    emit statusChanged(errorMsg);
    close(fd);
    return false;
  }
  
  // 设置波特率 115200
  cfsetospeed(&tty, B115200);
  cfsetispeed(&tty, B115200);
  
  // 8数据位，无校验，1停止位
  tty.c_cflag &= ~PARENB;  // 无校验
  tty.c_cflag &= ~CSTOPB;  // 1停止位
  tty.c_cflag &= ~CSIZE;   // 清除数据位设置
  tty.c_cflag |= CS8;      // 8数据位
  tty.c_cflag &= ~CRTSCTS; // 无硬件流控
  
  // 原始模式
  tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
  tty.c_iflag &= ~(IXON | IXOFF | IXANY);
  tty.c_oflag &= ~OPOST;
  
  // 设置超时
  tty.c_cc[VMIN] = 0;
  tty.c_cc[VTIME] = 10; // 1秒超时
  
  if (tcsetattr(fd, TCSANOW, &tty) != 0) {
    QString errorMsg = QStringLiteral("✗ 设置串口属性失败: ") + QString::fromLocal8Bit(strerror(errno));
    emit statusChanged(errorMsg);
    close(fd);
    return false;
  }
  
  // 发送命令
  ssize_t bytesWritten = write(fd, cmd, cmdSize);
  tcdrain(fd); // 等待数据发送完成
  
  close(fd);
  
  if (bytesWritten == cmdSize) {
    QByteArray hexCmd = QByteArray::fromRawData(reinterpret_cast<const char*>(cmd), cmdSize);
    emit statusChanged(QStringLiteral("✓ ") + cmdName + QStringLiteral("命令已发送到 ") + portName + 
                       QStringLiteral(": ") + hexCmd.toHex(' ').toUpper());
    return true;
  } else {
    QString errorMsg = QStringLiteral("✗ 发送失败，仅发送 ") + 
                       QString::number(bytesWritten) + 
                       QStringLiteral(" 字节，错误: ") + 
                       QString::fromLocal8Bit(strerror(errno));
    emit statusChanged(errorMsg);
    return false;
  }
}

