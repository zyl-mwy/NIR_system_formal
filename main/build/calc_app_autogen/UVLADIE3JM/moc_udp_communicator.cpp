/****************************************************************************
** Meta object code from reading C++ file 'udp_communicator.h'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.10.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../src/udp_communicator.h"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'udp_communicator.h' doesn't include <QObject>."
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
struct qt_meta_tag_ZN15UdpCommunicatorE_t {};
} // unnamed namespace

template <> constexpr inline auto UdpCommunicator::qt_create_metaobjectdata<qt_meta_tag_ZN15UdpCommunicatorE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "UdpCommunicator",
        "packetReceived",
        "",
        "QVariantList",
        "data",
        "statusChanged",
        "message",
        "receivingChanged",
        "receiving",
        "packetCountChanged",
        "count",
        "packetsPerSecondChanged",
        "rate",
        "spectrumReady",
        "averagedSpectrum",
        "minVal",
        "maxVal",
        "packetCount",
        "blackReferenceAccumulatingChanged",
        "accumulating",
        "blackReferenceProgressChanged",
        "progress",
        "blackReferenceReady",
        "whiteReferenceAccumulatingChanged",
        "whiteReferenceProgressChanged",
        "whiteReferenceReady",
        "predictionReady",
        "predictorIndex",
        "predictionValue",
        "onUdpPacketReceived",
        "onUdpStatusChanged",
        "onUdpErrorOccurred",
        "error",
        "onSecondTimer",
        "onSpectrumProcessed",
        "onBlackReferenceProgressChanged",
        "total",
        "onBlackReferenceProcessed",
        "onWhiteReferenceProgressChanged",
        "onWhiteReferenceProcessed",
        "onPredictionReady",
        "startReceiving",
        "port",
        "bindAddress",
        "stopReceiving",
        "resetPacketCount",
        "startBlackReference",
        "stopBlackReference",
        "startWhiteReference",
        "stopWhiteReference",
        "setPredictorIndex",
        "index",
        "packetsPerSecond",
        "blackReferenceAccumulating",
        "blackReferenceProgress",
        "whiteReferenceAccumulating",
        "whiteReferenceProgress"
    };

    QtMocHelpers::UintData qt_methods {
        // Signal 'packetReceived'
        QtMocHelpers::SignalData<void(const QVariantList &)>(1, 2, QMC::AccessPublic, QMetaType::Void, {{
            { 0x80000000 | 3, 4 },
        }}),
        // Signal 'statusChanged'
        QtMocHelpers::SignalData<void(const QString &)>(5, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::QString, 6 },
        }}),
        // Signal 'receivingChanged'
        QtMocHelpers::SignalData<void(bool)>(7, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Bool, 8 },
        }}),
        // Signal 'packetCountChanged'
        QtMocHelpers::SignalData<void(int)>(9, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 10 },
        }}),
        // Signal 'packetsPerSecondChanged'
        QtMocHelpers::SignalData<void(int)>(11, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 12 },
        }}),
        // Signal 'spectrumReady'
        QtMocHelpers::SignalData<void(const QVariantList &, double, double, int)>(13, 2, QMC::AccessPublic, QMetaType::Void, {{
            { 0x80000000 | 3, 14 }, { QMetaType::Double, 15 }, { QMetaType::Double, 16 }, { QMetaType::Int, 17 },
        }}),
        // Signal 'blackReferenceAccumulatingChanged'
        QtMocHelpers::SignalData<void(bool)>(18, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Bool, 19 },
        }}),
        // Signal 'blackReferenceProgressChanged'
        QtMocHelpers::SignalData<void(int)>(20, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 21 },
        }}),
        // Signal 'blackReferenceReady'
        QtMocHelpers::SignalData<void(const QVariantList &, double, double)>(22, 2, QMC::AccessPublic, QMetaType::Void, {{
            { 0x80000000 | 3, 14 }, { QMetaType::Double, 15 }, { QMetaType::Double, 16 },
        }}),
        // Signal 'whiteReferenceAccumulatingChanged'
        QtMocHelpers::SignalData<void(bool)>(23, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Bool, 19 },
        }}),
        // Signal 'whiteReferenceProgressChanged'
        QtMocHelpers::SignalData<void(int)>(24, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 21 },
        }}),
        // Signal 'whiteReferenceReady'
        QtMocHelpers::SignalData<void(const QVariantList &, double, double)>(25, 2, QMC::AccessPublic, QMetaType::Void, {{
            { 0x80000000 | 3, 14 }, { QMetaType::Double, 15 }, { QMetaType::Double, 16 },
        }}),
        // Signal 'predictionReady'
        QtMocHelpers::SignalData<void(int, double)>(26, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 27 }, { QMetaType::Double, 28 },
        }}),
        // Slot 'onUdpPacketReceived'
        QtMocHelpers::SlotData<void(const QVariantList &)>(29, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { 0x80000000 | 3, 4 },
        }}),
        // Slot 'onUdpStatusChanged'
        QtMocHelpers::SlotData<void(const QString &)>(30, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { QMetaType::QString, 6 },
        }}),
        // Slot 'onUdpErrorOccurred'
        QtMocHelpers::SlotData<void(const QString &)>(31, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { QMetaType::QString, 32 },
        }}),
        // Slot 'onSecondTimer'
        QtMocHelpers::SlotData<void()>(33, 2, QMC::AccessPrivate, QMetaType::Void),
        // Slot 'onSpectrumProcessed'
        QtMocHelpers::SlotData<void(const QVariantList &, double, double, int)>(34, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { 0x80000000 | 3, 14 }, { QMetaType::Double, 15 }, { QMetaType::Double, 16 }, { QMetaType::Int, 17 },
        }}),
        // Slot 'onBlackReferenceProgressChanged'
        QtMocHelpers::SlotData<void(int, int)>(35, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { QMetaType::Int, 10 }, { QMetaType::Int, 36 },
        }}),
        // Slot 'onBlackReferenceProcessed'
        QtMocHelpers::SlotData<void(const QVariantList &, double, double)>(37, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { 0x80000000 | 3, 14 }, { QMetaType::Double, 15 }, { QMetaType::Double, 16 },
        }}),
        // Slot 'onWhiteReferenceProgressChanged'
        QtMocHelpers::SlotData<void(int, int)>(38, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { QMetaType::Int, 10 }, { QMetaType::Int, 36 },
        }}),
        // Slot 'onWhiteReferenceProcessed'
        QtMocHelpers::SlotData<void(const QVariantList &, double, double)>(39, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { 0x80000000 | 3, 14 }, { QMetaType::Double, 15 }, { QMetaType::Double, 16 },
        }}),
        // Slot 'onPredictionReady'
        QtMocHelpers::SlotData<void(int, double)>(40, 2, QMC::AccessPrivate, QMetaType::Void, {{
            { QMetaType::Int, 27 }, { QMetaType::Double, 28 },
        }}),
        // Method 'startReceiving'
        QtMocHelpers::MethodData<bool(int, const QString &)>(41, 2, QMC::AccessPublic, QMetaType::Bool, {{
            { QMetaType::Int, 42 }, { QMetaType::QString, 43 },
        }}),
        // Method 'startReceiving'
        QtMocHelpers::MethodData<bool(int)>(41, 2, QMC::AccessPublic | QMC::MethodCloned, QMetaType::Bool, {{
            { QMetaType::Int, 42 },
        }}),
        // Method 'stopReceiving'
        QtMocHelpers::MethodData<void()>(44, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'resetPacketCount'
        QtMocHelpers::MethodData<void()>(45, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'startBlackReference'
        QtMocHelpers::MethodData<void()>(46, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'stopBlackReference'
        QtMocHelpers::MethodData<void()>(47, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'startWhiteReference'
        QtMocHelpers::MethodData<void()>(48, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'stopWhiteReference'
        QtMocHelpers::MethodData<void()>(49, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'setPredictorIndex'
        QtMocHelpers::MethodData<void(int)>(50, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 51 },
        }}),
    };
    QtMocHelpers::UintData qt_properties {
        // property 'receiving'
        QtMocHelpers::PropertyData<bool>(8, QMetaType::Bool, QMC::DefaultPropertyFlags, 2),
        // property 'packetCount'
        QtMocHelpers::PropertyData<int>(17, QMetaType::Int, QMC::DefaultPropertyFlags, 3),
        // property 'packetsPerSecond'
        QtMocHelpers::PropertyData<int>(52, QMetaType::Int, QMC::DefaultPropertyFlags, 4),
        // property 'blackReferenceAccumulating'
        QtMocHelpers::PropertyData<bool>(53, QMetaType::Bool, QMC::DefaultPropertyFlags, 6),
        // property 'blackReferenceProgress'
        QtMocHelpers::PropertyData<int>(54, QMetaType::Int, QMC::DefaultPropertyFlags, 7),
        // property 'whiteReferenceAccumulating'
        QtMocHelpers::PropertyData<bool>(55, QMetaType::Bool, QMC::DefaultPropertyFlags, 9),
        // property 'whiteReferenceProgress'
        QtMocHelpers::PropertyData<int>(56, QMetaType::Int, QMC::DefaultPropertyFlags, 10),
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<UdpCommunicator, qt_meta_tag_ZN15UdpCommunicatorE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject UdpCommunicator::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN15UdpCommunicatorE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN15UdpCommunicatorE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN15UdpCommunicatorE_t>.metaTypes,
    nullptr
} };

void UdpCommunicator::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<UdpCommunicator *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: _t->packetReceived((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1]))); break;
        case 1: _t->statusChanged((*reinterpret_cast<std::add_pointer_t<QString>>(_a[1]))); break;
        case 2: _t->receivingChanged((*reinterpret_cast<std::add_pointer_t<bool>>(_a[1]))); break;
        case 3: _t->packetCountChanged((*reinterpret_cast<std::add_pointer_t<int>>(_a[1]))); break;
        case 4: _t->packetsPerSecondChanged((*reinterpret_cast<std::add_pointer_t<int>>(_a[1]))); break;
        case 5: _t->spectrumReady((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[3])),(*reinterpret_cast<std::add_pointer_t<int>>(_a[4]))); break;
        case 6: _t->blackReferenceAccumulatingChanged((*reinterpret_cast<std::add_pointer_t<bool>>(_a[1]))); break;
        case 7: _t->blackReferenceProgressChanged((*reinterpret_cast<std::add_pointer_t<int>>(_a[1]))); break;
        case 8: _t->blackReferenceReady((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[3]))); break;
        case 9: _t->whiteReferenceAccumulatingChanged((*reinterpret_cast<std::add_pointer_t<bool>>(_a[1]))); break;
        case 10: _t->whiteReferenceProgressChanged((*reinterpret_cast<std::add_pointer_t<int>>(_a[1]))); break;
        case 11: _t->whiteReferenceReady((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[3]))); break;
        case 12: _t->predictionReady((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2]))); break;
        case 13: _t->onUdpPacketReceived((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1]))); break;
        case 14: _t->onUdpStatusChanged((*reinterpret_cast<std::add_pointer_t<QString>>(_a[1]))); break;
        case 15: _t->onUdpErrorOccurred((*reinterpret_cast<std::add_pointer_t<QString>>(_a[1]))); break;
        case 16: _t->onSecondTimer(); break;
        case 17: _t->onSpectrumProcessed((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[3])),(*reinterpret_cast<std::add_pointer_t<int>>(_a[4]))); break;
        case 18: _t->onBlackReferenceProgressChanged((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<int>>(_a[2]))); break;
        case 19: _t->onBlackReferenceProcessed((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[3]))); break;
        case 20: _t->onWhiteReferenceProgressChanged((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<int>>(_a[2]))); break;
        case 21: _t->onWhiteReferenceProcessed((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[3]))); break;
        case 22: _t->onPredictionReady((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2]))); break;
        case 23: { bool _r = _t->startReceiving((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QString>>(_a[2])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 24: { bool _r = _t->startReceiving((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 25: _t->stopReceiving(); break;
        case 26: _t->resetPacketCount(); break;
        case 27: _t->startBlackReference(); break;
        case 28: _t->stopBlackReference(); break;
        case 29: _t->startWhiteReference(); break;
        case 30: _t->stopWhiteReference(); break;
        case 31: _t->setPredictorIndex((*reinterpret_cast<std::add_pointer_t<int>>(_a[1]))); break;
        default: ;
        }
    }
    if (_c == QMetaObject::IndexOfMethod) {
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(const QVariantList & )>(_a, &UdpCommunicator::packetReceived, 0))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(const QString & )>(_a, &UdpCommunicator::statusChanged, 1))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(bool )>(_a, &UdpCommunicator::receivingChanged, 2))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(int )>(_a, &UdpCommunicator::packetCountChanged, 3))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(int )>(_a, &UdpCommunicator::packetsPerSecondChanged, 4))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(const QVariantList & , double , double , int )>(_a, &UdpCommunicator::spectrumReady, 5))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(bool )>(_a, &UdpCommunicator::blackReferenceAccumulatingChanged, 6))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(int )>(_a, &UdpCommunicator::blackReferenceProgressChanged, 7))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(const QVariantList & , double , double )>(_a, &UdpCommunicator::blackReferenceReady, 8))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(bool )>(_a, &UdpCommunicator::whiteReferenceAccumulatingChanged, 9))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(int )>(_a, &UdpCommunicator::whiteReferenceProgressChanged, 10))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(const QVariantList & , double , double )>(_a, &UdpCommunicator::whiteReferenceReady, 11))
            return;
        if (QtMocHelpers::indexOfMethod<void (UdpCommunicator::*)(int , double )>(_a, &UdpCommunicator::predictionReady, 12))
            return;
    }
    if (_c == QMetaObject::ReadProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: *reinterpret_cast<bool*>(_v) = _t->isReceiving(); break;
        case 1: *reinterpret_cast<int*>(_v) = _t->packetCount(); break;
        case 2: *reinterpret_cast<int*>(_v) = _t->packetsPerSecond(); break;
        case 3: *reinterpret_cast<bool*>(_v) = _t->isBlackReferenceAccumulating(); break;
        case 4: *reinterpret_cast<int*>(_v) = _t->blackReferenceProgress(); break;
        case 5: *reinterpret_cast<bool*>(_v) = _t->isWhiteReferenceAccumulating(); break;
        case 6: *reinterpret_cast<int*>(_v) = _t->whiteReferenceProgress(); break;
        default: break;
        }
    }
}

const QMetaObject *UdpCommunicator::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *UdpCommunicator::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN15UdpCommunicatorE_t>.strings))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int UdpCommunicator::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 32)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 32;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 32)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 32;
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
void UdpCommunicator::packetReceived(const QVariantList & _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 0, nullptr, _t1);
}

// SIGNAL 1
void UdpCommunicator::statusChanged(const QString & _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 1, nullptr, _t1);
}

// SIGNAL 2
void UdpCommunicator::receivingChanged(bool _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 2, nullptr, _t1);
}

// SIGNAL 3
void UdpCommunicator::packetCountChanged(int _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 3, nullptr, _t1);
}

// SIGNAL 4
void UdpCommunicator::packetsPerSecondChanged(int _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 4, nullptr, _t1);
}

// SIGNAL 5
void UdpCommunicator::spectrumReady(const QVariantList & _t1, double _t2, double _t3, int _t4)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 5, nullptr, _t1, _t2, _t3, _t4);
}

// SIGNAL 6
void UdpCommunicator::blackReferenceAccumulatingChanged(bool _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 6, nullptr, _t1);
}

// SIGNAL 7
void UdpCommunicator::blackReferenceProgressChanged(int _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 7, nullptr, _t1);
}

// SIGNAL 8
void UdpCommunicator::blackReferenceReady(const QVariantList & _t1, double _t2, double _t3)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 8, nullptr, _t1, _t2, _t3);
}

// SIGNAL 9
void UdpCommunicator::whiteReferenceAccumulatingChanged(bool _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 9, nullptr, _t1);
}

// SIGNAL 10
void UdpCommunicator::whiteReferenceProgressChanged(int _t1)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 10, nullptr, _t1);
}

// SIGNAL 11
void UdpCommunicator::whiteReferenceReady(const QVariantList & _t1, double _t2, double _t3)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 11, nullptr, _t1, _t2, _t3);
}

// SIGNAL 12
void UdpCommunicator::predictionReady(int _t1, double _t2)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 12, nullptr, _t1, _t2);
}
QT_WARNING_POP
