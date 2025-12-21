#pragma once

#include <QObject>
#include <QThread>
#include <QVariant>
#include <QMutex>
#include <QWaitCondition>

class SpectrumPredictorManager;

// 光谱数据处理线程，在后台处理数据累积和计算，不阻塞主界面
class SpectrumProcessor : public QThread {
  Q_OBJECT

 public:
  explicit SpectrumProcessor(QObject *parent = nullptr);
  ~SpectrumProcessor();

  // 添加一条光谱数据
  void addSpectrumData(const QVariantList &data);
  
  // 设置黑白参考数据（用于校正）
  void setBlackReferenceData(const QVariantList &data);
  void setWhiteReferenceData(const QVariantList &data);
  
  // 设置预测器管理器（用于预测）
  void setPredictorManager(SpectrumPredictorManager *manager);
  
  // 设置使用的预测器索引（-1 表示不使用预测）
  void setPredictorIndex(int index);
  
  // 停止处理
  void stopProcessing();

 signals:
  // 处理完成3950条数据后，发送处理好的光谱曲线数据
  void spectrumReady(const QVariantList &averagedSpectrum, double minVal, double maxVal, int packetCount);
  
  // 预测完成信号（预测器索引，预测值）
  void predictionReady(int predictorIndex, double predictionValue);

 protected:
  void run() override;

 private:
  // 黑白校正函数：校正后的数据 = (原始数据 - 黑参考) / (白参考 - 黑参考)
  QVariantList applyBlackWhiteCorrection(const QVariantList &rawData);
  
  // 使用预测器进行预测（在后台线程中执行）
  void performPrediction(const QVariantList &correctedSpectrum);

  QMutex mutex_;
  QWaitCondition condition_;
  QList<QVariantList> accumulatedData_;  // 累积的光谱数据
  QVariantList blackReferenceData_;  // 黑参考数据
  QVariantList whiteReferenceData_;  // 白参考数据
  SpectrumPredictorManager *predictorManager_;  // 预测器管理器
  int predictorIndex_;  // 当前使用的预测器索引（-1 表示不使用）
  bool stopRequested_;
  static const int SPECTRUM_THRESHOLD = 3950;  // 达到3950条后处理
};

