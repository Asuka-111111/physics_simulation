import streamlit as st
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go

# ================= 页面设置 =================
st.set_page_config(page_title="流畅版楞次定律仿真", layout="wide")
st.title("🧲 3D 楞次定律：空间感应磁场线全解析")
st.markdown("通过底部的 **▶ 播放** 按钮，观看磁铁穿过圆环的丝滑全过程。注意观察**绿色阻力**、**空间感应磁场线圈**的变化！")

# ================= 侧边栏：参数调节 =================
st.sidebar.header("⚙️ 物理参数 (调参后将重新计算)")
M = st.sidebar.slider("磁铁质量 (kg)", 0.1, 2.0, 0.5, 0.1)
m_dipole = st.sidebar.slider("磁性强度", 5.0, 25.0, 15.0, 1.0)
R_res = st.sidebar.slider("圆环电阻 (Ω)", 0.1, 5.0, 1.0, 0.1)

# 物理常数
g = 9.81
a = 1.2 # 圆环半径

# ================= 1. 物理引擎 (SciPy 预计算) =================
# 预计算 120 帧数据，保证播放极其流畅
num_frames = 120
t = np.linspace(0, 1.2, num_frames)

def derivatives(state, t, M, m_dipole, R_res):
    z, v = state
    # 楞次定律核心公式：计算感应磁场力
    C = (9 * m_dipole**2 * a**4) / (4 * R_res)
    denominator = (a**2 + z**2)**5
    F_mag = - C * (z**2 * v) / denominator if denominator > 0 else 0
    return [v, -g + (F_mag / M)]

# 计算运动轨迹
initial_state = [3.5, 0.0] # 从 Z=3.5 处静止下落
solution = odeint(derivatives, initial_state, t, args=(M, m_dipole, R_res))
z_vals = solution[:, 0]
v_vals = solution[:, 1]

# 预先计算每一帧的受力 (F) 和 感应磁场方向 (B_ind)
F_vals = np.zeros(num_frames)
B_ind_vals = np.zeros(num_frames)
current_angle = np.zeros(num_frames)
angle = 0

for i in range(num_frames):
    z = z_vals[i]
    v = v_vals[i]
    
    # 磁力
    C = (9 * m_dipole**2 * a**4) / (4 * R_res)
    F_vals[i] = - C * (z**2 * v) / (a**2 + z**2)**5
    
    # 感应磁场 B (正比于电流)。由于磁铁N极朝下，靠近时穿过环向下的磁通量增加，感应B朝上(正)
    # v 是负数(往下掉)，z>0 时靠近，z<0 时远离
    B_ind = - (m_dipole * z * v) / (a**2 + z**2)**2.5
    B_ind_vals[i] = B_ind * 0.5 # 缩放以便于在图中显示
    
    # 积分计算电子跑动的角度
    angle += B_ind * 0.5
    current_angle[i] = angle

# ================= 2. 空间磁场线生成算法 =================
max_B = np.max(np.abs(B_ind_vals))
if max_B == 0: max_B = 1.0 # 防止除零

def get_field_lines(B_val, max_B, a):
    """根据当前感应磁场强度，生成环绕导线的 3D 磁场线"""
    if abs(B_val) < 1e-4:
        return [None], [None], [None]
        
    X, Y, Z = [], [], []
    sign_B = np.sign(B_val)
    # 用平方根做缩放，使得磁场线在弱电流时也能明显看出形状变化
    scale = np.sqrt(abs(B_val) / max_B) 
    
    # 在 8 个方向上绘制磁场线圈
    theta_rots = np.linspace(0, 2*np.pi, 8, endpoint=False)
    # 每个方向绘制 3 层不同大小的线圈，代表空间弥漫的磁场
    r_factors = [0.4, 0.7, 1.0]
    phi = np.linspace(0, 2*np.pi, 35)
    
    for theta_rot in theta_rots:
        for r_fac in r_factors:
            R = a * r_fac * scale
            # 构造环绕在导线 (半径 a) 周围的线圈
            x_loc = a - R * np.cos(phi)
            z_loc = R * np.sin(phi) * sign_B
            
            # 旋转到对应的 3D 空间角度
            X.extend(x_loc * np.cos(theta_rot))
            X.append(None) # 使用 None 断开不同线条，提高 Plotly 渲染性能
            Y.extend(x_loc * np.sin(theta_rot))
            Y.append(None)
            Z.extend(z_loc)
            Z.append(None)
            
    return X, Y, Z

# ================= 3. Plotly 3D 动画构建 =================
fig = go.Figure()

def create_vector(x, y, z, u, v, w, color, name):
    return go.Scatter3d(
        x=[x, x+u], y=[y, y+v], z=[z, z+w],
        mode='lines+markers',
        line=dict(color=color, width=6),
        marker=dict(size=[0, 8], symbol='diamond', color=color),
        name=name
    )

theta = np.linspace(0, 2*np.pi, 100)

# --- 初始化动态元素 (第 0 帧) ---
# 0: 导电圆环
fig.add_trace(go.Scatter3d(
    x=a*np.cos(theta), y=a*np.sin(theta), z=np.zeros(100),
    mode='lines', line=dict(color='#b87333', width=8), name='导电圆环'
))
# 1: 磁铁 N 极 (红)
fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[z_vals[0]-0.4, z_vals[0]], mode='lines', line=dict(color='red', width=15), name='N极'))
# 2: 磁铁 S 极 (蓝)
fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[z_vals[0], z_vals[0]+0.4], mode='lines', line=dict(color='blue', width=15), name='S极'))
# 3: 阻力向量 (绿)
fig.add_trace(create_vector(0, 0, z_vals[0], 0, 0, F_vals[0], 'green', '安培阻力'))

# 4: 空间感应磁场线 (根据磁场方向变化颜色：青色/橙色)
X0, Y0, Z0 = get_field_lines(B_ind_vals[0], max_B, a)
color0 = '#00FFFF' if B_ind_vals[0] >= 0 else '#FF6600'
fig.add_trace(go.Scatter3d(
    x=X0, y=Y0, z=Z0, mode='lines',
    line=dict(color=color0, width=3), opacity=0.4, name='空间感应磁场线'
))

# 5: 电子位置 (黄)
fig.add_trace(go.Scatter3d(
    x=[a*np.cos(current_angle[0])], y=[a*np.sin(current_angle[0])], z=[0],
    mode='markers', marker=dict(color='yellow', size=8), name='感应电流'
))

# --- 生成动画帧 ---
frames = []
for i in range(1, num_frames):
    Xf, Yf, Zf = get_field_lines(B_ind_vals[i], max_B, a)
    color_f = '#00FFFF' if B_ind_vals[i] >= 0 else '#FF6600'
    
    frames.append(go.Frame(
        data=[
            go.Scatter3d(x=a*np.cos(theta), y=a*np.sin(theta), z=np.zeros(100)), # 0: 环不变
            go.Scatter3d(x=[0,0], y=[0,0], z=[z_vals[i]-0.4, z_vals[i]]), # 1: N极更新
            go.Scatter3d(x=[0,0], y=[0,0], z=[z_vals[i], z_vals[i]+0.4]), # 2: S极更新
            go.Scatter3d(x=[0, 0], y=[0, 0], z=[z_vals[i], z_vals[i] + F_vals[i]*0.5]), # 3: 阻力更新
            go.Scatter3d(x=Xf, y=Yf, z=Zf, line=dict(color=color_f)), # 4: 空间场磁感线更新 (含颜色反转)
            go.Scatter3d(x=[a*np.cos(current_angle[i])], y=[a*np.sin(current_angle[i])], z=[0]) # 5: 电子更新
        ],
        name=f'frame{i}'
    ))
fig.frames = frames

# --- 设置布局和播放按钮 ---
fig.update_layout(
    scene=dict(
        xaxis=dict(range=[-2.5, 2.5], showbackground=False),
        yaxis=dict(range=[-2.5, 2.5], showbackground=False),
        zaxis=dict(range=[-4, 5], showbackground=False),
        aspectmode='manual', aspectratio=dict(x=1, y=1, z=1.5),
        camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))
    ),
    height=750, margin=dict(l=0, r=0, b=0, t=0), template="plotly_dark",
    updatemenus=[dict(
        type="buttons", showactive=False, x=0.1, y=0, xanchor="right", yanchor="top",
        buttons=[
            dict(label="▶ 播放演示",
                 method="animate",
                 args=[None, dict(frame=dict(duration=30, redraw=True), 
                                  transition=dict(duration=0), 
                                  fromcurrent=True, mode="immediate")]),
            dict(label="⏸ 暂停",
                 method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])
        ]
    )]
)

st.plotly_chart(fig, use_container_width=True)

# ================= 物理现象解析 =================
st.markdown("""
### 🧠 观察指南与楞次定律解析
1. **多重空间感应磁场线（🌐 环形线圈）**：
   现在你可以直观地看到弥漫在空间的环形磁感线！当磁铁靠近时，它们像花朵一样**膨胀扩散**；当磁铁穿过圆环中心时，空间磁场瞬间归零并**翻转颜色（从青色变成橙色）**！
2. **安培阻力（🟢 绿色箭头）**：
   无论磁铁是在上半段（靠近）还是下半段（远离），绿色受力箭头**始终指向上方**，完美展现了“来拒去留”的本质。
3. **感应电流（🟡 黄色圆点）**：
   代表圆环内的电子运动。你会明显看到它在磁铁穿过圆环中心的那一瞬间，发生了一次**急刹车并掉头**。
""")
