#include "spectrum_predictor_manager.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <QDebug>

SpectrumPredictorManager::SpectrumPredictorManager(QObject *parent) : QObject(parent) {
  loadPredictors();
}

SpectrumPredictorManager::~SpectrumPredictorManager() {
  predictors_.clear();
}

QStringList SpectrumPredictorManager::predictorNames() const {
  QStringList names;
  names.reserve(static_cast<int>(predictors_.size()));
  for (const auto &p : predictors_) {
    names.push_back(p.displayName);
  }
  return names;
}

bool SpectrumPredictorManager::hasPredictors() const { 
  return !predictors_.empty(); 
}

bool SpectrumPredictorManager::loadModel(int index, const QString &modelPath) {
  if (index < 0 || index >= static_cast<int>(predictors_.size())) {
    qWarning() << "预测器索引无效:" << index;
    emit modelLoaded(index, false);
    return false;
  }

  auto *predictor = predictors_[static_cast<std::size_t>(index)].instance;
  if (!predictor) {
    qWarning() << "预测器实例无效";
    emit modelLoaded(index, false);
    return false;
  }

  bool success = predictor->loadModel(modelPath);
  emit modelLoaded(index, success);
  
  if (success) {
    qDebug() << "模型加载成功:" << modelPath << "预测器:" << predictor->name();
  } else {
    qWarning() << "模型加载失败:" << modelPath;
  }
  
  return success;
}

bool SpectrumPredictorManager::loadModelAuto(int index) {
  QString modelPath = getDefaultModelPath(index);
  if (modelPath.isEmpty()) {
    qWarning() << "无法获取默认模型路径，预测器索引:" << index;
    emit modelLoaded(index, false);
    return false;
  }
  
  return loadModel(index, modelPath);
}

QString SpectrumPredictorManager::getDefaultModelPath(int index) const {
  if (index < 0 || index >= static_cast<int>(predictors_.size())) {
    return QString();
  }
  
  auto *predictor = predictors_[static_cast<std::size_t>(index)].instance;
  if (!predictor) {
    qWarning() << "预测器实例无效";
    return QString();
  }
  
  // 直接从插件获取默认模型路径，路径构建逻辑在插件中实现
  return predictor->getDefaultModelPath();
}

double SpectrumPredictorManager::predict(int index, const QVariantList &spectrumData) {
  if (index < 0 || index >= static_cast<int>(predictors_.size())) {
    qWarning() << "预测器索引无效:" << index;
    return 0.0;
  }

  auto *predictor = predictors_[static_cast<std::size_t>(index)].instance;
  if (!predictor) {
    qWarning() << "预测器实例无效";
    return 0.0;
  }

  if (!predictor->isModelLoaded()) {
    qWarning() << "模型未加载，无法进行预测";
    return 0.0;
  }

  double result = predictor->predict(spectrumData);
  emit predictionCompleted(index, result);
  return result;
}

bool SpectrumPredictorManager::isModelLoaded(int index) const {
  if (index < 0 || index >= static_cast<int>(predictors_.size())) {
    return false;
  }

  auto *predictor = predictors_[static_cast<std::size_t>(index)].instance;
  if (!predictor) {
    return false;
  }

  return predictor->isModelLoaded();
}

QString SpectrumPredictorManager::getAlgorithm(int index) const {
  if (index < 0 || index >= static_cast<int>(predictors_.size())) {
    return QString();
  }

  return predictors_[static_cast<std::size_t>(index)].algorithm;
}

void SpectrumPredictorManager::loadPredictors() {
  const QString plugin_dir =
      QCoreApplication::applicationDirPath() + "/plugins";

  QDir dir(plugin_dir);
  if (!dir.exists()) {
    dir.mkpath(".");
  }

  const auto files = dir.entryInfoList(QDir::Files);
  for (const auto &info : files) {
    // 只加载预测器插件（rf_predictor_plugin.so 或 svm_predictor_plugin.so）
    if (!info.fileName().contains("predictor_plugin")) {
      continue;
    }
    
    auto loader = std::make_unique<QPluginLoader>(info.absoluteFilePath());
    QObject *obj = loader->instance();
    if (!obj) {
      qWarning() << "无法加载插件:" << info.fileName();
      continue;
    }

    auto *predictor = qobject_cast<SpectrumPredictorPlugin *>(obj);
    if (!predictor) {
      qWarning() << "插件不是预测器插件:" << info.fileName();
      continue;
    }

    LoadedPredictor lp;
    lp.loader = std::move(loader);
    lp.instance = predictor;
    lp.displayName = predictor->name();
    lp.algorithm = predictor->algorithm();
    predictors_.push_back(std::move(lp));
    
    qDebug() << "加载预测器插件:" << lp.displayName << "算法:" << lp.algorithm;
  }

  emit predictorsChanged();
}

