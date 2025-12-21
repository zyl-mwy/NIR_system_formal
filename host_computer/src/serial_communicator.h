#pragma once

#include <QObject>

// 串口通信类，负责通过串口发送启动/停止命令
class SerialCommunicator : public QObject {
  Q_OBJECT
  Q_PROPERTY(bool isStarted READ isStarted NOTIFY stateChanged)

 public:
  explicit SerialCommunicator(QObject *parent = nullptr);

  bool isStarted() const { return isStarted_; }

  Q_INVOKABLE bool sendStartCommand(const QString &portName = QStringLiteral("/dev/ttyUSB0"));
  Q_INVOKABLE bool sendStopCommand(const QString &portName = QStringLiteral("/dev/ttyUSB0"));
  Q_INVOKABLE bool toggleCommand(const QString &portName = QStringLiteral("/dev/ttyUSB0"));

 signals:
  void statusChanged(const QString &message);
  void stateChanged(bool started);

 private:
  bool sendCommand(const QString &portName, const unsigned char *cmd, int cmdSize, const QString &cmdName);
  
  bool isStarted_;
};

