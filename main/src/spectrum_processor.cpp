#include "spectrum_processor.h"

#include <QDebug>
#include <QtMath>

SpectrumProcessor::SpectrumProcessor(QObject *parent)
    : QThread(parent), stopRequested_(false) {
}

SpectrumProcessor::~SpectrumProcessor() {
  stopProcessing();
}

void SpectrumProcessor::addSpectrumData(const QVariantList &data) {
  QMutexLocker locker(&mutex_);
  accumulatedData_.append(data);
  condition_.wakeOne();  // 唤醒处理线程
}

void SpectrumProcessor::setBlackReferenceData(const QVariantList &data) {
  QMutexLocker locker(&mutex_);
  blackReferenceData_ = data;
}

void SpectrumProcessor::setWhiteReferenceData(const QVariantList &data) {
  QMutexLocker locker(&mutex_);
  whiteReferenceData_ = data;
}

void SpectrumProcessor::stopProcessing() {
  {
    QMutexLocker locker(&mutex_);
    stopRequested_ = true;
    condition_.wakeAll();  // 唤醒所有等待的线程
  }
  wait(1000);  // 等待最多1秒
  if (isRunning()) {
    terminate();
    wait();
  }
}

void SpectrumProcessor::run() {
  const int dataPoints = 1024;  // 每个数据包的点数

  while (!stopRequested_) {
    QMutexLocker locker(&mutex_);
    
    // 等待有数据或停止请求
    while (accumulatedData_.size() < SPECTRUM_THRESHOLD && !stopRequested_) {
      condition_.wait(&mutex_);
    }

    if (stopRequested_) {
      break;
    }

    // 如果累积的数据达到阈值，进行处理
    if (accumulatedData_.size() >= SPECTRUM_THRESHOLD) {
      // 复制数据到本地，释放锁
      QList<QVariantList> dataToProcess = accumulatedData_;
      accumulatedData_.clear();
      locker.unlock();

      // 在后台线程中处理数据，不阻塞主线程
      QVariantList averagedData;
      averagedData.reserve(dataPoints);

      // 初始化平均值数组
      for (int i = 0; i < dataPoints; i++) {
        averagedData.append(0.0);
      }

      // 计算平均值
      int packetCount = dataToProcess.size();
      for (const QVariantList &packet : dataToProcess) {
        if (packet.size() == dataPoints) {
          for (int i = 0; i < dataPoints; i++) {
            double currentValue = averagedData[i].toDouble();
            double packetValue = packet[i].toDouble();
            averagedData[i] = QVariant::fromValue(currentValue + packetValue);
          }
        }
      }

      // 除以数据包数量得到平均值
      for (int i = 0; i < dataPoints; i++) {
        double avg = averagedData[i].toDouble() / packetCount;
        averagedData[i] = QVariant::fromValue(avg);
      }

      // 如果黑白参考数据都存在，进行黑白校正（在后台线程中进行，不阻塞主线程）
      QVariantList finalData = averagedData;
      if (!blackReferenceData_.empty() && !whiteReferenceData_.empty() &&
          blackReferenceData_.size() == dataPoints && whiteReferenceData_.size() == dataPoints) {
        finalData = applyBlackWhiteCorrection(averagedData);
      }

      // 找到最大值和最小值（在校正后的数据上）
      double minVal = finalData[0].toDouble();
      double maxVal = finalData[0].toDouble();
      for (int i = 1; i < dataPoints; i++) {
        double val = finalData[i].toDouble();
        if (val < minVal) minVal = val;
        if (val > maxVal) maxVal = val;
      }

      // 发送处理好的数据到主线程（通过信号，自动使用QueuedConnection）
      emit spectrumReady(finalData, minVal, maxVal, packetCount);

      // 重新获取锁，继续下一轮
      locker.relock();
    }
  }
}

QVariantList SpectrumProcessor::applyBlackWhiteCorrection(const QVariantList &rawData) {
  // 黑白校正公式：校正后的数据 = (原始数据 - 黑参考) / (白参考 - 黑参考)
  QVariantList correctedData;
  correctedData.reserve(rawData.size());
  
  for (int i = 0; i < rawData.size(); i++) {
    double rawValue = rawData[i].toDouble();
    double blackValue = blackReferenceData_[i].toDouble();
    double whiteValue = whiteReferenceData_[i].toDouble();
    
    // 计算分母：白参考 - 黑参考
    double denominator = whiteValue - blackValue;
    
    // 避免除零，如果分母太小，使用原始值
    if (qAbs(denominator) < 1e-6) {
      correctedData.append(rawValue);
    } else {
      // 计算校正后的值：(原始数据 - 黑参考) / (白参考 - 黑参考)
      double correctedValue = (rawValue - blackValue) / denominator;
      correctedData.append(correctedValue);
    }
  }
  
  return correctedData;
}

