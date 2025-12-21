#include "reference_processor.h"

#include <QDebug>

ReferenceProcessor::ReferenceProcessor(ReferenceType type, QObject *parent)
    : QThread(parent), stopRequested_(false), accumulating_(false), referenceType_(type) {
}

ReferenceProcessor::~ReferenceProcessor() {
  stopProcessing();
}

void ReferenceProcessor::startAccumulating() {
  QMutexLocker locker(&mutex_);
  accumulating_ = true;
  accumulatedData_.clear();
  condition_.wakeOne();
}

void ReferenceProcessor::stopAccumulating() {
  QMutexLocker locker(&mutex_);
  accumulating_ = false;
  accumulatedData_.clear();
}

int ReferenceProcessor::getAccumulatedCount() const {
  QMutexLocker locker(const_cast<QMutex*>(&mutex_));
  return accumulatedData_.size();
}

void ReferenceProcessor::addSpectrumData(const QVariantList &data) {
  QMutexLocker locker(&mutex_);
  if (accumulating_ && accumulatedData_.size() < REFERENCE_THRESHOLD) {
    accumulatedData_.append(data);
    // 发送进度更新信号
    emit progressChanged(accumulatedData_.size(), REFERENCE_THRESHOLD);
    condition_.wakeOne();  // 唤醒处理线程
  }
}

void ReferenceProcessor::stopProcessing() {
  {
    QMutexLocker locker(&mutex_);
    stopRequested_ = true;
    accumulating_ = false;
    condition_.wakeAll();  // 唤醒所有等待的线程
  }
  wait(1000);  // 等待最多1秒
  if (isRunning()) {
    terminate();
    wait();
  }
}

void ReferenceProcessor::run() {
  const int dataPoints = 1024;  // 每个数据包的点数

  while (!stopRequested_) {
    QMutexLocker locker(&mutex_);
    
    // 等待有数据或停止请求
    while ((!accumulating_ || accumulatedData_.size() < REFERENCE_THRESHOLD) && !stopRequested_) {
      condition_.wait(&mutex_);
    }

    if (stopRequested_) {
      break;
    }

    // 如果累积的数据达到阈值，进行处理
    if (accumulating_ && accumulatedData_.size() >= REFERENCE_THRESHOLD) {
      // 复制数据到本地，释放锁
      QList<QVariantList> dataToProcess = accumulatedData_;
      accumulatedData_.clear();
      accumulating_ = false;  // 停止累积
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

      // 找到最大值和最小值
      double minVal = averagedData[0].toDouble();
      double maxVal = averagedData[0].toDouble();
      for (int i = 1; i < dataPoints; i++) {
        double val = averagedData[i].toDouble();
        if (val < minVal) minVal = val;
        if (val > maxVal) maxVal = val;
      }

      // 根据参考类型发送相应的信号
      if (referenceType_ == BlackReference) {
        emit blackReferenceReady(averagedData, minVal, maxVal);
      } else {
        emit whiteReferenceReady(averagedData, minVal, maxVal);
      }

      // 重新获取锁，继续下一轮
      locker.relock();
    }
  }
}

