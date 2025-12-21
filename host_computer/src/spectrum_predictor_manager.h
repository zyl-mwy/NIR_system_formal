#pragma once

#include <QObject>
#include <QPluginLoader>
#include <QStringList>
#include <QVariant>
#include <memory>
#include <vector>

#include "spectrum_predictor_interface.h"

// 负责加载光谱预测插件
class SpectrumPredictorManager : public QObject {
  Q_OBJECT
  Q_PROPERTY(QStringList predictorNames READ predictorNames NOTIFY predictorsChanged)
  Q_PROPERTY(bool hasPredictors READ hasPredictors NOTIFY predictorsChanged)

 public:
  explicit SpectrumPredictorManager(QObject *parent = nullptr);
  ~SpectrumPredictorManager();

  QStringList predictorNames() const;
  bool hasPredictors() const;

  // 加载模型到指定的预测器
  Q_INVOKABLE bool loadModel(int index, const QString &modelPath);
  
  // 根据算法类型自动加载对应文件夹的模型（自动路径）
  Q_INVOKABLE bool loadModelAuto(int index);
  
  // 使用指定的预测器进行预测
  Q_INVOKABLE double predict(int index, const QVariantList &spectrumData);
  
  // 检查模型是否已加载
  Q_INVOKABLE bool isModelLoaded(int index) const;
  
  // 获取预测器算法名称
  Q_INVOKABLE QString getAlgorithm(int index) const;
  
  // 获取默认模型路径（根据算法类型）
  Q_INVOKABLE QString getDefaultModelPath(int index) const;

 signals:
  void predictorsChanged();
  void modelLoaded(int index, bool success);
  void predictionCompleted(int index, double result);

 private:
  void loadPredictors();

  struct LoadedPredictor {
    std::unique_ptr<QPluginLoader> loader;
    SpectrumPredictorPlugin *instance = nullptr;  // owned by loader
    QString displayName;
    QString algorithm;
  };

  std::vector<LoadedPredictor> predictors_;
};

