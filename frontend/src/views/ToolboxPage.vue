<template>
  <div class="toolbox-page">
    <h1>🚀 我的工具箱</h1>

    <!-- 全屏加载动画叠加层 - 保持不变 -->
    <div v-if="isLoading" class="loading-overlay">
      <LoadingAnimation />
    </div>

    <!-- 工具列表内容 -->
    <div v-if="tools.length === 0" class="no-tools">
      <p>目前还没有可用的工具。敬请期待！</p>
    </div>
    <div v-else class="tool-list">
      <ToolCard
        v-for="tool in tools"
        :key="tool.id"
        :id="tool.id"
        :name="tool.name"
        :description="tool.description"
        :path="tool.path"
        :logoUrl="tool.logoUrl"
        :backgroundUrl="tool.backgroundUrl"
        :buttonText="tool.buttonText"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import ToolCard from '../components/ToolCard.vue';

interface Tool {
  id: number;
  name: string;
  description: string;
  path: string;
  logoUrl?: string;
  backgroundUrl?: string;
  buttonText?: string;
}

const isLoading = ref(true);
const tools = ref<Tool[]>([]);

onMounted(() => {
  setTimeout(() => {
    tools.value = [
      {
        id: 1,
        name: '绝区零驱动器统计工具',
        description: '深入分析您的驱动器装备属性、套装效果和强化记录，助您优化角色构建。',
        path: '/toolbox/drive',
        logoUrl: '/tool-icons/zzz-logo.png',
        backgroundUrl: '/tool-icons/zzz-card-bg.jpg',
        buttonText: '开始统计'
      },
      {
        id: 2,
        name: '海棠旅记',
        description: '记录生活中的美好瞬间，上传照片并按分类整理，让回忆更有序、更珍贵。',
        path: '/toolbox/travel',
        logoUrl: '/images/characters/zzjg.jpg',
        backgroundUrl: '/assets/images/青衣.webp',
        buttonText: '开始记录'
      },
      // 可以在这里添加更多工具
    ];
    isLoading.value = false;
  });
});
</script>

<style scoped>
.toolbox-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  min-height: calc(100vh - 40px);
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: transparent;
  z-index: 9999;
}

.loading-text {
  margin-top: 15px;
  font-size: 1.2em;
  color: #333;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

/* 工具卡片网格布局 - 居中按行排列 */
.tool-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 380px)); /* 固定最大宽度，确保能在一行显示 */
  gap: 30px; /* 卡片间距 */
  margin-bottom: 40px;
  justify-content: center; /* 整个网格居中 */
  justify-items: center; /* 在网格中居中项目 */
  max-width: 1200px; /* 限制最大宽度 */
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px; /* 左右内边距 */
}

/* 响应式调整：移动端优化 */
@media (max-width: 768px) {
  .toolbox-page {
    padding: 15px;
    padding-top: 100px; /* 适应移动端导航栏高度 */
  }
  
  h1 {
    font-size: 2em;
    margin-bottom: 20px;
    color: #fff; /* 移动端使用白色文字 */
  }
  
  .tool-list {
    grid-template-columns: repeat(auto-fit, minmax(280px, 350px)); /* 移动端适配 */
    gap: 20px; /* 移动端卡片间距 */
    padding: 0 15px; /* 移动端内边距 */
  }
}

@media (max-width: 480px) {
  .toolbox-page {
    padding: 10px;
    padding-top: 120px;
  }
  
  h1 {
    font-size: 1.8em;
  }
  
  .tool-list {
    grid-template-columns: 1fr; /* 小屏幕单列布局 */
    gap: 15px;
    padding: 0 10px; /* 小屏幕内边距 */
  }
}

.no-tools {
  color: #777;
  font-style: italic;
  margin-top: 50px;
}
</style>