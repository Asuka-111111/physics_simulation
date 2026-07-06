import streamlit as st
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ================= 设置页面 =================
st.set_page_config(page_title="3D电磁感应仿真", layout="wide")
st.title("🧲 3D 电磁感应：条形磁铁穿过带电圆环")
st.markdown("通过调节左侧侧边栏的物理参数，观察法拉第电磁感应定律与楞次定律在动态过程中的体现。")

# ================= 侧边栏：交互参数 =================
st.sidebar.header("⚙️ 调节物理参数")
M = st.sidebar.slider("磁铁质量 (kg)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
m_dipole = st.sidebar.slider("磁偶极矩 (强度)", min_value=1.0, max_value=20.0, value=10.0, step=1.0)
a = st.sidebar.slider("圆环半径 (m)", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
R_res = st.sidebar.slider("圆环电阻 (Ω)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# ================= 物理常数与方程 =================
g = 9.81
# 为了让视觉效果明显，我们使用无量纲化的等效磁导率因子 (缩放后的物理系统)
mu0_eff = 1.0 

def induction_derivatives(state, t, M, g, m_dipole, a, R_res, mu0):
    z, v = state
    # 感应电流产生的磁场力 (楞次定律：始终阻碍运动)
    # F_mag = - [9 * mu0^2 * m^2 * a^4 / (4 * R_res)] * [z^2 * v / (a^2 + z^2)^5]
    C = (9 * mu0**2 * m_dipole**2 * a**4) / (4 * R_res)
    F_mag = - C * (z**2 * v) / (a**2 + z**2)**5
    
    dzdt = v
    dvdt = -g + (F_mag / M)
    return [dzdt, dvdt]

# ================= 求解物理运动轨迹 =================
@st.cache_data
def solve_physics(M, m_dipole, a, R_res):
    t = np.linspace(0, 1.5, 150) # 模拟 1.5 秒
    initial_state = [3.0, 0.0]   # 初始位置 z=3.0, 初速度 v=0
    
    # 使用 ODE 解算器计算轨迹
    solution = odeint(induction_derivatives, initial_state, t, args=(M, g, m_dipole, a, R_res, mu0_eff))
    z = solution[:, 0]
    v = solution[:, 1]
    
    # 计算衍生物理量 (电流和磁力)
    C = (9 * mu0_eff**2 * m_dipole**2 * a**4) / (4 * R_res)
    F_mag = - C * (z**2 * v) / (a**2 + z**2)**5
    # 感应电流 I ∝ z * v / (a^2 + z^2)^(5/2)
    I = (3 * mu0_eff * m_dipole * a**2 * z * v) / (2 * R_res * (a**2 + z**2)**2.5)
    
    return t, z, v, F_mag, I

t, z, v, F_mag, I = solve_physics(M, m_dipole, a, R_res)

# ================= 时间轴控制器 =================
time_idx = st.slider("⏱️ 拖动时间轴观察下落过程", min_value=0, max_value=len(t)-1, value=0, format="第 %d 帧")
current_z = z[time_idx]
current_I = I[time_idx]
current_F = F_mag[time_idx]

# ================= 布局：左侧3D模型，右侧数据图 =================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("3D 物理空间")
    fig3d = go.Figure()

    # 1. 绘制导电圆环
    theta = np.linspace(0, 2*np.pi, 100)
    x_ring = a * np.cos(theta)
    y_ring = a * np.sin(theta)
    z_ring = np.zeros_like(theta)
    
    # 环的颜色根据电流大小和方向发光
    ring_color = 'red' if current_I > 0 else 'blue' if current_I < 0 else 'gray'
    line_width = 5 + abs(current_I) * 10 # 电流越大越粗

    fig3d.add_trace(go.Scatter3d(
        x=x_ring, y=y_ring, z=z_ring,
        mode='lines',
        line=dict(color=ring_color, width=line_width),
        name="导电环 (颜色=电流方向)"
    ))

    # 2. 绘制条形磁铁 (用两个圆柱面拼接代表 N/S 极)
    def get_cylinder(z_center, radius=0.2, length=0.6):
        z_vals = np.linspace(z_center - length/2, z_center + length/2, 2)
        theta_grid, z_grid = np.meshgrid(theta, z_vals)
        x_grid = radius * np.cos(theta_grid)
        y_grid = radius * np.sin(theta_grid)
        return x_grid, y_grid, z_grid

    mag_length = 0.6
    # N极 (红色, 下半部)
    x_n, y_n, z_n = get_cylinder(current_z - mag_length/4, length=mag_length/2)
    fig3d.add_trace(go.Surface(x=x_n, y=y_n, z=z_n, colorscale=[[0,'red'],[1,'red']], showscale=False, name="N极"))
    # S极 (蓝色, 上半部)
    x_s, y_s, z_s = get_cylinder(current_z + mag_length/4, length=mag_length/2)
    fig3d.add_trace(go.Surface(x=x_s, y=y_s, z=z_s, colorscale=[[0,'blue'],[1,'blue']], showscale=False, name="S极"))

    # 3. 绘制磁场力向量 (向上)
    if current_F > 0.1:
        fig3d.add_trace(go.Cone(
            x=[0], y=[0], z=[current_z + 0.5],
            u=[0], v=[0], w=[current_F * 0.1], # 缩放矢量以适应视图
            colorscale=[[0, 'green'], [1, 'green']],
            sizemode="absolute", sizeref=0.5, showscale=False, name="安培阻力"
        ))

    # 设置 3D 视图属性，锁定镜头比例
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(range=[-3, 3], showbackground=False),
            yaxis=dict(range=[-3, 3], showbackground=False),
            zaxis=dict(range=[-1, 4], showbackground=False),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600
    )
    st.plotly_chart(fig3d, use_container_width=True)

with col2:
    st.subheader("实时物理量监测")
    
    # 动态曲线图
    fig2d = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                          subplot_titles=("位置 Z (m) - 穿过0点", "感应电流 I (A) - 方向翻转", "磁场阻力 F (N) - 始终向上"))
    
    # 位置
    fig2d.add_trace(go.Scatter(x=t, y=z, name="位置", line=dict(color='purple')), row=1, col=1)
    fig2d.add_trace(go.Scatter(x=[t[time_idx]], y=[z[time_idx]], mode='markers', marker=dict(color='red', size=10), showlegend=False), row=1, col=1)
    
    # 电流
    fig2d.add_trace(go.Scatter(x=t, y=I, name="电流", line=dict(color='orange')), row=2, col=1)
    fig2d.add_trace(go.Scatter(x=[t[time_idx]], y=[I[time_idx]], mode='markers', marker=dict(color='red', size=10), showlegend=False), row=2, col=1)
    
    # 磁力
    fig2d.add_trace(go.Scatter(x=t, y=F_mag, name="磁力", line=dict(color='green')), row=3, col=1)
    fig2d.add_trace(go.Scatter(x=[t[time_idx]], y=[F_mag[time_idx]], mode='markers', marker=dict(color='red', size=10), showlegend=False), row=3, col=1)

    fig2d.update_layout(height=600, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
    # 增加一条垂直的指示线代表当前时间
    fig2d.add_vline(x=t[time_idx], line_width=1, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig2d, use_container_width=True)

st.info("💡 **物理洞察**：注意观察，当磁铁中心刚好穿过圆环平面 (Z=0) 的瞬间，磁通量变化率反转，导致**感应电流瞬间反向**。但无论电流方向如何，由于楞次定律，**安培力始终为正 (向上)**，阻碍磁铁下落，形成了电磁阻尼效应。")
