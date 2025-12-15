#pragma once

#include <QObject>
#include <QPluginLoader>
#include <QStringList>
#include <QVariant>
#include <memory>
#include <vector>

#include "plugin_interface.h"

// 负责加载计算插件并暴露给 QML
class PluginManager : public QObject {
  Q_OBJECT
  Q_PROPERTY(QStringList pluginNames READ pluginNames NOTIFY pluginsChanged)

 public:
  explicit PluginManager(QObject *parent = nullptr);

  QStringList pluginNames() const;

  Q_INVOKABLE bool hasPlugins() const;
  Q_INVOKABLE QVariant compute(int index, double a, double b);

 signals:
  void pluginsChanged();

 private:
  void loadPlugins();

  struct LoadedPlugin {
    std::unique_ptr<QPluginLoader> loader;
    CalcPlugin *instance = nullptr;  // owned by loader
    QString displayName;
  };

  std::vector<LoadedPlugin> plugins_;
};


