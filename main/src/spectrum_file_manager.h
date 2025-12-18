#pragma once

#include <QObject>
#include <QVariantList>

class SpectrumFileManager : public QObject {
  Q_OBJECT

public:
  explicit SpectrumFileManager(QObject *parent = nullptr);

  // 将一条光谱保存为 CSV（简单格式：单行，逗号分隔的数值）
  Q_INVOKABLE bool saveSpectrumToCsv(const QVariantList &spectrum,
                                     const QString &filePath);

  // 从 CSV 读取一条光谱（同样假定为单行、逗号分隔），失败返回空列表
  Q_INVOKABLE QVariantList loadSpectrumFromCsv(const QString &filePath);

  // 将当前所有记录（每条包含标签/时间/统计信息/光谱）保存为表格形式 CSV：
  // 前几列是 index, label, time, length, minVal, maxVal, moisture，
  // 后面依次是按波长（nm）标记的光谱点列，例如 1000.0, 1000.6, ..., 1600.0
  Q_INVOKABLE bool saveAllSpectraTableToCsv(const QVariantList &records,
                                            const QString &filePath);

  // 从表格形式 CSV 中读取全部记录，格式需与 saveAllSpectraTableToCsv 输出一致
  // 返回 QVariantList，每个元素是 QVariantMap，键包括：
  // index, label, time(QDateTime), length, minVal, maxVal, moisture, spectrum(QVariantList)
  Q_INVOKABLE QVariantList loadAllSpectraTableFromCsv(const QString &filePath);
};


