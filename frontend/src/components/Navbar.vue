<template>
  <nav class="navbar">
    <ul>
      <li><router-link to="/" class="nav-item">主页</router-link></li>
      <li><router-link to="/toolbox" class="nav-item">工具箱</router-link></li>
      <li><router-link to="/blog" class="nav-item">海棠旅记</router-link></li>
      <li><router-link to="/about" class="nav-item">关于我</router-link></li>
      <li><router-link to="/contact" class="nav-item">联系</router-link></li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
// 该组件不需要脚本逻辑
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background-color: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100; /* 确保导航栏在最顶层 */
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 20px; /* 按钮之间的间距 */
}

.nav-item {
  color: #fff;
  text-decoration: none;
  font-size: 18px; /* 保持字体大小不变 */
  font-weight: bold;
  padding: 10px 20px;
  border-radius: 9999px; /* 胶囊形状 */
  transition: all 0.3s ease-in-out;
  cursor: pointer;
  
  /* 初始状态下的样式 */
  background-color: transparent;
}

/* 鼠标悬停时的样式 */
.nav-item:hover {
  color: #000; /* 悬停时字体变为黑色 */
  background-color: #fff; /* 悬停时背景变为白色 */
}

/* 导航项被激活时的样式 (router-link-active 类) */
.nav-item.router-link-active {
  color: #000; /* 字体变为黑色 */
  background-color: #fff; /* 背景变为白色，保持胶囊状态 */
  /* 移除 hover 效果中的 transform 和 box-shadow，避免抖动 */
  transform: none; 
  box-shadow: none;
}
</style>