import streamlit as st
import streamlit.components.v1 as components

st.title("🪐 3D 天体轨道物理仿真")
st.write("鼠标左键：旋转视角 | 滚轮：缩放 | 鼠标右键：平移。通过左侧调节宇宙参数。")

# --- 1. Python 侧：调节天体物理参数 ---
st.sidebar.header("🌌 宇宙参数设置")
# 为了演示方便，我们设定万有引力常数 G = 1
star_mass = st.sidebar.slider("中心恒星质量 (M)", min_value=500, max_value=2000, value=1000, step=100)

st.sidebar.subheader("🌍 行星初始状态")
# 若 G=1, M=1000, 初始距离 r=10，则完美圆轨道的理论速度 v = sqrt(GM/r) = 10
init_r = st.sidebar.slider("初始距离 (半径)", min_value=5.0, max_value=20.0, value=10.0, step=1.0)
init_v = st.sidebar.slider("初始切向速度 (V)", min_value=5.0, max_value=15.0, value=10.0, step=0.5)


# --- 2. 拼接 HTML 与 JS 渲染代码 ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #000000; }}
        canvas {{ width: 100%; height: 100% }}
    </style>
</head>
<body>
    <script>
        // 接收 Python 传来的参数
        const M = {star_mass};
        const G = 1; // 假设引力常数为1
        let pos = [{init_r}, 0, 0]; // 初始位置 (X, Y, Z)
        let vel = [0, {init_v}, 0]; // 初始速度：沿着 Y 轴发射

        // --- 场景、相机、渲染器 ---
        const scene = new THREE.Scene();
        // 加上星空背景效果
        scene.fog = new THREE.FogExp2(0x000000, 0.02);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(20, 20, 20);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // 【核心新增】：激活镜头控制器！
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; // 增加滑动阻尼感，让旋转更丝滑
        controls.dampingFactor = 0.05;

        // --- 创建 3D 物体 ---
        // 1. 中心恒星 (太阳)
        const starGeo = new THREE.SphereGeometry(2, 32, 32);
        const starMat = new THREE.MeshBasicMaterial({{ color: 0xffaa00, wireframe: true }});
        const star = new THREE.Mesh(starGeo, starMat);
        scene.add(star);

        // 2. 环绕行星 (地球)
        const planetGeo = new THREE.SphereGeometry(0.5, 16, 16);
        const planetMat = new THREE.MeshBasicMaterial({{ color: 0x00aaff }});
        const planet = new THREE.Mesh(planetGeo, planetMat);
        scene.add(planet);

        // 3. 轨迹线 (保留行星走过的路径)
        const maxTrail = 200; // 保留200个点
        const trailPositions = new Float32Array(maxTrail * 3);
        const trailGeo = new THREE.BufferGeometry();
        trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
        const trailMat = new THREE.LineBasicMaterial({{ color: 0x00aaff, transparent: true, opacity: 0.5 }});
        const trail = new THREE.Line(trailGeo, trailMat);
        scene.add(trail);

        let trailIndex = 0;
        const dt = 0.016; // 时间步长

        // --- 万有引力物理引擎循环 ---
        function animate() {{
            requestAnimationFrame(animate);

            // 1. 计算行星到恒星的距离 r 和 r^3
            const r_sq = pos[0]*pos[0] + pos[1]*pos[1] + pos[2]*pos[2];
            const r = Math.sqrt(r_sq);
            const r_cb = r_sq * r; 

            // 2. 根据万有引力公式计算 3D 加速度：a = -GM/r^2，方向为 -pos/r
            // 整理后得：ax = -GM * x / r^3
            if (r > 2) {{ // 防止距离过近导致加速度无限大发生穿模
                const ax = -G * M * pos[0] / r_cb;
                const ay = -G * M * pos[1] / r_cb;
                const az = -G * M * pos[2] / r_cb;

                // 3. 更新速度和位置
                vel[0] += ax * dt;
                vel[1] += ay * dt;
                vel[2] += az * dt;

                pos[0] += vel[0] * dt;
                pos[1] += vel[1] * dt;
                pos[2] += vel[2] * dt;
            }}

            // 4. 将计算结果赋予 3D 模型
            planet.position.set(pos[0], pos[1], pos[2]);

            // 5. 更新轨迹线
            trailPositions[trailIndex * 3] = pos[0];
            trailPositions[trailIndex * 3 + 1] = pos[1];
            trailPositions[trailIndex * 3 + 2] = pos[2];
            trailIndex = (trailIndex + 1) % maxTrail;
            trailGeo.attributes.position.needsUpdate = true;

            // 更新镜头控制器
            controls.update(); 
            renderer.render(scene, camera);
        }}
        
        animate();
    </script>
</body>
</html>
"""

# 把 HTML 渲染到 Streamlit 中
components.html(html_code, height=600)
