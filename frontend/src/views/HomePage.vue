<template>
  <div class="home-page-container">
    <!-- 你的主页内容 -->
    <h1 class="welcome-title">欢迎来到秋海棠的个人网站</h1>
    <p class="welcome-text">探索我的博客、工具箱和更多内容。</p>
    
    <!-- 资料卡片组件 -->
    <ProfileCard />
    
    <!-- 照片轮播组件 -->
    <PhotoCarousel />
    
    <!-- 名言轮播组件 -->
    <QuoteDialog />
    
    <div class="spacer"></div> <!-- 一个撑开空间的 div -->
    
    <!-- 强制增加页面高度的隐形div -->
    <div class="height-filler"></div>

    <!-- Live2D模型已移至App.vue，以保持屏幕固定位置 -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue';
import PhotoCarousel from '../components/PhotoCarousel.vue';
import QuoteDialog from '../components/QuoteDialog.vue';
import ProfileCard from '../components/ProfileCard.vue';

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

// 从环境变量读取 Live2D 模型配置
// Live2D相关代码已移至App.vue

onMounted(() => {
  console.log("HomePage mounted.");
  
  // 检测移动设备
  checkMobileDevice();
  
  // 监听窗口大小变化
  window.addEventListener('resize', checkMobileDevice);
});

onBeforeUnmount(() => {
  console.log("HomePage unmounted.");
  
  // 移除事件监听器
  window.removeEventListener('resize', checkMobileDevice);
});
</script>

<style scoped>
.home-page-container {
  padding-top: 60px;
  padding-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
  position: absolute; /* 改为绝对定位 */
  top: 0;
  left: 0;
  z-index: 5;
  color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  /* 强制设置固定高度，确保有滚动内容 */
  height: calc(100vh + 1200px) !important; /* 增加高度 */
  min-height: calc(100vh + 1200px);
}

.welcome-title {
  font-size: 3.5em;
  font-weight: bold;
  margin-bottom: 20px;
  color: #eee;
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
}

.welcome-text {
  font-size: 1.5em;
  color: #ccc;
  margin-bottom: 40px;
}

.spacer {
  flex-grow: 1;
}

/* 强制增加页面高度 */
.height-filler {
  height: 800px !important;
  width: 100%;
  pointer-events: none;
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .home-page-container {
    padding-top: 100px; /* 适应移动端导航栏高度 */
    padding-left: 15px;
    padding-right: 15px;
    width: 100%;
    height: calc(100vh + 800px) !important; /* 强制移动端也有足够高度 */
    min-height: calc(100vh + 800px) !important; /* 移动端也需要足够空间 */
  }
  .welcome-title {
    font-size: 2.5em;
    margin-bottom: 15px;
  }
  .welcome-text {
    font-size: 1.2em;
    margin-bottom: 30px;
  }
}

@media (max-width: 480px) {
  .home-page-container {
    padding-top: 120px;
    padding-left: 10px;
    padding-right: 10px;
    height: calc(100vh + 800px) !important; /* 强制小屏幕也有足够高度 */
    min-height: calc(100vh + 800px) !important; /* 小屏幕也需要足够空间 */
  }
  .welcome-title {
    font-size: 2em;
    margin-bottom: 12px;
  }
  .welcome-text {
    font-size: 1.1em;
    margin-bottom: 25px;
  }
}
</style>
