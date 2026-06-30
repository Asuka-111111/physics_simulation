import numpy as np

class SpringOscillator3D:
    # 注意参数变化：初始位置和速度变成了包含3个数字的列表
    def __init__(self, mass: float, k: float, initial_pos: list, initial_vel: list):
        self.mass = mass
        self.k = k
        
        # 【核心魔法】：把普通的 Python 列表转换成 Numpy 数组
        # 比如把 [10.0, 5.0, 0.0] 变成可以进行高等数学运算的向量
        self.pos = np.array(initial_pos, dtype=float)
        self.vel = np.array(initial_vel, dtype=float)

    def update(self, dt: float) -> None:
        """
        核心物理引擎：和 1D 的代码完全一模一样！
        因为 Numpy 知道如何把一个数字(mass)和一个三维向量(self.pos)相乘。
        """
        # 计算 3D 加速度 (a_x, a_y, a_z)
        a = -(self.k / self.mass) * self.pos
        
        # 更新 3D 速度 (v_x, v_y, v_z)
        self.vel += a * dt
        
        # 更新 3D 位置 (x, y, z)
        self.pos += self.vel * dt
        
    def __str__(self) -> str:
        # np.round 保留两位小数，方便查看
        return f"3D坐标: {np.round(self.pos, 2)}, 3D速度: {np.round(self.vel, 2)}"

# --- 测试我们的 3D 引擎 ---
# 质量1.0, 弹簧系数0.5
# 初始把小球拉到坐标 (10, 5, 0) 的位置，并且给它一个沿 Z 轴的初始速度 (0, 0, 5)
oscillator_3d = SpringOscillator3D(
    mass=1.0, 
    k=0.5, 
    initial_pos=[10.0, 5.0, 0.0], 
    initial_vel=[0.0, 0.0, 5.0]
)

dt = 0.1
print("开始 3D 简谐运动模拟...")
for step in range(5):
    oscillator_3d.update(dt)
    print(f"第 {step+1:02d} 帧 | {oscillator_3d}")
