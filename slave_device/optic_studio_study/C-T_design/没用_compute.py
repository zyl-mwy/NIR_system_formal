import math

alpha = 25.9556*math.pi/180
beta = -14.0444*math.pi/180
lambda_ = 650
f = 300
k = 1
D_v = beta - alpha

a = math.sin(alpha) + math.sin(beta)
b = 10**(-6) * k * f * lambda_

print(a, b)

c = math.asin(10**(-6)*k*f*lambda_/2/math.cos(D_v/2))-D_v/2
print(alpha, beta)
print(c)