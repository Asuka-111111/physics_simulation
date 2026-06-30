import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# 1. 保持你原汁原味的 3D 物理引擎类
class SpringOscillator3D:
    def __init__(self, mass: float, k: float, initial_pos: list, initial_vel: list):
        self.mass = mass
        self.k = k
        self.pos = np.array(initial_pos, dtype=float)
        self.vel = np.array(initial_vel, dtype=float)

    def update(self, dt: float) -> None:
        a = -(self.k / self.mass) * self.pos
        self.vel += a * dt
        self.pos += self.vel * dt

# 网页标题和说明
st.title("3D 弹簧振子交互仿真模型 🌌")
st.write("利用 Plotly 3D 动画和 Streamlit 实现。在左侧调节物理参数，点击图表下方的 **Play** 观看 3D 运动轨迹。")

# 2. 侧边栏交互：让用户能随时调节参数
st.sidebar.header("🛠️ 调节物理参数")
mass = st.sidebar.slider("小球质量 (mass)", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
k = st.sidebar.slider("弹簧劲度系数 (k)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)

st.sidebar.subheader("📍 初始位置 (X, Y, Z)")
init_x = st.sidebar.slider("初始 X", -15.0, 15.0, 10.0, 1.0)
init_y = st.sidebar.slider("初始 Y", -15.0, 15.0, 5.0, 1.0)
init_z = st.sidebar.slider("初始 Z", -15.0, 15.0, 0.0, 1.0)

st.sidebar.subheader("🚀 初始速度 (Vx, Vy, Vz)")
init_vx = st.sidebar.slider("初始 Vx", -5.0, 5.0, 0.0, 0.5)
init_vy = st.sidebar.slider("初始 Vy", -5.0, 5.0, 0.0, 0.5)
init_vz = st.sidebar.slider("初始 Vz", -5.0, 5.0, 5.0, 0.5)

# 3. 预计算仿真数据
# 实例化你的 3D 引擎，传入滑块实时获取的参数
oscillator = SpringOscillator3D(
    mass=mass, 
    k=k, 
    initial_pos=[init_x, init_y, init_z], 
    initial_vel=[init_vx, init_vy, init_vz]
)

dt = 0.1
total_frames = 150  # 总共模拟 150 帧，形成一个连续的动画

# 循环运行物理引擎，并一次性记录每一帧的数据
data_list = []
for step in range(total_frames):
    oscillator.update(dt)
    data_list.append({
        "X": oscillator.pos[0],
        "Y": oscillator.pos[1],
        "Z": oscillator.pos[2],
        "时间帧": step,
        "物体": "小球"
    })

# 转换为 Pandas DataFrame
df_animation = pd.DataFrame(data_list)

# 4. 生成 Plotly 3D 动画图表
fig = px.scatter_3d(
    df_animation,
    x="X", y="Y", z="Z",
    animation_frame="时间帧", # 告诉 Plotly 按照这一列逐帧播放
    range_x=[-20, 20],        # 固定 3D 坐标轴范围，防止播放时镜头乱晃
    range_y=[-20, 20],
    range_z=[-20, 20],
    title="3D 空间内的简谐运动轨迹"
)

# 调整 3D 样式，让小球更明显，并加上中心原点参考
fig.update_traces(marker=dict(size=10, symbol="circle"))
fig.update_layout(
    scene=dict(
        xaxis_title='X 轴',
        yaxis_title='Y 轴',
        zaxis_title='Z 轴'
    )
)

# 5. 将 3D 交互图表渲染到网页
st.plotly_chart(fig, use_container_width=True)
