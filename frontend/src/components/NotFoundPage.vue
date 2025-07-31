<template>
  <div class="not-found-container">
    <h1>404</h1>
    <h2>页面未找到</h2>
    <p>抱歉，你访问的页面不存在。</p>
    <router-link to="/" class="go-home-btn">返回主页</router-link>
  </div>
</template>

<script setup lang="ts">
// 404 页面通常不需要复杂的脚本逻辑
</script>

<style scoped>
.not-found-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #fff; /* 白色字体 */
  z-index: 5; /* 确保在背景之上 */
  padding-top: 60px; /* 导航栏下方 */
}

h1 {
  font-size: 8em;
  margin-bottom: 0.2em;
  color: #e74c3c; /* 醒目的红色 */
  text-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
}

h2 {
  font-size: 2em;
  margin-bottom: 1em;
}

p {
  font-size: 1.2em;
  margin-bottom: 2em;
}

.go-home-btn {
  display: inline-block;
  padding: 12px 25px;
  background-color: #3498db; /* 蓝色按钮 */
  color: #fff;
  text-decoration: none;
  border-radius: 9999px; /* 胶囊形状 */
  transition: background-color 0.3s ease, transform 0.2s ease;
  font-weight: bold;
}

.go-home-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

/* 响应式调整 */
@media (max-width: 768px) {
  h1 {
    font-size: 6em;
  }
  h2 {
    font-size: 1.8em;
  }
  p {
    font-size: 1em;
  }
}
</style>