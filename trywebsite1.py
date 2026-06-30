import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.title("滑块交互示例：动态正弦波 🌊")
st.write("试着拖动下面的滑块，观察图形如何实时变化！")

# 1. 创建滑块组件，捕获用户的输入值
# 参数依次为：标签文字, 最小值, 最大值, 默认值, 步长
freq = st.slider("调节频率 (Frequency):", min_value=1, max_value=10, value=3, step=1)
amp = st.slider("调节振幅 (Amplitude):", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

# 2. 根据滑块传递过来的变量，动态计算数据
x = np.linspace(0, 10, 200) # 生成 0 到 10 的 200 个点
y = amp * np.sin(freq * x)  # 应用滑块的 freq 和 amp 变量
df = pd.DataFrame({"时间": x, "数值": y})

# 3. 使用 Plotly 渲染图形
fig = px.line(
    df, 
    x="时间", 
    y="数值", 
    title=f"当前状态：频率 = {freq}, 振幅 = {amp}"
)

# 固定 Y 轴范围，防止图形跳动，让视觉变化更直观
fig.update_yaxes(range=[-5.5, 5.5])

# 4. 在网页上显示图表
st.plotly_chart(fig, use_container_width=True)
