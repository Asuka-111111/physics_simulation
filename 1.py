import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import math

st.title("动态物理模型：抛体运动演示 🚀")
st.write("通过左侧滑块调节参数，点击图表下方的 **播放(Play)** 按钮观看运动轨迹。")

# 1. 在侧边栏设置物理参数滑块
st.sidebar.header("调节物理参数")
v0 = st.sidebar.slider("初始速度 (m/s)", min_value=10, max_value=100, value=50, step=5)
angle_deg = st.sidebar.slider("发射角度 (度)", min_value=10, max_value=90, value=45, step=5)
g = st.sidebar.slider("重力加速度 (m/s²)", min_value=1.0, max_value=20.0, value=9.8, step=0.2)

# 将角度转换为弧度
angle_rad = math.radians(angle_deg)

# 2. 预计算物理轨迹数据
# 计算飞行总时间: t = 2 * v0 * sin(theta) / g
t_total = (2 * v0 * math.sin(angle_rad)) / g
# 生成时间序列（比如取 50 个时间点作为动画帧）
t_array = np.linspace(0, t_total, 50)

# 计算每个时间点的 X 和 Y 坐标
x_array = v0 * math.cos(angle_rad) * t_array
y_array = v0 * math.sin(angle_rad) * t_array - 0.5 * g * t_array**2

# 为了让轨迹保留，我们需要构建一个包含历史轨迹的数据框
# 我们不仅要记录当前点，还要为每一帧记录当前时刻之前的所有点
frames = []
for i in range(len(t_array)):
    # 取出从 0 到当前时刻 i 的数据
    temp_df = pd.DataFrame({
        "X位置": x_array[:i+1],
        "Y位置": y_array[:i+1],
        "时间帧": i, # 告诉 Plotly 这是第几帧
        "标识": "炮弹"
    })
    frames.append(temp_df)

# 将所有帧的数据合并成一个大表
df_animation = pd.concat(frames)

# 3. 使用 Plotly 生成动画图表
# 这里的关键是 animation_frame 参数
fig = px.scatter(
    df_animation,
    x="X位置",
    y="Y位置",
    animation_frame="时间帧",
    color="标识",
    range_x=[0, 1000],  # 固定坐标轴范围，防止播放时画面跳动
    range_y=[0, 300],
    title=f"当前参数: 速度={v0}m/s, 角度={angle_deg}°, 重力={g}m/s²"
)

# 让轨迹看起来像线而不是离散的点，并调整样式
fig.update_traces(mode="lines+markers", marker=dict(size=8))
fig.update_layout(showlegend=False)

# 4. 在网页中渲染
st.plotly_chart(fig, use_container_width=True)
