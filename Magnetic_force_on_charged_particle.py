import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="动态带电粒子运动模型", layout="wide")

st.title("🧲 带电粒子在磁场中的动态运动")
st.markdown("通过左侧侧边栏调节参数，点击图表下方的 **播放 (Play)** 按钮，观察粒子的实时运动过程。")

# 侧边栏：参数输入
st.sidebar.header("⚙️ 调节参数")

# 粒子参数
q = st.sidebar.slider("电荷量 q (C)", min_value=-5.0, max_value=5.0, value=1.0, step=0.5)
m = st.sidebar.slider("质量 m (kg)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# 速度参数
vx = st.sidebar.slider("X轴初始速度 (vx)", min_value=-10.0, max_value=10.0, value=5.0, step=0.5)
vy = st.sidebar.slider("Y轴初始速度 (vy)", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)
vz = st.sidebar.slider("Z轴初始速度 (vz)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5)

# 磁场参数 (Z轴方向)
Bz = st.sidebar.slider("Z轴磁场强度 (Bz)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5)

# 仿真时间
t_max = st.sidebar.slider("仿真总时间 (s)", min_value=1.0, max_value=20.0, value=10.0, step=1.0)

# --- 物理计算逻辑 ---
# 为了保证网页端动画流畅度，将数据点控制在 150 个左右
num_points = 150
t = np.linspace(0, t_max, num_points)

if q == 0 or Bz == 0:
    x = vx * t
    y = vy * t
    z = vz * t
else:
    omega = (q * Bz) / m
    x = (vx / omega) * np.sin(omega * t) + (vy / omega) * (1 - np.cos(omega * t))
    y = (vx / omega) * (np.cos(omega * t) - 1) + (vy / omega) * np.sin(omega * t)
    z = vz * t

# --- 3D 动画可视化 (使用 Plotly Frames) ---
fig = go.Figure()

# 1. 初始化图表 (初始状态的轨迹和粒子位置)
fig.add_trace(go.Scatter3d(
    x=[x[0]], y=[y[0]], z=[z[0]],
    mode='lines',
    name='运动轨迹',
    line=dict(color='cyan', width=5)
))

fig.add_trace(go.Scatter3d(
    x=[x[0]], y=[y[0]], z=[z[0]],
    mode='markers',
    name='带电粒子',
    marker=dict(size=8, color='yellow')
))

# 2. 生成动画帧
frames = []
for i in range(1, num_points):
    frames.append(go.Frame(
        data=[
            # 更新轨迹线 (从0到当前时刻 i)
            go.Scatter3d(x=x[:i+1], y=y[:i+1], z=z[:i+1]),
            # 更新粒子当前位置 (时刻 i)
            go.Scatter3d(x=[x[i]], y=[y[i]], z=[z[i]])
        ],
        name=f'frame{i}'
    ))
fig.frames = frames

# 3. 设置布局和播放控件
# 计算坐标轴的固定范围，防止动画播放时坐标轴跳动
max_range = max(np.max(np.abs(x)), np.max(np.abs(y)), np.max(np.abs(z)))
axis_range = [-max_range - 1, max_range + 1]

fig.update_layout(
    scene=dict(
        xaxis=dict(range=axis_range, title='X 轴'),
        yaxis=dict(range=axis_range, title='Y 轴'),
        zaxis=dict(range=axis_range, title='Z 轴'),
        aspectmode='cube',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
    ),
    height=750,
    margin=dict(l=0, r=0, b=0, t=0),
    template="plotly_dark",
    # 添加播放和暂停按钮
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        x=0.1, y=0, xanchor="right", yanchor="top",
        buttons=[
            dict(label="▶ 播放",
                 method="animate",
                 args=[None, dict(frame=dict(duration=50, redraw=True), 
                                  transition=dict(duration=0),
                                  fromcurrent=True,
                                  mode="immediate")]),
            dict(label="⏸ 暂停",
                 method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), 
                                    mode="immediate")])
        ]
    )]
)

# 在 Streamlit 中渲染带有动画的图表
st.plotly_chart(fig, use_container_width=True)

# 底部展示计算出的物理量
st.markdown("---")
st.subheader("📊 物理参数解析")
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
