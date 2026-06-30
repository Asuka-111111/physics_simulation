import streamlit as st
import streamlit.components.v1 as components

st.title("3D魔丸")
st.write("我有一颗高玩！！！")

# 1. 在 Python 端获取用户输入的参数
radius = st.slider("调节小球半径", min_value=1.0, max_value=9.0, value=2.0)
color = st.selectbox("选择小球颜色", ["red", "#00ff00", "blue", "orange", "black"])

# 2. 编写 HTML/JS 模板
# 注意前面的 f"..."，这让我们可以在长文本里直接插入 Python 变量！
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body style="margin: 0; overflow: hidden; background-color: #f0f2f6;">
    <script>
        // 【关键点】这里我们直接把 Python 的变量，注入到了 JS 代码中！
        const ballRadius = {radius}; 
        const ballColor = "{color}";

        // --- 下面这些标准的 3D 渲染模板，以后你可以直接让 AI 帮你写 ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // 创建球体和材质
        const geometry = new THREE.SphereGeometry(ballRadius, 32, 32);
        // wireframe: true 让它显示为网格线框，看起来更有物理感
        const material = new THREE.MeshBasicMaterial({{ color: ballColor, wireframe: true }});
        const sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);

        camera.position.z = 10;

        // 真正的 60 FPS 动画循环！
        function animate() {{
            requestAnimationFrame(animate);
            // 让小球自己丝滑地旋转
            sphere.rotation.x += 0.01;
            sphere.rotation.y += 0.01;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
</body>
</html>
"""

# 3. 把这段拼接好的代码丢给 Streamlit 渲染
components.html(html_code, height=400)
