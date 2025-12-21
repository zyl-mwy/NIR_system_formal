#include "spectrum_file_manager.h"

#include <QDateTime>
#include <QDebug>
#include <QFile>
#include <QTextStream>
#include <QVariantMap>

SpectrumFileManager::SpectrumFileManager(QObject *parent)
    : QObject(parent) {}

bool SpectrumFileManager::saveSpectrumToCsv(const QVariantList &spectrum,
                                            const QString &filePath) {
  if (filePath.isEmpty()) {
    qWarning() << "[SpectrumFileManager] saveSpectrumToCsv: empty filePath";
    return false;
  }

  QFile file(filePath);
  if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
    qWarning() << "[SpectrumFileManager] Failed to open file for writing:"
               << filePath << ", error:" << file.errorString();
    return false;
  }

  QTextStream out(&file);
  out.setRealNumberNotation(QTextStream::FixedNotation);
  out.setRealNumberPrecision(10);

  for (int i = 0; i < spectrum.size(); ++i) {
    bool ok = false;
    const double value = spectrum[i].toDouble(&ok);
    if (!ok) {
      qWarning() << "[SpectrumFileManager] Non-numeric value at index" << i
                 << "when saving to CSV";
      continue;
    }
    if (i > 0) {
      out << ",";
    }
    out << value;
  }
  out << "\n";

  file.close();
  qDebug() << "[SpectrumFileManager] Saved spectrum to CSV:" << filePath
           << ", length:" << spectrum.size();
  return true;
}

QVariantList SpectrumFileManager::loadSpectrumFromCsv(const QString &filePath) {
  QVariantList result;

  if (filePath.isEmpty()) {
    qWarning() << "[SpectrumFileManager] loadSpectrumFromCsv: empty filePath";
    return result;
  }

  QFile file(filePath);
  if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    qWarning() << "[SpectrumFileManager] Failed to open file for reading:"
               << filePath << ", error:" << file.errorString();
    return result;
  }

  QTextStream in(&file);
  const QString line = in.readLine();
  file.close();

  if (line.isEmpty()) {
    qWarning() << "[SpectrumFileManager] CSV file is empty:" << filePath;
    return result;
  }

  const QStringList parts = line.split(",", Qt::SkipEmptyParts);
  for (const QString &part : parts) {
    bool ok = false;
    const double value = part.trimmed().toDouble(&ok);
    if (ok) {
      result.append(value);
    } else {
      qWarning() << "[SpectrumFileManager] Invalid numeric value in CSV:"
                 << part;
    }
  }

  qDebug() << "[SpectrumFileManager] Loaded spectrum from CSV:" << filePath
           << ", length:" << result.size();
  return result;
}

bool SpectrumFileManager::saveAllSpectraTableToCsv(const QVariantList &records,
                                                   const QString &filePath) {
  if (filePath.isEmpty()) {
    qWarning() << "[SpectrumFileManager] saveAllSpectraTableToCsv: empty filePath";
    return false;
  }

  QFile file(filePath);
  if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
    qWarning() << "[SpectrumFileManager] Failed to open file for writing (all spectra table):"
               << filePath << ", error:" << file.errorString();
    return false;
  }

  // 计算所有记录中光谱的最大长度，用于决定光谱列数
  int maxLen = 0;
  for (const QVariant &recVar : records) {
    const QVariantMap recMap = recVar.toMap();
    const QVariantList spectrum = recMap.value(QStringLiteral("spectrum")).toList();
    if (spectrum.size() > maxLen) {
      maxLen = spectrum.size();
    }
  }

  QTextStream out(&file);
  out.setRealNumberNotation(QTextStream::FixedNotation);
  out.setRealNumberPrecision(10);

  // 表头：索引 / 标签 / 时间 / 长度 / 最小值 / 最大值 / 水分 / λ0 ... λN （波长，单位 nm）
  // 假定光谱为等间隔采样，波长范围为 1000~1600 nm
  const double lambdaStart = 1000.0;
  const double lambdaEnd = 1600.0;
  out << "index,label,time,length,minVal,maxVal,moisture";
  if (maxLen > 0) {
    const double step = (maxLen > 1) ? (lambdaEnd - lambdaStart) / (maxLen - 1) : 0.0;
    for (int i = 0; i < maxLen; ++i) {
      const double lambda = lambdaStart + step * i;
      // 只保留两位小数即可用于标识波长点
      out << "," << QString::number(lambda, 'f', 2);
    }
  }
  out << "\n";

  // 每条记录一行
  for (const QVariant &recVar : records) {
    const QVariantMap recMap = recVar.toMap();
    const int index = recMap.value(QStringLiteral("index")).toInt();
    QString label = recMap.value(QStringLiteral("label")).toString();

    QString timeStr;
    const QVariant timeVar = recMap.value(QStringLiteral("time"));
    if (timeVar.canConvert<QDateTime>()) {
      const QDateTime dt = timeVar.toDateTime();
      timeStr = dt.toString(Qt::ISODate);
    } else {
      // 退化为直接 toString
      timeStr = timeVar.toString();
    }

    const int length = recMap.value(QStringLiteral("length")).toInt();
    const double minVal = recMap.value(QStringLiteral("minVal")).toDouble();
    const double maxVal = recMap.value(QStringLiteral("maxVal")).toDouble();
    const double moisture = recMap.value(QStringLiteral("moisture")).toDouble();
    const QVariantList spectrum = recMap.value(QStringLiteral("spectrum")).toList();

    // 为了不修改原始字符串，这里用局部变量做转义
    label.replace("\"", "\"\"");
    timeStr.replace("\"", "\"\"");

    // 先写前几列元数据（用引号包裹 label 和 time，避免逗号影响）
    out << index << ",";
    out << "\"" << label << "\",";
    out << "\"" << timeStr << "\",";
    out << length << ",";
    out << minVal << ",";
    out << maxVal << ",";
    out << moisture;

    // 再写光谱数据列
    for (int i = 0; i < maxLen; ++i) {
      out << ",";
      if (i < spectrum.size()) {
        bool ok = false;
        const double value = spectrum[i].toDouble(&ok);
        if (ok) {
          out << value;
        }
      }
    }
    out << "\n";
  }

  file.close();
  qDebug() << "[SpectrumFileManager] Saved all spectra table to CSV:" << filePath
           << ", records:" << records.size() << ", maxLen:" << maxLen;
  return true;
}

// 简单 CSV 行解析器，支持双引号包裹、双引号转义 "" -> "
static QStringList splitCsvLine(const QString &line) {
  QStringList result;
  QString current;
  bool inQuotes = false;

  const int n = line.size();
  for (int i = 0; i < n; ++i) {
    const QChar c = line.at(i);
    if (c == '\"') {
      if (inQuotes && i + 1 < n && line.at(i + 1) == '\"') {
        // 转义双引号
        current.append('\"');
        ++i;  // 跳过下一个引号
      } else {
        inQuotes = !inQuotes;
      }
    } else if (c == ',' && !inQuotes) {
      result.append(current);
      current.clear();
    } else {
      current.append(c);
    }
  }
  result.append(current);
  return result;
}

QVariantList SpectrumFileManager::loadAllSpectraTableFromCsv(const QString &filePath) {
  QVariantList records;

  if (filePath.isEmpty()) {
    qWarning() << "[SpectrumFileManager] loadAllSpectraTableFromCsv: empty filePath";
    return records;
  }

  QFile file(filePath);
  if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    qWarning() << "[SpectrumFileManager] Failed to open file for reading (all spectra table):"
               << filePath << ", error:" << file.errorString();
    return records;
  }

  QTextStream in(&file);
  const QString headerLine = in.readLine();
  if (headerLine.isEmpty()) {
    qWarning() << "[SpectrumFileManager] CSV table file is empty:" << filePath;
    return records;
  }

  const QStringList headerCols = splitCsvLine(headerLine);
  if (headerCols.size() < 7) {
    qWarning() << "[SpectrumFileManager] CSV table header too short, expected at least 7 columns:";
    return records;
  }

  // 逐行解析数据
  while (!in.atEnd()) {
    const QString line = in.readLine();
    if (line.trimmed().isEmpty())
      continue;

    const QStringList cols = splitCsvLine(line);
    if (cols.size() < 7) {
      qWarning() << "[SpectrumFileManager] CSV data row too short, skip:" << line;
      continue;
    }

    bool ok = false;
    const int index = cols[0].trimmed().toInt(&ok);
    if (!ok) {
      qWarning() << "[SpectrumFileManager] Invalid index value in CSV row, skip:" << cols[0];
      continue;
    }

    const QString label = cols[1];  // 引号已在解析时去掉
    const QString timeStr = cols[2];

    const int length = cols[3].trimmed().toInt(&ok);
    if (!ok) {
      qWarning() << "[SpectrumFileManager] Invalid length value in CSV row, skip:" << cols[3];
      continue;
    }

    const double minVal = cols[4].trimmed().toDouble(&ok);
    if (!ok) {
      qWarning() << "[SpectrumFileManager] Invalid minVal value in CSV row, skip:" << cols[4];
      continue;
    }

    const double maxVal = cols[5].trimmed().toDouble(&ok);
    if (!ok) {
      qWarning() << "[SpectrumFileManager] Invalid maxVal value in CSV row, skip:" << cols[5];
      continue;
    }

    const double moisture = cols[6].trimmed().toDouble(&ok);
    if (!ok) {
      qWarning() << "[SpectrumFileManager] Invalid moisture value in CSV row, set to 0:" << cols[6];
    }

    // 光谱数据从第 7 列开始
    QVariantList spectrum;
    for (int i = 7; i < cols.size(); ++i) {
      const QString part = cols[i].trimmed();
      if (part.isEmpty())
        continue;
      const double v = part.toDouble(&ok);
      if (ok) {
        spectrum.append(v);
      } else {
        qWarning() << "[SpectrumFileManager] Invalid spectrum value in CSV row, column" << i << ":" << part;
      }
    }

    // 尝试将时间字符串解析为 QDateTime
    QDateTime dt = QDateTime::fromString(timeStr, Qt::ISODate);
    QVariant timeVar;
    if (dt.isValid()) {
      timeVar = dt;
    } else {
      timeVar = timeStr;
    }

    QVariantMap recMap;
    recMap.insert(QStringLiteral("index"), index);
    recMap.insert(QStringLiteral("label"), label);
    recMap.insert(QStringLiteral("time"), timeVar);
    recMap.insert(QStringLiteral("length"), length);
    recMap.insert(QStringLiteral("minVal"), minVal);
    recMap.insert(QStringLiteral("maxVal"), maxVal);
    recMap.insert(QStringLiteral("moisture"), moisture);
    recMap.insert(QStringLiteral("spectrum"), spectrum);

    records.append(recMap);
  }

  file.close();
  qDebug() << "[SpectrumFileManager] Loaded all spectra table from CSV:" << filePath
           << ", records:" << records.size();
  return records;
}


