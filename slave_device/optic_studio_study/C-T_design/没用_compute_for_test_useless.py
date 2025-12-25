from math import *
import numpy as np

# 计算中心波长
def compute_center_wavelength(lambda_1, lambda_2):
    return (lambda_1 + lambda_2) / 2

# 角度转换为弧度
def angle_to_radian(angle_deg):
    return angle_deg * (pi / 180)

def radian_to_angle(angle_rad):
    return angle_rad * (180 / pi)

# 计算光栅入射角alpha（弧度制）- 修正版本
def compute_alpha_correct(lambda_c_nm, f_lines_mm, k, D_v_deg):
    """
    修正的光栅入射角计算
    lambda_c_nm: 中心波长 (nm)
    f_lines_mm: 光栅刻线密度 (lines/mm)
    k: 衍射级次
    D_v_deg: 光栅两臂夹角 (度)
    返回: (alpha_rad, beta_rad)
    """
    # 转换为标准单位
    lambda_c = lambda_c_nm * 1e-9  # 转换为米
    d = 1 / (f_lines_mm * 1000)   # 光栅周期 (米)
    D_v = angle_to_radian(D_v_deg)
    
    # 正确的光栅方程: kλ = d(sinα + sinβ)
    # 对于Czerny-Turner结构，通常有: β = -(α + D_v) 或 β = D_v - α
    
    # 方法1: 使用关系 β = -(α + D_v)
    def equation1(alpha):
        beta = -(alpha + D_v)
        return k * lambda_c - d * (sin(alpha) + sin(beta))
    
    # 方法2: 使用关系 β = α - D_v (另一种常见定义)
    def equation2(alpha):
        beta = alpha - D_v
        return k * lambda_c - d * (sin(alpha) + sin(beta))
    
    # 尝试求解方法1
    try:
        # 使用数值方法求解
        # 搜索合理的alpha范围
        alpha_guesses = np.linspace(-pi/3, pi/3, 100)
        
        solutions = []
        for i in range(len(alpha_guesses)-1):
            a1, a2 = alpha_guesses[i], alpha_guesses[i+1]
            f1, f2 = equation1(a1), equation1(a2)
            
            if f1 * f2 <= 0:  # 有根
                # 二分法求解
                left, right = a1, a2
                for _ in range(50):
                    mid = (left + right) / 2
                    f_mid = equation1(mid)
                    
                    if f1 * f_mid <= 0:
                        right = mid
                        f2 = f_mid
                    else:
                        left = mid
                        f1 = f_mid
                
                alpha_sol = (left + right) / 2
                beta_sol = -(alpha_sol + D_v)
                solutions.append((alpha_sol, beta_sol))
        
        if solutions:
            # 选择绝对值较小的解
            alpha_sol, beta_sol = min(solutions, key=lambda x: abs(x[0]))
            
            # 验证解是否合理
            left_side = k * lambda_c
            right_side = d * (sin(alpha_sol) + sin(beta_sol))
            
            if abs(left_side - right_side) / left_side < 0.01:  # 1%误差内
                return alpha_sol, beta_sol
    
    except:
        pass
    
    # 如果方法1失败，尝试方法2
    try:
        alpha_guesses = np.linspace(-pi/3, pi/3, 100)
        
        solutions = []
        for i in range(len(alpha_guesses)-1):
            a1, a2 = alpha_guesses[i], alpha_guesses[i+1]
            f1, f2 = equation2(a1), equation2(a2)
            
            if f1 * f2 <= 0:
                left, right = a1, a2
                for _ in range(50):
                    mid = (left + right) / 2
                    f_mid = equation2(mid)
                    
                    if f1 * f_mid <= 0:
                        right = mid
                        f2 = f_mid
                    else:
                        left = mid
                        f1 = f_mid
                
                alpha_sol = (left + right) / 2
                beta_sol = alpha_sol - D_v
                solutions.append((alpha_sol, beta_sol))
        
        if solutions:
            alpha_sol, beta_sol = min(solutions, key=lambda x: abs(x[0]))
            
            # 验证
            left_side = k * lambda_c
            right_side = d * (sin(alpha_sol) + sin(beta_sol))
            
            if abs(left_side - right_side) / left_side < 0.01:
                return alpha_sol, beta_sol
    
    except:
        pass
    
    # 如果都失败，使用近似公式
    print("警告: 无法精确求解光栅方程，使用近似解")
    
    # 近似: 假设在中心波长处近似满足 Littrow 条件
    alpha_approx = asin(k * lambda_c / (2 * d))  # Littrow条件: α = -β
    beta_approx = -alpha_approx
    
    return alpha_approx, beta_approx

# 计算光栅衍射角（弧度制），与法线的夹角
def compute_beta(alpha_rad, D_v_rad):
    return -(alpha_rad + D_v_rad)

# 计算出射距离L_out（mm）
def compute_L_out(L_sensor, beta_rad, k, f, lambda_2, lambda_1):
    return L_sensor * cos(beta_rad) * (10**6) / (k * f * (lambda_2 - lambda_1))

# 计算入射距离L_in（mm）
def compute_L_in(L_out, alpha_rad, beta_rad, M):
    return L_out * cos(alpha_rad) / (cos(beta_rad) * M)

# 计算会聚镜转角theta_2（弧度制）
def compute_theta_2(theta_1_rad, alpha_rad, beta_rad, M):
    return atan(M**2 * tan(theta_1_rad) * cos(alpha_rad) / cos(beta_rad))

# 计算准直镜曲率半径R_1（mm）
def compute_R_1(L_in, theta_1_rad):
    return 2 * L_in / cos(theta_1_rad)

# 计算会聚镜曲率半径R_2（mm）
def compute_R_2(L_out, theta_2_rad):
    return 2 * L_out / cos(theta_2_rad)

# 计算准直镜到光栅的距离d_1（mm）
def compute_d_1(R_1):
    return R_1 * (1 - 1/sqrt(3))

# 计算光栅到会聚镜的距离d_2（mm）
def compute_d_2(R_2):
    return R_2 * (1 - 1/sqrt(3))

# 验证光栅参数
def validate_grating_params(lambda_c_nm, f_lines_mm, k, D_v_deg):
    """
    验证光栅参数是否合理
    """
    lambda_c = lambda_c_nm * 1e-9  # 米
    d = 1 / (f_lines_mm * 1000)    # 光栅周期(米)
    
    print("\n=== 光栅参数验证 ===")
    print(f"中心波长: {lambda_c_nm} nm = {lambda_c:.3e} m")
    print(f"光栅密度: {f_lines_mm} lines/mm")
    print(f"光栅周期: d = {d:.3e} m")
    print(f"kλ/d = {k * lambda_c / d:.4f}")
    
    # 光栅方程要求: |sinα + sinβ| = kλ/d ≤ 2
    max_value = k * lambda_c / d
    if max_value > 2:
        print(f"❌ 错误: kλ/d = {max_value:.3f} > 2")
        print(f"   理论最大值应为2，当前参数不满足光栅方程")
        print(f"   建议: 降低光栅密度或使用更高衍射级次")
        
        # 计算最大允许的光栅密度
        f_max = k * lambda_c * 1000 / 2  # lines/mm
        print(f"   最大允许光栅密度: {f_max:.1f} lines/mm")
        return False
    elif max_value > 1.8:
        print(f"⚠️ 警告: kλ/d = {max_value:.3f} 接近极限值2")
        print(f"   可能导致光线衍射效率低")
    else:
        print(f"✓ 通过: kλ/d = {max_value:.3f} ≤ 2")
    
    return True

if __name__ == "__main__":
    # 输入参数
    lambda_1 = 200      # nm 起始波长
    lambda_2 = 1100     # nm 终止波长
    f = 300             # lines/mm 光栅密度刻线
    k = 1               # 衍射级别
    D_v = 40            # 度 光栅夹角
    L_sensor = 28.4     # mm 传感器长度
    M = 1.15            # 放大倍率
    theta_1 = 11        # 度 准直镜转角
    
    print("=========光谱仪参数计算（修正版）=========")
    print("---------输入参数:---------")
    print(f"起始波长 (nm): {lambda_1}")
    print(f"终止波长 (nm): {lambda_2}")
    print(f"光栅密度 (lines/mm): {f}")
    print(f"衍射级别: {k}")
    print(f"光栅夹角 (度): {D_v}")
    print(f"传感器长度 (mm): {L_sensor}")
    print(f"放大倍率: {M}")
    print(f"准直镜转角 (度): {theta_1}")
    print("--------------------------")
    
    # 计算中心波长
    lambda_c = compute_center_wavelength(lambda_1, lambda_2)
    
    # 验证光栅参数
    is_valid = validate_grating_params(lambda_c, f, k, D_v)
    
    if not is_valid:
        print("\n❌ 光栅参数不合理，请调整参数后再运行")
        exit()
    
    # 转换角度
    theta_1_rad = angle_to_radian(theta_1)
    D_v_rad = angle_to_radian(D_v)
    
    # 使用修正的函数计算光栅角度
    alpha_rad, beta_rad = compute_alpha_correct(lambda_c, f, k, D_v)
    
    print("\n---------输出参数:---------")
    print(f"中心波长 (nm): {lambda_c:.1f}")
    print(f"计算得到的入射角 alpha (度): {radian_to_angle(alpha_rad):.4f}")
    print(f"计算得到的出射角 beta (度): {radian_to_angle(beta_rad):.4f}")
    
    # 验证光栅方程
    d = 1 / (f * 1000)  # 光栅周期(米)
    left_side = k * lambda_c * 1e-9
    right_side = d * (sin(alpha_rad) + sin(beta_rad))
    print(f"光栅方程验证: kλ = {left_side:.3e}, d(sinα+sinβ) = {right_side:.3e}")
    print(f"相对误差: {abs(left_side-right_side)/left_side*100:.2f}%")
    
    # 计算其他参数
    L_out = compute_L_out(L_sensor, beta_rad, k, f, lambda_2, lambda_1)
    L_in = compute_L_in(L_out, alpha_rad, beta_rad, M)
    theta_2_rad = compute_theta_2(theta_1_rad, alpha_rad, beta_rad, M)
    R_1 = compute_R_1(L_in, theta_1_rad)
    R_2 = compute_R_2(L_out, theta_2_rad)
    d_1 = compute_d_1(R_1)
    d_2 = compute_d_2(R_2)
    
    print(f"计算得到的光谱仪有效工作长度 L_out (mm): {L_out:.2f}")
    print(f"计算得到的光谱仪入射光束长度 L_in (mm): {L_in:.2f}")
    print(f"计算得到的会聚镜转角 theta_2 (度): {radian_to_angle(theta_2_rad):.4f}")
    print(f"计算得到的准直镜曲率半径 R_1 (mm): {R_1:.2f}")
    print(f"计算得到的会聚镜曲率半径 R_2 (mm): {R_2:.2f}")
    print(f"计算得到的准直镜到光栅的距离 d_1 (mm): {d_1:.2f}")
    print(f"计算得到的光栅到会聚镜的距离 d_2 (mm): {d_2:.2f}")
    
    print("\n============== Zemax光谱仪仿真指导 ================")
    print("============== 系统选项 ================")
    print("系统选项——系统孔径——孔径类型：物方空间NA；孔径值：0.125")
    print("系统选项——视场——打开视场编辑器——属性：视场类型：类型：物高；视场1：X：-0.3；视场2：X：0；视场3：X：0.3")
    print(f"系统选项——波长——设置：波长1：{lambda_1}；波长2：{lambda_c}+主波长；波长3：{lambda_2}")
    
    print("\n============== 镜片设计 ================")
    print(f"面0(物面)——厚度：{L_in:.6f}")
    print(f"面1——表面类型：坐标中断；倾斜X：{theta_1}")
    print(f"面2——表面类型：曲率半径：-{R_1:.6f}；材料：MIRROR")
    print(f"面3——表面类型：坐标中断；厚度：-{d_1:.6f}；倾斜X：{theta_1}+拾取")
    print(f"面4——表面类型：坐标中断；倾斜X：{radian_to_angle(alpha_rad):.6f}")
    print(f"面5(光阑面)——表面类型：衍射光栅；材料：MIRROR；刻线/微米：{f/1000:.6f}；衍射级次：{k}")
    print(f"面6——表面类型：坐标中断；厚度：{d_2:.6f}；倾斜X：{radian_to_angle(beta_rad):.6f}")
    print(f"面7——表面类型：坐标中断；倾斜X：{radian_to_angle(theta_2_rad):.6f}")
    print(f"面8——曲率半径：-{R_2:.6f}；材料：MIRROR")
    print(f"面9——表面类型：坐标中断；厚度：-{L_out:.6f}；倾斜X：{radian_to_angle(theta_2_rad):.6f}+拾取")
    print("面10(像面)")