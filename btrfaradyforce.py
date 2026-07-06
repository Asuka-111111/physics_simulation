import streamlit as st
import streamlit.components.v1 as components

# ================= 设置页面 =================
st.set_page_config(page_title="流畅版 3D电磁感应", layout="wide")
st.title("🧲 3D 电磁感应：60帧流畅版")
st.markdown("现在，物理引擎和渲染已全部转移至你的本地浏览器。点击下方的**开始/重置**按钮，体验丝滑的电磁阻尼下落。")

# ================= 侧边栏：传递给前端的参数 =================
st.sidebar.header("⚙️ 物理参数 (修改后模型会自动重载)")
mass = st.sidebar.slider("磁铁质量 (kg)", 0.1, 2.0, 0.5, 0.1)
mag_strength = st.sidebar.slider("磁场强度系数", 1.0, 20.0, 10.0, 1.0)
resistance = st.sidebar.slider("圆环电阻 (Ω)", 0.1, 5.0, 1.0, 0.1)

# ================= 核心：内嵌 HTML + Three.js 前端引擎 =================
# 我们使用 f-string 将 Streamlit 的变量直接注入到 JS 代码中
html_code = f"""
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; overflow: hidden; font-family: sans-serif; background-color: #0e1117; color: white; }}
        #canvas-container {{ width: 100vw; height: 100vh; display: block; }}
        #ui-layer {{ position: absolute; top: 10px; left: 10px; z-index: 10; background: rgba(0,0,0,0.6); padding: 15px; border-radius: 8px; }}
        button {{ padding: 10px 20px; font-size: 16px; cursor: pointer; background-color: #ff4b4b; color: white; border: none; border-radius: 4px; font-weight: bold; transition: 0.3s; }}
        button:hover {{ background-color: #ff3333; }}
        .data-text {{ margin: 10px 0 5px 0; font-size: 14px; font-family: monospace; color: #00ff00; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui-layer">
        <button id="startBtn">▶ 开始下落</button>
        <div class="data-text" id="posText">高度 Z: 3.00 m</div>
        <div class="data-text" id="velText">速度 V: 0.00 m/s</div>
        <div class="data-text" id="forceText">磁阻力 F: 0.00 N</div>
    </div>
    <div id="canvas-container"></div>

    <script>
        // 1. 接收来自 Streamlit 的物理参数
        const MASS = {mass};
        const MAG_STRENGTH = {mag_strength};
        const RESISTANCE = {resistance};
        const g = 9.81;
        const RING_RADIUS = 1.0;
        
        // 计算磁力常数 C
        const C_const = (9 * Math.pow(MAG_STRENGTH, 2) * Math.pow(RING_RADIUS, 4)) / (4 * RESISTANCE);

        // 2. 初始化 Three.js 场景
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0e1117);
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3, 6);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // 添加光源
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 5);
        scene.add(dirLight);

        // 3. 创建物体：导电圆环
        const ringGeo = new THREE.TorusGeometry(RING_RADIUS, 0.05, 16, 100);
        const ringMat = new THREE.MeshPhongMaterial({{ color: 0x888888, emissive: 0x000000 }});
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2; // 水平放置
        scene.add(ring);

        // 4. 创建物体：条形磁铁 (N极红，S极蓝)
        const magnetGroup = new THREE.Group();
        const magGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.4, 32);
        
        const sMat = new THREE.MeshPhongMaterial({{ color: 0x0000ff }}); // 蓝 S
        const sPole = new THREE.Mesh(magGeo, sMat);
        sPole.position.y = 0.2;
        
        const nMat = new THREE.MeshPhongMaterial({{ color: 0xff0000 }}); // 红 N
        const nPole = new THREE.Mesh(magGeo, nMat);
        nPole.position.y = -0.2;

        magnetGroup.add(sPole);
        magnetGroup.add(nPole);
        scene.add(magnetGroup);

        // 5. 物理状态变量
        let isRunning = false;
        let zPos = 3.0;
        let velocity = 0.0;
        let forceMag = 0.0;
        magnetGroup.position.y = zPos;

        // UI 元素
        const btn = document.getElementById('startBtn');
        const posText = document.getElementById('posText');
        const velText = document.getElementById('velText');
        const forceText = document.getElementById('forceText');

        // 按钮事件
        btn.addEventListener('click', () => {{
            if (isRunning || zPos < -3.0) {{
                // 重置状态
                isRunning = false;
                zPos = 3.0;
                velocity = 0.0;
                forceMag = 0.0;
                magnetGroup.position.y = zPos;
                ringMat.emissive.setHex(0x000000); // 熄灭光芒
                btn.innerText = "▶ 开始下落";
                updateUI();
            }} else {{
                // 开始下落
                isRunning = true;
                btn.innerText = "🔄 重置";
            }}
        }});

        function updateUI() {{
            posText.innerText = `高度 Z: ${{zPos.toFixed(2)}} m`;
            velText.innerText = `速度 V: ${{velocity.toFixed(2)}} m/s`;
            forceText.innerText = `磁阻力 F: ${{forceMag.toFixed(2)}} N (向上)`;
        }}

        // 6. 核心物理演算循环 (60fps)
        const dt = 0.016; // 固定时间步长
        
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();

            if (isRunning) {{
                // 计算受力 (楞次定律阻力)
                const z2 = zPos * zPos;
                const a2 = RING_RADIUS * RING_RADIUS;
                const denominator = Math.pow(a2 + z2, 5);
                
                if (denominator > 0) {{
                    forceMag = - (C_const * z2 * velocity) / denominator;
                }} else {{
                    forceMag = 0;
                }}

                // 加速度 = 重力加速度 + (安培力 / 质量)
                const accel = -g + (forceMag / MASS);
                
                // 欧拉积分更新速度和位置
                velocity += accel * dt;
                zPos += velocity * dt;
                magnetGroup.position.y = zPos;

                // 视觉效果：电流越大，圆环越亮 (电流正比于 v*z / (a^2+z^2)^2.5)
                const currentIntensity = Math.abs(velocity * zPos) / Math.pow(a2 + z2, 2.5);
                const glow = Math.min(currentIntensity * MAG_STRENGTH * 0.5, 1.0);
                ringMat.emissive.setRGB(glow, glow * 0.5, 0); // 发出橙红光

                updateUI();

                // 跌出边界后自动停止
                if (zPos < -3.5) {{
                    isRunning = false;
                    velocity = 0;
                    ringMat.emissive.setHex(0x000000);
                }}
            }}

            renderer.render(scene, camera);
        }}

        // 处理窗口缩放
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        animate();
    </script>
</body>
</html>
"""

# ================= 渲染组件 =================
# 高度设置为 700px，宽度自适应
components.html(html_code, height=700)

st.info("💡 **操作指南**：在 3D 画面中，你可以**按住鼠标左键拖动**来旋转视角，**滚动鼠标滚轮**来缩放。调节左侧滑块后，3D 场景会自动刷新读取新参数，点击画布内的【开始下落】即可体验。")
