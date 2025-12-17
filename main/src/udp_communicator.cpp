#include "udp_communicator.h"
#include "udp_receiver.h"
#include "spectrum_processor.h"
#include "reference_processor.h"
#include "spectrum_predictor_manager.h"

#include <QVariant>
#include <QTimer>

UdpCommunicator::UdpCommunicator(QObject *parent)
    : QObject(parent), udpReceiver_(nullptr), spectrumProcessor_(nullptr),
      blackReferenceProcessor_(nullptr), whiteReferenceProcessor_(nullptr),
      receiving_(false), packetCount_(0), packetsPerSecond_(0), packetsThisSecond_(0), 
      blackReferenceAccumulating_(false), blackReferenceProgress_(0),
      whiteReferenceAccumulating_(false), whiteReferenceProgress_(0),
      predictorManager_(nullptr), currentPredictorIndex_(-1) {
  // 创建每秒统计定时器
  secondTimer_ = new QTimer(this);
  secondTimer_->setInterval(1000);  // 1秒
  connect(secondTimer_, &QTimer::timeout, this, &UdpCommunicator::onSecondTimer);
}

UdpCommunicator::~UdpCommunicator() {
  stopReceiving();
  if (blackReferenceProcessor_) {
    blackReferenceProcessor_->stopProcessing();
    delete blackReferenceProcessor_;
    blackReferenceProcessor_ = nullptr;
  }
  if (whiteReferenceProcessor_) {
    whiteReferenceProcessor_->stopProcessing();
    delete whiteReferenceProcessor_;
    whiteReferenceProcessor_ = nullptr;
  }
}

bool UdpCommunicator::startReceiving(int port, const QString &bindAddress) {
  if (receiving_) {
    emit statusChanged(QStringLiteral("UDP接收已在运行"));
    return false;
  }

  if (udpReceiver_) {
    delete udpReceiver_;
  }

  // 创建光谱处理线程（仅在启动UDP接收时创建）
  if (!spectrumProcessor_) {
    spectrumProcessor_ = new SpectrumProcessor(this);
    connect(spectrumProcessor_, &SpectrumProcessor::spectrumReady,
            this, &UdpCommunicator::onSpectrumProcessed, Qt::QueuedConnection);
    connect(spectrumProcessor_, &SpectrumProcessor::predictionReady,
            this, &UdpCommunicator::onPredictionReady, Qt::QueuedConnection);
    // 设置预测器管理器（如果已设置）
    if (predictorManager_) {
      spectrumProcessor_->setPredictorManager(predictorManager_);
    }
    
    // 恢复已保存的黑白参考数据（如果存在）
    // 原因：停止获取光谱时会删除 spectrumProcessor_，但黑白参考数据仍保存在 UdpCommunicator 中
    //       重新开始获取光谱时创建了新的 spectrumProcessor_，需要将之前保存的数据传递给它
    const int dataPoints = 1024;
    if (!blackReferenceData_.empty() && blackReferenceData_.size() == dataPoints) {
      spectrumProcessor_->setBlackReferenceData(blackReferenceData_);
    }
    if (!whiteReferenceData_.empty() && whiteReferenceData_.size() == dataPoints) {
      spectrumProcessor_->setWhiteReferenceData(whiteReferenceData_);
    }
    
    // 恢复预测器索引（如果之前已启用）
    // 原因：停止获取光谱时会删除 spectrumProcessor_，但预测器索引仍保存在 UdpCommunicator 中
    //       重新开始获取光谱时创建了新的 spectrumProcessor_，需要将之前保存的预测器索引传递给它
    if (currentPredictorIndex_ >= 0) {
      spectrumProcessor_->setPredictorIndex(currentPredictorIndex_);
    }
    
    spectrumProcessor_->start();  // 启动处理线程
  }

  udpReceiver_ = new UdpReceiverThread(this);
  // 使用QueuedConnection确保信号在主线程的事件循环中处理，不阻塞接收线程
  connect(udpReceiver_, &UdpReceiverThread::packetReceived,
          this, &UdpCommunicator::onUdpPacketReceived, Qt::QueuedConnection);
  connect(udpReceiver_, &UdpReceiverThread::statusChanged,
          this, &UdpCommunicator::onUdpStatusChanged, Qt::QueuedConnection);
  connect(udpReceiver_, &UdpReceiverThread::errorOccurred,
          this, &UdpCommunicator::onUdpErrorOccurred, Qt::QueuedConnection);

  if (udpReceiver_->startReceiving(port, bindAddress)) {
    receiving_ = true;
    packetCount_ = 0;  // 重置计数器
    packetsPerSecond_ = 0;
    packetsThisSecond_ = 0;
    secondTimer_->start();  // 启动每秒统计定时器
    emit receivingChanged(true);
    emit packetCountChanged(0);
    emit packetsPerSecondChanged(0);
    return true;
  } else {
    delete udpReceiver_;
    udpReceiver_ = nullptr;
    // 如果UDP接收启动失败，停止并删除光谱处理线程
    if (spectrumProcessor_) {
      spectrumProcessor_->stopProcessing();
      delete spectrumProcessor_;
      spectrumProcessor_ = nullptr;
    }
    return false;
  }
}

void UdpCommunicator::stopReceiving() {
  if (udpReceiver_) {
    udpReceiver_->stopReceiving();
    delete udpReceiver_;
    udpReceiver_ = nullptr;
  }
  
  // 停止并删除光谱处理线程（仅在停止UDP接收时删除）
  if (spectrumProcessor_) {
    spectrumProcessor_->stopProcessing();
    delete spectrumProcessor_;
    spectrumProcessor_ = nullptr;
  }
  
  secondTimer_->stop();  // 停止统计定时器
  receiving_ = false;
  packetsPerSecond_ = 0;
  packetsThisSecond_ = 0;
  emit receivingChanged(false);
  emit packetsPerSecondChanged(0);
}

void UdpCommunicator::resetPacketCount() {
  packetCount_ = 0;
  emit packetCountChanged(0);
}

void UdpCommunicator::onUdpPacketReceived(const QVariantList &data) {
  // 增加计数器
  packetCount_++;
  packetsThisSecond_++;  // 当前秒内的计数
  emit packetCountChanged(packetCount_);
  
  // 将数据添加到后台处理线程（非阻塞）
  if (spectrumProcessor_) {
    spectrumProcessor_->addSpectrumData(data);
  }
  
  // 如果正在累积黑参考数据，添加到黑参考处理线程
  if (blackReferenceProcessor_ && blackReferenceAccumulating_) {
    blackReferenceProcessor_->addSpectrumData(data);
  }
  
  // 如果正在累积白参考数据，添加到白参考处理线程
  if (whiteReferenceProcessor_ && whiteReferenceAccumulating_) {
    whiteReferenceProcessor_->addSpectrumData(data);
  }
  
  // 数据已经在接收线程中转换完成，直接转发给QML
  emit packetReceived(data);
}

void UdpCommunicator::onSecondTimer() {
  // 每秒更新一次接收速率
  packetsPerSecond_ = packetsThisSecond_;
  packetsThisSecond_ = 0;  // 重置当前秒计数
  emit packetsPerSecondChanged(packetsPerSecond_);
}

void UdpCommunicator::onUdpStatusChanged(const QString &message) {
  emit statusChanged(message);
}

void UdpCommunicator::onUdpErrorOccurred(const QString &error) {
  emit statusChanged(QStringLiteral("✗ ") + error);
  receiving_ = false;
  emit receivingChanged(false);
}

void UdpCommunicator::onSpectrumProcessed(const QVariantList &averagedSpectrum, 
                                          double minVal, double maxVal, int packetCount) {
  // 数据已经在后台线程中处理完成（包括平均值计算和黑白校正），直接转发到QML
  emit spectrumReady(averagedSpectrum, minVal, maxVal, packetCount);
}

void UdpCommunicator::startBlackReference() {
  if (blackReferenceAccumulating_) {
    emit statusChanged(QStringLiteral("黑参考累积已在运行"));
    return;
  }
  
  if (!receiving_) {
    emit statusChanged(QStringLiteral("✗ 请先启动UDP接收"));
    return;
  }
  
  // 如果线程不存在，创建并启动黑参考处理线程
  if (!blackReferenceProcessor_) {
    blackReferenceProcessor_ = new ReferenceProcessor(ReferenceProcessor::BlackReference, this);
    connect(blackReferenceProcessor_, &ReferenceProcessor::progressChanged,
            this, &UdpCommunicator::onBlackReferenceProgressChanged, Qt::QueuedConnection);
    connect(blackReferenceProcessor_, &ReferenceProcessor::blackReferenceReady,
            this, &UdpCommunicator::onBlackReferenceProcessed, Qt::QueuedConnection);
    blackReferenceProcessor_->start();  // 启动处理线程
  }
  
  blackReferenceProcessor_->startAccumulating();
  blackReferenceAccumulating_ = true;
  blackReferenceProgress_ = 0;
  emit blackReferenceAccumulatingChanged(true);
  emit blackReferenceProgressChanged(0);
  emit statusChanged(QStringLiteral("✓ 开始累积黑参考数据，需要39500个数据包"));
}

void UdpCommunicator::stopBlackReference() {
  if (!blackReferenceAccumulating_) {
    return;
  }
  
  if (blackReferenceProcessor_) {
    blackReferenceProcessor_->stopAccumulating();
    blackReferenceAccumulating_ = false;
    blackReferenceProgress_ = 0;
    emit blackReferenceAccumulatingChanged(false);
    emit blackReferenceProgressChanged(0);
    emit statusChanged(QStringLiteral("黑参考累积已停止"));
    
    // 停止并删除黑参考处理线程（不再常驻）
    blackReferenceProcessor_->stopProcessing();
    delete blackReferenceProcessor_;
    blackReferenceProcessor_ = nullptr;
  }
}

void UdpCommunicator::onBlackReferenceProgressChanged(int count, int total) {
  blackReferenceProgress_ = count;
  emit blackReferenceProgressChanged(count);
  
  // 每1000个数据包更新一次状态
  if (count % 1000 == 0 || count == total) {
    emit statusChanged(QStringLiteral("黑参考累积进度: ") + QString::number(count) + 
                       QStringLiteral("/") + QString::number(total));
  }
}

void UdpCommunicator::onBlackReferenceProcessed(const QVariantList &averagedSpectrum, 
                                                 double minVal, double maxVal) {
  blackReferenceAccumulating_ = false;
  blackReferenceProgress_ = 0;
  emit blackReferenceAccumulatingChanged(false);
  emit blackReferenceProgressChanged(0);
  
  // 保存黑参考数据
  blackReferenceData_ = averagedSpectrum;
  
  // 将黑参考数据传递给光谱处理线程（如果存在）
  if (spectrumProcessor_) {
    spectrumProcessor_->setBlackReferenceData(averagedSpectrum);
  }
  
  emit statusChanged(QStringLiteral("✓ 黑参考数据处理完成！平均值: ") + 
                     QString::number(minVal, 'f', 2) + QStringLiteral(" ~ ") + 
                     QString::number(maxVal, 'f', 2));
  
  // 检查是否可以进行黑白校正
  if (!whiteReferenceData_.empty()) {
    emit statusChanged(QStringLiteral("✓ 黑白参考数据已就绪，光谱数据将在后台线程进行黑白校正"));
  }
  
  // 将处理好的黑参考数据发送到QML
  emit blackReferenceReady(averagedSpectrum, minVal, maxVal);
  
  // 处理完成后，停止并删除黑参考处理线程（不再常驻）
  if (blackReferenceProcessor_) {
    blackReferenceProcessor_->stopProcessing();
    delete blackReferenceProcessor_;
    blackReferenceProcessor_ = nullptr;
  }
}

void UdpCommunicator::startWhiteReference() {
  if (whiteReferenceAccumulating_) {
    emit statusChanged(QStringLiteral("白参考累积已在运行"));
    return;
  }
  
  if (!receiving_) {
    emit statusChanged(QStringLiteral("✗ 请先启动UDP接收"));
    return;
  }
  
  // 如果线程不存在，创建并启动白参考处理线程
  if (!whiteReferenceProcessor_) {
    whiteReferenceProcessor_ = new ReferenceProcessor(ReferenceProcessor::WhiteReference, this);
    connect(whiteReferenceProcessor_, &ReferenceProcessor::progressChanged,
            this, &UdpCommunicator::onWhiteReferenceProgressChanged, Qt::QueuedConnection);
    connect(whiteReferenceProcessor_, &ReferenceProcessor::whiteReferenceReady,
            this, &UdpCommunicator::onWhiteReferenceProcessed, Qt::QueuedConnection);
    whiteReferenceProcessor_->start();  // 启动处理线程
  }
  
  whiteReferenceProcessor_->startAccumulating();
  whiteReferenceAccumulating_ = true;
  whiteReferenceProgress_ = 0;
  emit whiteReferenceAccumulatingChanged(true);
  emit whiteReferenceProgressChanged(0);
  emit statusChanged(QStringLiteral("✓ 开始累积白参考数据，需要39500个数据包"));
}

void UdpCommunicator::stopWhiteReference() {
  if (!whiteReferenceAccumulating_) {
    return;
  }
  
  if (whiteReferenceProcessor_) {
    whiteReferenceProcessor_->stopAccumulating();
    whiteReferenceAccumulating_ = false;
    whiteReferenceProgress_ = 0;
    emit whiteReferenceAccumulatingChanged(false);
    emit whiteReferenceProgressChanged(0);
    emit statusChanged(QStringLiteral("白参考累积已停止"));
    
    // 停止并删除白参考处理线程（不再常驻）
    whiteReferenceProcessor_->stopProcessing();
    delete whiteReferenceProcessor_;
    whiteReferenceProcessor_ = nullptr;
  }
}

void UdpCommunicator::onWhiteReferenceProgressChanged(int count, int total) {
  whiteReferenceProgress_ = count;
  emit whiteReferenceProgressChanged(count);
  
  // 每1000个数据包更新一次状态
  if (count % 1000 == 0 || count == total) {
    emit statusChanged(QStringLiteral("白参考累积进度: ") + QString::number(count) + 
                       QStringLiteral("/") + QString::number(total));
  }
}

void UdpCommunicator::onWhiteReferenceProcessed(const QVariantList &averagedSpectrum, 
                                                 double minVal, double maxVal) {
  whiteReferenceAccumulating_ = false;
  whiteReferenceProgress_ = 0;
  emit whiteReferenceAccumulatingChanged(false);
  emit whiteReferenceProgressChanged(0);
  
  // 保存白参考数据
  whiteReferenceData_ = averagedSpectrum;
  
  // 将白参考数据传递给光谱处理线程（如果存在）
  if (spectrumProcessor_) {
    spectrumProcessor_->setWhiteReferenceData(averagedSpectrum);
  }
  
  emit statusChanged(QStringLiteral("✓ 白参考数据处理完成！平均值: ") + 
                     QString::number(minVal, 'f', 2) + QStringLiteral(" ~ ") + 
                     QString::number(maxVal, 'f', 2));
  
  // 检查是否可以进行黑白校正
  if (!blackReferenceData_.empty()) {
    emit statusChanged(QStringLiteral("✓ 黑白参考数据已就绪，光谱数据将在后台线程进行黑白校正"));
  }
  
  // 将处理好的白参考数据发送到QML
  emit whiteReferenceReady(averagedSpectrum, minVal, maxVal);
  
  // 处理完成后，停止并删除白参考处理线程（不再常驻）
  if (whiteReferenceProcessor_) {
    whiteReferenceProcessor_->stopProcessing();
    delete whiteReferenceProcessor_;
    whiteReferenceProcessor_ = nullptr;
  }
}

void UdpCommunicator::setPredictorManager(SpectrumPredictorManager *manager) {
  predictorManager_ = manager;
  // 如果光谱处理线程已创建，设置预测器管理器
  if (spectrumProcessor_) {
    spectrumProcessor_->setPredictorManager(manager);
  }
}

void UdpCommunicator::setPredictorIndex(int index) {
  // 保存预测器索引
  currentPredictorIndex_ = index;
  
  // 设置预测器索引到光谱处理线程（如果存在）
  if (spectrumProcessor_) {
    spectrumProcessor_->setPredictorIndex(index);
  }
}

void UdpCommunicator::onPredictionReady(int predictorIndex, double predictionValue) {
  // 转发预测结果信号到 QML
  emit predictionReady(predictorIndex, predictionValue);
}

