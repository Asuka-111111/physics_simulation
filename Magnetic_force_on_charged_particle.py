import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(page_title="带电粒子磁场运动模型", layout="wide")

st.title("🧲 带电粒子在匀强磁场中的运动可视化")
st.markdown("通过左侧侧边栏调节粒子的参数，观察洛伦兹力 $\mathbf{F} = q(\mathbf{v} \times \mathbf{B})$ 对粒子运动轨迹的影响。")

# 侧边栏：参数输入
st.sidebar.header("⚙️ 调节参数")

# 粒子参数
st.sidebar.subheader("粒子属性")
q = st.sidebar.slider("电荷量 q (C)", min_value=-5.0, max_value=5.0, value=1.0, step=0.5)
m = st.sidebar.slider("质量 m (kg)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# 速度参数
st.sidebar.subheader("初始速度 v (m/s)")
vx = st.sidebar.slider("X轴速度 (vx)", min_value=-10.0, max_value=10.0, value=5.0, step=0.5)
vy = st.sidebar.slider("Y轴速度 (vy)", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)
vz = st.sidebar.slider("Z轴速度 (vz)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5)

# 磁场参数 (假设磁场方向沿Z轴)
st.sidebar.subheader("磁场 B (T)")
Bz = st.sidebar.slider("Z轴磁场强度 (Bz)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5)

# 仿真时间
t_max = st.sidebar.slider("仿真总时间 (s)", min_value=1.0, max_value=20.0, value=10.0, step=1.0)

# 物理计算逻辑
# -----------------------------
# 假设粒子从原点 (0,0,0) 出发，磁场仅存在Z轴分量 (0, 0, Bz)
# 回旋频率 omega = qB / m
t = np.linspace(0, t_max, 1000)

if q == 0 or Bz == 0:
    # 不受洛伦兹力，做匀速直线运动
    x = vx * t
    y = vy * t
    z = vz * t
else:
    # 受洛伦兹力，做螺旋/圆周运动
    omega = (q * Bz) / m
    # 参数方程求解
    x = (vx / omega) * np.sin(omega * t) + (vy / omega) * (1 - np.cos(omega * t))
    y = (vx / omega) * (np.cos(omega * t) - 1) + (vy / omega) * np.sin(omega * t)
    z = vz * t

# 3D 可视化 (使用 Plotly)
# -----------------------------
fig = go.Figure()

# 绘制粒子轨迹
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines',
    name='粒子轨迹',
    line=dict(
        color='cyan',
        width=5
    )
))

# 绘制起点
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers',
    name='起点',
    marker=dict(size=8, color='red')
))

# 绘制当前终点（当前位置）
fig.add_trace(go.Scatter3d(
    x=[x[-1]], y=[y[-1]], z=[z[-1]],
    mode='markers',
    name='终点',
    marker=dict(size=8, color='yellow')
))

# 设置图表布局
fig.update_layout(
    scene=dict(
        xaxis_title='X 轴',
        yaxis_title='Y 轴',
        zaxis_title='Z 轴 (磁场方向)',
        # 强制比例一致，使得圆看起来不扁
        aspectmode='data', 
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    height=700,
    margin=dict(l=0, r=0, b=0, t=0),
    template="plotly_dark"
)

# 在 Streamlit 中渲染图表
st.plotly_chart(fig, use_container_width=True)

# 底部展示计算出的物理量
st.markdown("---")
st.subheader("📊 实时物理量")
col1, col2, col3 = st.columns(3)
if q != 0 and Bz != 0:
    radius = (m * np.sqrt(vx**2 + vy**2)) / abs(q * Bz)
    period = (2 * np.pi * m) / abs(q * Bz)
    col1.metric("回旋半径 (R)", f"{radius:.2f} m")
    col2.metric("运动周期 (T)", f"{period:.2f} s")
    col3.metric("螺距 (Pitch)", f"{vz * period:.2f} m")
else:
    col1.metric("运动状态", "匀速直线运动")
    col2.metric("加速度", "0 m/s²")
    col3.metric("受力情况", "0 N")
