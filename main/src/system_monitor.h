#pragma once

#include <QObject>
#include <QTimer>
#include <QVariantMap>

// 简单系统监控：
// - 周期性读取 CPU 占用率、CPU 温度、内存占用、磁盘占用等
// - 通过只读属性暴露给 QML，用于实时展示
class SystemMonitor : public QObject {
  Q_OBJECT
  Q_PROPERTY(double cpuUsage READ cpuUsage NOTIFY metricsUpdated)
  Q_PROPERTY(double cpuTemperature READ cpuTemperature NOTIFY metricsUpdated)
  Q_PROPERTY(double memoryUsage READ memoryUsage NOTIFY metricsUpdated)
  Q_PROPERTY(double memoryTotal READ memoryTotal NOTIFY metricsUpdated)
  Q_PROPERTY(double diskUsage READ diskUsage NOTIFY metricsUpdated)
  Q_PROPERTY(double diskTotal READ diskTotal NOTIFY metricsUpdated)
  Q_PROPERTY(int updateIntervalMs READ updateIntervalMs WRITE setUpdateIntervalMs NOTIFY updateIntervalChanged)

 public:
  explicit SystemMonitor(QObject *parent = nullptr);

  double cpuUsage() const { return cpuUsage_; }             // 0~100 %
  double cpuTemperature() const { return cpuTemperature_; } // 摄氏度
  double memoryUsage() const { return memoryUsage_; }       // 已用内存 MB
  double memoryTotal() const { return memoryTotal_; }       // 总内存 MB
  double diskUsage() const { return diskUsage_; }           // 已用磁盘 GB
  double diskTotal() const { return diskTotal_; }           // 总磁盘 GB

  int updateIntervalMs() const { return updateIntervalMs_; }
  void setUpdateIntervalMs(int ms);

 signals:
  void metricsUpdated();
  void updateIntervalChanged();

 private slots:
  void updateMetrics();

 private:
  // CPU 相关
  bool readCpuTimes(qulonglong &user, qulonglong &nice,
                    qulonglong &system, qulonglong &idle,
                    qulonglong &iowait, qulonglong &irq,
                    qulonglong &softirq);

  // 其它指标
  void updateCpuUsage();
  void updateCpuTemperature();
  void updateMemory();
  void updateDisk();

  QTimer timer_;
  int updateIntervalMs_;

  // 上一次 CPU 时间，用于计算利用率
  bool hasPrevCpuTimes_;
  qulonglong prevUser_, prevNice_, prevSystem_, prevIdle_, prevIowait_, prevIrq_, prevSoftIrq_;

  // 当前值
  double cpuUsage_;
  double cpuTemperature_;
  double memoryUsage_;
  double memoryTotal_;
  double diskUsage_;
  double diskTotal_;
};


