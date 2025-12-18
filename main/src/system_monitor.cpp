#include "system_monitor.h"

#include <QDebug>
#include <QFile>
#include <QStorageInfo>
#include <sys/sysinfo.h>

SystemMonitor::SystemMonitor(QObject *parent)
    : QObject(parent),
      updateIntervalMs_(1000),
      hasPrevCpuTimes_(false),
      prevUser_(0),
      prevNice_(0),
      prevSystem_(0),
      prevIdle_(0),
      prevIowait_(0),
      prevIrq_(0),
      prevSoftIrq_(0),
      cpuUsage_(0.0),
      cpuTemperature_(0.0),
      memoryUsage_(0.0),
      memoryTotal_(0.0),
      diskUsage_(0.0),
      diskTotal_(0.0) {
  connect(&timer_, &QTimer::timeout, this, &SystemMonitor::updateMetrics);
  timer_.start(updateIntervalMs_);
}

void SystemMonitor::setUpdateIntervalMs(int ms) {
  if (ms <= 0 || ms == updateIntervalMs_) {
    return;
  }
  updateIntervalMs_ = ms;
  timer_.start(updateIntervalMs_);
  emit updateIntervalChanged();
}

bool SystemMonitor::readCpuTimes(qulonglong &user, qulonglong &nice,
                                 qulonglong &system, qulonglong &idle,
                                 qulonglong &iowait, qulonglong &irq,
                                 qulonglong &softirq) {
  QFile file(QStringLiteral("/proc/stat"));
  if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    return false;
  }

  QByteArray line = file.readLine();
  // 期望格式：cpu  user nice system idle iowait irq softirq ...
  if (!line.startsWith("cpu ")) {
    return false;
  }

  QList<QByteArray> parts = line.split(' ');
  QList<qulonglong> values;
  for (const QByteArray &p : parts) {
    if (p.isEmpty() || p == "cpu") continue;
    bool ok = false;
    qulonglong v = p.toULongLong(&ok);
    if (ok) {
      values.append(v);
    }
  }
  if (values.size() < 7) {
    return false;
  }

  user = values[0];
  nice = values[1];
  system = values[2];
  idle = values[3];
  iowait = values[4];
  irq = values[5];
  softirq = values[6];
  return true;
}

void SystemMonitor::updateCpuUsage() {
  qulonglong user, nice, system, idle, iowait, irq, softirq;
  if (!readCpuTimes(user, nice, system, idle, iowait, irq, softirq)) {
    return;
  }

  if (!hasPrevCpuTimes_) {
    hasPrevCpuTimes_ = true;
  } else {
    qulonglong prevIdleAll = prevIdle_ + prevIowait_;
    qulonglong idleAll = idle + iowait;

    qulonglong prevNonIdle = prevUser_ + prevNice_ + prevSystem_ + prevIrq_ + prevSoftIrq_;
    qulonglong nonIdle = user + nice + system + irq + softirq;

    qulonglong prevTotal = prevIdleAll + prevNonIdle;
    qulonglong total = idleAll + nonIdle;

    qulonglong totalDelta = total - prevTotal;
    qulonglong idleDelta = idleAll - prevIdleAll;

    if (totalDelta > 0) {
      double usage = (double)(totalDelta - idleDelta) * 100.0 / (double)totalDelta;
      cpuUsage_ = usage;
    }
  }

  prevUser_ = user;
  prevNice_ = nice;
  prevSystem_ = system;
  prevIdle_ = idle;
  prevIowait_ = iowait;
  prevIrq_ = irq;
  prevSoftIrq_ = softirq;
}

void SystemMonitor::updateCpuTemperature() {
  // 树莓派等 Linux 通常在 /sys/class/thermal/thermal_zone0/temp
  const char *paths[] = {
      "/sys/class/thermal/thermal_zone0/temp",
      "/sys/class/hwmon/hwmon0/temp1_input"};

  for (const char *p : paths) {
    QFile f(QString::fromLatin1(p));
    if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
      QByteArray data = f.readAll().trimmed();
      bool ok = false;
      int milli = data.toInt(&ok);
      if (ok) {
        cpuTemperature_ = milli / 1000.0;  // 转为摄氏度
        return;
      }
    }
  }
}

void SystemMonitor::updateMemory() {
  // 优先尝试从 /proc/meminfo 读取
  qulonglong memTotalKb = 0;
  qulonglong memAvailableKb = 0;
  qulonglong memFreeKb = 0;
  qulonglong buffersKb = 0;
  qulonglong cachedKb = 0;

  QFile file(QStringLiteral("/proc/meminfo"));
  if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    while (!file.atEnd()) {
      QByteArray line = file.readLine();
      if (line.startsWith("MemTotal:")) {
        QList<QByteArray> parts = line.split(' ');
        for (const QByteArray &p : parts) {
          bool ok = false;
          qulonglong v = p.toULongLong(&ok);
          if (ok) {
            memTotalKb = v;
            break;
          }
        }
      } else if (line.startsWith("MemAvailable:")) {
        QList<QByteArray> parts = line.split(' ');
        for (const QByteArray &p : parts) {
          bool ok = false;
          qulonglong v = p.toULongLong(&ok);
          if (ok) {
            memAvailableKb = v;
            break;
          }
        }
      } else if (line.startsWith("MemFree:")) {
        QList<QByteArray> parts = line.split(' ');
        for (const QByteArray &p : parts) {
          bool ok = false;
          qulonglong v = p.toULongLong(&ok);
          if (ok) {
            memFreeKb = v;
            break;
          }
        }
      } else if (line.startsWith("Buffers:")) {
        QList<QByteArray> parts = line.split(' ');
        for (const QByteArray &p : parts) {
          bool ok = false;
          qulonglong v = p.toULongLong(&ok);
          if (ok) {
            buffersKb = v;
            break;
          }
        }
      } else if (line.startsWith("Cached:")) {
        QList<QByteArray> parts = line.split(' ');
        for (const QByteArray &p : parts) {
          bool ok = false;
          qulonglong v = p.toULongLong(&ok);
          if (ok) {
            cachedKb = v;
            break;
          }
        }
      }
    }
  }

  if (memTotalKb > 0) {
    // 正常情况：使用 /proc/meminfo 结果
    memoryTotal_ = memTotalKb / 1024.0;  // MB
    qulonglong memUsedKb = 0;
    if (memAvailableKb > 0) {
      // 推荐的计算方式：已用 = 总 - 可用
      memUsedKb = memTotalKb - memAvailableKb;
    } else {
      // 某些系统可能没有 MemAvailable 字段，退化为：已用 ≈ 总 - (空闲 + 缓冲 + 缓存)
      qulonglong availableApproxKb = memFreeKb + buffersKb + cachedKb;
      if (availableApproxKb < memTotalKb) {
        memUsedKb = memTotalKb - availableApproxKb;
      } else {
        memUsedKb = memTotalKb - memFreeKb;
      }
    }
    memoryUsage_ = memUsedKb / 1024.0;   // MB

    qDebug() << "[SystemMonitor] (meminfo) memTotalKb:" << memTotalKb
             << "memAvailableKb:" << memAvailableKb
             << "memFreeKb:" << memFreeKb
             << "buffersKb:" << buffersKb
             << "cachedKb:" << cachedKb
             << "memUsedKb:" << memUsedKb
             << "memoryUsage(MB):" << memoryUsage_;
    return;
  }

  // 兜底方案：使用 sysinfo 系统调用（万一 /proc/meminfo 不可用）
  struct sysinfo info;
  if (sysinfo(&info) == 0 && info.totalram > 0) {
    double unit = info.mem_unit > 0 ? (double)info.mem_unit : 1.0;
    double totalBytes = (double)info.totalram * unit;
    double freeBytes = (double)info.freeram * unit;
    memoryTotal_ = totalBytes / (1024.0 * 1024.0);                 // MB
    memoryUsage_ = (totalBytes - freeBytes) / (1024.0 * 1024.0);   // MB

    qDebug() << "[SystemMonitor] (sysinfo) totalBytes:" << totalBytes
             << "freeBytes:" << freeBytes
             << "memoryUsage(MB):" << memoryUsage_ << "/" << memoryTotal_;
  } else {
    qDebug() << "[SystemMonitor] memory info unavailable";
  }
}

void SystemMonitor::updateDisk() {
  QStorageInfo storage = QStorageInfo::root();
  if (!storage.isValid() || !storage.isReady()) {
    return;
  }

  qint64 totalBytes = storage.bytesTotal();
  qint64 freeBytes = storage.bytesAvailable();
  if (totalBytes > 0) {
    diskTotal_ = (double)totalBytes / (1024.0 * 1024.0 * 1024.0);              // GB
    diskUsage_ = (double)(totalBytes - freeBytes) / (1024.0 * 1024.0 * 1024.0); // GB
  }
}

void SystemMonitor::updateMetrics() {
  updateCpuUsage();
  updateCpuTemperature();
  updateMemory();
  updateDisk();

  // 打印一次概要信息，便于调试观察
  qDebug() << "[SystemMonitor] cpuUsage:" << cpuUsage_
           << "cpuTemp:" << cpuTemperature_
           << "memUsed(MB):" << memoryUsage_ << "/" << memoryTotal_
           << "diskUsed(GB):" << diskUsage_ << "/" << diskTotal_;

  emit metricsUpdated();
}


