<template>
  <header class="navbar">
    <div class="navbar-brand">
      <router-link to="/" class="logo-link">
        <img src="@/assets/logo/logo.png" alt="Website Logo" class="logo">
        <span class="site-name">海棠小栈</span> <!-- 可以保留网站名称文本 -->
      </router-link>
    </div>
    <nav class="navbar-nav">
      <router-link to="/" class="nav-link">首页</router-link>
      <router-link to="/blog" class="nav-link">博客</router-link>
      <router-link to="/blog/new" class="nav-link">撰写新文章</router-link>
      <!-- 更多导航链接，如 /about, /contact -->
    </nav>
  </header>
</template>

<script setup lang="ts">
// 如果有需要，可以在这里添加脚本逻辑
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: rgba(44, 62, 80, 0.95); /* 深色背景，略透明 */
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  position: fixed; /* 固定在顶部 */
  width: 100%;
  top: 0;
  left: 0;
  z-index: 1000; /* 确保在其他内容之上 */
  backdrop-filter: blur(5px); /* 磨砂玻璃效果 */
}

.navbar-brand {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none; /* 移除下划线 */
  color: inherit; /* 继承父元素颜色 */
}

.logo {
  height: 40px; /* Logo 的高度 */
  width: auto; /* 宽度自适应 */
  margin-right: 10px; /* Logo 和网站名称之间的间距 */
  border-radius: 50%; /* 如果是圆形 Logo 可以添加 */
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); /* 简单阴影 */
}

.site-name {
  font-size: 1.8em;
  font-weight: bold;
  color: #ecf0f1;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.navbar-nav {
  display: flex;
  gap: 20px; /* 导航链接之间的间距 */
}

.nav-link {
  color: #ecf0f1;
  text-decoration: none;
  font-size: 1.1em;
  padding: 8px 15px;
  border-radius: 6px;
  transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  background-color: rgba(52, 152, 219, 0.7); /* 悬停和激活状态的背景色 */
  color: white;
  transform: translateY(-2px); /* 悬停时略微上浮 */
}

/* 移动端适配 */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    padding: 10px;
    height: auto; /* 移动端高度自适应 */
  }

  .navbar-brand {
    margin-bottom: 10px;
  }

  .logo {
    height: 35px; /* 移动端 Logo 稍小 */
    margin-right: 8px;
  }

  .site-name {
    font-size: 1.5em;
  }

  .navbar-nav {
    flex-direction: column; /* 导航链接垂直堆叠 */
    gap: 5px;
    width: 100%; /* 占据全部宽度 */
    align-items: center; /* 居中对齐 */
  }

  .nav-link {
    width: calc(100% - 20px); /* 减去 padding */
    text-align: center;
    padding: 10px 0;
  }
}
</style>
