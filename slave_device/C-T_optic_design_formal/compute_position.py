# read_zemax_to_numpy_extension.py
# -*- coding: utf-8 -*-
"""
Zemax OpticStudio 2024 (ZOS-API) - Interactive Extension 模式
读取当前已打开系统的：
  1) LDE: 每一面的关键列 + Par1..Par6 + SurfaceData(Decenter/Tilt等)
  2) System Explorer: Aperture / Fields / Wavelengths

输出：
  - lde_table_object: np.ndarray(dtype=object)  (N, M)
  - lde_table_numeric: np.ndarray(float)        (N, K) 纯数值列
  - systemdata: dict

并可选保存到 npz/json/csv。
"""

import os
import sys
import json
import numpy as np
from math import *

# -------------------------
# 1) 连接 OpticStudio（复用你脚本的思路）
# -------------------------

def _get_zemax_root_from_registry():
    """
    参考你脚本：HKCU\\Software\\Zemax 里的 ZemaxRoot。:contentReference[oaicite:1]{index=1}
    增加若干回退项（有的机器装在 HKLM/WOW6432Node）。
    """
    import winreg

    candidates = [
        (winreg.HKEY_CURRENT_USER, r"Software\Zemax", "ZemaxRoot"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Zemax", "ZemaxRoot"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Zemax", "ZemaxRoot"),
    ]
    last_err = None
    for hive, key_path, value_name in candidates:
        try:
            with winreg.OpenKey(hive, key_path) as key:
                v, _ = winreg.QueryValueEx(key, value_name)
                if v and os.path.isdir(v):
                    return v
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"未能从注册表读取 ZemaxRoot（最后一次错误：{last_err}）。")


def _clr_add_reference_safely(clr, dll_path: str):
    """
    兼容不同 pythonnet：优先用绝对路径加载。
    """
    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"DLL 不存在：{dll_path}")

    # 有的环境 clr.AddReference(绝对路径) 可用；有的需要 AddReferenceToFileAndPath
    try:
        clr.AddReference(dll_path)
        return
    except Exception:
        pass

    try:
        clr.AddReferenceToFileAndPath(dll_path)
        return
    except Exception as e:
        raise RuntimeError(f"加载 DLL 失败：{dll_path}\n{e}")


def load_zosapi():
    """
    按你脚本的结构：ZemaxRoot -> ZOSAPI_NetHelper -> GetZemaxDirectory -> ZOSAPI.dll。:contentReference[oaicite:2]{index=2}
    """
    import clr  # pythonnet

    zemax_root = _get_zemax_root_from_registry()
    nethelper = os.path.join(zemax_root, "ZOS-API", "Libraries", "ZOSAPI_NetHelper.dll")
    _clr_add_reference_safely(clr, nethelper)

    # 让 import 能找到同目录依赖（稳妥）
    lib_dir = os.path.dirname(nethelper)
    if lib_dir not in sys.path:
        sys.path.append(lib_dir)

    import ZOSAPI_NetHelper  # type: ignore

    if not ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize():
        raise RuntimeError("ZOSAPI_Initializer.Initialize() 失败：请确认 OpticStudio 2024 正常安装。")

    zos_dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()

    _clr_add_reference_safely(clr, os.path.join(zos_dir, "ZOSAPI.dll"))
    _clr_add_reference_safely(clr, os.path.join(zos_dir, "ZOSAPI_Interfaces.dll"))

    import ZOSAPI  # type: ignore
    return ZOSAPI


def connect_as_extension(instance_id: int = 0):
    """
    ConnectAsExtension：与你脚本一致。:contentReference[oaicite:3]{index=3}
    """
    ZOSAPI = load_zosapi()
    conn = ZOSAPI.ZOSAPI_Connection()
    app = conn.ConnectAsExtension(int(instance_id))
    if app is None:
        raise RuntimeError("ConnectAsExtension 失败：请在 OpticStudio 内启用 Interactive Extension，并保持系统已打开。")
    if not app.IsValidLicenseForAPI:
        raise RuntimeError("当前许可证不支持 ZOS-API。")
    return app, app.PrimarySystem, ZOSAPI


# -------------------------
# 2) 读取 System Explorer（孔径/视场/波长）
# -------------------------

def export_systemdata(system):
    sd = system.SystemData
    out = {}

    # Units
    try:
        u = sd.Units
        out["Units"] = {
            "LensUnits": str(u.LensUnits),
            "WavelengthUnits": str(u.WavelengthUnits),
        }
    except Exception:
        out["Units"] = {}

    # Aperture
    try:
        ap = sd.Aperture
        out["Aperture"] = {
            "ApertureType": str(ap.ApertureType),
            "ApertureValue": float(ap.ApertureValue),
        }
    except Exception:
        out["Aperture"] = {}

    # Fields
    fields = []
    try:
        f = sd.Fields
        out["FieldType"] = str(f.FieldType)
        for i in range(1, f.NumberOfFields + 1):
            fi = f.GetField(i)
            fields.append({"Index": i, "X": float(fi.X), "Y": float(fi.Y), "Weight": float(fi.Weight)})
    except Exception:
        pass
    out["Fields"] = fields

    # Wavelengths
    wls = []
    try:
        w = sd.Wavelengths
        for i in range(1, w.NumberOfWavelengths + 1):
            wi = w.GetWavelength(i)
            wls.append({"Index": i, "Wavelength": float(wi.Wavelength), "Weight": float(wi.Weight)})
    except Exception:
        pass
    out["Wavelengths"] = wls

    return out


# -------------------------
# 3) 读取 LDE 并组装 NumPy 表格
# -------------------------

def _safe_float(x):
    try:
        if x is None:
            return np.nan
        return float(x)
    except Exception:
        return np.nan


def _safe_str(x):
    try:
        if x is None:
            return ""
        return str(x)
    except Exception:
        return ""


def export_lde_numpy(system, ZOSAPI, par_count: int = 6):
    """
    输出两张表：
      - object 表：含字符串/枚举
      - numeric 表：只保留可可靠转 float 的列（便于优化/统计）
    """
    lde = system.LDE
    n = int(lde.NumberOfSurfaces)

    # 常用列：你关心的“镜头数据”
    cols_obj = [
        "Surf",
        "TypeName",
        "Comment",
        "Radius",
        "Thickness",
        "Material",
        "SemiDiameter",
        "Conic",
    ] + [f"Par{i}" for i in range(1, par_count + 1)] + [
        # SurfaceData（坐标间断/倾斜/去心等通常在这里更直观）
        "SD_DecenterX",
        "SD_DecenterY",
        "SD_TiltX",
        "SD_TiltY",
        "SD_TiltZ",
    ]

    cols_num = [
        "Surf",
        "Radius",
        "Thickness",
        "SemiDiameter",
        "Conic",
    ] + [f"Par{i}" for i in range(1, par_count + 1)] + [
        "SD_DecenterX",
        "SD_DecenterY",
        "SD_TiltX",
        "SD_TiltY",
        "SD_TiltZ",
    ]

    SC = ZOSAPI.Editors.LDE.SurfaceColumn

    rows_obj = []
    rows_num = []

    for i in range(n):
        s = lde.GetSurfaceAt(i)

        # 基础属性（多数面都有）
        surf = int(i)
        type_name = _safe_str(getattr(s, "TypeName", ""))
        comment = _safe_str(getattr(s, "Comment", ""))
        material = _safe_str(getattr(s, "Material", ""))

        radius = getattr(s, "Radius", None)
        thickness = getattr(s, "Thickness", None)
        semidia = getattr(s, "SemiDiameter", None)
        try:
            conic = s.Conic
        except Exception:
            conic = None

        # Par1..ParN（光栅/坐标间断等常用）
        pars = []
        for k in range(1, par_count + 1):
            col = getattr(SC, f"Par{k}")
            try:
                cell = s.GetSurfaceCell(col)
                # Par 通常是 DoubleValue
                pars.append(cell.DoubleValue)
            except Exception:
                pars.append(None)

        # SurfaceData: decenter/tilt（若无则留空）
        dx = dy = tx = ty = tz = None
        try:
            sd = s.SurfaceData
            dx = getattr(sd, "Decenter_X", None)
            dy = getattr(sd, "Decenter_Y", None)
            tx = getattr(sd, "TiltAboutX", None)
            ty = getattr(sd, "TiltAboutY", None)
            tz = getattr(sd, "TiltAboutZ", None)
        except Exception:
            pass

        row_obj = [
            surf, type_name, comment,
            radius, thickness, material, semidia, conic,
            *pars,
            dx, dy, tx, ty, tz
        ]
        rows_obj.append(row_obj)

        row_num = [
            float(surf),
            _safe_float(radius),
            _safe_float(thickness),
            _safe_float(semidia),
            _safe_float(conic),
            *[_safe_float(v) for v in pars],
            _safe_float(dx),
            _safe_float(dy),
            _safe_float(tx),
            _safe_float(ty),
            _safe_float(tz),
        ]
        rows_num.append(row_num)

    table_obj = np.array(rows_obj, dtype=object)
    table_num = np.array(rows_num, dtype=float)
    return table_obj, cols_obj, table_num, cols_num

def deg2rad(deg):
        return deg * pi / 180.0

def compute_detailed_position_of_B(point, width, height, angle, distance, distance_2):
    point_up = [point[0], point[1] + height - distance]
    point_down = [point[0], point[1] - distance]
    point_left_up = [point[0] - width/2, point[1] + height - distance]
    point_left_down = [point[0] - width/2, point[1] - distance]
    point_right_up = [point[0] + width/2, point[1] - distance + distance_2]
    point_right_down = [point[0] + width/2, point[1] - distance]
    return point, point_up, point_down, point_left_up, point_left_down, point_right_up, point_right_down

def compute_detailed_position_of_C(point, width, height, angle, distance, distance_2):
    point_up = [point[0], point[1] - (height - distance)]
    point_down = [point[0], point[1] + distance]
    point_left_up = [point[0] + width/2, point[1] + distance - distance_2]
    point_left_down = [point[0] + width/2, point[1] + distance]
    point_right_up = [point[0] - width/2, point[1] - (height - distance)]
    point_right_down = [point[0] - width/2, point[1] + distance]
    return point, point_up, point_down, point_left_up, point_left_down, point_right_up, point_right_down

def compute_detailed_position_of_D(point, width, height, angle, distance, thick):
    point_up = [point[0] - height + distance + thick/2, point[1]]
    point_down = [point[0] + distance + thick/2, point[1]]
    point_left_up = [point[0] - height + distance + thick/2, point[1] - width/2]
    point_left_down = [point[0] + distance + thick/2, point[1] - width/2]
    point_right_up = [point[0] - height + distance + thick/2, point[1] + width/2]
    point_right_down = [point[0] + distance + thick/2, point[1] + width/2]
    return point, point_up, point_down, point_left_up, point_left_down, point_right_up, point_right_down

def compute_detailed_position_of_E(point, width, height, angle, distance):
    point_up = [point[0] - (height - distance) * cos(deg2rad(180 - angle)), point[1] + (height - distance) * sin(deg2rad(180 - angle))]
    point_down = [point[0] + distance * cos(deg2rad(180 - angle)), point[1] - distance * sin(deg2rad(180 - angle))]
    point_left_up = [point_up[0] - width/2 * sin(deg2rad(180 - angle)), point_up[1] - width/2 * cos(deg2rad(180 - angle))]
    point_left_down = [point_down[0] - width/2 * sin(deg2rad(180 - angle)), point_down[1] - width/2 * cos(deg2rad(180 - angle))]
    point_right_up = [point_up[0] + width/2 * sin(deg2rad(180 - angle)), point_up[1] + width/2 * cos(deg2rad(180 - angle))]
    point_right_down = [point_down[0] + width/2 * sin(deg2rad(180 - angle)), point_down[1] + width/2 * cos(deg2rad(180 - angle))]
    return point, point_up, point_down, point_left_up, point_left_down, point_right_up, point_right_down

def compute_detailed_position_of_F(point, width, height, angle):
    point_up = [point[0], point[1]]
    point_down = [point[0] - height * cos(deg2rad(-angle)), point[1] + height * sin(deg2rad(-angle))]
    point_left_up = [point_up[0] + width/2 * sin(deg2rad(-angle)), point_up[1] + width/2 * cos(deg2rad(-angle))]
    point_left_down = [point_down[0] + width/2 * sin(deg2rad(-angle)), point_down[1] + width/2 * cos(deg2rad(-angle))]
    point_right_up = [point_up[0] - width/2 * sin(deg2rad(-angle)), point_up[1] - width/2 * cos(deg2rad(-angle))]
    point_right_down = [point_down[0] - width/2 * sin(deg2rad(-angle)), point_down[1] - width/2 * cos(deg2rad(-angle))]
    return point, point_up, point_down, point_left_up, point_left_down, point_right_up, point_right_down

def compute_detailed_position_of_G(point, width, height, angle, distance):
    point_up = [point[0] - (height - distance) * sin(deg2rad(angle - 90)), point[1] + (height - distance) * cos(deg2rad(angle - 90))]
    point_down = [point[0] + distance * sin(deg2rad(angle - 90)), point[1] - distance * cos(deg2rad(angle - 90))]
    point_left_up = [point_up[0] - width/2 * cos(deg2rad(angle - 90)), point_up[1] - width/2 * sin(deg2rad(angle - 90))]
    point_left_down = [point_down[0] - width/2 * cos(deg2rad(angle - 90)), point_down[1] - width/2 * sin(deg2rad(angle - 90))]
    point_right_up = [point_up[0] + width/2 * cos(deg2rad(angle - 90)), point_up[1] + width/2 * sin(deg2rad(angle - 90))]
    point_right_down = [point_down[0] + width/2 * cos(deg2rad(angle - 90)), point_down[1] + width/2 * sin(deg2rad(angle - 90))]
    # print(height, distance, height - distance)
    return point, point_up, point_down, point_left_up, point_left_down, point_right_up, point_right_down

def compute_detailed_position_of_H(point, width, angle):
    point_left = [point[0] + width/2 * cos(deg2rad(90+angle)), point[1] + width/2 * sin(deg2rad(90+angle))]
    point_right = [point[0] - width/2 * cos(deg2rad(90+angle)), point[1] - width/2 * sin(deg2rad(90+angle))]
    # print(height, distance, height - distance)
    return point, point_left, point_right

def compute_position(lde_obj, parallel_length=24.8):
    point_start = [0, 0]
    point_parabolic_1 = [point_start[0]-abs(lde_obj[2, 3]), point_start[1]]
    point_parabolic_2 = [point_parabolic_1[0], point_parabolic_1[1]+parallel_length]
    point_silt = [point_parabolic_2[0]+abs(lde_obj[5, 3]), point_parabolic_2[1]]

    # point_silt = [-0.625, 0]
    point_silt = [0, 0]
    point_parabolic_2 = [point_silt[0]-abs(lde_obj[5, 3]), point_silt[1]]
    point_parabolic_1 = [point_parabolic_2[0], point_parabolic_2[1]-parallel_length]
    point_start = [point_parabolic_1[0]+abs(lde_obj[2, 3]), point_parabolic_1[1]]

    point_mirror_1 = [point_silt[0]+abs(lde_obj[15, 4]), point_silt[1]]
    point_grating = [point_mirror_1[0]-abs(lde_obj[21, 4])*cos(deg2rad(2*lde_obj[19, 10])), point_mirror_1[1]+abs(lde_obj[21, 4])*sin(deg2rad(2*lde_obj[19, 10]))]
    point_mirror_2 = [point_grating[0]+abs(lde_obj[24, 4])*cos(deg2rad(2*lde_obj[19, 10]+lde_obj[22, 10]+lde_obj[24, 10])), point_grating[1]-abs(lde_obj[24, 4])*sin(deg2rad(2*lde_obj[19, 10]+lde_obj[22, 10]+lde_obj[24, 10]))]
    point_sensor = [point_mirror_2[0]-abs(lde_obj[27, 4])*cos(deg2rad(2*lde_obj[19, 10]+lde_obj[22, 10]+lde_obj[24, 10]+2*lde_obj[27, 10])), point_mirror_2[1]+abs(lde_obj[27, 4])*sin(deg2rad(2*lde_obj[19, 10]+lde_obj[22, 10]+lde_obj[24, 10]+2*lde_obj[27, 10]))]
    print("point_start", [format(point_start[0], '.3f'), format(point_start[1], '.3f')])
    print("point_parabolic_1", [format(point_parabolic_1[0], '.3f'), format(point_parabolic_1[1], '.3f')])
    print("point_parabolic_2", [format(point_parabolic_2[0], '.3f'), format(point_parabolic_2[1], '.3f')])
    print("point_silt", [format(point_silt[0], '.3f'), format(point_silt[1], '.3f')])
    print("point_mirror_1", [format(point_mirror_1[0], '.3f'), format(point_mirror_1[1], '.3f')])
    print("point_grating", [format(point_grating[0], '.3f'), format(point_grating[1], '.3f')])
    print("point_mirror_2", [format(point_mirror_2[0], '.3f'), format(point_mirror_2[1], '.3f')])
    print("point_sensor", [format(point_sensor[0], '.3f'), format(point_sensor[1], '.3f')])
    # print(2*lde_obj[19, 10]+lde_obj[22, 10]+lde_obj[24, 10]+2*lde_obj[27, 10])

    angle_start = 180
    angle_parabolic_1 = angle_start - 90
    angle_parabolic_2 = angle_parabolic_1 - 180
    angle_silt = 180
    angle_mirror_1 = angle_silt - lde_obj[19, 10]
    angle_grating = - (180 - angle_mirror_1) - lde_obj[21, 10] - lde_obj[22, 10] #  - lde_obj[24, 10]
    angle_mirror_2 = angle_grating + 180 - lde_obj[24, 10] - lde_obj[25, 10]
    angle_sensor = angle_mirror_2 - 180 - lde_obj[27, 10] - lde_obj[28, 10]
    print("angle_start", format(angle_start, '.3f'))
    print("angle_parabolic_1", format(angle_parabolic_1, '.3f'))
    print("angle_parabolic_2", format(angle_parabolic_2, '.3f'))
    print("angle_silt", format(angle_silt, '.3f'))
    print("angle_mirror_1", format(angle_mirror_1, '.3f'))
    print("angle_grating", format(angle_grating, '.3f'))
    print("angle_mirror_2", format(angle_mirror_2, '.3f'))
    print("angle_sensor", format(angle_sensor, '.3f'))

    # (point, width, height, angle, distance)
    print("detailed positions of B:", compute_detailed_position_of_B(point_parabolic_1, 12.7, 20, angle_parabolic_1, 12.3, 7.2))
    print("detailed positions of C:", compute_detailed_position_of_C(point_parabolic_2, 12.7, 18.8, angle_parabolic_2, 11.7, 6.0))
    print("detailed positions of D:", compute_detailed_position_of_D(point_silt, 25.4, 2.5, angle_silt, 0.6, 0.05))
    print("detailed positions of E:", compute_detailed_position_of_E(point_mirror_1, 25.4, 6.5, angle_mirror_1, 6.0))
    print("detailed positions of F:", compute_detailed_position_of_F(point_grating, 25.4, 6, angle_grating))
    print("detailed positions of G:", compute_detailed_position_of_G(point_mirror_2, 50.8, 10.6, angle_mirror_2, 9.0))
    print("detailed positions of H:", compute_detailed_position_of_H(point_sensor, 60, angle_sensor))
    pass

# -------------------------
# 4) main：打印 + 保存
# -------------------------

def main():
    out_dir = os.path.abspath("./zemax_read_dump")
    os.makedirs(out_dir, exist_ok=True)

    app, system, ZOSAPI = connect_as_extension(instance_id=0)

    # 1) System Explorer
    systemdata = export_systemdata(system)
    with open(os.path.join(out_dir, "systemdata.json"), "w", encoding="utf-8") as f:
        json.dump(systemdata, f, ensure_ascii=False, indent=2)

    # 2) LDE -> numpy
    lde_obj, cols_obj, lde_num, cols_num = export_lde_numpy(system, ZOSAPI, par_count=6)

    print("LDE object-table:", lde_obj.shape)
    print("Columns:", cols_obj)
    # print("First 12 rows:\n", lde_obj[:12])

    print("lde_obj", lde_obj)

    # 保存
    np.savez(os.path.join(out_dir, "lde_table_object.npz"),
             data=lde_obj, cols=np.array(cols_obj, dtype=object))
    np.savez(os.path.join(out_dir, "lde_table_numeric.npz"),
             data=lde_num, cols=np.array(cols_num, dtype=object))

    # 可选：保存 CSV（object 表包含字符串，建议用简单写法）
    csv_path = os.path.join(out_dir, "lde_table_object.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(",".join(cols_obj) + "\n")
        for r in lde_obj:
            f.write(",".join([_safe_str(x).replace(",", ";") for x in r]) + "\n")

    print("Export done ->", out_dir)

    # 交互拓展模式：不要 CloseApplication()，避免关闭你正在用的 OpticStudio
    print('---------------------')
    compute_position(lde_obj)
    print('---------------------')

if __name__ == "__main__":
    main()
