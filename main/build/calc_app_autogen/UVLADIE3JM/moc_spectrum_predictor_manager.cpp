/****************************************************************************
** Meta object code from reading C++ file 'spectrum_predictor_manager.h'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.10.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../src/spectrum_predictor_manager.h"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'spectrum_predictor_manager.h' doesn't include <QObject>."
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
struct qt_meta_tag_ZN24SpectrumPredictorManagerE_t {};
} // unnamed namespace

template <> constexpr inline auto SpectrumPredictorManager::qt_create_metaobjectdata<qt_meta_tag_ZN24SpectrumPredictorManagerE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "SpectrumPredictorManager",
        "predictorsChanged",
        "",
        "modelLoaded",
        "index",
        "success",
        "predictionCompleted",
        "result",
        "loadModel",
        "modelPath",
        "loadModelAuto",
        "predict",
        "QVariantList",
        "spectrumData",
        "isModelLoaded",
        "getAlgorithm",
        "getDefaultModelPath",
        "predictorNames",
        "hasPredictors"
    };

    QtMocHelpers::UintData qt_methods {
        // Signal 'predictorsChanged'
        QtMocHelpers::SignalData<void()>(1, 2, QMC::AccessPublic, QMetaType::Void),
        // Signal 'modelLoaded'
        QtMocHelpers::SignalData<void(int, bool)>(3, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 4 }, { QMetaType::Bool, 5 },
        }}),
        // Signal 'predictionCompleted'
        QtMocHelpers::SignalData<void(int, double)>(6, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::Int, 4 }, { QMetaType::Double, 7 },
        }}),
        // Method 'loadModel'
        QtMocHelpers::MethodData<bool(int, const QString &)>(8, 2, QMC::AccessPublic, QMetaType::Bool, {{
            { QMetaType::Int, 4 }, { QMetaType::QString, 9 },
        }}),
        // Method 'loadModelAuto'
        QtMocHelpers::MethodData<bool(int)>(10, 2, QMC::AccessPublic, QMetaType::Bool, {{
            { QMetaType::Int, 4 },
        }}),
        // Method 'predict'
        QtMocHelpers::MethodData<double(int, const QVariantList &)>(11, 2, QMC::AccessPublic, QMetaType::Double, {{
            { QMetaType::Int, 4 }, { 0x80000000 | 12, 13 },
        }}),
        // Method 'isModelLoaded'
        QtMocHelpers::MethodData<bool(int) const>(14, 2, QMC::AccessPublic, QMetaType::Bool, {{
            { QMetaType::Int, 4 },
        }}),
        // Method 'getAlgorithm'
        QtMocHelpers::MethodData<QString(int) const>(15, 2, QMC::AccessPublic, QMetaType::QString, {{
            { QMetaType::Int, 4 },
        }}),
        // Method 'getDefaultModelPath'
        QtMocHelpers::MethodData<QString(int) const>(16, 2, QMC::AccessPublic, QMetaType::QString, {{
            { QMetaType::Int, 4 },
        }}),
    };
    QtMocHelpers::UintData qt_properties {
        // property 'predictorNames'
        QtMocHelpers::PropertyData<QStringList>(17, QMetaType::QStringList, QMC::DefaultPropertyFlags, 0),
        // property 'hasPredictors'
        QtMocHelpers::PropertyData<bool>(18, QMetaType::Bool, QMC::DefaultPropertyFlags, 0),
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<SpectrumPredictorManager, qt_meta_tag_ZN24SpectrumPredictorManagerE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject SpectrumPredictorManager::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN24SpectrumPredictorManagerE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN24SpectrumPredictorManagerE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN24SpectrumPredictorManagerE_t>.metaTypes,
    nullptr
} };

void SpectrumPredictorManager::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<SpectrumPredictorManager *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: _t->predictorsChanged(); break;
        case 1: _t->modelLoaded((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<bool>>(_a[2]))); break;
        case 2: _t->predictionCompleted((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<double>>(_a[2]))); break;
        case 3: { bool _r = _t->loadModel((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QString>>(_a[2])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 4: { bool _r = _t->loadModelAuto((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 5: { double _r = _t->predict((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[2])));
            if (_a[0]) *reinterpret_cast<double*>(_a[0]) = std::move(_r); }  break;
        case 6: { bool _r = _t->isModelLoaded((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 7: { QString _r = _t->getAlgorithm((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QString*>(_a[0]) = std::move(_r); }  break;
        case 8: { QString _r = _t->getDefaultModelPath((*reinterpret_cast<std::add_pointer_t<int>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QString*>(_a[0]) = std::move(_r); }  break;
        default: ;
        }
    }
    if (_c == QMetaObject::IndexOfMethod) {
        if (QtMocHelpers::indexOfMethod<void (SpectrumPredictorManager::*)()>(_a, &SpectrumPredictorManager::predictorsChanged, 0))
            return;
        if (QtMocHelpers::indexOfMethod<void (SpectrumPredictorManager::*)(int , bool )>(_a, &SpectrumPredictorManager::modelLoaded, 1))
            return;
        if (QtMocHelpers::indexOfMethod<void (SpectrumPredictorManager::*)(int , double )>(_a, &SpectrumPredictorManager::predictionCompleted, 2))
            return;
    }
    if (_c == QMetaObject::ReadProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: *reinterpret_cast<QStringList*>(_v) = _t->predictorNames(); break;
        case 1: *reinterpret_cast<bool*>(_v) = _t->hasPredictors(); break;
        default: break;
        }
    }
}

const QMetaObject *SpectrumPredictorManager::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *SpectrumPredictorManager::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN24SpectrumPredictorManagerE_t>.strings))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int SpectrumPredictorManager::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 9)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 9;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 9)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 9;
    }
    if (_c == QMetaObject::ReadProperty || _c == QMetaObject::WriteProperty
            || _c == QMetaObject::ResetProperty || _c == QMetaObject::BindableProperty
            || _c == QMetaObject::RegisterPropertyMetaType) {
        qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}

// SIGNAL 0
void SpectrumPredictorManager::predictorsChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void SpectrumPredictorManager::modelLoaded(int _t1, bool _t2)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 1, nullptr, _t1, _t2);
}

// SIGNAL 2
void SpectrumPredictorManager::predictionCompleted(int _t1, double _t2)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 2, nullptr, _t1, _t2);
}
QT_WARNING_POP
