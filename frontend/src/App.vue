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
  
  <!-- Live2D模型 - 固定在屏幕右下角 -->
  <Live2DModel 
    v-if="!isMobileDevice"
    modelId="furina" 
    :canvasWidth="300"
    :canvasHeight="300"
    :position="[100, 0]"
    @model-loaded="handleModelLoaded"
    @model-error="handleModelError"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import LoadingAnimation from './components/LoadingAnimation.vue';
import Background from './components/Background.vue';
import Navbar from './components/Navbar.vue';
import Footer from './components/Footer.vue';
import MetricsSidebar from './components/MetricsSidebar.vue';
import Live2DModel from './components/Live2DModel.vue';

const isLoading = ref(false);

// 移动设备检测
const isMobileDevice = ref(false);

// 检测是否为移动设备
const checkMobileDevice = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  const mobileKeywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone'];
  const isMobile = mobileKeywords.some(keyword => userAgent.includes(keyword));
  const isSmallScreen = window.innerWidth <= 768;
  
  isMobileDevice.value = isMobile || isSmallScreen;
};

// Live2D模型事件处理
const handleModelLoaded = (model: any) => {
  console.log('App收到事件：Live2D模型已加载', model);
};

const handleModelError = (error: any) => {
  console.error('App收到事件：Live2D模型加载失败', error);
};

onMounted(() => {
  // 初始检测移动设备
  checkMobileDevice();
  
  // 监听窗口大小变化
  window.addEventListener('resize', checkMobileDevice);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobileDevice);
}); 
</script>

<style>
/* 全局样式：确保 body, html, 和 #app 的样式是干净的，不影响布局 */
html, body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  overflow: hidden; /* 禁用原生滚动 */
}

#app {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  width: 100%;
  height: 100vh; /* 固定高度 */
  overflow: hidden; /* 禁用滚动 */
  display: flex; 
  flex-direction: column; 
  position: relative; /* 为内容提供定位上下文 */
}

/* 可滚动容器 */
.scrollable-container {
  flex: 1;
  overflow: hidden; /* 禁用原生滚动 */
  position: relative;
  transform: translateY(0); /* 用于JS控制滚动 */
  transition: none; /* 禁用CSS过渡 */
}

/* 新增样式：确保主内容区域至少占据视口高度，将页脚推到下方 */
.main-content-wrapper {
  padding-top: 60px; /* 为导航栏留出空间 */
  min-height: calc(100vh + 800px);
}

/* 移动端响应式设计 */
@media (max-width: 768px) {
  .main-content-wrapper {
    padding-top: 80px; /* 移动端导航栏更高 */
  }
}

@media (max-width: 480px) {
  .main-content-wrapper {
    padding-top: 100px; /* 小屏幕导航栏最高 */
  }
}
</style>
