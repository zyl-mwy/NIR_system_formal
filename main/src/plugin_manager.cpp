#include "plugin_manager.h"

#include <QCoreApplication>
#include <QDir>
#include <QVariant>

PluginManager::PluginManager(QObject *parent) : QObject(parent) {
  loadPlugins();
}

QStringList PluginManager::pluginNames() const {
  QStringList names;
  names.reserve(static_cast<int>(plugins_.size()));
  for (const auto &p : plugins_) {
    names.push_back(p.displayName);
  }
  return names;
}

bool PluginManager::hasPlugins() const { return !plugins_.empty(); }

QVariant PluginManager::compute(int index, double a, double b) {
  if (index < 0 || index >= static_cast<int>(plugins_.size())) {
    return {};
  }

  auto *calc = plugins_[static_cast<std::size_t>(index)].instance;
  if (!calc) return {};

  const double result = calc->compute(a, b);
  return QVariant::fromValue(result);
}

void PluginManager::loadPlugins() {
  const QString plugin_dir =
      QCoreApplication::applicationDirPath() + "/plugins";

  QDir dir(plugin_dir);
  if (!dir.exists()) {
    dir.mkpath(".");
  }

  const auto files = dir.entryInfoList(QDir::Files);
  for (const auto &info : files) {
    auto loader = std::make_unique<QPluginLoader>(info.absoluteFilePath());
    QObject *obj = loader->instance();
    if (!obj) continue;

    auto *calc = qobject_cast<CalcPlugin *>(obj);
    if (!calc) continue;

    LoadedPlugin lp;
    lp.loader = std::move(loader);
    lp.instance = calc;
    lp.displayName = calc->name();
    plugins_.push_back(std::move(lp));
  }

  emit pluginsChanged();
}


