class SpringOscillator:
    def __init__(self, mass: float, k: float, initial_x: float):
        # 物理常数（不变的属性）
        self.mass = mass  # 质量
        self.k = k        # 弹簧劲度系数
        
        # 状态变量（随着时间不断变化的属性）
        self.x = initial_x  # 初始位置（比如把弹簧拉开 5 米）
        self.v = 0.0        # 初始速度为 0（松手瞬间没速度）

    def update(self, dt: float) -> None:
        """
        核心物理引擎：根据经过的时间片段 dt，更新小球的状态
        """
        # 1. 根据当前位置计算加速度: a = -(k/m) * x
        a = -(self.k / self.mass) * self.x
        
        # 2. 更新速度: 新速度 = 老速度 + 加速度 * 时间
        self.v += a * dt
        
        # 3. 更新位置: 新位置 = 老位置 + 速度 * 时间
        self.x += self.v * dt
        
    def __str__(self) -> str:
        # 利用魔术方法，方便我们随时打印查看小球状态
        return f"位移: {self.x: .2f} m, 速度: {self.v: .2f} m/s"

# 1. 创造一个具体的小球：质量1.0kg，弹簧系数0.5，初始拉开10米
oscillator = SpringOscillator(mass=1.0, k=0.5, initial_x=10.0)

# 2. 设定时间步长 dt（比如每 0.1 秒刷新一次）
dt = 0.1

# 3. 模拟前 20 帧的过程
print("开始模拟简谐运动...")
for step in range(20):
    oscillator.update(dt) # 时间往前走了一步，小球状态改变！
    
    # 打印当前帧的状态
    print(f"第 {step+1:02d} 帧 | {oscillator}")
