<template>
  <div class="home-page-container">
    <!-- 你的主页内容 -->
    <h1 class="welcome-title">欢迎来到秋海棠的个人网站</h1>
    <p class="welcome-text">探索我的博客、工具箱和更多内容。</p>
    
    <!-- 照片轮播组件 -->
    <PhotoCarousel />
    
    <!-- 名言轮播组件 -->
    <QuoteDialog />
    
    <div class="spacer"></div> <!-- 一个撑开空间的 div -->

    <!-- 使用 Live2DCanvas 组件 -->
    <Live2DCanvas 
      modelId="furina" 
      :canvasWidth="live2dModelWidth"
      :canvasHeight="live2dModelHeight"
      :position="[100, 0]"
      @model-loaded="handleModelLoaded"
      @model-error="handleModelError"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue';
import Live2DCanvas from '../components/Live2DModel.vue'; // 确保路径正确，现在是 Live2DCanvas
import PhotoCarousel from '../components/PhotoCarousel.vue';
import QuoteDialog from '../components/QuoteDialog.vue';

// 从环境变量读取 Live2D 模型配置
// 使用 parseInt 确保宽度和高度是数字类型，并提供默认值以防环境变量未定义
// 注意：live2dModelPath 变量已移除，因为 Live2DCanvas 组件通过 modelId 构造路径
const live2dModelWidth = parseInt(import.meta.env.VITE_LIVE2D_MODEL_WIDTH || '400');
const live2dModelHeight = parseInt(import.meta.env.VITE_LIVE2D_MODEL_HEIGHT || '500');

// 定义 Live2D 模型相关的类型接口，与 Live2DModel.vue 中保持一致
interface IL2DModel {
  setPosition: (position: [number, number]) => void;
  setScale: (scale: number | 'auto') => void;
  setVolume: (volume: number) => void;
  on: (event: 'hit', callback: (area: string[] | Record<string, any> | undefined) => void) => void;
  showHitAreaFrames: () => void;
  hideHitAreaFrames: () => void;
  dispose?: () => void;
}

const handleModelLoaded = (model: IL2DModel) => {
  console.log('主页收到事件：模型已加载', model);
};

const handleModelError = (error: any) => {
  console.error('主页收到事件：模型加载失败', error);
};

onMounted(() => {
  console.log("HomePage mounted. Live2DModel component will handle canvas.");
});

onBeforeUnmount(() => {
  console.log("HomePage unmounted.");
});
</script>

<style scoped>
.home-page-container {
  padding-top: 60px;
  padding-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  z-index: 5;
  color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 60px);
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

/* 响应式调整 */
@media (max-width: 768px) {
  .home-page-container {
    padding-top: 100px; /* 适应移动端导航栏高度 */
    padding-left: 15px;
    padding-right: 15px;
    width: 100%;
    min-height: calc(100vh - 100px);
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
    min-height: calc(100vh - 120px);
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
