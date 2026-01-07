from math import *
# 计算中心波长
def compute_center_wavelength(lambda_1, lambda_2):
    return (lambda_1 + lambda_2) / 2
# 角度转换为弧度
def angle_to_radian(angle_deg):
    return angle_deg * (pi / 180)
def radian_to_angle(angle_rad):
    return angle_rad * (180 / pi)
# 计算修正后的光栅夹角（弧度制）
def compute_correct_D_v(D_v):
    return angle_to_radian(D_v) # 转换为弧度 !!!
# 计算光栅入射角alpha（弧度制），与法线的夹角
def compute_alpha(lambda_c, f, k, D_v_rad):
    return asin(10**(-6)*k*f*lambda_c/2/cos(D_v_rad/2))+D_v_rad/2
# 计算光栅衍射角（弧度制），与法线的夹角
def compute_beta(alpha_rad, D_v_rad):
    return D_v_rad - alpha_rad
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
def compute_R_2(L_out_rad, theta_2_rad):
    return 2 * L_out_rad / cos(theta_2_rad)
# 计算准直镜到光栅的距离d_1（mm）
def compute_d_1(R_1):
    return R_1 * (1-1/sqrt(3))
# 计算光栅到会聚镜的距离d_2（mm）
def compute_d_2(R_2):
    return R_2 * (1-1/sqrt(3))
def compute_R_1_known_f1_f2(F_1):
        return F_1 * 2
    
def compute_R_2_known_f1_f2(F_2):
    return F_2 * 2

def compute_L_out_known_f1_f2(theta_2_rad, R_2):
    return R_2 * cos(theta_2_rad) / 2

def compute_L_in_known_f1_f2(theta_1_rad, R_1):
    return R_1 * cos(theta_1_rad) / 2

def compute_theta_2_known_f1_f2(L_out, R_2):
    return acos(2*L_out/R_2)

def compute_theta_1_known_f1_f2(L_in, R_1):
    return acos(2*L_in/R_1)

if __name__ == "__main__":
    spec_type = '非交叉型' # 非交叉型 交叉型
    lambda_1 = 200 # nm 起始波长
    lambda_2 = 1100 # nm 终止波长

    lambda_1 = 1000 # nm 起始波长
    lambda_2 = 1600 # nm 终止波长
    
    f = 300 # lines/mm 光栅密度刻线
    k = 1 # 衍射级别
    D_v = 40 # 度 光栅夹角
    L_sensor = 28.4 # mm 传感器长度
    M = 1.15 # 放大倍率 一般是 [1, 1.25]
    theta_1 = 11 # 度 准直镜转角 一般是 [8, 12]
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

    lambda_c = compute_center_wavelength(lambda_1, lambda_2)
    D_v_rad = compute_correct_D_v(D_v)
    theta_1_rad = angle_to_radian(theta_1)
    # print("中心波长 (nm):", lambda_c)


    alpha_rad = compute_alpha(lambda_c, f, k, D_v_rad)
    beta_rad = compute_beta(alpha_rad, D_v_rad)
    L_out = compute_L_out(L_sensor, beta_rad, k, f, lambda_2, lambda_1)
    L_in = compute_L_in(L_out, alpha_rad, beta_rad, M)
    theta_2_rad = compute_theta_2(theta_1_rad, alpha_rad, beta_rad, M)
    R_1 = compute_R_1(L_in, theta_1_rad)
    R_2 = compute_R_2(L_out, theta_2_rad)
    d_1 = compute_d_1(R_1)
    d_2 = compute_d_2(R_2)
    print("---------输出参数:---------")
    print("计算得到的入射角 alpha (度):", radian_to_angle(alpha_rad))
    print("计算得到的出射角 beta (度):", radian_to_angle(beta_rad))
    print("计算得到的光谱仪有效工作长度 L_out (mm):", L_out)
    print("计算得到的光谱仪入射光束长度 L_in (mm):", L_in)
    print("计算得到的会聚镜转角 theta_2 (度):", radian_to_angle(theta_2_rad))
    print("计算得到的准直镜曲率半径 R_1 (mm):", R_1)
    print("计算得到的会聚镜曲率半径 R_2 (mm):", R_2)
    print("计算得到的准直镜到光栅的距离 d_1 (mm):", d_1)
    print("计算得到的光栅到会聚镜的距离 d_2 (mm):", d_2)

    print("==============zemax光谱仪仿真指导================")
    print("==============系统选项================")
    print("系统选项——系统孔径——孔径类型：物方空间NA；孔径值：0.125")
    print("系统选项——视场——打开视场编辑器——属性：视场类型：类型：物高；视场1：X：-0.3；视场2：X：0；视场3：X：0.3")
    print("系统选项——波长——设置：波长1："+str(lambda_1/1000)+"微米；波长2："+str(lambda_c/1000)+"微米+主波长；波长3："+str(lambda_2/1000)+"微米")
    print("==============镜片设计================")
    print("面0(物面)——厚度："+str(L_in))
    print("面1——表面类型：坐标中断；倾斜X："+str(theta_1))
    print("面2——曲率半径：-"+str(R_1)+"；材料：MIRROR")
    print("面3——表面类型：坐标中断；厚度：-"+str(d_1)+"；倾斜X："+str(theta_1)+"+拾取")
    if spec_type == "交叉型":
        print("面4——表面类型：坐标中断；倾斜X："+str(radian_to_angle(alpha_rad)))
        print("面5(光阑面)——表面类型：衍射光栅；材料：MIRROR；刻线/微米："+str(f/1000)+"；衍射级次："+str(k))
        print("面6——表面类型：坐标中断；厚度："+str(d_2)+"；倾斜X："+str(radian_to_angle(beta_rad)))
    elif spec_type == "非交叉型":
        print("面4——表面类型：坐标中断；倾斜X：-"+str(radian_to_angle(alpha_rad)))
        print("面5(光阑面)——表面类型：衍射光栅；材料：MIRROR；刻线/微米："+str(f/1000)+"；衍射级次：-"+str(k))
        print("面6——表面类型：坐标中断；厚度："+str(d_2)+"；倾斜X：-"+str(radian_to_angle(beta_rad)))
    print("面7——表面类型：坐标中断；倾斜X："+str(radian_to_angle(theta_2_rad)))
    print("面8——曲率半径：-"+str(R_2)+"；材料：MIRROR")
    print("面9——表面类型：坐标中断；厚度：-"+str(L_out)+"；倾斜X："+str(radian_to_angle(theta_2_rad))+"+拾取")
    print("面10——表面类型：坐标中断；倾斜X：-4")
    print("面10(像面)")