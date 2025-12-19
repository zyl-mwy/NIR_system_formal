/****************************************************************************
** Meta object code from reading C++ file 'system_monitor.h'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.10.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../src/system_monitor.h"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'system_monitor.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 69
#error "This file was generated using the moc from 6.10.1. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

#ifndef Q_CONSTINIT
#define Q_CONSTINIT
#endif

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
QT_WARNING_DISABLE_GCC("-Wuseless-cast")
namespace {
struct qt_meta_tag_ZN13SystemMonitorE_t {};
} // unnamed namespace

template <> constexpr inline auto SystemMonitor::qt_create_metaobjectdata<qt_meta_tag_ZN13SystemMonitorE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "SystemMonitor",
        "metricsUpdated",
        "",
        "updateIntervalChanged",
        "updateMetrics",
        "cpuUsage",
        "cpuTemperature",
        "memoryUsage",
        "memoryTotal",
        "diskUsage",
        "diskTotal",
        "updateIntervalMs"
    };

    QtMocHelpers::UintData qt_methods {
        // Signal 'metricsUpdated'
        QtMocHelpers::SignalData<void()>(1, 2, QMC::AccessPublic, QMetaType::Void),
        // Signal 'updateIntervalChanged'
        QtMocHelpers::SignalData<void()>(3, 2, QMC::AccessPublic, QMetaType::Void),
        // Slot 'updateMetrics'
        QtMocHelpers::SlotData<void()>(4, 2, QMC::AccessPrivate, QMetaType::Void),
    };
    QtMocHelpers::UintData qt_properties {
        // property 'cpuUsage'
        QtMocHelpers::PropertyData<double>(5, QMetaType::Double, QMC::DefaultPropertyFlags, 0),
        // property 'cpuTemperature'
        QtMocHelpers::PropertyData<double>(6, QMetaType::Double, QMC::DefaultPropertyFlags, 0),
        // property 'memoryUsage'
        QtMocHelpers::PropertyData<double>(7, QMetaType::Double, QMC::DefaultPropertyFlags, 0),
        // property 'memoryTotal'
        QtMocHelpers::PropertyData<double>(8, QMetaType::Double, QMC::DefaultPropertyFlags, 0),
        // property 'diskUsage'
        QtMocHelpers::PropertyData<double>(9, QMetaType::Double, QMC::DefaultPropertyFlags, 0),
        // property 'diskTotal'
        QtMocHelpers::PropertyData<double>(10, QMetaType::Double, QMC::DefaultPropertyFlags, 0),
        // property 'updateIntervalMs'
        QtMocHelpers::PropertyData<int>(11, QMetaType::Int, QMC::DefaultPropertyFlags | QMC::Writable | QMC::StdCppSet, 1),
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<SystemMonitor, qt_meta_tag_ZN13SystemMonitorE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject SystemMonitor::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN13SystemMonitorE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN13SystemMonitorE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN13SystemMonitorE_t>.metaTypes,
    nullptr
} };

void SystemMonitor::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<SystemMonitor *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: _t->metricsUpdated(); break;
        case 1: _t->updateIntervalChanged(); break;
        case 2: _t->updateMetrics(); break;
        default: ;
        }
    }
    if (_c == QMetaObject::IndexOfMethod) {
        if (QtMocHelpers::indexOfMethod<void (SystemMonitor::*)()>(_a, &SystemMonitor::metricsUpdated, 0))
            return;
        if (QtMocHelpers::indexOfMethod<void (SystemMonitor::*)()>(_a, &SystemMonitor::updateIntervalChanged, 1))
            return;
    }
    if (_c == QMetaObject::ReadProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: *reinterpret_cast<double*>(_v) = _t->cpuUsage(); break;
        case 1: *reinterpret_cast<double*>(_v) = _t->cpuTemperature(); break;
        case 2: *reinterpret_cast<double*>(_v) = _t->memoryUsage(); break;
        case 3: *reinterpret_cast<double*>(_v) = _t->memoryTotal(); break;
        case 4: *reinterpret_cast<double*>(_v) = _t->diskUsage(); break;
        case 5: *reinterpret_cast<double*>(_v) = _t->diskTotal(); break;
        case 6: *reinterpret_cast<int*>(_v) = _t->updateIntervalMs(); break;
        default: break;
        }
    }
    if (_c == QMetaObject::WriteProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 6: _t->setUpdateIntervalMs(*reinterpret_cast<int*>(_v)); break;
        default: break;
        }
    }
}

const QMetaObject *SystemMonitor::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *SystemMonitor::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN13SystemMonitorE_t>.strings))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int SystemMonitor::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 3)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 3;
    }
    if (_c == QMetaObject::ReadProperty || _c == QMetaObject::WriteProperty
            || _c == QMetaObject::ResetProperty || _c == QMetaObject::BindableProperty
            || _c == QMetaObject::RegisterPropertyMetaType) {
        qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    }
    return _id;
}

// SIGNAL 0
void SystemMonitor::metricsUpdated()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void SystemMonitor::updateIntervalChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}
QT_WARNING_POP
