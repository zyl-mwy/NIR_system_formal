#pragma once

#include <QObject>
#include <QThread>
#include <QVariant>
#include <QMutex>
#include <QWaitCondition>

// 通用参考数据处理线程，可以处理黑参考或白参考，累积39500个数据包并计算平均值
class ReferenceProcessor : public QThread {
  Q_OBJECT

 public:
  enum ReferenceType {
    BlackReference,
    WhiteReference
  };

  explicit ReferenceProcessor(ReferenceType type, QObject *parent = nullptr);
  ~ReferenceProcessor();

  // 开始累积参考数据
  void startAccumulating();
  
  // 停止累积
  void stopAccumulating();
  
  // 添加一条光谱数据
  void addSpectrumData(const QVariantList &data);
  
  // 停止处理
  void stopProcessing();
  
  // 获取当前累积进度
  int getAccumulatedCount() const;
  
  // 获取参考类型
  ReferenceType getReferenceType() const { return referenceType_; }

 signals:
  // 累积进度更新
  void progressChanged(int count, int total);
  
  // 黑参考数据处理完成
  void blackReferenceReady(const QVariantList &averagedSpectrum, double minVal, double maxVal);
  
  // 白参考数据处理完成
  void whiteReferenceReady(const QVariantList &averagedSpectrum, double minVal, double maxVal);

 protected:
  void run() override;

 private:
  QMutex mutex_;
  QWaitCondition condition_;
  QList<QVariantList> accumulatedData_;  // 累积的光谱数据
  bool stopRequested_;
  bool accumulating_;  // 是否正在累积
  ReferenceType referenceType_;  // 参考类型（黑参考或白参考）
  static const int REFERENCE_THRESHOLD = 39500;  // 需要累积39500条数据
};

