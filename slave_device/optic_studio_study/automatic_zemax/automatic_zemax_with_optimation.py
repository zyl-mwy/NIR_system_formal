"""CT spectrometer (crossed Czerny–Turner) Zemax automation (OpticStudio 2024).

This file is a *structured/refactored* version of the previously working script.
It keeps the same behavior and core formulas, but splits the workflow into
separate classes:

  1) CTDesignCalculator:        base0-consistent parameter computation
  2) ZemaxConnector:            ZOS-API connection / licensing checks
  3) SystemExplorerConfigurator:aperture/fields/wavelengths setup
  4) LDEBuilder:                lens data editor surface construction
  5) SolveConfigurator:         variables & pickups (solve settings)
  6) MeritFunctionBuilder:      cross CT geometric constraints (MFE)
  7) SeqOptimizationWizard:     (optional) Optimization Wizard -> Spot Diagram
  8) CTSpectrometerPipeline:    orchestration; retains push_to_zemax() wrapper

Notes
-----
* The computation path is kept identical to base0.py when available.
* Tested conceptually for OpticStudio 2024 ZOS-API patterns; however, API
  member names can vary by patch/hotfix. The wizard module is defensive.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple


# ============================================================
# 0) Computation module import (prefer base0.py; fallback embedded)
# ============================================================

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)


class _CalcProxy:
    """A tiny module-like proxy to host compute_* functions."""


try:
    import base0 as _calc  # reuse user's validated formulas if present
except Exception:
    from math import asin, atan, cos, pi, sqrt, tan  # noqa

    def compute_center_wavelength(lambda_1, lambda_2):
        return (lambda_1 + lambda_2) / 2

    def angle_to_radian(angle_deg):
        return angle_deg * (pi / 180)

    def radian_to_angle(angle_rad):
        return angle_rad * (180 / pi)

    def compute_correct_D_v(D_v):
        return angle_to_radian(D_v)

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

    _calc = _CalcProxy()
    for _name, _obj in list(locals()).items():
        if _name.startswith("compute_") or _name in ("angle_to_radian", "radian_to_angle"):
            setattr(_calc, _name, _obj)


# ============================================================
# 1) Data models
# ============================================================


@dataclass(frozen=True)
class SpectrometerInputs:
    """Inputs to the CT spectrometer design calculator (same meaning as base0)."""

    spec_type: str  # "交叉型" or "非交叉型"
    lambda_1_nm: float
    lambda_2_nm: float
    grating_lines_per_mm: float
    diffraction_order: int
    D_v_deg: float
    sensor_length_mm: float
    magnification: float
    theta_1_deg: float


@dataclass
class ComputedParams:
    """Computed outputs (mirrors the keys returned previously)."""

    spec_type: str
    lambda_1: float
    lambda_2: float
    lambda_c: float
    f: float
    k: float
    D_v: float
    L_sensor: float
    M: float
    theta_1: float

    D_v_rad: float
    theta_1_rad: float
    alpha_rad: float
    beta_rad: float
    L_out: float
    L_in: float
    theta_2_rad: float
    R_1: float
    R_2: float
    d_1: float
    d_2: float

    # bookkeeping
    wizard_applied: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


# ============================================================
# 2) Calculator
# ============================================================


class CTDesignCalculator:
    """Compute CT spectrometer layout parameters using base0-consistent chain."""

    @staticmethod
    def compute(inputs: SpectrometerInputs) -> ComputedParams:
        lambda_1 = float(inputs.lambda_1_nm)
        lambda_2 = float(inputs.lambda_2_nm)
        f = float(inputs.grating_lines_per_mm)
        k = float(inputs.diffraction_order)
        D_v = float(inputs.D_v_deg)
        L_sensor = float(inputs.sensor_length_mm)
        M = float(inputs.magnification)
        theta_1 = float(inputs.theta_1_deg)

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

        return ComputedParams(
            spec_type=inputs.spec_type,
            lambda_1=lambda_1,
            lambda_2=lambda_2,
            lambda_c=lambda_c,
            f=f,
            k=k,
            D_v=D_v,
            L_sensor=L_sensor,
            M=M,
            theta_1=theta_1,
            D_v_rad=D_v_rad,
            theta_1_rad=theta_1_rad,
            alpha_rad=alpha_rad,
            beta_rad=beta_rad,
            L_out=L_out,
            L_in=L_in,
            theta_2_rad=theta_2_rad,
            R_1=R_1,
            R_2=R_2,
            d_1=d_1,
            d_2=d_2,
        )


# ============================================================
# 3) ZOS-API connector
# ============================================================


class ZemaxConnector:
    """Load ZOS-API assemblies and connect to OpticStudio."""

    @staticmethod
    def _load_zosapi():
        import clr  # type: ignore
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Zemax") as key:
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

    @staticmethod
    def connect(*, mode: str = "extension", instance_id: int = 0):
        ZOSAPI = ZemaxConnector._load_zosapi()
        conn = ZOSAPI.ZOSAPI_Connection()

        if mode == "extension":
            app = conn.ConnectAsExtension(instance_id)
        elif mode == "standalone":
            app = conn.CreateNewApplication()
        else:
            raise ValueError("mode 必须是 'extension' 或 'standalone'")

        if app is None:
            raise RuntimeError("未能连接到 OpticStudio（请确认启用 Interactive Extension，或许可可用）")
        if not app.IsValidLicenseForAPI:
            raise RuntimeError("当前 OpticStudio 许可不支持 ZOS-API")

        system = app.PrimarySystem
        return app, system, ZOSAPI


# ============================================================
# 4) System Explorer configuration
# ============================================================


class SystemExplorerConfigurator:
    @staticmethod
    def configure(
        system: Any,
        ZOSAPI: Any,
        *,
        na_obj: float = 0.125,
        fields_x: Tuple[float, ...] = (-0.3, 0.0, 0.3),
        wavelengths_um: Tuple[float, float, float] = (1.0, 1.3, 1.6),
    ) -> None:
        sd = system.SystemData

        # Aperture: Object Space NA
        sd.Aperture.ApertureType = ZOSAPI.SystemData.ZemaxApertureType.ObjectSpaceNA
        sd.Aperture.ApertureValue = float(na_obj)

        # Fields: Object height
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

        # Wavelengths (um)
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
        sysWave.GetWavelength(2).MakePrimary()


# ============================================================
# 5) LDE builder (surfaces)
# ============================================================


class LDEBuilder:
    @staticmethod
    def _ensure_surfaces(system: Any, n_surfaces: int):
        lde = system.LDE
        current = lde.NumberOfSurfaces
        if current > n_surfaces:
            lde.RemoveSurfacesAt(1, current - n_surfaces)
            current = lde.NumberOfSurfaces
        while current < n_surfaces:
            lde.InsertNewSurfaceAt(current - 1)
            current = lde.NumberOfSurfaces
        return lde

    @staticmethod
    def _set_cb_tiltx(surface: Any, ZOSAPI: Any, tilt_x_deg: float) -> None:
        cell = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par3)
        cell.DoubleValue = float(tilt_x_deg)

    @staticmethod
    def _set_grating(surface: Any, ZOSAPI: Any, *, lines_per_um: float, order: int) -> None:
        par1 = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par1)
        par2 = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par2)
        par1.DoubleValue = float(lines_per_um)
        par2.DoubleValue = float(order)

    @staticmethod
    def build_cross_ct_like_base0(system: Any, ZOSAPI: Any, p: ComputedParams) -> None:
        """Replicates the base0 print-surface sequence (12 surfaces)."""
        lde = LDEBuilder._ensure_surfaces(system, 12)
        spec_type = p.spec_type

        # Surface 0: object thickness = L_in
        s0 = lde.GetSurfaceAt(0)
        s0.Thickness = float(p.L_in)

        # Surface 1: coordinate break; tilt x = theta_1
        s1 = lde.GetSurfaceAt(1)
        s1.ChangeType(s1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        LDEBuilder._set_cb_tiltx(s1, ZOSAPI, p.theta_1)

        # Surface 2: mirror, radius = -R1
        s2 = lde.GetSurfaceAt(2)
        s2.Radius = -float(p.R_1)
        s2.Material = "MIRROR"

        # Surface 3: coordinate break; thickness = -d1; tilt x = theta_1
        s3 = lde.GetSurfaceAt(3)
        s3.ChangeType(s3.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s3.Thickness = -float(p.d_1)
        LDEBuilder._set_cb_tiltx(s3, ZOSAPI, p.theta_1)

        # Surface 4: coordinate break; tilt x = ±alpha
        s4 = lde.GetSurfaceAt(4)
        s4.ChangeType(s4.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        alpha_deg = float(_calc.radian_to_angle(p.alpha_rad))
        LDEBuilder._set_cb_tiltx(s4, ZOSAPI, +alpha_deg if spec_type == "交叉型" else -alpha_deg)

        # Surface 5: diffraction grating (stop)
        s5 = lde.GetSurfaceAt(5)
        s5.ChangeType(s5.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.DiffractionGrating))
        s5.Material = "MIRROR"
        lines_per_um = float(p.f) / 1000.0
        order = int(+p.k) if spec_type == "交叉型" else int(-p.k)
        LDEBuilder._set_grating(s5, ZOSAPI, lines_per_um=lines_per_um, order=order)

        # Surface 6: coordinate break; thickness=d2; tilt x = ±beta
        s6 = lde.GetSurfaceAt(6)
        s6.ChangeType(s6.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s6.Thickness = float(p.d_2)
        beta_deg = float(_calc.radian_to_angle(p.beta_rad))
        LDEBuilder._set_cb_tiltx(s6, ZOSAPI, +beta_deg if spec_type == "交叉型" else -beta_deg)

        # Surface 7: coordinate break; tilt x = theta_2
        s7 = lde.GetSurfaceAt(7)
        s7.ChangeType(s7.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        LDEBuilder._set_cb_tiltx(s7, ZOSAPI, float(_calc.radian_to_angle(p.theta_2_rad)))

        # Surface 8: mirror, radius = -R2
        s8 = lde.GetSurfaceAt(8)
        s8.Radius = -float(p.R_2)
        s8.Material = "MIRROR"

        # Surface 9: coordinate break; thickness = -L_out; tilt x = theta_2
        s9 = lde.GetSurfaceAt(9)
        s9.ChangeType(s9.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s9.Thickness = -float(p.L_out)
        LDEBuilder._set_cb_tiltx(s9, ZOSAPI, float(_calc.radian_to_angle(p.theta_2_rad)))

        # Surface 10: coordinate break; image tilt preset
        s10 = lde.GetSurfaceAt(10)
        s10.ChangeType(s10.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        LDEBuilder._set_cb_tiltx(s10, ZOSAPI, -4.0)


# ============================================================
# 6) Solve configuration: variables & pickups
# ============================================================


class SolveConfigurator:
    @staticmethod
    def _cell_make_variable(cell: Any, ZOSAPI: Any) -> None:
        try:
            solve = cell.CreateSolveType(ZOSAPI.Editors.SolveType.Variable)._S_Variable
            cell.SetSolveData(solve)
        except Exception:
            if hasattr(cell, "MakeSolveType"):
                cell.MakeSolveType(ZOSAPI.Editors.SolveType.Variable)

    @staticmethod
    def _cell_make_surface_pickup(cell: Any, ZOSAPI: Any, *, from_surface: int, scale: float = 1.0, offset: float = 0.0) -> None:
        solve_data = cell.CreateSolveType(ZOSAPI.Editors.SolveType.SurfacePickup)
        sp = getattr(solve_data, "_S_SurfacePickup", None)
        if sp is None:
            raise RuntimeError("无法创建 SurfacePickup solve（检查 ZOS-API 版本）")
        sp.Surface = int(from_surface)
        if hasattr(sp, "ScaleFactor"):
            sp.ScaleFactor = float(scale)
        if hasattr(sp, "Offset"):
            sp.Offset = float(offset)
        cell.SetSolveData(sp)

    @staticmethod
    def configure_cross_ct(system: Any, ZOSAPI: Any) -> None:
        lde = system.LDE
        SC = ZOSAPI.Editors.LDE.SurfaceColumn

        # Variable cells
        variable_cells = (
            (2, SC.Radius),
            (8, SC.Radius),
            (0, SC.Thickness),
            (3, SC.Thickness),
            (9, SC.Thickness),
            (1, SC.Par3),
            (4, SC.Par3),
            (6, SC.Par3),
            (7, SC.Par3),
            (10, SC.Par3),
        )
        for surf_idx, col in variable_cells:
            try:
                s = lde.GetSurfaceAt(int(surf_idx))
                cell = s.GetSurfaceCell(col)
                SolveConfigurator._cell_make_variable(cell, ZOSAPI)
            except Exception:
                pass

        # Pickups
        pickup_specs = (
            (6, SC.Thickness, 3, -1.0),
            (3, SC.Par3, 1, 1.0),
            (9, SC.Par3, 7, 1.0),
        )
        for surf_idx, col, from_surf, scale in pickup_specs:
            try:
                s = lde.GetSurfaceAt(int(surf_idx))
                cell = s.GetSurfaceCell(col)
                SolveConfigurator._cell_make_surface_pickup(cell, ZOSAPI, from_surface=int(from_surf), scale=float(scale), offset=0.0)
            except Exception:
                pass


# ============================================================
# 7) Merit Function Builder (cross CT constraints)
# ============================================================


@dataclass(frozen=False)
class MeritConstraintsConfig:
    target_Lccd_mm: float = 28.5
    Dv_min_deg: float = 36.0
    Dv_max_deg: float = 40.0
    # thickness bounds
    Lin_min_mm: float = 90.0
    Lin_max_mm: float = 100.0
    d1_min_mm: float = -80.0
    d1_max_mm: float = -70.0
    d2_min_mm: float = 70.0
    d2_max_mm: float = 75.0
    Lout_min_mm: float = -110.0
    Lout_max_mm: float = -90.0
    # angles bounds
    theta1_min_deg: float = 9.0
    theta1_max_deg: float = 12.0
    theta2_min_deg: float = 11.0
    theta2_max_deg: float = 14.0
    img_tilt_min_deg: float = -6.0
    img_tilt_max_deg: float = -3.0

    # surface indices (must match LDEBuilder)
    surf_image: int = 11
    surf_grating: int = 5
    surf_object: int = 0
    surf_cb_d1: int = 3
    surf_cb_d2: int = 6
    surf_cb_Lout: int = 9
    surf_cb_theta1: int = 1
    surf_cb_theta2: int = 7
    surf_cb_imgtilt: int = 10
    par_tiltx: int = 3
    surf_cb_alpha: int = 4
    surf_cb_beta: int = 6

    alpha_max = 0
    alpha_min = -45
    beta_max = 0
    beta_min = -45


class MeritFunctionBuilder:
    @staticmethod
    def _mfe_clear_all(mfe: Any) -> None:
        try:
            n = int(mfe.NumberOfOperands)
        except Exception:
            n = 0
        if n <= 0:
            return
        if hasattr(mfe, "RemoveOperandsAt"):
            try:
                mfe.RemoveOperandsAt(1, n)
                return
            except Exception:
                pass
        if hasattr(mfe, "RemoveOperandAt"):
            for _ in range(n):
                try:
                    mfe.RemoveOperandAt(1)
                except Exception:
                    break

    @staticmethod
    def _add_operand(mfe: Any, ZOSAPI: Any, op_type: str) -> Any:
        op = mfe.AddOperand()
        op_enum = getattr(ZOSAPI.Editors.MFE.MeritOperandType, op_type, None)
        if op_enum is None:
            raise RuntimeError(f"未知/不支持的 MeritOperandType: {op_type}")
        op.ChangeType(op_enum)
        return op

    @staticmethod
    def _set_param(op: Any, ZOSAPI: Any, idx: int, value: Any) -> None:
        col = getattr(ZOSAPI.Editors.MFE.MeritColumn, f"Param{idx}", None)
        if col is None:
            raise RuntimeError("未找到 MeritColumn.ParamX 枚举")
        cell = op.GetOperandCell(col)
        if isinstance(value, bool) or isinstance(value, int):
            cell.IntegerValue = int(value)
        else:
            cell.DoubleValue = float(value)

    @staticmethod
    def _set_target_weight(op: Any, ZOSAPI: Any, *, target: Optional[float] = None, weight: Optional[float] = None) -> None:
        if target is not None:
            op.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Target).DoubleValue = float(target)
        if weight is not None:
            op.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Weight).DoubleValue = float(weight)

    @staticmethod
    def configure_cross_ct(
        system: Any,
        ZOSAPI: Any,
        *,
        clear_existing: bool = True,
        start_row: int = 1,
        insert_dmfs_anchor: bool = True,
        cfg: MeritConstraintsConfig = MeritConstraintsConfig(),
        p: None, 
    ) -> None:
        mfe = system.MFE
        if clear_existing:
            MeritFunctionBuilder._mfe_clear_all(mfe)

        start_row = max(1, int(start_row))
        for _ in range(start_row - 1):
            try:
                op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "BLNK")
                MeritFunctionBuilder._set_target_weight(op, ZOSAPI, weight=0.0)
            except Exception:
                op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "REAY")
                MeritFunctionBuilder._set_param(op, ZOSAPI, 1, cfg.surf_image)
                MeritFunctionBuilder._set_param(op, ZOSAPI, 2, 2)
                MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=0.0, weight=0.0)

        def _row() -> int:
            # Merit Function Editor rows are 1-indexed
            try:
                return int(mfe.NumberOfOperands)
            except Exception:
                # best effort
                return 1

        # 1) center wavelength ray at detector center
        op1 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "REAY")
        MeritFunctionBuilder._set_param(op1, ZOSAPI, 1, cfg.surf_image)
        MeritFunctionBuilder._set_param(op1, ZOSAPI, 2, 2)
        MeritFunctionBuilder._set_target_weight(op1, ZOSAPI, target=0.0, weight=1.0)
        row_op1 = _row()

        # 2-4) spectral length constraint
        op2 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "REAY")
        MeritFunctionBuilder._set_param(op2, ZOSAPI, 1, cfg.surf_image)
        MeritFunctionBuilder._set_param(op2, ZOSAPI, 2, 1)
        MeritFunctionBuilder._set_target_weight(op2, ZOSAPI, target=0.0, weight=0.0)
        row_op2 = _row()

        op3 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "REAY")
        MeritFunctionBuilder._set_param(op3, ZOSAPI, 1, cfg.surf_image)
        MeritFunctionBuilder._set_param(op3, ZOSAPI, 2, 3)
        MeritFunctionBuilder._set_target_weight(op3, ZOSAPI, target=0.0, weight=0.0)
        row_op3 = _row()

        op4 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "DIFF")
        # DIFF(#1=#3, #2=#2) => spectral length
        MeritFunctionBuilder._set_param(op4, ZOSAPI, 1, row_op3)
        MeritFunctionBuilder._set_param(op4, ZOSAPI, 2, row_op2)
        MeritFunctionBuilder._set_target_weight(op4, ZOSAPI, target=cfg.target_Lccd_mm, weight=1.0)
        row_op4 = _row()

        # 5-9) grating angle constraint
        op5 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "RAID")
        MeritFunctionBuilder._set_param(op5, ZOSAPI, 1, cfg.surf_grating)
        MeritFunctionBuilder._set_param(op5, ZOSAPI, 2, 2)
        MeritFunctionBuilder._set_target_weight(op5, ZOSAPI, weight=0.0)
        row_op5 = _row()

        op6 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "RAED")
        MeritFunctionBuilder._set_param(op6, ZOSAPI, 1, cfg.surf_grating)
        MeritFunctionBuilder._set_param(op6, ZOSAPI, 2, 2)
        MeritFunctionBuilder._set_target_weight(op6, ZOSAPI, weight=0.0)
        row_op6 = _row()

        op7 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "SUMM")
        MeritFunctionBuilder._set_param(op7, ZOSAPI, 1, row_op5)
        MeritFunctionBuilder._set_param(op7, ZOSAPI, 2, row_op6)
        MeritFunctionBuilder._set_target_weight(op7, ZOSAPI, weight=0.0)
        row_op7 = _row()

        op8 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "OPGT")
        MeritFunctionBuilder._set_param(op8, ZOSAPI, 1, row_op7)
        MeritFunctionBuilder._set_target_weight(op8, ZOSAPI, target=cfg.Dv_min_deg, weight=1.0)

        op9 = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "OPLT")
        MeritFunctionBuilder._set_param(op9, ZOSAPI, 1, row_op7)
        MeritFunctionBuilder._set_target_weight(op9, ZOSAPI, target=cfg.Dv_max_deg, weight=1.0)

        # 10-17) thickness bounds
        for op_type, surf, tgt in (
            ("FTGT", cfg.surf_object, cfg.Lin_min_mm),
            ("FTLT", cfg.surf_object, cfg.Lin_max_mm),
            ("FTGT", cfg.surf_cb_d1, cfg.d1_min_mm),
            ("FTLT", cfg.surf_cb_d1, cfg.d1_max_mm),
            ("FTGT", cfg.surf_cb_d2, cfg.d2_min_mm),
            ("FTLT", cfg.surf_cb_d2, cfg.d2_max_mm),
            ("FTGT", cfg.surf_cb_Lout, cfg.Lout_min_mm),
            ("FTLT", cfg.surf_cb_Lout, cfg.Lout_max_mm),
        ):
            op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, op_type)
            MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))
            MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(tgt), weight=1.0)

        # 18-23) angle bounds
        for op_type, surf, par, tgt in (
            ("PMGT", cfg.surf_cb_theta1, cfg.par_tiltx, cfg.theta1_min_deg),
            ("PMLT", cfg.surf_cb_theta1, cfg.par_tiltx, cfg.theta1_max_deg),
            ("PMGT", cfg.surf_cb_theta2, cfg.par_tiltx, cfg.theta2_min_deg),
            ("PMLT", cfg.surf_cb_theta2, cfg.par_tiltx, cfg.theta2_max_deg),
            ("PMGT", cfg.surf_cb_imgtilt, cfg.par_tiltx, cfg.img_tilt_min_deg),
            ("PMLT", cfg.surf_cb_imgtilt, cfg.par_tiltx, cfg.img_tilt_max_deg),
        ):
            op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, op_type)
            MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))
            MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(par))
            MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(tgt), weight=1.0)
        # print("-------------------------------------")
        # print(p.spec_type)

        # op_type_sign = "PMGT" if p.spec_type=="交叉型" else "PMLT"

        # for surf in (cfg.surf_cb_alpha, cfg.surf_cb_beta):  # 通常对应 4 和 6
        #     op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, op_type_sign)
        #     MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))          # Int1 = surface
        #     MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(cfg.par_tiltx)) # Int2 = parameter (TiltX=3)
        #     MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=0.0, weight=1.0)

        print(cfg)
        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "PMGT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(cfg.surf_cb_alpha))          # Int1 = surface
        MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(cfg.par_tiltx)) # Int2 = parameter (TiltX=3)
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=cfg.alpha_min, weight=1.0)

        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "PMLT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(cfg.surf_cb_alpha))          # Int1 = surface
        MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(cfg.par_tiltx)) # Int2 = parameter (TiltX=3)
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=cfg.alpha_max, weight=1.0)

        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "PMGT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(cfg.surf_cb_beta))          # Int1 = surface
        MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(cfg.par_tiltx)) # Int2 = parameter (TiltX=3)
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=cfg.beta_min, weight=1.0)

        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "PMLT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(cfg.surf_cb_beta))          # Int1 = surface
        MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(cfg.par_tiltx)) # Int2 = parameter (TiltX=3)
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=cfg.beta_max, weight=1.0)


        # op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVGT")
        # MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))  # Int1 = Surf
        # MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(C_min), weight=float(weight))

        # # CVLT: curvature <= C_max
        # op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVLT")
        # MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))  # Int1 = Surf
        # MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(C_max), weight=float(weight))

        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVGT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(2))  # Int1 = Surf
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(cfg.R_1_min), weight=float(1))
        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVLT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(2))  # Int1 = Surf
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(cfg.R_1_max), weight=float(1))

        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVGT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(8))  # Int1 = Surf
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(cfg.R_2_min), weight=float(1))
        op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVLT")
        MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(8))  # Int1 = Surf
        MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(cfg.R_2_max), weight=float(1))

        if insert_dmfs_anchor:
            try:
                op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "DMFS")
                MeritFunctionBuilder._set_target_weight(op, ZOSAPI, weight=0.0)
            except Exception:
                pass


# ============================================================
# 8) Optimization Wizard wrapper (Spot Y-only recommended)
# ============================================================


class SeqOptimizationWizard:
    """OpticStudio 2024: Optimization Wizard -> Image Quality: Spot Diagram.

    This implementation is intentionally defensive: OpticStudio 2024 patches
    may rename wizard properties. We therefore attempt multiple property names
    and fall back to .NET reflection + keyword matching over the wizard object
    graph.
    """

    @staticmethod
    def _try_set_first_attr(obj: Any, names: Sequence[str], value: Any) -> bool:
        for nm in names:
            if hasattr(obj, nm):
                try:
                    setattr(obj, nm, value)
                    return True
                except Exception:
                    continue
        return False

    @staticmethod
    def _try_set_enum_property_by_name(
        obj: Any,
        *,
        prop_names: Sequence[str],
        enum_member_candidates: Sequence[str],
    ) -> bool:
        """Set an enum-type property by parsing member name (reflection)."""
        try:
            import System  # type: ignore
        except Exception:
            return False

        try:
            t = obj.GetType()
        except Exception:
            return False

        for pn in prop_names:
            try:
                pi = t.GetProperty(pn)
            except Exception:
                pi = None
            if pi is None:
                continue
            try:
                et = pi.PropertyType
                if not getattr(et, "IsEnum", False):
                    continue
            except Exception:
                continue

            for mem in enum_member_candidates:
                try:
                    val = System.Enum.Parse(et, mem, True)  # ignoreCase=True
                    pi.SetValue(obj, val, None)
                    return True
                except Exception:
                    continue

        return False

    @staticmethod
    def run_spotdiagram(
        system: Any,
        ZOSAPI: Any,
        *,
        start_row: int = 1,
        spot_mode: str = "Y_ONLY",  # "Y_ONLY" or "XY"
        x_weight: float = 0.0,
        ignore_lateral_color: bool = True,
        verbose: bool = False,
    ) -> bool:
        """Generate default merit function via SEQOptimizationWizard and write into MFE.

        Equivalent UI path:
          Optimize -> Optimization Wizard
            Image quality: Spot Diagram
            X weight: (x_weight)
            Ignore lateral color: (ignore_lateral_color)
            Start at: (start_row)
            OK
        """

        mfe = getattr(system, "MFE", None)
        if mfe is None:
            return False

        wiz = getattr(mfe, "SEQOptimizationWizard", None)
        if wiz is None:
            return False

        # ------------------------------
        # Helpers for deep reflection search
        # ------------------------------
        import re

        try:
            import System  # type: ignore
        except Exception:
            System = None  # type: ignore

        def _net_is_simple(obj: Any) -> bool:
            if System is None:
                return True
            try:
                t = obj.GetType()
                if t.IsValueType:
                    return True
                if t == System.String:
                    return True
            except Exception:
                return True
            return False

        def _walk_object_graph(root: Any, *, max_depth: int = 4):
            out = []
            q = [(root, 0)]
            seen = set()
            while q:
                obj, d = q.pop(0)
                if obj is None:
                    continue
                oid = id(obj)
                if oid in seen:
                    continue
                seen.add(oid)
                out.append(obj)
                if d >= max_depth:
                    continue
                if System is None:
                    continue
                try:
                    t = obj.GetType()
                    props = t.GetProperties()
                except Exception:
                    continue
                for p in props:
                    try:
                        if p.GetIndexParameters().Length != 0:
                            continue
                        if not p.CanRead:
                            continue
                        pn = str(p.Name)
                        if pn.lower() in ("parent", "application", "system", "primarysystem", "owner"):
                            continue
                        child = p.GetValue(obj, None)
                        if child is None or _net_is_simple(child):
                            continue
                        q.append((child, d + 1))
                    except Exception:
                        continue
            return out

        def _try_set_by_reflection(obj: Any, name: str, value: Any) -> bool:
            if System is None:
                return False
            try:
                t = obj.GetType()
                pi = t.GetProperty(name)
                if pi is None or (not pi.CanWrite):
                    return False
                pi.SetValue(obj, value, None)
                return True
            except Exception:
                return False

        def _set_first(root: Any, name_candidates: Sequence[str], value: Any, *, max_depth: int = 4) -> bool:
            objs = _walk_object_graph(root, max_depth=max_depth)
            for nm in name_candidates:
                for o in objs:
                    if (hasattr(o, nm) and SeqOptimizationWizard._try_set_first_attr(o, (nm,), value)) or _try_set_by_reflection(o, nm, value):
                        return True
            return False

        def _set_all_matching_flag(root: Any, *, desired_ignore: bool, max_depth: int = 4) -> Tuple[int, list]:
            if System is None:
                return 0, []

            patterns_direct = [
                (re.compile(r"ignore.*(lateral|transverse).*(color|chromatic|tca|aberration)", re.I), desired_ignore),
                (re.compile(r"ignore.*tca", re.I), desired_ignore),
                (re.compile(r"ignore.*lateral.*color", re.I), desired_ignore),
                (re.compile(r"ignore.*transverse.*(chromatic|aberration|tca)", re.I), desired_ignore),
                (re.compile(r"ignore.*(lateral|tca|chromatic|transverse)", re.I), desired_ignore),
            ]
            patterns_inverse = [
                (re.compile(r"(use|used|enable|enabled|consider|account).*lateral.*color", re.I), (not desired_ignore)),
                (re.compile(r"lateral.*color.*(use|used|enable|enabled|consider|account)", re.I), (not desired_ignore)),
                (re.compile(r"(use|used|enable|enabled|consider|account).*(tca|chromatic|transverse)", re.I), (not desired_ignore)),
            ]

            hits = []
            for o in _walk_object_graph(root, max_depth=max_depth):
                try:
                    t = o.GetType()
                    props = t.GetProperties()
                except Exception:
                    continue
                for p in props:
                    try:
                        if p.GetIndexParameters().Length != 0:
                            continue
                        if not p.CanWrite:
                            continue
                        pt = p.PropertyType
                        is_bool = (pt == System.Boolean)
                        is_int = pt in (System.Int16, System.Int32, System.Int64, System.Byte)
                        if not (is_bool or is_int):
                            continue
                        pn = str(p.Name)

                        vset = None
                        for rgx, vv in patterns_direct:
                            if rgx.search(pn):
                                vset = vv
                                break
                        if vset is None:
                            for rgx, vv in patterns_inverse:
                                if rgx.search(pn):
                                    vset = vv
                                    break
                        if vset is None:
                            continue

                        if is_bool:
                            p.SetValue(o, bool(vset), None)
                            hits.append(f"{t.FullName}.{pn}={bool(vset)}")
                        else:
                            p.SetValue(o, int(1 if bool(vset) else 0), None)
                            hits.append(f"{t.FullName}.{pn}={int(1 if bool(vset) else 0)}")
                    except Exception:
                        continue
            return len(hits), hits

        def _set_double_by_regex(root: Any, patterns: Sequence[str], value: float, *, max_depth: int = 4) -> Tuple[int, list]:
            if System is None:
                return 0, []
            rx = [re.compile(p, re.I) for p in patterns]
            hits = []
            for o in _walk_object_graph(root, max_depth=max_depth):
                try:
                    t = o.GetType()
                    props = t.GetProperties()
                except Exception:
                    continue
                for p in props:
                    try:
                        if p.GetIndexParameters().Length != 0:
                            continue
                        if not p.CanWrite:
                            continue
                        pn = str(p.Name)
                        if not any(r.search(pn) for r in rx):
                            continue
                        pt = p.PropertyType
                        if pt not in (System.Double, System.Single):
                            continue
                        p.SetValue(o, float(value), None)
                        hits.append(f"{t.FullName}.{pn}={float(value)}")
                    except Exception:
                        continue
            return len(hits), hits

        # ------------------------------
        # 1) Start row & do NOT delete existing MF
        # ------------------------------
        _set_first(wiz, ("StartAt", "StartRow", "StartingRow", "StartAtRow"), int(start_row))
        _set_first(
            wiz,
            (
                "DeleteExistingMeritFunction",
                "DeleteExisting",
                "IsDeleteExistingMeritFunction",
                "IsDeleteExisting",
                "DeleteAll",
                "IsDeleteAll",
            ),
            False,
        )

        # ------------------------------
        # 2) Image Quality: Spot Diagram
        # ------------------------------
        spot_mode_u = str(spot_mode or "").strip().upper()
        if spot_mode_u in ("Y", "Y_ONLY", "YONLY", "SPOTY", "SPOT_Y_ONLY"):
            set_data_ok = _set_first(wiz, ("Data", "ImageQualityData", "CriterionData"), 3)
            if not set_data_ok:
                set_data_ok = _set_first(wiz, ("Data", "ImageQualityData", "CriterionData"), 1)
        else:
            set_data_ok = _set_first(wiz, ("Data", "ImageQualityData", "CriterionData"), 4)
            if not set_data_ok:
                set_data_ok = _set_first(wiz, ("Data", "ImageQualityData", "CriterionData"), 1)

        if not set_data_ok:
            SeqOptimizationWizard._try_set_enum_property_by_name(
                wiz,
                prop_names=("Criterion", "ImageQualityCriterion", "ImageQuality", "ImageQualityType"),
                enum_member_candidates=("SpotDiagram", "Spot", "Spot_Diagram", "SpotDiagramRMS", "RMS_Spot", "RMSSpot"),
            )

        # ------------------------------
        # 3) X/Y weights (XY mode only)
        # ------------------------------
        if spot_mode_u not in ("Y", "Y_ONLY", "YONLY", "SPOTY", "SPOT_Y_ONLY"):
            ok_xw = _set_first(wiz, ("XWeight", "RelativeXWeight", "SpotXWeight", "Xweight"), float(x_weight))
            if not ok_xw:
                _set_double_by_regex(
                    wiz,
                    patterns=[r"(^|_)xweight$", r"x\s*weight", r"relativexweight", r"spotxweight"],
                    value=float(x_weight),
                )
            ok_yw = _set_first(wiz, ("YWeight", "RelativeYWeight", "SpotYWeight", "Yweight"), 1.0)
            if not ok_yw:
                _set_double_by_regex(
                    wiz,
                    patterns=[r"(^|_)yweight$", r"y\s*weight", r"relativeyweight", r"spotyweight"],
                    value=1.0,
                )

        # ------------------------------
        # 4) Ignore lateral color / TCA
        # ------------------------------
        ok_ignore = _set_first(
            wiz,
            (
                "IgnoreLateralColor",
                "IgnoreTCA",
                "IgnoreTransverseChromaticAberration",
                "IgnoreTransverseColor",
                "IgnoreLateralChromaticAberration",
            ),
            bool(ignore_lateral_color),
        )
        if not ok_ignore:
            _set_first(
                wiz,
                ("IsLateralColorUsed", "UseLateralColor", "LateralColorUsed", "UseTransverseChromaticAberration"),
                bool(not ignore_lateral_color),
            )

        hit_n, hit_list = _set_all_matching_flag(wiz, desired_ignore=bool(ignore_lateral_color))
        if verbose:
            if hit_n == 0 and (not ok_ignore):
                print("[SEQOptimizationWizard] 未找到与 'Ignore lateral color/TCA' 相关的可写属性。")
            elif hit_n > 0:
                print(f"[SEQOptimizationWizard] 已写入 {hit_n} 个(含子对象)与忽略垂轴色差相关的选项：")
                for s in hit_list[:30]:
                    print("  -", s)

        # 5) Overall weight (optional)
        _set_first(wiz, ("OverallWeight", "Weight", "Overall"), 1.0)

        # 6) Apply (OK)
        applied = False
        for meth in ("Apply", "ApplyAndClose", "OK", "Accept", "Run"):
            fn = getattr(wiz, meth, None)
            if callable(fn):
                try:
                    fn()
                    applied = True
                    break
                except Exception:
                    continue

        if verbose and not applied:
            try:
                print("[SEQOptimizationWizard] Apply failed; available members sample:")
                names = [n for n in dir(wiz) if not n.startswith("_")]
                print(names[:80])
            except Exception:
                pass

        return bool(applied)


# ============================================================
# 9) Pipeline (orchestrator) + compatibility wrapper
# ============================================================


@dataclass(frozen=False)
class ZemaxRunOptions:
    zos_mode: str = "extension"
    instance_id: int = 0
    na_obj: float = 0.125
    save_path: Optional[str] = None

    auto_set_variables_pickups: bool = False
    auto_configure_mfe: bool = False
    auto_run_optimization_wizard: bool = False

    wizard_start_row: Optional[int] = None
    wizard_spot_mode: str = "Y_ONLY"  # "Y_ONLY" or "XY"
    wizard_x_weight: float = 0.0
    wizard_ignore_transverse_error: bool = True
    wizard_allow_fail: bool = True

    mfe_clear_existing: bool = True
    mfe_start_row: int = 1
    constraints_cfg: MeritConstraintsConfig = MeritConstraintsConfig()


class CTSpectrometerPipeline:
    @staticmethod
    def run(inputs: SpectrometerInputs, opts: ZemaxRunOptions) -> ComputedParams:
        # 1) compute
        p = CTDesignCalculator.compute(inputs)
        info2(p)
        print(opts)
        calculate_micro_adjust(opts, p)
        print(opts)
        # print(opts.constraints_cfg.img_hahah)

        # 2) connect
        app, system, ZOSAPI = ZemaxConnector.connect(mode=opts.zos_mode, instance_id=opts.instance_id)

        # 3) new system
        system.New(False)

        # 4) system explorer
        SystemExplorerConfigurator.configure(
            system,
            ZOSAPI,
            na_obj=opts.na_obj,
            fields_x=(-0.3, 0.0, 0.3),
            wavelengths_um=(p.lambda_1 / 1000.0, p.lambda_c / 1000.0, p.lambda_2 / 1000.0),
        )

        # 5) LDE
        LDEBuilder.build_cross_ct_like_base0(system, ZOSAPI, p)

        # 6) solves
        if opts.auto_set_variables_pickups:
            SolveConfigurator.configure_cross_ct(system, ZOSAPI)

        # 7) constraints MFE
        if opts.auto_configure_mfe:
            MeritFunctionBuilder.configure_cross_ct(
                system,
                ZOSAPI,
                clear_existing=opts.mfe_clear_existing,
                start_row=opts.mfe_start_row,
                insert_dmfs_anchor=not opts.auto_run_optimization_wizard,
                cfg=opts.constraints_cfg,
                p=p
            )

        # 8) optional wizard
        wizard_applied = False
        if opts.auto_run_optimization_wizard:
            try:
                if opts.wizard_start_row is None:
                    try:
                        start_row = int(system.MFE.NumberOfOperands) + 1
                    except Exception:
                        start_row = 1
                else:
                    start_row = int(opts.wizard_start_row)

                wizard_applied = SeqOptimizationWizard.run_spotdiagram(
                    system,
                    ZOSAPI,
                    start_row=start_row,
                    spot_mode=str(opts.wizard_spot_mode),
                    x_weight=float(opts.wizard_x_weight),
                    ignore_lateral_color=bool(opts.wizard_ignore_transverse_error),
                    verbose=False,
                )
            except Exception:
                wizard_applied = False

            if (not wizard_applied) and (not opts.wizard_allow_fail):
                raise RuntimeError(
                    "Optimization Wizard 自动写入失败：可能是当前 ZOS-API 版本未暴露向导接口或属性名不匹配。"
                )

        p.wizard_applied = bool(wizard_applied)

        if opts.save_path:
            system.SaveAs(opts.save_path)

        return p


# -----------------------------------------------------------------
# Backward-compatible wrapper (same signature style as your previous script)
# -----------------------------------------------------------------


def push_to_zemax(
    *,
    inputs: Dict[str, Any],
    zos_mode: str = "extension",
    instance_id: int = 0,
    na_obj: float = 0.125,
    save_path: Optional[str] = None,
    auto_set_variables_pickups: bool = False,
    auto_configure_mfe: bool = False,
    auto_run_optimization_wizard: bool = False,
    wizard_start_row: Optional[int] = None,
    wizard_spot_mode: str = "Y_ONLY",
    wizard_x_weight: float = 0.0,
    wizard_ignore_transverse_error: bool = True,
    wizard_allow_fail: bool = True,
    mfe_clear_existing: bool = True,
    mfe_start_row: int = 1,
    target_Lccd_mm: float = 28.5,
    Dv_min_deg: float = 36.0,
    Dv_max_deg: float = 40.0,
) -> Dict[str, Any]:
    """Compatibility wrapper returning a dict (same as your earlier push_to_zemax)."""

    sinputs = SpectrometerInputs(
        spec_type=str(inputs["spec_type"]),
        lambda_1_nm=float(inputs["lambda_1"]),
        lambda_2_nm=float(inputs["lambda_2"]),
        grating_lines_per_mm=float(inputs["f"]),
        diffraction_order=int(inputs["k"]),
        D_v_deg=float(inputs["D_v"]),
        sensor_length_mm=float(inputs["L_sensor"]),
        magnification=float(inputs["M"]),
        theta_1_deg=float(inputs["theta_1"]),
    )

    cfg = MeritConstraintsConfig(
        target_Lccd_mm=float(target_Lccd_mm),
        Dv_min_deg=float(Dv_min_deg),
        Dv_max_deg=float(Dv_max_deg),
    )

    opts = ZemaxRunOptions(
        zos_mode=zos_mode,
        instance_id=int(instance_id),
        na_obj=float(na_obj),
        save_path=save_path,
        auto_set_variables_pickups=bool(auto_set_variables_pickups),
        auto_configure_mfe=bool(auto_configure_mfe),
        auto_run_optimization_wizard=bool(auto_run_optimization_wizard),
        wizard_start_row=wizard_start_row,
        wizard_spot_mode=str(wizard_spot_mode),
        wizard_x_weight=float(wizard_x_weight),
        wizard_ignore_transverse_error=bool(wizard_ignore_transverse_error),
        wizard_allow_fail=bool(wizard_allow_fail),
        mfe_clear_existing=bool(mfe_clear_existing),
        mfe_start_row=int(mfe_start_row),
        constraints_cfg=cfg,
    )
    p = CTSpectrometerPipeline.run(sinputs, opts)
    return p.as_dict()


# ============================================================
# 10) Minimal runnable example
# ============================================================

def info2(p):
    print("=================输入参数信息===================")
    print("光谱仪类型：", p.spec_type)
    print("起始波长 (nm):", p.lambda_1)
    print("终止波长 (nm):", p.lambda_2)
    print("光栅密度 (lines/mm):", p.f)
    print("衍射级别:", p.k)
    print("光栅夹角 (度):", p.D_v)
    print("传感器长度 (mm):", p.L_sensor)
    print("放大倍率:", p.M)
    print("准直镜转角 (度):", p.theta_1)

    print("=================输出参数信息===================")
    print("计算得到的入射角 alpha (度):", _calc.radian_to_angle(p.alpha_rad))
    print("计算得到的出射角 beta (度):", _calc.radian_to_angle(p.beta_rad))
    print("计算得到的光谱仪有效工作长度 L_out (mm):", p.L_out)
    print("计算得到的光谱仪入射光束长度 L_in (mm):", p.L_in)
    print("计算得到的会聚镜转角 theta_2 (度):", _calc.radian_to_angle(p.theta_2_rad))
    print("计算得到的准直镜曲率半径 R_1 (mm):", p.R_1)
    print("计算得到的会聚镜曲率半径 R_2 (mm):", p.R_2)
    print("计算得到的准直镜到光栅的距离 d_1 (mm):", p.d_1)
    print("计算得到的光栅到会聚镜的距离 d_2 (mm):", p.d_2)

def calculate_micro_adjust(opts, p):
    opts.constraints_cfg.target_Lccd_mm = p.L_sensor
    # if p.spec_type == "交叉型":
    opts.constraints_cfg.Dv_min_deg = int(p.D_v - p.D_v / 10)
    opts.constraints_cfg.Dv_max_deg = int(p.D_v + p.D_v / 10)
    # elif p.spec_type == "非交叉型":
        # opts.constraints_cfg.Dv_min_deg = - int(p.D_v + p.D_v / 10)
        # opts.constraints_cfg.Dv_max_deg = - int(p.D_v - p.D_v / 10)
    opts.constraints_cfg.Lin_min_mm = int(p.L_in - 5)
    opts.constraints_cfg.Lin_max_mm = int(p.L_in + 5)
    opts.constraints_cfg.d1_min_mm = - int(p.d_1 + 5)
    opts.constraints_cfg.d1_max_mm = - int(p.d_1 - 5)
    opts.constraints_cfg.d2_min_mm = int(p.d_2 - 2.5)
    opts.constraints_cfg.d2_max_mm = int(p.d_2 + 2.5)
    opts.constraints_cfg.Lout_min_mm = - int(p.L_out + 10)
    opts.constraints_cfg.Lout_max_mm = - int(p.L_out - 10)
    opts.constraints_cfg.theta1_min_deg = int(p.theta_1 - 1.5)
    opts.constraints_cfg.theta1_max_deg = int(p.theta_1 + 1.5)
    opts.constraints_cfg.theta2_min_deg = int(_calc.radian_to_angle(p.theta_2_rad) - 1.5)
    opts.constraints_cfg.theta2_max_deg = int(_calc.radian_to_angle(p.theta_2_rad) + 1.5)
    opts.constraints_cfg.img_tilt_min_deg = - int(4 + 1.5)
    opts.constraints_cfg.img_tilt_max_deg = - int(4 - 1.5)
    if p.spec_type == "交叉型":
        opts.constraints_cfg.alpha_max = int(p.D_v + p.D_v / 10)
        opts.constraints_cfg.alpha_min = int(0)
        opts.constraints_cfg.beta_max = int(p.D_v + p.D_v / 10)
        opts.constraints_cfg.beta_min = int(0)
    elif p.spec_type == "非交叉型":
        opts.constraints_cfg.alpha_max = - int(0)
        opts.constraints_cfg.alpha_min = - int(p.D_v + p.D_v / 10)
        opts.constraints_cfg.beta_max = - int(0)
        opts.constraints_cfg.beta_min = - int(p.D_v + p.D_v / 10)
    opts.constraints_cfg.R_1_max = 1 / (- p.R_1 - 5)
    opts.constraints_cfg.R_1_min = 1 / (- p.R_1 + 5)
    opts.constraints_cfg.R_2_max = 1 / (- p.R_2 - 5)
    opts.constraints_cfg.R_2_min = 1 / (- p.R_2 + 5)
    return opts


if __name__ == "__main__":
    # Example inputs (edit as needed)
    inputs = {
        "spec_type": "交叉型",
        "lambda_1": 200,
        "lambda_2": 1100,
        "f": 300,
        "k": 1,
        "D_v": 40,
        "L_sensor": 28.4,
        "M": 1.15,
        "theta_1": 11,
    }

    other_settings = {
        "zos_mode": "extension",
        "instance_id": 0,
        "NA": 0.125, # 入射光的参数
        "save_path": None,
        "auto_set_variables_pickups": True, # 参数设置为变量，为了后续优化
        "auto_configure_mfe": True, # 评价函数编辑器中写入约束
        "auto_run_optimization_wizard": True, # 设置好点列图优化
        "wizard_spot_mode": "Y_ONLY", # 点列图优化只优化Y方向
        "wizard_x_weight": 0.0, # 非Y_ONLY时需要加的，没有实际意义
        "wizard_ignore_transverse_error": True # 忽略垂轴色差，配合Y_ONLY使用的
    }

    # Run and push to Zemax
    out = push_to_zemax(
        inputs=inputs,
        zos_mode=other_settings["zos_mode"],
        instance_id=other_settings["instance_id"],
        na_obj=other_settings["NA"],
        save_path=other_settings["save_path"],
        auto_set_variables_pickups=other_settings["auto_set_variables_pickups"],
        auto_configure_mfe=other_settings["auto_configure_mfe"],
        auto_run_optimization_wizard=other_settings["auto_run_optimization_wizard"],
        wizard_spot_mode=other_settings["wizard_spot_mode"],
        wizard_x_weight=other_settings["wizard_x_weight"],
        wizard_ignore_transverse_error=other_settings["wizard_ignore_transverse_error"],
    )
