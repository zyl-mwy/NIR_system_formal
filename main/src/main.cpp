#include <QCoreApplication>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>

#include "plugin_manager.h"
#include "serial_communicator.h"
#include "udp_communicator.h"

int main(int argc, char *argv[]) {
  QGuiApplication app(argc, argv);

  PluginManager pluginManager;
  SerialCommunicator serialComm;
  UdpCommunicator udpComm;

  // 连接串口状态改变信号，自动控制UDP接收
  // 默认UDP端口和绑定地址
  const int defaultUdpPort = 1234;
  const QString defaultUdpBindAddress = QStringLiteral("192.168.1.102");
  
  QObject::connect(&serialComm, &SerialCommunicator::stateChanged, 
                   [&udpComm, defaultUdpPort, defaultUdpBindAddress](bool started) {
    if (started) {
      // 发送启动命令后，自动启动UDP接收
      udpComm.startReceiving(defaultUdpPort, defaultUdpBindAddress);
    } else {
      // 发送停止命令后，自动停止UDP接收
      udpComm.stopReceiving();
    }
  });

  QQmlApplicationEngine engine;
  engine.rootContext()->setContextProperty("pluginManager", &pluginManager);
  engine.rootContext()->setContextProperty("serialComm", &serialComm);
  engine.rootContext()->setContextProperty("udpComm", &udpComm);

  const QUrl url(QStringLiteral("qrc:/Main.qml"));
  QObject::connect(
      &engine, &QQmlApplicationEngine::objectCreated, &app,
      [url](QObject *obj, const QUrl &objUrl) {
        if (!obj && objUrl == url) {
          QCoreApplication::exit(-1);
        }
      },
      Qt::QueuedConnection);

  engine.load(url);
  if (engine.rootObjects().isEmpty()) {
    return -1;
  }

  // 连接应用程序退出信号，在关闭前自动发送停止命令（如果还在运行）
  QObject::connect(&app, &QGuiApplication::aboutToQuit, [&serialComm]() {
    if (serialComm.isStarted()) {
      // 如果串口还在运行状态，自动发送停止命令
      // 使用默认串口名称，如果需要可以从QML获取，但这里使用默认值
      serialComm.sendStopCommand(QStringLiteral("/dev/ttyUSB0"));
    }
  });

  return app.exec();
}
