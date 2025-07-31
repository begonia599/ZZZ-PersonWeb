<template>
  <!-- 导航栏组件放在最顶部 -->
  <Navbar />
  
  <!-- 背景组件始终显示 -->
  <Background />

  <!-- 加载动画在 isLoading 为 true 时显示 -->
  <LoadingAnimation v-if="isLoading" />
  
  <!-- 关键：为 router-view 添加 :key 属性 -->
  <div class="main-content-wrapper" v-else>
    <router-view :key="$route.fullPath" /> 
  </div>

  <!-- 网站指标侧边栏 -->
  <MetricsSidebar /> 

  <!-- 页脚组件 -->
  <Footer />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import LoadingAnimation from './components/LoadingAnimation.vue';
import Background from './components/Background.vue';
import Navbar from './components/Navbar.vue';
import Footer from './components/Footer.vue';
import MetricsSidebar from './components/MetricsSidebar.vue'; // **新增：导入 MetricsSidebar 组件**

const isLoading = ref(false); 
</script>

<style>
/* 全局样式：确保 body, html, 和 #app 的样式是干净的，不影响布局 */
html, body, #app {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  overflow-y: auto; /* 允许内容滚动 */
  overflow-x: hidden; /* 隐藏水平滚动条 */
  display: flex; /* 关键：使用 Flexbox 布局 */
  flex-direction: column; /* 关键：垂直方向排列子元素 */
}

/* 新增样式：确保主内容区域至少占据视口高度，将页脚推到下方 */
.main-content-wrapper {
  flex: 1; /* 关键：让它占据所有可用空间并根据内容增长 */
  padding-top: 60px; /* 为导航栏留出空间 */
}
</style>
