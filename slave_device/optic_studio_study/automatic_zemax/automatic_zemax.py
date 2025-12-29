### 使用方法
### python 3.8 ; conda install pythonnet 
### zemax 打开，点击 编程：交互拓展

# -*- coding: utf-8 -*-
"""test2.py

目标：保证“参数计算部分”的计算流程/公式 **与 base0.py 完全一致**，
并在此基础上把计算结果通过 ZOS-API 自动写入 OpticStudio（Zemax）。

- 计算部分：直接复用 base0.py 中的函数（如 base0.py 在同目录），从而确保一致性。
- Zemax 写入部分：保持你原 test2 的 ZOS-API 结构，并修正 Coordinate Break 的 Tilt About X -> Par3。

运行方式（Extension 模式）：
1) 先打开 OpticStudio
2) Programming -> Interactive Extension，记下 instance id（常见为 0）
3) python test2.py

如需 Standalone 模式：把 __main__ 里的 zos_mode 改成 "standalone"。
"""

from __future__ import annotations

import os
import sys


# ============================================================
# 计算部分：强制与 base0.py 完全一致
# ============================================================
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

try:
    import base0 as _calc  # 与 base0.py 同目录时，直接复用其计算函数
except Exception as e:
    # 理论上你把 base0.py 和 test2.py 放同一目录就不会进到这里。
    # 作为兜底：复制 base0.py 的实现，确保公式仍然一致。
    from math import *  # noqa

    def compute_center_wavelength(lambda_1, lambda_2):
        return (lambda_1 + lambda_2) / 2

    def angle_to_radian(angle_deg):
        return angle_deg * (pi / 180)

    def radian_to_angle(angle_rad):
        return angle_rad * (180 / pi)

    def compute_correct_D_v(D_v):
        return angle_to_radian(D_v)  # 转换为弧度 !!!

    def compute_alpha(lambda_c, f, k, D_v_rad):
        return asin(10 ** (-6) * k * f * lambda_c / 2 / cos(D_v_rad / 2)) + D_v_rad / 2

    def compute_beta(alpha_rad, D_v_rad):
        return D_v_rad - alpha_rad

    def compute_L_out(L_sensor, beta_rad, k, f, lambda_2, lambda_1):
        return L_sensor * cos(beta_rad) * (10 ** 6) / (k * f * (lambda_2 - lambda_1))

    def compute_L_in(L_out, alpha_rad, beta_rad, M):
        return L_out * cos(alpha_rad) / (cos(beta_rad) * M)

    def compute_theta_2(theta_1_rad, alpha_rad, beta_rad, M):
        return atan(M ** 2 * tan(theta_1_rad) * cos(alpha_rad) / cos(beta_rad))

    def compute_R_1(L_in, theta_1_rad):
        return 2 * L_in / cos(theta_1_rad)

    def compute_R_2(L_out_rad, theta_2_rad):
        return 2 * L_out_rad / cos(theta_2_rad)

    def compute_d_1(R_1):
        return R_1 * (1 - 1 / sqrt(3))

    def compute_d_2(R_2):
        return R_2 * (1 - 1 / sqrt(3))

    class _CalcModuleProxy:
        pass

    _calc = _CalcModuleProxy()
    for _name in list(locals().keys()):
        if _name.startswith("compute_") or _name in ("angle_to_radian", "radian_to_angle"):
            setattr(_calc, _name, locals()[_name])


def compute_all_params_like_base0(
    *,
    spec_type: str,
    lambda_1: float,
    lambda_2: float,
    f: float,
    k: float,
    D_v: float,
    L_sensor: float,
    M: float,
    theta_1: float,
) -> dict:
    """严格按 base0.py 的变量名与调用顺序计算所有输出。"""

    lambda_c = _calc.compute_center_wavelength(lambda_1, lambda_2)
    D_v_rad = _calc.compute_correct_D_v(D_v)
    theta_1_rad = _calc.angle_to_radian(theta_1)

    alpha_rad = _calc.compute_alpha(lambda_c, f, k, D_v_rad)
    beta_rad = _calc.compute_beta(alpha_rad, D_v_rad)
    L_out = _calc.compute_L_out(L_sensor, beta_rad, k, f, lambda_2, lambda_1)
    L_in = _calc.compute_L_in(L_out, alpha_rad, beta_rad, M)
    theta_2_rad = _calc.compute_theta_2(theta_1_rad, alpha_rad, beta_rad, M)
    R_1 = _calc.compute_R_1(L_in, theta_1_rad)
    R_2 = _calc.compute_R_2(L_out, theta_2_rad)
    d_1 = _calc.compute_d_1(R_1)
    d_2 = _calc.compute_d_2(R_2)

    return {
        "spec_type": spec_type,
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "lambda_c": lambda_c,
        "f": f,
        "k": k,
        "D_v": D_v,
        "L_sensor": L_sensor,
        "M": M,
        "theta_1": theta_1,
        "D_v_rad": D_v_rad,
        "theta_1_rad": theta_1_rad,
        "alpha_rad": alpha_rad,
        "beta_rad": beta_rad,
        "L_out": L_out,
        "L_in": L_in,
        "theta_2_rad": theta_2_rad,
        "R_1": R_1,
        "R_2": R_2,
        "d_1": d_1,
        "d_2": d_2,
    }


# ============================================================
# ZOS-API：连接与写入（保持你原 test2 的结构）
# ============================================================

def _load_zosapi():
    """加载 ZOS-API .NET assemblies（Windows + OpticStudio 安装环境）"""
    import clr  # type: ignore
    import winreg

    # ZemaxRoot（当前用户）
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Zemax") as key:
        zemax_root, _ = winreg.QueryValueEx(key, "ZemaxRoot")

    nethelper = os.path.join(zemax_root, "ZOS-API", "Libraries", "ZOSAPI_NetHelper.dll")
    if not os.path.isfile(nethelper):
        raise FileNotFoundError(f"找不到 ZOSAPI_NetHelper.dll: {nethelper}")

    clr.AddReference(nethelper)
    import ZOSAPI_NetHelper  # type: ignore

    ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
    zos_dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()

    clr.AddReference(os.path.join(zos_dir, "ZOSAPI.dll"))
    clr.AddReference(os.path.join(zos_dir, "ZOSAPI_Interfaces.dll"))

    import ZOSAPI  # type: ignore

    return ZOSAPI


def connect_opticstudio(*, mode: str = "extension", instance_id: int = 0):
    """连接到 OpticStudio"""
    ZOSAPI = _load_zosapi()
    conn = ZOSAPI.ZOSAPI_Connection()

    if mode == "extension":
        app = conn.ConnectAsExtension(instance_id)
    elif mode == "standalone":
        app = conn.CreateNewApplication()
    else:
        raise ValueError("mode 必须是 'extension' 或 'standalone'")

    if app is None:
        raise RuntimeError("未能连接到 OpticStudio（请确认已启用 Interactive Extension，或许可可用）")

    if not app.IsValidLicenseForAPI:
        raise RuntimeError("当前 OpticStudio 许可不支持 ZOS-API")

    system = app.PrimarySystem
    return app, system, ZOSAPI


def set_system_explorer(system, ZOSAPI, *, na_obj=0.125, fields_x=(-0.3, 0.0, 0.3), wavelengths_um=(1.0, 1.3, 1.6)):
    """写 System Explorer：孔径 / 视场 / 波长"""
    sd = system.SystemData

    # 孔径：物方 NA
    sd.Aperture.ApertureType = ZOSAPI.SystemData.ZemaxApertureType.ObjectSpaceNA
    sd.Aperture.ApertureValue = float(na_obj)

    # 视场：物高
    sysField = sd.Fields
    sysField.SetFieldType(ZOSAPI.SystemData.FieldType.ObjectHeight)

    target_n = len(fields_x)
    while sysField.NumberOfFields < target_n:
        sysField.AddField(0.0, 0.0, 1.0)
    while sysField.NumberOfFields > target_n:
        sysField.RemoveField(sysField.NumberOfFields)

    for i, x in enumerate(fields_x, start=1):
        ff = sysField.GetField(i)
        ff.X = float(x)
        ff.Y = 0.0
        ff.Weight = 1.0

    # 波长：µm
    sysWave = sd.Wavelengths
    target_w = len(wavelengths_um)

    while sysWave.NumberOfWavelengths < target_w:
        sysWave.AddWavelength(0.55, 1.0)
    while sysWave.NumberOfWavelengths > target_w:
        sysWave.RemoveWavelength(sysWave.NumberOfWavelengths)

    for i, w_um in enumerate(wavelengths_um, start=1):
        ww = sysWave.GetWavelength(i)
        ww.Wavelength = float(w_um)
        ww.Weight = 1.0

    # 主波长：第2个（中心波长）
    sysWave.GetWavelength(2).MakePrimary()


def _ensure_lde_surfaces(system, target_number_of_surfaces: int):
    """确保 LDE 总面数 = target_number_of_surfaces（含物面0与像面末面）"""
    lde = system.LDE
    current = lde.NumberOfSurfaces

    if current > target_number_of_surfaces:
        remove_count = current - target_number_of_surfaces
        lde.RemoveSurfacesAt(1, remove_count)
        current = lde.NumberOfSurfaces

    while current < target_number_of_surfaces:
        lde.InsertNewSurfaceAt(current - 1)
        current = lde.NumberOfSurfaces

    return lde


def _set_coordinate_break_tiltx(surface, ZOSAPI, tilt_x_deg: float):
    """Coordinate Break: Tilt About X -> Par3（你已指出的正确列）"""
    cell = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par3)
    cell.DoubleValue = float(tilt_x_deg)


def _set_diffraction_grating(surface, ZOSAPI, *, lines_per_um: float, order: int):
    """Diffraction Grating: Par1=lines/um, Par2=order"""
    par1 = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par1)
    par2 = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par2)
    par1.DoubleValue = float(lines_per_um)
    par2.DoubleValue = float(order)


def build_lde_like_base0_print(system, ZOSAPI, *, p: dict):
    """按 base0.py 的 print 面序列写入 LDE。"""

    spec_type = p["spec_type"]

    # 你 base0 print 的面0..面10 + 像面 => 12 面
    lde = _ensure_lde_surfaces(system, 12)

    # 面0(物面)——厚度：L_in
    s0 = lde.GetSurfaceAt(0)
    s0.Thickness = float(p["L_in"])

    # 面1——坐标中断；倾斜X：theta_1
    s1 = lde.GetSurfaceAt(1)
    s1.ChangeType(s1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    _set_coordinate_break_tiltx(s1, ZOSAPI, p["theta_1"])

    # 面2——曲率半径：-R_1；材料：MIRROR
    s2 = lde.GetSurfaceAt(2)
    s2.Radius = -float(p["R_1"])
    s2.Material = "MIRROR"

    # 面3——坐标中断；厚度：-d_1；倾斜X：theta_1 + 拾取
    s3 = lde.GetSurfaceAt(3)
    s3.ChangeType(s3.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    s3.Thickness = -float(p["d_1"])
    _set_coordinate_break_tiltx(s3, ZOSAPI, p["theta_1"])

    # 面4——坐标中断；倾斜X：±alpha
    s4 = lde.GetSurfaceAt(4)
    s4.ChangeType(s4.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    alpha_deg = _calc.radian_to_angle(p["alpha_rad"])
    if spec_type == "交叉型":
        _set_coordinate_break_tiltx(s4, ZOSAPI, +alpha_deg)
    else:
        _set_coordinate_break_tiltx(s4, ZOSAPI, -alpha_deg)

    # 面5(光阑面)——衍射光栅；材料：MIRROR；刻线/微米：f/1000；衍射级次：±k
    s5 = lde.GetSurfaceAt(5)
    s5.ChangeType(s5.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.DiffractionGrating))
    s5.Material = "MIRROR"
    lines_per_um = float(p["f"]) / 1000.0
    if spec_type == "交叉型":
        _set_diffraction_grating(s5, ZOSAPI, lines_per_um=lines_per_um, order=int(+p["k"]))
    else:
        _set_diffraction_grating(s5, ZOSAPI, lines_per_um=lines_per_um, order=int(-p["k"]))

    # 面6——坐标中断；厚度：d_2；倾斜X：±beta
    s6 = lde.GetSurfaceAt(6)
    s6.ChangeType(s6.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    s6.Thickness = float(p["d_2"])
    beta_deg = _calc.radian_to_angle(p["beta_rad"])
    if spec_type == "交叉型":
        _set_coordinate_break_tiltx(s6, ZOSAPI, +beta_deg)
    else:
        _set_coordinate_break_tiltx(s6, ZOSAPI, -beta_deg)

    # 面7——坐标中断；倾斜X：theta_2
    s7 = lde.GetSurfaceAt(7)
    s7.ChangeType(s7.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    _set_coordinate_break_tiltx(s7, ZOSAPI, _calc.radian_to_angle(p["theta_2_rad"]))

    # 面8——曲率半径：-R_2；材料：MIRROR
    s8 = lde.GetSurfaceAt(8)
    s8.Radius = -float(p["R_2"])
    s8.Material = "MIRROR"

    # 面9——坐标中断；厚度：-L_out；倾斜X：theta_2 + 拾取
    s9 = lde.GetSurfaceAt(9)
    s9.ChangeType(s9.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    s9.Thickness = -float(p["L_out"])
    _set_coordinate_break_tiltx(s9, ZOSAPI, _calc.radian_to_angle(p["theta_2_rad"]))

    # 面10——坐标中断；倾斜X：4
    s10 = lde.GetSurfaceAt(10)
    s10.ChangeType(s10.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
    _set_coordinate_break_tiltx(s10, ZOSAPI, -4.0)


def push_to_zemax(*, inputs: dict, zos_mode="extension", instance_id=0, na_obj=0.125, save_path: str | None = None):
    """用 base0 一模一样的计算结果写入 Zemax。"""

    # 1) 计算（严格 base0 顺序）
    p = compute_all_params_like_base0(
        spec_type=inputs["spec_type"],
        lambda_1=inputs["lambda_1"],
        lambda_2=inputs["lambda_2"],
        f=inputs["f"],
        k=inputs["k"],
        D_v=inputs["D_v"],
        L_sensor=inputs["L_sensor"],
        M=inputs["M"],
        theta_1=inputs["theta_1"],
    )

    # 2) 连接
    app, system, ZOSAPI = connect_opticstudio(mode=zos_mode, instance_id=instance_id)

    # 3) 新系统（如需基于已有文件修改，可注释）
    system.New(False)

    # 4) System Explorer：孔径/视场/波长（波长用 base0 的 λ1/λc/λ2）
    set_system_explorer(
        system,
        ZOSAPI,
        na_obj=na_obj,
        fields_x=(-0.3, 0.0, 0.3),
        wavelengths_um=(p["lambda_1"] / 1000.0, p["lambda_c"] / 1000.0, p["lambda_2"] / 1000.0),
    )

    # 5) LDE：按 base0 的 print 面序列写
    build_lde_like_base0_print(system, ZOSAPI, p=p)

    if save_path:
        system.SaveAs(save_path)

    # 返回结果（方便你核对与 base0 输出一致）
    return p


# ============================================================
# main：保留 base0.py 的输入/覆盖方式（确保方法完全一致）
# ============================================================
if __name__ == "__main__":
    from math import *  # noqa: F401,F403

    # 与 base0.py 一致的输入风格
    spec_type = "非交叉型"  # 非交叉型 交叉型

    lambda_1 = 200
    lambda_2 = 1100

    lambda_1 = 1000
    lambda_2 = 1600

    f = 300
    k = 1
    D_v = 40
    L_sensor = 28.4
    M = 1.15
    theta_1 = 11

    inputs = {
        "spec_type": spec_type,
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "f": f,
        "k": k,
        "D_v": D_v,
        "L_sensor": L_sensor,
        "M": M,
        "theta_1": theta_1,
    }

    # 先在本地打印一份（方便对照 base0 的输出）
    p = compute_all_params_like_base0(**inputs)

    print("=========光谱仪参数计算:=========")
    print("---------输入参数:---------")
    print("光谱仪类型：", spec_type)
    print("起始波长 (nm):", lambda_1)
    print("终止波长 (nm):", lambda_2)
    print("光栅密度 (lines/mm):", f)
    print("衍射级别:", k)
    print("光栅夹角 (度):", D_v)
    print("传感器长度 (mm):", L_sensor)
    print("放大倍率:", M)
    print("准直镜转角 (度):", theta_1)
    print("--------------------------")

    print("---------输出参数:---------")
    print("计算得到的入射角 alpha (度):", _calc.radian_to_angle(p["alpha_rad"]))
    print("计算得到的出射角 beta (度):", _calc.radian_to_angle(p["beta_rad"]))
    print("计算得到的光谱仪有效工作长度 L_out (mm):", p["L_out"])
    print("计算得到的光谱仪入射光束长度 L_in (mm):", p["L_in"])
    print("计算得到的会聚镜转角 theta_2 (度):", _calc.radian_to_angle(p["theta_2_rad"]))
    print("计算得到的准直镜曲率半径 R_1 (mm):", p["R_1"])
    print("计算得到的会聚镜曲率半径 R_2 (mm):", p["R_2"])
    print("计算得到的准直镜到光栅的距离 d_1 (mm):", p["d_1"])
    print("计算得到的光栅到会聚镜的距离 d_2 (mm):", p["d_2"])

    # === 写入 Zemax ===
    # Extension 模式：需在 OpticStudio 中启用 Programming -> Interactive Extension
    # Standalone 模式：改 zos_mode="standalone"（无需打开 UI）
    zemax_results = push_to_zemax(
        inputs=inputs,
        zos_mode="extension",
        instance_id=0,
        na_obj=0.125,
        save_path=None,
    )

    print("\n已写入 OpticStudio。用于核对的关键计算结果：")
    for kk in ("lambda_c", "L_in", "L_out", "R_1", "R_2", "d_1", "d_2"):
        print(f"{kk}: {zemax_results[kk]}")
