#pragma once

#include <QObject>
#include <QThread>
#include <QVariant>
#include <atomic>

// UDP接收线程类，在独立线程中接收UDP数据包
class UdpReceiverThread : public QThread {
  Q_OBJECT

 public:
  explicit UdpReceiverThread(QObject *parent = nullptr);
  ~UdpReceiverThread();

  bool startReceiving(int port, const QString &bindAddress = QString());
  void stopReceiving();

 signals:
  void packetReceived(const QVariantList &data);
  void statusChanged(const QString &message);
  void errorOccurred(const QString &error);

 protected:
  void run() override;

 private:
  std::atomic<bool> running_;
  int port_;
  QString bindAddress_;
  int socket_fd_;
  int stop_pipe_[2];  // 管道，用于立即唤醒select()
};

