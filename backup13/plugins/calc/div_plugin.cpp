#include <QObject>

#include "plugin_interface.h"

class DivPlugin : public QObject, public CalcPlugin {
  Q_OBJECT
  Q_PLUGIN_METADATA(IID CalcPlugin_iid)
  Q_INTERFACES(CalcPlugin)

 public:
  QString name() const override { return "除法 (/)"; }
  double compute(double a, double b) override { return a / b; }
};

#include "div_plugin.moc"

