<template>
  <div class="drive-card">
    <!-- 背景图片层，应用滤镜效果 -->
    <div class="card-image-filtered" :style="{ backgroundImage: 'url(' + backgroundUrl + ')' }"></div>
    
    <!-- 渐变叠加层 -->
    <div class="card-gradient-overlay"></div>

    <!-- 内容层 -->
    <div class="drive-content">
      <div class="tool-logo-container" v-if="logoUrl">
        <img :src="logoUrl" :alt="name + ' Logo'" class="tool-logo" />
      </div>

      <div class="drive-name">{{ name }}</div>
      <div class="drive-desc">{{ description }}</div>
      
      <router-link :to="path" class="drive-btn">
        {{ buttonText || '进入工具' }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps<{
  id: number;
  name: string;
  description: string;
  path: string;
  logoUrl?: string;
  backgroundUrl?: string;
  buttonText?: string;
}>();
</script>

<style scoped>
/* 核心：将 drive.css 中 .drive-card 及其子元素的样式迁移到这里 */

.drive-card {
  position: relative;
  border-radius: 15px;
  overflow: hidden;
  width: 100%; /* 卡片宽度填满网格 */
  max-width: 380px; /* 限制最大宽度 */
  min-height: 400px; /* 桌面端最小高度 */
  height: 400px; /* 固定高度，确保所有卡片一致 */
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  text-align: center;
  color: white;
}

.drive-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.25);
}

/* 新增：背景图片层，应用滤镜效果 */
.card-image-filtered {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  /* “淡淡的滤镜效果”：降低亮度并轻微模糊 */
  filter: brightness(0.7) blur(1px);
  transition: filter 0.3s ease; /* 悬停时滤镜效果的过渡 */
  z-index: 1; /* 在渐变层和内容层之下 */
}

.drive-card:hover .card-image-filtered {
  filter: brightness(0.8) blur(0px); /* 悬停时背景更亮更清晰 */
}

/* 渐变叠加层 (从 drive.css 复制) */
.card-gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, 
                              rgba(0, 0, 0, 0.5), 
                              rgba(0, 0, 0, 0.75));
  z-index: 2; /* 在背景图片层之上，内容层之下 */
}

.drive-content {
  position: relative;
  z-index: 3; /* 确保内容在最上层 */
  padding: 20px;
  width: 100%; /* 确保内容区宽度 */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* 垂直居中内容 */
  flex-grow: 1; /* 允许内容区填充剩余空间 */
}

.tool-logo-container {
  margin-bottom: 15px; /* Logo 与标题的间距 */
  width: 80px; /* Logo 容器大小 */
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1); /* Logo 背景，可选 */
  border-radius: 50%; /* 圆形 Logo 背景 */
  padding: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.tool-logo {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
}

.drive-name {
  font-size: 1.8rem; /* 根据 drive.css 调整 */
  font-weight: 700;
  color: #fff;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}

.drive-desc {
  font-size: 1rem; /* 根据 drive.css 调整 */
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 25px; /* 描述与按钮的间距 */
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  flex-grow: 1; /* 允许描述撑开空间 */
  display: flex; /* 确保文字居中 */
  align-items: center;
  justify-content: center;
}

.drive-btn {
  display: inline-block;
  background: linear-gradient(45deg, #007bff, #0056b3); /* 蓝色渐变按钮 */
  color: white;
  padding: 12px 25px;
  border-radius: 30px; /* 圆角按钮 */
  text-decoration: none;
  font-weight: 600;
  font-size: 1.05rem;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.drive-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  background: linear-gradient(45deg, #0056b3, #007bff); /* 悬停时渐变方向或颜色变化 */
}

/* 响应式调整 */
@media (max-width: 768px) {
    .drive-card {
        min-height: 350px;
        height: 350px; /* 移动端固定高度 */
        max-width: 100%; /* 移动端最大宽度 */
    }
    .drive-name {
        font-size: 1.5rem;
    }
    .drive-desc {
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    .drive-btn {
        padding: 10px 20px;
        font-size: 0.95rem;
    }
    .tool-logo-container {
        width: 60px;
        height: 60px;
        margin-bottom: 12px;
    }
}

@media (max-width: 480px) {
    .drive-card {
        height: 320px; /* 小屏幕更紧凑的高度 */
        min-height: 320px;
    }
    .drive-content {
        padding: 15px;
    }
    .drive-name {
        font-size: 1.3rem;
    }
    .drive-desc {
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
    .tool-logo-container {
        width: 50px;
        height: 50px;
        margin-bottom: 10px;
    }
}
</style>