#include "log_manager.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QMutexLocker>
#include <QTextStream>

LogManager *LogManager::s_instance = nullptr;
QtMessageHandler LogManager::s_prevHandler = nullptr;

LogManager::LogManager(QObject *parent)
    : QObject(parent),
      resultSpectrumLen_(1024) {  // 默认光谱点数（1000~1600nm 分成 1024 点）
  // 简单单例：保存最后一个创建的实例指针
  s_instance = this;

  // 确定日志文件路径：<应用目录>/log/...
  const QString baseDir = QCoreApplication::applicationDirPath();
  QDir dir(baseDir);
  if (!dir.exists(QStringLiteral("log"))) {
    dir.mkpath(QStringLiteral("log"));
  }
  logFilePath_ = dir.filePath(QStringLiteral("log/app.log"));
  resultCsvPath_ = dir.filePath(QStringLiteral("log/result.csv"));
}

LogManager::~LogManager() {
  if (s_instance == this) {
    s_instance = nullptr;
  }
}

LogManager *LogManager::instance() {
  return s_instance;
}

QVariantList LogManager::entries() const {
  QMutexLocker locker(&mutex_);
  return entries_;
}

void LogManager::clear() {
  {
    QMutexLocker locker(&mutex_);
    entries_.clear();
  }
  emit entriesChanged();
}

void LogManager::logInfo(const QString &source, const QString &message) {
  QString fullMsg = message;
  if (!source.isEmpty()) {
    fullMsg = QStringLiteral("[%1] %2").arg(source, message);
  }
  append(QtInfoMsg, fullMsg);
}

void LogManager::logPredictionResult(int predictorIndex,
                                     double value,
                                     const QString &status,
                                     bool monitorEnabled,
                                     double lowerLimit,
                                     double upperLimit,
                                     const QVariantList &spectrum) {
  if (resultCsvPath_.isEmpty()) {
    return;
  }

  QMutexLocker locker(&mutex_);

  QFile file(resultCsvPath_);
  const bool exists = file.exists();
  if (!file.open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text)) {
    qWarning() << "[LogManager] Failed to open prediction result CSV:" << resultCsvPath_
               << ", error:" << file.errorString();
    return;
  }

  QTextStream out(&file);

  // 如果文件是新建的，先写表头
  if (!exists) {
    out << "timestamp,predictorIndex,value,status,monitorEnabled,lowerLimit,upperLimit";
    // 如果有光谱长度信息，追加对应波长列（单位 nm），假定 1000~1600 等间隔
    if (resultSpectrumLen_ > 0) {
      const double lambdaStart = 1000.0;
      const double lambdaEnd = 1600.0;
      const double step = (resultSpectrumLen_ > 1)
                            ? (lambdaEnd - lambdaStart) / (resultSpectrumLen_ - 1)
                            : 0.0;
      for (int i = 0; i < resultSpectrumLen_; ++i) {
        const double lambda = lambdaStart + step * i;
        out << "," << QString::number(lambda, 'f', 2);
      }
    }
    out << "\n";
  }

  const QString ts = QDateTime::currentDateTime().toString(Qt::ISODate);

  // 写基础字段
  out << ts << ","
      << predictorIndex << ","
      << QString::number(value, 'f', 10) << ","
      << "\"" << status << "\"" << ","
      << (monitorEnabled ? "1" : "0") << ",";

  if (monitorEnabled) {
    out << QString::number(lowerLimit, 'f', 10) << ","
        << QString::number(upperLimit, 'f', 10);
  } else {
    out << ",";  // lowerLimit 空
    out << "";   // upperLimit 空
  }

  // 追加光谱数据列（如果有配置长度）
  if (resultSpectrumLen_ > 0) {
    for (int i = 0; i < resultSpectrumLen_; ++i) {
      out << ",";
      if (i < spectrum.size()) {
        bool ok = false;
        const double v = spectrum[i].toDouble(&ok);
        if (ok) {
          out << QString::number(v, 'f', 10);
        }
      }
    }
  }

  out << "\n";

  file.close();
}

void LogManager::append(QtMsgType type, const QString &msg) {
  QVariantMap entry;

  // 时间戳
  entry.insert(QStringLiteral("timestamp"),
               QDateTime::currentDateTime().toString(QStringLiteral("yyyy-MM-dd hh:mm:ss.zzz")));

  // 日志级别
  QString level;
  switch (type) {
    case QtDebugMsg:
      level = QStringLiteral("DEBUG");
      break;
    case QtInfoMsg:
      level = QStringLiteral("INFO");
      break;
    case QtWarningMsg:
      level = QStringLiteral("WARN");
      break;
    case QtCriticalMsg:
      level = QStringLiteral("ERROR");
      break;
    case QtFatalMsg:
      level = QStringLiteral("FATAL");
      break;
  }
  entry.insert(QStringLiteral("level"), level);

  // 消息文本
  entry.insert(QStringLiteral("message"), msg);

  {
    QMutexLocker locker(&mutex_);
    entries_.append(entry);

    // 控制最大条数，避免内存无限增长
    while (entries_.size() > kMaxEntries) {
      entries_.removeFirst();
    }
  }

  emit entriesChanged();

  // 同步追加写入到本地 .log 文件
  if (!logFilePath_.isEmpty()) {
    QFile file(logFilePath_);
    if (file.open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text)) {
      QTextStream out(&file);
      out << entry.value(QStringLiteral("timestamp")).toString()
          << " [" << entry.value(QStringLiteral("level")).toString() << "] "
          << entry.value(QStringLiteral("message")).toString() << '\n';
      file.close();
    }
  }
}

void LogManager::messageHandler(QtMsgType type,
                                const QMessageLogContext &context,
                                const QString &msg) {
  // 先调用原来的处理函数，保持终端输出行为
  if (s_prevHandler) {
    s_prevHandler(type, context, msg);
  } else {
    // 默认输出到 stderr，仿照 Qt 默认实现
    QByteArray localMsg = msg.toLocal8Bit();
    const char *file = context.file ? context.file : "";
    const char *function = context.function ? context.function : "";
    fprintf(stderr, "%s (%s:%u, %s)\n", localMsg.constData(), file, context.line, function);
    fflush(stderr);
  }

  // 再写入到 LogManager（如果存在实例）
  if (s_instance) {
    s_instance->append(type, msg);
  }
}

void LogManager::installGlobalHandler() {
  // 只安装一次
  static bool installed = false;
  if (installed) {
    return;
  }
  installed = true;

  s_prevHandler = qInstallMessageHandler(&LogManager::messageHandler);
}


