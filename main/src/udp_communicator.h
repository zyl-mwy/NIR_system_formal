#pragma once

#include <QObject>
#include <QVariant>
#include <QTimer>

class UdpReceiverThread;
class SpectrumProcessor;
class ReferenceProcessor;
class SpectrumPredictorManager;

// UDP通信管理类，负责UDP数据包接收
class UdpCommunicator : public QObject {
  Q_OBJECT
  Q_PROPERTY(bool receiving READ isReceiving NOTIFY receivingChanged)
  Q_PROPERTY(int packetCount READ packetCount NOTIFY packetCountChanged)
  Q_PROPERTY(int packetsPerSecond READ packetsPerSecond NOTIFY packetsPerSecondChanged)
  Q_PROPERTY(bool blackReferenceAccumulating READ isBlackReferenceAccumulating NOTIFY blackReferenceAccumulatingChanged)
  Q_PROPERTY(int blackReferenceProgress READ blackReferenceProgress NOTIFY blackReferenceProgressChanged)
  Q_PROPERTY(bool whiteReferenceAccumulating READ isWhiteReferenceAccumulating NOTIFY whiteReferenceAccumulatingChanged)
  Q_PROPERTY(int whiteReferenceProgress READ whiteReferenceProgress NOTIFY whiteReferenceProgressChanged)

 public:
  explicit UdpCommunicator(QObject *parent = nullptr);
  ~UdpCommunicator();

  bool isReceiving() const { return receiving_; }
  int packetCount() const { return packetCount_; }
  int packetsPerSecond() const { return packetsPerSecond_; }
  bool isBlackReferenceAccumulating() const { return blackReferenceAccumulating_; }
  int blackReferenceProgress() const { return blackReferenceProgress_; }
  bool isWhiteReferenceAccumulating() const { return whiteReferenceAccumulating_; }
  int whiteReferenceProgress() const { return whiteReferenceProgress_; }

  Q_INVOKABLE bool startReceiving(int port, const QString &bindAddress = QString());
  Q_INVOKABLE void stopReceiving();
  Q_INVOKABLE void resetPacketCount();
  Q_INVOKABLE void startBlackReference();
  Q_INVOKABLE void stopBlackReference();
  Q_INVOKABLE void startWhiteReference();
  Q_INVOKABLE void stopWhiteReference();
  
  // 设置预测器管理器
  void setPredictorManager(SpectrumPredictorManager *manager);
  
  // 设置使用的预测器索引（-1 表示不使用预测）
  Q_INVOKABLE void setPredictorIndex(int index);

 signals:
  void packetReceived(const QVariantList &data);
  void statusChanged(const QString &message);
  void receivingChanged(bool receiving);
  void packetCountChanged(int count);
  void packetsPerSecondChanged(int rate);
  // 光谱曲线数据准备好（在后台线程处理完成后发送）
  void spectrumReady(const QVariantList &averagedSpectrum, double minVal, double maxVal, int packetCount);
  // 黑参考数据累积状态改变
  void blackReferenceAccumulatingChanged(bool accumulating);
  // 黑参考累积进度更新
  void blackReferenceProgressChanged(int progress);
  // 黑参考数据处理完成
  void blackReferenceReady(const QVariantList &averagedSpectrum, double minVal, double maxVal);
  // 白参考数据累积状态改变
  void whiteReferenceAccumulatingChanged(bool accumulating);
  // 白参考累积进度更新
  void whiteReferenceProgressChanged(int progress);
  // 白参考数据处理完成
  void whiteReferenceReady(const QVariantList &averagedSpectrum, double minVal, double maxVal);
  
  // 预测完成信号（预测器索引，预测值）
  void predictionReady(int predictorIndex, double predictionValue);

 private slots:
  void onUdpPacketReceived(const QVariantList &data);
  void onUdpStatusChanged(const QString &message);
  void onUdpErrorOccurred(const QString &error);
  void onSecondTimer();
  void onSpectrumProcessed(const QVariantList &averagedSpectrum, double minVal, double maxVal, int packetCount);
  void onBlackReferenceProgressChanged(int count, int total);
  void onBlackReferenceProcessed(const QVariantList &averagedSpectrum, double minVal, double maxVal);
  void onWhiteReferenceProgressChanged(int count, int total);
  void onWhiteReferenceProcessed(const QVariantList &averagedSpectrum, double minVal, double maxVal);
  void onPredictionReady(int predictorIndex, double predictionValue);

 private:
  UdpReceiverThread *udpReceiver_;
  SpectrumProcessor *spectrumProcessor_;  // 后台处理线程
  ReferenceProcessor *blackReferenceProcessor_;  // 黑参考处理线程
  ReferenceProcessor *whiteReferenceProcessor_;  // 白参考处理线程
  bool receiving_;
  int packetCount_;
  int packetsPerSecond_;
  int packetsThisSecond_;  // 当前秒内接收的数据包数
  QTimer *secondTimer_;   // 每秒统计一次的定时器
  bool blackReferenceAccumulating_;  // 是否正在累积黑参考数据
  int blackReferenceProgress_;  // 黑参考累积进度
  bool whiteReferenceAccumulating_;  // 是否正在累积白参考数据
  int whiteReferenceProgress_;  // 白参考累积进度
  QVariantList blackReferenceData_;  // 存储黑参考数据
  QVariantList whiteReferenceData_;  // 存储白参考数据
  SpectrumPredictorManager *predictorManager_;  // 预测器管理器
};

