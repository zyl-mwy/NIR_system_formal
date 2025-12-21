#pragma once

#include <QObject>
#include <QVariant>
#include <QDateTime>
#include <QMutex>
#include <QString>

// 简单日志管理器：
// - 通过全局 Qt 消息处理函数收集 qDebug/qWarning 等日志
// - 将日志存到内存中的 QVariantList，供 QML 显示
// - 每条日志包含：时间戳、级别、消息文本
class LogManager : public QObject {
  Q_OBJECT
  Q_PROPERTY(QVariantList entries READ entries NOTIFY entriesChanged)

 public:
  explicit LogManager(QObject *parent = nullptr);
  ~LogManager() override;

  // 返回所有日志条目（每条是一个 QVariantMap: { timestamp, level, message }）
  QVariantList entries() const;

  // 清空日志
  Q_INVOKABLE void clear();

  // 供 QML / 业务代码显式记录一条“通信状态”等信息日志
  Q_INVOKABLE void logInfo(const QString &source, const QString &message);

  // 将单条预测结果追加写入 log/result.csv
  // predictorIndex: 预测器索引
  // value: 预测值
  // status: "正常"/"异常"/"未启用异常监控"
  // monitorEnabled: 是否启用了异常监控
  // lowerLimit/upperLimit: 上下限（未启用监控时可忽略）
  // spectrum: 当前预测使用的光谱数据（例如 1024 点），会按 s0,s1,... 列写入
  Q_INVOKABLE void logPredictionResult(int predictorIndex,
                                       double value,
                                       const QString &status,
                                       bool monitorEnabled,
                                       double lowerLimit,
                                       double upperLimit,
                                       const QVariantList &spectrum);

  // 安装全局 Qt 消息处理函数，用于捕获 qDebug/qWarning 等日志
  static void installGlobalHandler();

  // 单例访问（供内部使用）
  static LogManager *instance();

  // 最大保留的日志条数（超过后会丢弃最旧的）
  static const int kMaxEntries = 10000;

 signals:
  void entriesChanged();

 private:
  void append(QtMsgType type, const QString &msg);

  QVariantList entries_;
  mutable QMutex mutex_;
  QString logFilePath_;      // 文本日志路径 log/app.log
  QString resultCsvPath_;    // 预测结果 CSV 路径 log/result.csv
  int resultSpectrumLen_;    // 预测结果 CSV 中光谱列的长度（首次写入时确定）

  static LogManager *s_instance;
  static QtMessageHandler s_prevHandler;

  static void messageHandler(QtMsgType type,
                             const QMessageLogContext &context,
                             const QString &msg);
};


