// 光谱预测插件公共接口
#pragma once

#include <QtCore/QtPlugin>
#include <QString>
#include <QVariant>

class SpectrumPredictorPlugin {
 public:
  virtual ~SpectrumPredictorPlugin() = default;
  virtual QString name() const = 0;
  virtual QString algorithm() const = 0;  // 算法名称：random_forest 或 svm
  virtual bool loadModel(const QString &modelPath) = 0;  // 加载模型
  virtual double predict(const QVariantList &spectrumData) = 0;  // 预测：输入1024个数据点，返回预测值
  virtual bool isModelLoaded() const = 0;  // 检查模型是否已加载
};

#define SpectrumPredictorPlugin_iid "org.demo.SpectrumPredictorPlugin/1.0"
Q_DECLARE_INTERFACE(SpectrumPredictorPlugin, SpectrumPredictorPlugin_iid)


