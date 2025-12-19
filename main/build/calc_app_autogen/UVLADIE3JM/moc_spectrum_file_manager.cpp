/****************************************************************************
** Meta object code from reading C++ file 'spectrum_file_manager.h'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.10.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../src/spectrum_file_manager.h"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'spectrum_file_manager.h' doesn't include <QObject>."
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
struct qt_meta_tag_ZN19SpectrumFileManagerE_t {};
} // unnamed namespace

template <> constexpr inline auto SpectrumFileManager::qt_create_metaobjectdata<qt_meta_tag_ZN19SpectrumFileManagerE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "SpectrumFileManager",
        "saveSpectrumToCsv",
        "",
        "QVariantList",
        "spectrum",
        "filePath",
        "loadSpectrumFromCsv",
        "saveAllSpectraTableToCsv",
        "records",
        "loadAllSpectraTableFromCsv"
    };

    QtMocHelpers::UintData qt_methods {
        // Method 'saveSpectrumToCsv'
        QtMocHelpers::MethodData<bool(const QVariantList &, const QString &)>(1, 2, QMC::AccessPublic, QMetaType::Bool, {{
            { 0x80000000 | 3, 4 }, { QMetaType::QString, 5 },
        }}),
        // Method 'loadSpectrumFromCsv'
        QtMocHelpers::MethodData<QVariantList(const QString &)>(6, 2, QMC::AccessPublic, 0x80000000 | 3, {{
            { QMetaType::QString, 5 },
        }}),
        // Method 'saveAllSpectraTableToCsv'
        QtMocHelpers::MethodData<bool(const QVariantList &, const QString &)>(7, 2, QMC::AccessPublic, QMetaType::Bool, {{
            { 0x80000000 | 3, 8 }, { QMetaType::QString, 5 },
        }}),
        // Method 'loadAllSpectraTableFromCsv'
        QtMocHelpers::MethodData<QVariantList(const QString &)>(9, 2, QMC::AccessPublic, 0x80000000 | 3, {{
            { QMetaType::QString, 5 },
        }}),
    };
    QtMocHelpers::UintData qt_properties {
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<SpectrumFileManager, qt_meta_tag_ZN19SpectrumFileManagerE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject SpectrumFileManager::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN19SpectrumFileManagerE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN19SpectrumFileManagerE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN19SpectrumFileManagerE_t>.metaTypes,
    nullptr
} };

void SpectrumFileManager::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<SpectrumFileManager *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: { bool _r = _t->saveSpectrumToCsv((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QString>>(_a[2])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 1: { QVariantList _r = _t->loadSpectrumFromCsv((*reinterpret_cast<std::add_pointer_t<QString>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        case 2: { bool _r = _t->saveAllSpectraTableToCsv((*reinterpret_cast<std::add_pointer_t<QVariantList>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QString>>(_a[2])));
            if (_a[0]) *reinterpret_cast<bool*>(_a[0]) = std::move(_r); }  break;
        case 3: { QVariantList _r = _t->loadAllSpectraTableFromCsv((*reinterpret_cast<std::add_pointer_t<QString>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        default: ;
        }
    }
}

const QMetaObject *SpectrumFileManager::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *SpectrumFileManager::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN19SpectrumFileManagerE_t>.strings))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int SpectrumFileManager::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 4)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 4;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 4)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 4;
    }
    return _id;
}
QT_WARNING_POP
