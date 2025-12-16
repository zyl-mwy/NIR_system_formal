// 计算插件公共接口
#pragma once

#include <QtCore/QtPlugin>
#include <QString>

class CalcPlugin {
 public:
  virtual ~CalcPlugin() = default;
  virtual QString name() const = 0;
  virtual double compute(double a, double b) = 0;
};

#define CalcPlugin_iid "org.demo.CalcPlugin/1.0"
Q_DECLARE_INTERFACE(CalcPlugin, CalcPlugin_iid)

