import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple
from math import asin, atan, cos, pi, sqrt, tan, acos, sin  # noqa

class SeqOptimizationWizard:
    """OpticStudio 2024: Optimization Wizard -> Image Quality: Spot Diagram.

    This implementation is intentionally defensive: OpticStudio 2024 patches
    may rename wizard properties. We therefore attempt multiple property names
    and fall back to .NET reflection + keyword matching over the wizard object
    graph.
    """

    def _try_set_first_attr(self, obj: Any, names: Sequence[str], value: Any) -> bool:
        for nm in names:
            if hasattr(obj, nm):
                try:
                    setattr(obj, nm, value)
                    return True
                except Exception:
                    continue
        return False

    def _try_set_enum_property_by_name(
        self, 
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

    def run_spotdiagram(
        self, 
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
                    if (hasattr(o, nm) and self._try_set_first_attr(o, (nm,), value)) or _try_set_by_reflection(o, nm, value):
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
            self._try_set_enum_property_by_name(
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

class MeritFunctionBuilder:
    def _mfe_clear_all(self, mfe: Any) -> None:
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

    def _add_operand(self, mfe: Any, ZOSAPI: Any, op_type: str) -> Any:
        op = mfe.AddOperand()
        op_enum = getattr(ZOSAPI.Editors.MFE.MeritOperandType, op_type, None)
        if op_enum is None:
            raise RuntimeError(f"未知/不支持的 MeritOperandType: {op_type}")
        op.ChangeType(op_enum)
        return op

    def _set_param(self, op: Any, ZOSAPI: Any, idx: int, value: Any) -> None:
        col = getattr(ZOSAPI.Editors.MFE.MeritColumn, f"Param{idx}", None)
        if col is None:
            raise RuntimeError("未找到 MeritColumn.ParamX 枚举")
        cell = op.GetOperandCell(col)
        if isinstance(value, bool) or isinstance(value, int):
            cell.IntegerValue = int(value)
        else:
            cell.DoubleValue = float(value)

    def _set_target_weight(self, op: Any, ZOSAPI: Any, *, target: Optional[float] = None, weight: Optional[float] = None) -> None:
        if target is not None:
            op.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Target).DoubleValue = float(target)
        if weight is not None:
            op.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Weight).DoubleValue = float(weight)

    def configure_cross_ct(
        self, 
        system: Any,
        ZOSAPI: Any,
        *,
        clear_existing: bool = True,
        start_row: int = 1,
        insert_dmfs_anchor: bool = True,
        cfg: Dict[str, Any],
        p: Dict[str, Any], 
        opts: Dict[str, Any],
        basicStructure: list,
    ) -> None:
        mfe = system.MFE
        if clear_existing:
            self._mfe_clear_all(mfe)

        start_row = max(1, int(start_row))
        for _ in range(start_row - 1):
            try:
                op = self._add_operand(mfe, ZOSAPI, "BLNK")
                self._set_target_weight(op, ZOSAPI, weight=0.0)
            except Exception:
                op = self._add_operand(mfe, ZOSAPI, "REAY")
                self._set_param(op, ZOSAPI, 1, basicStructure.index("surf_image"))
                self._set_param(op, ZOSAPI, 2, 2)
                self._set_target_weight(op, ZOSAPI, target=0.0, weight=0.0)

        def _row() -> int:
            # Merit Function Editor rows are 1-indexed
            try:
                return int(mfe.NumberOfOperands)
            except Exception:
                # best effort
                return 1
            
        # if opts["avoid_shelter"] == True:
        #     cfg["surf_image"] += 2
        #     cfg["surf_cb_Lout"] += 2
        #     cfg["surf_cb_imgtilt"] += 2

        #     cfg["surf_cb_avoid_1"] = 8
        #     cfg["surf_cb_avoid_2"] = 10

        #     cfg["surf_cb_mirror_2"] += 1

        # 1) center wavelength ray at detector center
        op1 = self._add_operand(mfe, ZOSAPI, "REAY")
        self._set_param(op1, ZOSAPI, 1, basicStructure.index("surf_image"))
        self._set_param(op1, ZOSAPI, 2, 2)
        self._set_target_weight(op1, ZOSAPI, target=0.0, weight=1.0)
        row_op1 = _row()

        # 2-4) spectral length constraint
        op2 = self._add_operand(mfe, ZOSAPI, "REAY")
        self._set_param(op2, ZOSAPI, 1, basicStructure.index("surf_image"))
        self._set_param(op2, ZOSAPI, 2, 1)
        self._set_target_weight(op2, ZOSAPI, target=0.0, weight=0.0)
        row_op2 = _row()

        op3 = self._add_operand(mfe, ZOSAPI, "REAY")
        self._set_param(op3, ZOSAPI, 1, basicStructure.index("surf_image"))
        self._set_param(op3, ZOSAPI, 2, 3)
        self._set_target_weight(op3, ZOSAPI, target=0.0, weight=0.0)
        row_op3 = _row()

        op4 = self._add_operand(mfe, ZOSAPI, "DIFF")
        # DIFF(#1=#3, #2=#2) => spectral length
        self._set_param(op4, ZOSAPI, 1, row_op3)
        self._set_param(op4, ZOSAPI, 2, row_op2)
        # self._set_target_weight(op4, ZOSAPI, target=cfg["target_Lccd_mm"], weight=1.0)
        self._set_target_weight(op4, ZOSAPI, target=cfg["target_Lccd_mm"], weight=0.0) # important
        row_op4 = _row()

        # 5-9) grating angle constraint
        op5 = self._add_operand(mfe, ZOSAPI, "RAID")
        self._set_param(op5, ZOSAPI, 1, basicStructure.index("surf_grating"))
        self._set_param(op5, ZOSAPI, 2, 2)
        self._set_target_weight(op5, ZOSAPI, weight=0.0)
        row_op5 = _row()

        op6 = self._add_operand(mfe, ZOSAPI, "RAED")
        self._set_param(op6, ZOSAPI, 1, basicStructure.index("surf_grating"))
        self._set_param(op6, ZOSAPI, 2, 2)
        self._set_target_weight(op6, ZOSAPI, weight=0.0)
        row_op6 = _row()

        op7 = self._add_operand(mfe, ZOSAPI, "SUMM")
        self._set_param(op7, ZOSAPI, 1, row_op5)
        self._set_param(op7, ZOSAPI, 2, row_op6)
        self._set_target_weight(op7, ZOSAPI, weight=0.0)
        row_op7 = _row()

        op8 = self._add_operand(mfe, ZOSAPI, "OPGT")
        self._set_param(op8, ZOSAPI, 1, row_op7)
        self._set_target_weight(op8, ZOSAPI, target=cfg["Dv_min_deg"], weight=1.0)

        op9 = self._add_operand(mfe, ZOSAPI, "OPLT")
        self._set_param(op9, ZOSAPI, 1, row_op7)
        self._set_target_weight(op9, ZOSAPI, target=cfg["Dv_max_deg"], weight=1.0)

        # 10-17) thickness bounds
        for op_type, surf, tgt in (
            ("FTGT", basicStructure.index("surf_object"), cfg["Lin_min_mm"]),
            ("FTLT", basicStructure.index("surf_object"), cfg["Lin_max_mm"]),
            ("FTGT", basicStructure.index("surf_cb_d1"), cfg["d1_min_mm"]),
            ("FTLT", basicStructure.index("surf_cb_d1"), cfg["d1_max_mm"]),
            ("FTGT", basicStructure.index("surf_cb_d2"), cfg["d2_min_mm"]),
            ("FTLT", basicStructure.index("surf_cb_d2"), cfg["d2_max_mm"]),
            ("FTGT", basicStructure.index("surf_cb_Lout"), cfg["Lout_min_mm"]),
            ("FTLT", basicStructure.index("surf_cb_Lout"), cfg["Lout_max_mm"]),
        ):
            op = self._add_operand(mfe, ZOSAPI, op_type)
            self._set_param(op, ZOSAPI, 1, int(surf))
            self._set_target_weight(op, ZOSAPI, target=float(tgt), weight=1.0)

        # 18-23) angle bounds
        for op_type, surf, par, tgt in (
            ("PMGT", basicStructure.index("surf_cb_theta1"), cfg["par_tiltx"], cfg["theta1_min_deg"]),
            ("PMLT", basicStructure.index("surf_cb_theta1"), cfg["par_tiltx"], cfg["theta1_max_deg"]),
            ("PMGT", basicStructure.index("surf_cb_theta2"), cfg["par_tiltx"], cfg["theta2_min_deg"]),
            ("PMLT", basicStructure.index("surf_cb_theta2"), cfg["par_tiltx"], cfg["theta2_max_deg"]),
            ("PMGT", basicStructure.index("surf_cb_imgtilt"), cfg["par_tiltx"], cfg["img_tilt_min_deg"]),
            ("PMLT", basicStructure.index("surf_cb_imgtilt"), cfg["par_tiltx"], cfg["img_tilt_max_deg"]),
        ):
            op = self._add_operand(mfe, ZOSAPI, op_type)
            self._set_param(op, ZOSAPI, 1, int(surf))
            self._set_param(op, ZOSAPI, 2, int(par))
            self._set_target_weight(op, ZOSAPI, target=float(tgt), weight=1.0)
        # print("-------------------------------------")
        # print(p.spec_type)

        # op_type_sign = "PMGT" if p.spec_type=="交叉型" else "PMLT"

        # for surf in (cfg.surf_cb_alpha, cfg.surf_cb_beta):  # 通常对应 4 和 6
        #     op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, op_type_sign)
        #     MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))          # Int1 = surface
        #     MeritFunctionBuilder._set_param(op, ZOSAPI, 2, int(cfg.par_tiltx)) # Int2 = parameter (TiltX=3)
        #     MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=0.0, weight=1.0)

        # print(cfg)
        op = self._add_operand(mfe, ZOSAPI, "PMGT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_alpha")))          # Int1 = surface
        self._set_param(op, ZOSAPI, 2, int(cfg["par_tiltx"])) # Int2 = parameter (TiltX=3)
        self._set_target_weight(op, ZOSAPI, target=cfg["alpha_min"], weight=1.0)

        op = self._add_operand(mfe, ZOSAPI, "PMLT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_alpha")))          # Int1 = surface
        self._set_param(op, ZOSAPI, 2, int(cfg["par_tiltx"])) # Int2 = parameter (TiltX=3)
        self._set_target_weight(op, ZOSAPI, target=cfg["alpha_max"], weight=1.0)

        op = self._add_operand(mfe, ZOSAPI, "PMGT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_d2")))          # Int1 = surface
        self._set_param(op, ZOSAPI, 2, int(cfg["par_tiltx"])) # Int2 = parameter (TiltX=3)
        self._set_target_weight(op, ZOSAPI, target=cfg["beta_min"], weight=1.0)

        op = self._add_operand(mfe, ZOSAPI, "PMLT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_d2")))          # Int1 = surface
        self._set_param(op, ZOSAPI, 2, int(cfg["par_tiltx"])) # Int2 = parameter (TiltX=3)
        self._set_target_weight(op, ZOSAPI, target=cfg["beta_max"], weight=1.0)


        # op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVGT")
        # MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))  # Int1 = Surf
        # MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(C_min), weight=float(weight))

        # # CVLT: curvature <= C_max
        # op = MeritFunctionBuilder._add_operand(mfe, ZOSAPI, "CVLT")
        # MeritFunctionBuilder._set_param(op, ZOSAPI, 1, int(surf))  # Int1 = Surf
        # MeritFunctionBuilder._set_target_weight(op, ZOSAPI, target=float(C_max), weight=float(weight))

        op = self._add_operand(mfe, ZOSAPI, "CVGT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_mirror_1")))  # Int1 = Surf
        self._set_target_weight(op, ZOSAPI, target=float(cfg["R_1_min"]), weight=float(1))
        op = self._add_operand(mfe, ZOSAPI, "CVLT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_mirror_1")))  # Int1 = Surf
        self._set_target_weight(op, ZOSAPI, target=float(cfg["R_1_max"]), weight=float(1))

        op = self._add_operand(mfe, ZOSAPI, "CVGT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_mirror_2")))  # Int1 = Surf
        self._set_target_weight(op, ZOSAPI, target=float(cfg["R_2_min"]), weight=float(1))
        op = self._add_operand(mfe, ZOSAPI, "CVLT")
        self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_mirror_2")))  # Int1 = Surf
        self._set_target_weight(op, ZOSAPI, target=float(cfg["R_2_max"]), weight=float(1))

        if opts["avoid_shelter"] == True:
            op = self._add_operand(mfe, ZOSAPI, "PMGT")
            self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_avoid_1")))          # Int1 = surface
            self._set_param(op, ZOSAPI, 2, int(cfg["par_tilty"])) # Int2 = parameter (TiltX=3)
            self._set_target_weight(op, ZOSAPI, target=cfg["tilty_min"], weight=1.0)

            op = self._add_operand(mfe, ZOSAPI, "PMLT")
            self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_avoid_1")))          # Int1 = surface
            self._set_param(op, ZOSAPI, 2, int(cfg["par_tilty"])) # Int2 = parameter (TiltX=3)
            self._set_target_weight(op, ZOSAPI, target=cfg["tilty_max"], weight=1.0)

            op = self._add_operand(mfe, ZOSAPI, "PMGT")
            self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_avoid_2")))          # Int1 = surface
            self._set_param(op, ZOSAPI, 2, int(cfg["par_tiltz"])) # Int2 = parameter (TiltX=3)
            self._set_target_weight(op, ZOSAPI, target=cfg["tiltz_min"], weight=1.0)

            op = self._add_operand(mfe, ZOSAPI, "PMLT")
            self._set_param(op, ZOSAPI, 1, int(basicStructure.index("surf_cb_avoid_2")))          # Int1 = surface
            self._set_param(op, ZOSAPI, 2, int(cfg["par_tiltz"])) # Int2 = parameter (TiltX=3)
            self._set_target_weight(op, ZOSAPI, target=cfg["tiltz_max"], weight=1.0)
        if insert_dmfs_anchor:
            try:
                op = self._add_operand(mfe, ZOSAPI, "DMFS")
                self._set_target_weight(op, ZOSAPI, weight=0.0)
            except Exception:
                pass

class SolveConfigurator:
    def _cell_make_variable(self, cell: Any, ZOSAPI: Any) -> None:
        try:
            solve = cell.CreateSolveType(ZOSAPI.Editors.SolveType.Variable)._S_Variable
            cell.SetSolveData(solve)
        except Exception:
            if hasattr(cell, "MakeSolveType"):
                cell.MakeSolveType(ZOSAPI.Editors.SolveType.Variable)

    def _cell_make_surface_pickup(self, cell: Any, ZOSAPI: Any, *, from_surface: int, scale: float = 1.0, offset: float = 0.0) -> None:
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

    def _cell_make_pickup_chief_ray(self, lde, ZOSAPI, surf_no, surface_column, field=1, wavelength=2):
        srf = lde.GetSurfaceAt(surf_no)
        cell = srf.GetSurfaceCell(surface_column)

        # 1) 创建通用 SolveData
        sd = cell.CreateSolveType(ZOSAPI.Editors.SolveType.PickupChiefRay)

        # 2) 通过 _S_PickupChiefRay 访问派生接口，再设置 Field/Wavelength
        sd._S_PickupChiefRay.Field = int(field)
        sd._S_PickupChiefRay.Wavelength = int(wavelength)

        # 3) 写回 cell（SetSolveData 会返回 SolveStatus，建议打印出来）
        status = cell.SetSolveData(sd)
        # print("[PickupChiefRay] SetSolveData status =", status)

        # 4) 读回验证（避免“看起来没生效”）
        sd_back = cell.GetSolveData()
        # print("[PickupChiefRay] back type =", sd_back.Type, "isValid =", sd_back.IsValid)
        # print("[PickupChiefRay] back Field/Wave =",
        #     sd_back._S_PickupChiefRay.Field,
        #     sd_back._S_PickupChiefRay.Wavelength)

        return sd_back._S_PickupChiefRay

    def configure_cross_ct(self, system: Any, ZOSAPI: Any, opts: Dict[str, Any], basicStructure: list) -> None:
        lde = system.LDE
        SC = ZOSAPI.Editors.LDE.SurfaceColumn

        # def _check_fields_waves(system):
        #     sd = system.SystemData
        #     nF = sd.Fields.NumberOfFields
        #     nW = sd.Wavelengths.NumberOfWavelengths
        #     print(f"[System] NumberOfFields={nF}, NumberOfWavelengths={nW}")
        #     return nF, nW
        # _check_fields_waves(system)

        variable_cells = [
                    # (2, SC.Radius),
                    # (8, SC.Radius),
                    [basicStructure.index("surf_object"), SC.Thickness],
                    [basicStructure.index("surf_cb_d1"), SC.Thickness],
                    [basicStructure.index("surf_cb_Lout"), SC.Thickness],
                    [basicStructure.index("surf_cb_theta1"), SC.Par3],
                    [basicStructure.index("surf_cb_alpha"), SC.Par3],
                    [basicStructure.index("surf_cb_d2"), SC.Par3],
                    [basicStructure.index("surf_cb_theta2"), SC.Par3],
                    [basicStructure.index("surf_cb_imgtilt"), SC.Par3],

                    # change
                    # (6, SC.Thickness),
                ]
        if opts["symmetric"] == False:
            variable_cells.append((basicStructure.index("surf_cb_d2"), SC.Thickness))
        if opts["avoid_shelter"] == True:
            # for i in range(len(variable_cells)):
            #     if variable_cells[i][0] > 7:
            #         variable_cells[i][0] += 2
            variable_cells.append((basicStructure.index("surf_cb_avoid_1"), SC.Par4))
            variable_cells.append((basicStructure.index("surf_cb_avoid_2"), SC.Par5))
        # print(variable_cells)
        
        for surf_idx, col in variable_cells:
            try:
                s = lde.GetSurfaceAt(int(surf_idx))
                cell = s.GetSurfaceCell(col)
                self._cell_make_variable(cell, ZOSAPI)
            except Exception:
                pass

        pickup_specs = [
                    # change
                    # (6, SC.Thickness, 3, -1.0),


                    [basicStructure.index("surf_cb_d1"), SC.Par3, basicStructure.index("surf_cb_theta1"), 1.0],
                    [basicStructure.index("surf_cb_Lout"), SC.Par3, basicStructure.index("surf_cb_theta2"), 1.0],
                ]
        if opts["move_grating"] != 0:
            pickup_specs.append((basicStructure.index("surf_cb_move_2"), SC.Par2, basicStructure.index("surf_cb_move_1"), -1.0))

        if opts["symmetric"] == True:
            pickup_specs.append((basicStructure.index("surf_cb_d2"), SC.Thickness, basicStructure.index("surf_cb_d1"), -1.0))

        # if opts["avoid_shelter"] == True:
        #     for i in range(len(pickup_specs)):
        #         if pickup_specs[i][0] > 7:
        #             pickup_specs[i][0] += 2
            
        for surf_idx, col, from_surf, scale in pickup_specs:
            try:
                s = lde.GetSurfaceAt(int(surf_idx))
                cell = s.GetSurfaceCell(col)
                self._cell_make_surface_pickup(cell, ZOSAPI, from_surface=int(from_surf), scale=float(scale), offset=0.0)
            except Exception:
                pass

        if True:

            self._cell_make_pickup_chief_ray(lde, ZOSAPI, surf_no=basicStructure.index("surf_cb_imgtilt"), surface_column=SC.Par2, field=1, wavelength=2)

class LDEBuilder:
    def _ensure_surfaces(self, system: Any, n_surfaces: int):
        lde = system.LDE
        current = lde.NumberOfSurfaces
        if current > n_surfaces:
            lde.RemoveSurfacesAt(1, current - n_surfaces)
            current = lde.NumberOfSurfaces
        while current < n_surfaces:
            lde.InsertNewSurfaceAt(current - 1)
            current = lde.NumberOfSurfaces
        return lde
    
    def _set_cb_movey(self, surface: Any, ZOSAPI: Any, move_y: float) -> None:
        cell = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par2)
        cell.DoubleValue = float(move_y)

    def _set_cb_tiltx(self, surface: Any, ZOSAPI: Any, tilt_x_deg: float) -> None:
        cell = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par3)
        cell.DoubleValue = float(tilt_x_deg)

    def _set_cb_tilty(self, surface: Any, ZOSAPI: Any, tilt_x_deg: float) -> None:
        cell = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par4)
        cell.DoubleValue = float(tilt_x_deg)
    
    def _set_cb_tiltz(self, surface: Any, ZOSAPI: Any, tilt_x_deg: float) -> None:
        cell = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par5)
        cell.DoubleValue = float(tilt_x_deg)
        
    def _set_grating(self, surface: Any, ZOSAPI: Any, *, lines_per_um: float, order: int) -> None:
        par1 = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par1)
        par2 = surface.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par2)
        par1.DoubleValue = float(lines_per_um)
        par2.DoubleValue = float(order)

    def build_cross_ct_like_base0(self, system: Any, ZOSAPI: Any, p: Dict[str, Any], opts: Dict[str, Any], basicStructure: list) -> None:
        """Replicates the base0 print-surface sequence (12 surfaces)."""

        handleAngle = ComputeForZemax()
        # lde = LDEBuilder._ensure_surfaces(system, 12)
        layer_quantity = len(basicStructure)
            
        lde = self._ensure_surfaces(system, layer_quantity)
        
        spec_type = p["spec_type"]

        # num = 0
        # Surface 0: object thickness = L_in
        s0 = lde.GetSurfaceAt(basicStructure.index("surf_object"))
        s0.Thickness = float(p["L_in"])
        s0.Comment = "光源"
        # num += 1

        # Surface 1: coordinate break; tilt x = theta_1
        s1 = lde.GetSurfaceAt(basicStructure.index("surf_cb_theta1"))
        s1.ChangeType(s1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        self._set_cb_tiltx(s1, ZOSAPI, p["theta_1"])
        s1.Comment = "准直镜倾斜theta1"
        # num += 1

        # Surface 2: mirror, radius = -R1
        s2 = lde.GetSurfaceAt(basicStructure.index("surf_cb_mirror_1"))
        s2.Radius = -float(p["R_1"])
        s2.Material = "MIRROR"
        s2.Comment = "准直镜"
        s2.IsStop = True
        # s.TypeData.IsStop = True
        if opts["real_size"] == True:
            # set size
            s2.SemiDiameter = p["semi_mirror_1"]
            # print(s2.DrawData.MirrorSubstrate.GetType().FullName)

            # dd = s2.DrawData
            # t = dd.GetType()
            # print("DrawData runtime type:", t.FullName)

            # props = [p.Name for p in t.GetProperties()]
            # for name in props:
            #     if "Substrate" in name or "Thick" in name:
            #         print("  ", name)

            s2.DrawData.MirrorSubstrate = ZOSAPI.Editors.LDE.SubstrateType.Flat
            s2.DrawData.MirrorThickness = float(p["thickness_mirror_1"])


            ap = s2.ApertureData.CreateApertureTypeSettings(
                ZOSAPI.Editors.LDE.SurfaceApertureTypes.CircularAperture
            )
            # ap.MaximumRadius = p["semi_mirror_1"]
            s2.ApertureData.ChangeApertureTypeSettings(ap)
        if opts["move_mirror_1"] != 0:
            s2_1 = lde.GetSurfaceAt(basicStructure.index("move_mirror_1_move"))
            # move_mirror_1_move
            s2_1.ChangeType(s2_1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
            s2_1.Comment = "移动准直镜"
            self._set_cb_movey(s2_1, ZOSAPI, opts["move_mirror_1"])

        # Surface 3: coordinate break; thickness = -d1; tilt x = theta_1
        s3 = lde.GetSurfaceAt(basicStructure.index("surf_cb_d1"))
        s3.ChangeType(s3.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s3.Thickness = -float(p["d_1"])
        s3.Comment = "设置准直镜和光栅间距，抵消theta1"
        self._set_cb_tiltx(s3, ZOSAPI, p["theta_1"])
        # num += 1

        # Surface 4: coordinate break; tilt x = ±alpha
        s4 = lde.GetSurfaceAt(basicStructure.index("surf_cb_alpha"))
        s4.ChangeType(s4.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s4.Comment = "光栅入射角"
        alpha_deg = float(handleAngle.radian_to_angle(p["alpha_rad"]))
        self._set_cb_tiltx(s4, ZOSAPI, +alpha_deg if spec_type == "交叉型" else -alpha_deg)
        # num += 1

        if opts["move_grating"] != 0:
            s4_1 = lde.GetSurfaceAt(basicStructure.index("surf_cb_move_1"))
            s4_1.ChangeType(s4_1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
            s4_1.Comment = "平移光栅"
            self._set_cb_movey(s4_1, ZOSAPI, -opts["move_grating"])

        # Surface 5: diffraction grating (stop)
        s5 = lde.GetSurfaceAt(basicStructure.index("surf_grating"))
        s5.ChangeType(s5.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.DiffractionGrating))
        s5.Material = "MIRROR"
        s5.Comment = "光栅"

        if opts["real_size"] == True:
            # set size
            s5.SemiDiameter = p["semi_grating"]
            s5.DrawData.MirrorSubstrate = ZOSAPI.Editors.LDE.SubstrateType.Flat
            s5.DrawData.MirrorThickness = float(p["thickness_grating"])

            ap = s5.ApertureData.CreateApertureTypeSettings(
                ZOSAPI.Editors.LDE.SurfaceApertureTypes.RectangularAperture
            )._S_RectangularAperture
            ap.XHalfWidth = p["semi_grating"]
            ap.YHalfWidth = p["semi_grating"]
            # 提交更改
            ok = s5.ApertureData.ChangeApertureTypeSettings(ap)
            # print(ap.GetType().GetProperty("XHalfWidth"))
            # print(ap.GetType().FullName)


        lines_per_um = float(p["f"]) / 1000.0
        order = int(+p["k"]) if spec_type == "交叉型" else int(-p["k"])
        if opts["exchange_angle"] == True:
            order = - order
        self._set_grating(s5, ZOSAPI, lines_per_um=lines_per_um, order=order)
        # num += 1

        if opts["move_grating"] != 0:
            s5_1 = lde.GetSurfaceAt(basicStructure.index("surf_cb_move_2"))
            s5_1.ChangeType(s5_1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
            s5_1.Comment = "平移光栅"
            self._set_cb_movey(s5_1, ZOSAPI, opts["move_grating"])

        # Surface 6: coordinate break; thickness=d2; tilt x = ±beta
        s6 = lde.GetSurfaceAt(basicStructure.index("surf_cb_d2"))
        s6.ChangeType(s6.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s6.Thickness = float(p["d_2"])
        s6.Comment = "光栅汇聚镜距离，光栅衍射角"
        beta_deg = float(handleAngle.radian_to_angle(p["beta_rad"]))
        self._set_cb_tiltx(s6, ZOSAPI, +beta_deg if spec_type == "交叉型" else -beta_deg)
        # num += 1

        # Surface 7: coordinate break; tilt x = theta_2
        s7 = lde.GetSurfaceAt(basicStructure.index("surf_cb_theta2"))
        s7.ChangeType(s7.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s7.Comment = "汇聚镜倾斜theta2"
        self._set_cb_tiltx(s7, ZOSAPI, float(handleAngle.radian_to_angle(p["theta_2_rad"])))
        # num += 1

        # Surface 7_1: coordinate break; tilt y = 6
        if opts["avoid_shelter"] == True:
            s7_1 = lde.GetSurfaceAt(basicStructure.index("surf_cb_avoid_1"))
            s7_1.ChangeType(s7_1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
            s7_1.Comment = "引入第三维度避免碰撞"
            self._set_cb_tilty(s7_1, ZOSAPI, float(6))
            # num += 1

        # Surface 8: mirror, radius = -R2
        s8 = lde.GetSurfaceAt(basicStructure.index("surf_cb_mirror_2"))
        s8.Radius = -float(p["R_2"])
        s8.Material = "MIRROR"
        s8.Comment = "汇聚镜"
        if opts["real_size"] == True:
            # set size
            s8.SemiDiameter = p["semi_mirror_2"]
            s8.DrawData.MirrorSubstrate = ZOSAPI.Editors.LDE.SubstrateType.Flat
            s8.DrawData.MirrorThickness = float(p["thickness_mirror_2"])

            ap = s8.ApertureData.CreateApertureTypeSettings(
                ZOSAPI.Editors.LDE.SurfaceApertureTypes.CircularAperture
            )
            # ap.MaximumRadius = p["semi_mirror_2"]
            s8.ApertureData.ChangeApertureTypeSettings(ap)
        # num += 1

        # Surface 8_1: coordinate break; tilt z = 6
        if opts["avoid_shelter"] == True:
            s8_1 = lde.GetSurfaceAt(basicStructure.index("surf_cb_avoid_2"))
            s8_1.ChangeType(s8_1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
            s8_1.Comment = "引入第三维度避免碰撞"
            self._set_cb_tiltz(s8_1, ZOSAPI, float(6))
            # num += 1

        # Surface 9: coordinate break; thickness = -L_out; tilt x = theta_2
        s9 = lde.GetSurfaceAt(basicStructure.index("surf_cb_Lout"))
        s9.ChangeType(s9.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s9.Thickness = -float(p["L_out"])
        s9.Comment = "抵消汇聚镜转角theta2，汇聚镜像面距离"
        self._set_cb_tiltx(s9, ZOSAPI, float(handleAngle.radian_to_angle(p["theta_2_rad"])))
        # num += 1

        # Surface 10: coordinate break; image tilt preset
        s10 = lde.GetSurfaceAt(basicStructure.index("surf_cb_imgtilt"))
        s10.ChangeType(s10.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak))
        s10.Comment = "修正像面位置和角度"
        self._set_cb_tiltx(s10, ZOSAPI, -4.0)

        self._set_cb_movey(s10, ZOSAPI, -1.5) # important 17

        s11 = lde.GetSurfaceAt(basicStructure.index("surf_image"))
        if opts["real_size"] == True:
            # set size
            s11.SemiDiameter = p["L_sensor"]
            
            ap = s11.ApertureData.CreateApertureTypeSettings(
                ZOSAPI.Editors.LDE.SurfaceApertureTypes.RectangularAperture
            )._S_RectangularAperture
            ap.XHalfWidth = p["W_sensor"]
            ap.YHalfWidth = p["L_sensor"]
            # 提交更改
            ok = s11.ApertureData.ChangeApertureTypeSettings(ap)


class ZemaxHandle:
    """Load ZOS-API assemblies and connect to OpticStudio."""

    def _load_zosapi(self):
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

    def connect(self, *, mode: str = "extension", instance_id: int = 0):
        ZOSAPI = self._load_zosapi()
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
    
    def configure_light(
        self,
        system: Any,
        ZOSAPI: Any,
        *,
        na_obj: float = 0.125,
        fields_x: Tuple[float, ...] = (-0.3, 0.0, 0.3),
        wavelengths_um: Tuple[float, float, float] = (1.0, 1.3, 1.6),
    ) -> None:
        sd = system.SystemData

        wavelengths_um = list(wavelengths_um) # important 110
        wavelengths_um.append(wavelengths_um[0] + (wavelengths_um[2]-wavelengths_um[0])/1024)
        wavelengths_um.append(wavelengths_um[1] - (wavelengths_um[2]-wavelengths_um[0])/1024)
        wavelengths_um.append(wavelengths_um[1] + (wavelengths_um[2]-wavelengths_um[0])/1024)
        wavelengths_um.append(wavelengths_um[2] - (wavelengths_um[2]-wavelengths_um[0])/1024)
        # print(wavelengths_um[2], wavelengths_um[0], wavelengths_um[2]-wavelengths_um[0])
        # print((wavelengths_um[2]-wavelengths_um[0])/1024)
        # print(wavelengths_um)

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
            # ff.X = float(x)
            # ff.Y = 0.0
            ff.X = 0.0
            ff.Y = float(x) # important
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

    def configure_basic_Structure(
            self,
            basicStructure: list, 
            other_settings: Dict[str, Any],
        ):
        if other_settings["avoid_shelter"] == True:
            index_surf_cb_mirror_2 = basicStructure.index("surf_cb_mirror_2")
            basicStructure.insert(index_surf_cb_mirror_2+1, "surf_cb_avoid_2")
            basicStructure.insert(index_surf_cb_mirror_2, "surf_cb_avoid_1")
        if other_settings["move_grating"] != 0:
            index_surf_grating = basicStructure.index("surf_grating")
            basicStructure.insert(index_surf_grating+1, "surf_cb_move_2")
            basicStructure.insert(index_surf_grating, "surf_cb_move_1")
        if other_settings["move_mirror_1"] != 0:
            index_surf_cb_mirror_2 = basicStructure.index("surf_cb_mirror_1")
            basicStructure.insert(index_surf_cb_mirror_2, "move_mirror_1_move")

        return basicStructure

    def push_to_zemax(
        self,
        inputs: Dict[str, Any], 
        other_settings: Dict[str, Any],
        basicStructure: list,
        ) -> Dict[str, Any] :
    
        computeForZemax = ComputeForZemax()
        basic_parameter = computeForZemax.compute_basic_parameter(inputs, other_settings)
        micro_adjust = computeForZemax.calculate_micro_adjust()
        computeForZemax.print_info()

        app, system, ZOSAPI = self.connect(mode=other_settings["zos_mode"], instance_id=other_settings["instance_id"])
        system.New(False)
        self.configure_light(
                system,
                ZOSAPI,
                na_obj=other_settings["NA"],
                fields_x=(-0.3, 0.0, 0.3),
                wavelengths_um=(basic_parameter["lambda_1"] / 1000.0, basic_parameter["lambda_c"] / 1000.0, basic_parameter["lambda_2"] / 1000.0),
            )
        
        basicStructure = self.configure_basic_Structure(
            basicStructure,
            other_settings,
        )
        # print(basicStructure)
        
        ldeBuilder = LDEBuilder()
        ldeBuilder.build_cross_ct_like_base0(system, ZOSAPI, basic_parameter, other_settings, basicStructure)

        if other_settings["auto_set_variables_pickups"]:
            solveConfigurator = SolveConfigurator()
            solveConfigurator.configure_cross_ct(system, ZOSAPI, other_settings, basicStructure)

        if other_settings["auto_configure_mfe"]:
            meritFunctionBuilder = MeritFunctionBuilder()
            meritFunctionBuilder.configure_cross_ct(
                system,
                ZOSAPI,
                clear_existing=True,
                start_row=1,
                insert_dmfs_anchor=not other_settings["auto_run_optimization_wizard"],
                cfg=micro_adjust,
                p=basic_parameter,
                opts=other_settings,
                basicStructure=basicStructure,
            )

        if other_settings["auto_run_optimization_wizard"]:
            try:
                if other_settings["wizard_start_row"] is None:
                    try:
                        start_row = int(system.MFE.NumberOfOperands) + 1
                    except Exception:
                        start_row = 1
                else:
                    start_row = int(other_settings["wizard_start_row"])
                    
                seqOptimizationWizard = SeqOptimizationWizard()
                wizard_applied = seqOptimizationWizard.run_spotdiagram(
                    system,
                    ZOSAPI,
                    start_row=start_row,
                    spot_mode=str(other_settings["wizard_spot_mode"]),
                    x_weight=float(other_settings["wizard_x_weight"]),
                    ignore_lateral_color=bool(other_settings["wizard_ignore_transverse_error"]),
                    verbose=False,
                )
            except Exception:
                wizard_applied = False

            if (not wizard_applied):
                raise RuntimeError(
                    "Optimization Wizard 自动写入失败：可能是当前 ZOS-API 版本未暴露向导接口或属性名不匹配。"
                )
        
        return basic_parameter, micro_adjust

class ComputeForZemax:
    def compute_center_wavelength(self, lambda_1, lambda_2):
        return (lambda_1 + lambda_2) / 2
    def angle_to_radian(self, angle_deg):
        return angle_deg * (pi / 180)
    def radian_to_angle(self, angle_rad):
        return angle_rad * (180 / pi)
    def compute_correct_Phi(self, Phi):
        return self.angle_to_radian(Phi)
    def compute_alpha(self, lambda_c, f, k, Phi_rad):
        return asin(10 ** (-6) * k * f * lambda_c / 2 / cos(Phi_rad / 2)) + Phi_rad / 2
    # def compute_alpha(self, lambda_c, f, k, Phi_rad):
    #     val = 1e-6 * k * f * lambda_c / (2.0 * sin(Phi_rad / 2.0))
    #     val = max(-1.0, min(1.0, val))  # clamp
    #     return Phi_rad / 2.0 + acos(val)   # 分支1：alpha >= Phi/2
    def compute_beta(self, alpha_rad, Phi_rad):
        return Phi_rad - alpha_rad
    def compute_beta_known_f1_f2(self, L_sensor, k, f, lambda_2, lambda_1):
        return acos((k * f * (lambda_2 - lambda_1))/(10**6)/L_sensor)
    def compute_L_out(self, L_sensor, beta_rad, k, f, lambda_2, lambda_1):
        return L_sensor * cos(beta_rad) * (10 ** 6) / (k * f * (lambda_2 - lambda_1))
    def compute_L_in(self, L_out, alpha_rad, beta_rad, M):
        return L_out * cos(alpha_rad) / (cos(beta_rad) * M)
    def compute_theta_2(self, theta_1_rad, alpha_rad, beta_rad, M):
        return atan(M ** 2 * tan(theta_1_rad) * cos(alpha_rad) / cos(beta_rad))
    def compute_R_1(self, L_in, theta_1_rad):
        return 2 * L_in / cos(theta_1_rad)
    def compute_R_2(self, L_out_rad, theta_2_rad):
        return 2 * L_out_rad / cos(theta_2_rad)
    def compute_d_1(self, R_1):
        return R_1 * (1 - 1 / sqrt(3))
    def compute_d_2(self, R_2):
        return R_2 * (1 - 1 / sqrt(3))
    def compute_R_1_known_f1_f2(self, F_1):
        return F_1 * 2
    def compute_R_2_known_f1_f2(self, F_2):
        return F_2 * 2
    def compute_L_out_known_f1_f2(self, theta_2_rad, R_2):
        return R_2 * cos(theta_2_rad) / 2
    def compute_L_in_known_f1_f2(self, theta_1_rad, R_1):
        return R_1 * cos(theta_1_rad) / 2
    def compute_semi_need(self, value):
        real_size_list = [(12.7, 3.2, 6), (25.4, 6.8, 6), (50.8, 10.6, 9.5), (75, 12.0, 0)]
        for size in real_size_list:
            if value*2 <= size[0]:
                return size[0] / 2, size[1], size[2]
            
    
    def compute_basic_parameter(self, inputs: Dict[str, Any], other_settings: Dict[str, Any]) -> Dict[str, Any]:
        self.lambda_1 = float(inputs["lambda_1_nm"])
        self.lambda_2 = float(inputs["lambda_2_nm"])
        self.f = float(inputs["grating_lines_per_mm"])
        self.k = float(inputs["diffraction_order"])
        self.Phi = float(inputs["Phi_deg"])
        self.L_sensor = float(inputs["sensor_length_mm"])
        self.M = float(inputs["magnification"])
        self.theta_1 = float(inputs["theta_1_deg"])
        self.F_1 = float(inputs["f_coll_mm"])
        self.F_2 = float(inputs["f_cam_mm"])

        self.semi_mirror_1 = float(inputs["semi_mirror_1"])
        self.semi_grating = float(inputs["semi_grating"])
        self.semi_mirror_2 = float(inputs["semi_mirror_2"])

        self.lambda_c = self.compute_center_wavelength(self.lambda_1, self.lambda_2)
        self.Phi_rad = self.compute_correct_Phi(self.Phi)
        self.theta_1_rad = self.angle_to_radian(self.theta_1)

        # self.alpha_rad = self.compute_alpha(self.lambda_c, self.f, self.k, self.Phi_rad)
        # self.beta_rad = self.compute_beta(self.alpha_rad, self.Phi_rad)
        
        if other_settings["exchange_angle"] == False:
            self.alpha_rad = self.compute_alpha(self.lambda_c, self.f, self.k, self.Phi_rad)
            self.beta_rad = self.compute_beta(self.alpha_rad, self.Phi_rad)
        else:
            self.beta_rad = self.compute_alpha(self.lambda_c, self.f, self.k, self.Phi_rad)
            self.alpha_rad = self.compute_beta(self.beta_rad, self.Phi_rad)

        
        # L_out = compute_L_out(L_sensor, beta_rad, k, f, lambda_2, lambda_1)
        # L_in = compute_L_in(L_out, alpha_rad, beta_rad, M)

        # theta_2_rad = compute_theta_2(theta_1_rad, alpha_rad, beta_rad, M)
        # R_1 = compute_R_1(L_in, theta_1_rad)
        # R_2 = compute_R_2(L_out, theta_2_rad)
        self.R_1 = self.compute_R_1_known_f1_f2(self.F_1)
        self.R_2 = self.compute_R_2_known_f1_f2(self.F_2)

        self.theta_2_rad = self.compute_theta_2(self.theta_1_rad, self.alpha_rad, self.beta_rad, self.M)

        self.L_out = self.compute_L_out_known_f1_f2(self.theta_2_rad, self.R_2)
        self.L_in = self.compute_L_in_known_f1_f2(self.theta_1_rad, self.R_1)

        self.d_1 = self.compute_d_1(self.R_1)
        self.d_2 = self.compute_d_2(self.R_2)

        self.semi_mirror_1, self.thickness_mirror_1, _ = self.compute_semi_need(self.semi_mirror_1)
        self.semi_grating, _, self.thickness_grating = self.compute_semi_need(self.semi_grating)
        self.semi_mirror_2, self.thickness_mirror_2, _ = self.compute_semi_need(self.semi_mirror_2)


        self.spec_type = inputs["spec_type"]
        self.f_coll_mm = inputs["f_coll_mm"]
        self.f_cam_mm = inputs["f_cam_mm"]

        return {
            "spec_type": inputs["spec_type"],
            "lambda_1": self.lambda_1,
            "lambda_2": self.lambda_2,
            "lambda_c": self.lambda_c,
            "f": self.f,
            "k": self.k,
            "Phi": self.Phi,
            "L_sensor": self.L_sensor,
            "W_sensor": inputs["sensor_width_mm"],
            "M": M,
            "theta_1": self.theta_1,
            "f_coll_mm": float(inputs["f_coll_mm"]),
            "f_cam_mm": float(inputs["f_cam_mm"]),
            "Phi_rad": self.Phi_rad,
            "theta_1_rad": self.theta_1_rad,
            "alpha_rad": self.alpha_rad,
            "beta_rad": self.beta_rad,
            "L_out": self.L_out,
            "L_in": self.L_in,
            "theta_2_rad": self.theta_2_rad,
            "R_1": self.R_1,
            "R_2": self.R_2,
            "d_1": self.d_1,
            "d_2": self.d_2,
            "semi_mirror_1": self.semi_mirror_1,
            "semi_grating": self.semi_grating,
            "semi_mirror_2": self.semi_mirror_2,
            "thickness_mirror_1": self.thickness_mirror_1,
            "thickness_grating": self.thickness_grating,
            "thickness_mirror_2": self.thickness_mirror_2,
        }
    
    def calculate_micro_adjust(self) -> Dict[str, Any]:
        self.target_Lccd_mm = self.L_sensor
        # if p.spec_type == "交叉型":
        self.Dv_min_deg = int(self.Phi - self.Phi / 10)
        self.Dv_max_deg = int(self.Phi + self.Phi / 10)
        # elif p.spec_type == "非交叉型":
            # opts.constraints_cfg.Dv_min_deg = - int(p.D_v + p.D_v / 10)
            # opts.constraints_cfg.Dv_max_deg = - int(p.D_v - p.D_v / 10)
        self.Lin_min_mm = int(self.L_in - 2)
        self.Lin_max_mm = int(self.L_in + 2)
        self.Lin_max_mm = 52 # important 18
        self.d1_min_mm = - int(self.d_1 + 2)
        # self.d1_min_mm = - 24 # important 3
        self.d1_max_mm = - int(self.d_1 - 2)
        self.d2_min_mm = int(self.d_2 - 2)
        self.d2_max_mm = int(self.d_2 + 2)
        self.Lout_min_mm = - int(self.L_out + 2)
        self.Lout_max_mm = - int(self.L_out - 2)
        self.theta1_min_deg = int(self.theta_1 - 2)
        # self.theta1_max_deg = int(self.theta_1 + 2) 
        self.theta1_max_deg = 24 # important 16
        # self.theta1_max_deg = 17 # important 5
        # self.theta1_max_deg = 19 # important 7
        # self.theta2_min_deg = int(self.radian_to_angle(self.theta_2_rad) - 2)
        self.theta2_min_deg = 14 # important 15
        self.theta2_max_deg = int(self.radian_to_angle(self.theta_2_rad) + 2)
        self.img_tilt_min_deg = - int(4 + 2)
        # self.img_tilt_min_deg = - int(8) # important 2
        self.img_tilt_min_deg = - int(8) # important 2 20
        self.img_tilt_max_deg = - int(4 - 2)
        # opts.constraints_cfg.img_tilt_min_deg = - int(1.5)
        # opts.constraints_cfg.img_tilt_max_deg = - int(- 1.5)
        if self.spec_type == "交叉型":
            self.alpha_max = int(self.Phi + self.Phi / 10)
            self.alpha_min = int(0)
            # opts.constraints_cfg.alpha_min = - int(p.Phi + p.Phi / 10)

            self.beta_max = int(self.Phi + self.Phi / 10)
            # self.beta_min = int(0)
            # self.beta_min = - 4 # important 1
            # self.beta_min = - 6.5 # important 4
            # self.beta_min = - 6.5 # important 13
            # self.beta_min = - 7 # important 18
            self.beta_min = - 9 # important 19
            # opts.constraints_cfg.beta_min = - int(p.D_v + p.D_v / 10)
        elif self.spec_type == "非交叉型":
            self.alpha_max = - int(0)
            self.alpha_min = - int(self.Phi + self.Phi / 10)
            self.beta_max = - int(0)
            self.beta_min = - int(self.Phi + self.Phi / 10)
        # --- curvature constraints for commercial mirrors (CVGT/CVLT) ---
        # In LDE: mirror Radius is set to (-R), where R>0 is the physical radius of curvature.
        # So curvature used by CVGT/CVLT is: C = 1/Radius = -1/R.
        dR = 5.0  # mm tolerance around the nominal RoC of purchased mirrors
        R1_t = 2.0 * float(inputs["f_coll_mm"])  # nominal RoC for collimator mirror
        R2_t = 2.0 * float(inputs["f_cam_mm"])   # nominal RoC for camera mirror

        self.R_1_min = -1.0 / (R1_t - dR)
        self.R_1_max = -1.0 / (R1_t + dR)
        self.R_2_min = -1.0 / (R2_t - dR)
        self.R_2_max = -1.0 / (R2_t + dR)

        self.tilty_min = 6
        self.tilty_max = 6 + 1.5

        self.tiltz_min = 6 - 1.5
        self.tiltz_max = 6 + 1.5

        return {
            "target_Lccd_mm": self.target_Lccd_mm,
            "Dv_min_deg": self.Dv_min_deg,
            "Dv_max_deg": self.Dv_max_deg,
            "Lin_min_mm": self.Lin_min_mm,
            "Lin_max_mm": self.Lin_max_mm,
            "d1_min_mm": self.d1_min_mm,
            "d1_max_mm": self.d1_max_mm,
            "d2_min_mm": self.d2_min_mm,
            "d2_max_mm": self.d2_max_mm,
            "Lout_min_mm": self.Lout_min_mm,
            "Lout_max_mm": self.Lout_max_mm,
            "theta1_min_deg": self.theta1_min_deg,
            "theta1_max_deg": self.theta1_max_deg,
            "theta2_min_deg": self.theta2_min_deg,
            "theta2_max_deg": self.theta2_max_deg,
            "img_tilt_min_deg": self.img_tilt_min_deg,
            "img_tilt_max_deg": self.img_tilt_max_deg,
            "alpha_max": self.alpha_max,
            "alpha_min": self.alpha_min,
            "beta_max": self.beta_max,
            "beta_min": self.beta_min,
            "R_1_min": self.R_1_min,
            "R_1_max": self.R_1_max,
            "R_2_min": self.R_2_min,
            "R_2_max": self.R_2_max,

            "tilty_min": self.tilty_min,
            "tilty_max": self.tilty_max,

            "tiltz_min": self.tiltz_min,
            "tiltz_max": self.tiltz_max,


            # "surf_image": 11,
            # "surf_grating": 5,
            # "surf_object": 0,
            # "surf_cb_d1": 3,
            # "surf_cb_d2": 6,
            # "surf_cb_Lout": 9,
            # "surf_cb_theta1": 1,
            # "surf_cb_theta2": 7,
            # "surf_cb_imgtilt": 10,
            "par_tiltx": 3,
            "par_tilty": 4,
            "par_tiltz": 5,
            # "surf_cb_alpha": 4,
            # "surf_cb_beta": 6,

            # "surf_cb_mirror_1": 2,
            # "surf_cb_mirror_2": 8,

            # "surf_cb_avoid_1": -1,
            # "surf_cb_avoid_2": -1,
        }
    
    def print_info(self):
        print("=================输入参数信息===================")
        print("光谱仪类型：", self.spec_type)
        print("起始波长 (nm):", self.lambda_1)
        print("终止波长 (nm):", self.lambda_2)
        print("光栅密度 (lines/mm):", self.f)
        print("衍射级别:", self.k)
        print("光栅夹角 (度):", self.Phi)
        print("传感器长度 (mm):", self.L_sensor)
        print("放大倍率:", self.M)
        print("准直镜转角 (度):", self.theta_1)
        print("准直镜标称焦距 F1 (mm):", self.f_coll_mm)
        print("汇聚镜标称焦距 F2 (mm):", self.f_cam_mm)

        print("=================输出参数信息===================")
        print("计算得到的入射角 alpha (度):", self.radian_to_angle(self.alpha_rad))
        print("计算得到的出射角 beta (度):", self.radian_to_angle(self.beta_rad))
        print("计算得到的光谱仪有效工作长度 L_out (mm):", self.L_out)
        print("计算得到的光谱仪入射光束长度 L_in (mm):", self.L_in)
        print("计算得到的会聚镜转角 theta_2 (度):", self.radian_to_angle(self.theta_2_rad))
        print("计算得到的准直镜曲率半径 R_1 (mm):", self.R_1)
        print("计算得到的会聚镜曲率半径 R_2 (mm):", self.R_2)
        print("计算得到的准直镜到光栅的距离 d_1 (mm):", self.d_1)
        print("计算得到的光栅到会聚镜的距离 d_2 (mm):", self.d_2)


if __name__ == "__main__":
    F1 = 50
    F2 = 75
    M = F2 / F1
    # M = 1.6
    # M = 1
    inputs = {
        "spec_type": "交叉型",
        "lambda_1_nm": 900,
        "lambda_2_nm": 1700,
        "grating_lines_per_mm": 600,
        "diffraction_order": 1,
        "Phi_deg": 52,
        "sensor_length_mm": 12.5*1024/1000,
        "sensor_width_mm": 125/1000,
        "magnification": M,
        "theta_1_deg": 11,
        "f_coll_mm": F1,
        "f_cam_mm": F2,

        "semi_mirror_1": 6.3 * 2, # 50 50
        "semi_grating": 6.3 * 2, # 50 50
        "semi_mirror_2": 12.6 * 2, # 50 50
    }

    other_settings = {
        "zos_mode": "extension",
        "instance_id": 0,
        "NA": 0.125, # 入射光的参数 # 50 50
        "wizard_start_row": None,
        "auto_set_variables_pickups": True, # 参数设置为变量，为了后续优化
        "auto_configure_mfe": True, # 评价函数编辑器中写入约束
        "auto_run_optimization_wizard": True, # 设置好点列图优化
        "wizard_spot_mode": "Y_ONLY", # 点列图优化只优化Y方向
        "wizard_x_weight": 0.0, # 非Y_ONLY时需要加的，没有实际意义
        "wizard_ignore_transverse_error": True, # 忽略垂轴色差，配合Y_ONLY使用的
        "avoid_shelter": False, # 错的优化方向
        "symmetric": False,
        "real_size": False,
        # "move_grating": 1.3, 
        # "move_grating": 1.95, # important 8
        "move_grating": 0, # important 11
        # "move_mirror_1": 3.0, 
        # "move_mirror_1": 2.9, # important 6
        # "move_mirror_1": 0, # important 12
        "move_mirror_1": 0, # important 14
        "exchange_angle": False,
        "change_angle_cal_way": True,
    }

    basicStructure = [
        "surf_object", # 物面
        "surf_cb_theta1", # 坐标间断，为了让准直镜旋转theta1
        "surf_cb_mirror_1", # 准直镜
        "surf_cb_d1", # 坐标间断，为了抵消准直镜旋转theta1，并设置光栅离准直镜的距离d1
        "surf_cb_alpha", # 坐标间断，设置光栅的入射角alpha
        "surf_grating", # 光栅面
        "surf_cb_d2", # 坐标间断，设置光栅出射角，并设置光栅离汇聚镜的距离d2
        "surf_cb_theta2", # 坐标间断，为了让汇聚镜旋转theta2
        "surf_cb_mirror_2", # 汇聚镜
        "surf_cb_Lout", # 坐标间断，为了抵消汇聚镜旋转theta2，并设置汇聚镜离物面的距离Lout
        "surf_cb_imgtilt", # 坐标间断，抵消计算角度误差 
        "surf_image", # 像面
    ]

    zemaxHandle = ZemaxHandle()
    zemaxHandle.push_to_zemax(
        inputs=inputs,
        other_settings=other_settings,
        basicStructure=basicStructure,
    )