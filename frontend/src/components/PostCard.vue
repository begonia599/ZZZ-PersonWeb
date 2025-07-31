<template>
  <!-- 将整个卡片包装在 router-link 中 -->
  <router-link :to="`/blog/${id}`" class="post-card">
    <div class="card-image-wrapper">
      <img :src="imageUrl" alt="文章封面" class="card-image" @error="handleImageError">
    </div>
    <div class="card-content">
      <h3 class="card-title">{{ title }}</h3>
      <p class="card-excerpt">{{ excerpt }}</p>
      <!-- 新增：阅读量显示 -->
      <div class="card-views">
        <svg class="eye-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zm0 13c-3.03 0-5.5-2.47-5.5-5.5s2.47-5.5 5.5-5.5 5.5 2.47 5.5 5.5-2.47 5.5-5.5 5.5zm0-9c-1.93 0-3.5 1.57-3.5 3.5s1.57 3.5 3.5 3.5 3.5-1.57 3.5-3.5-1.57-3.5-3.5-3.5z"/>
        </svg>
        <span>{{ views }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

// **关键修改：直接解构 defineProps 返回的对象**
const { id, title, excerpt, imageUrl, views } = defineProps({
  id: {
    type: [String, Number], // ID 可以是字符串或数字
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  excerpt: {
    type: String,
    default: '这是一个文章的简短描述。',
  },
  imageUrl: {
    type: String,
    default: 'https://placehold.co/300x200/000000/FFFFFF?text=Default+Image', // 默认占位图也使用 placehold.co
  },
  // 新增：views 属性
  views: {
    type: Number,
    default: 0, // 默认阅读量为 0
  },
});

const handleImageError = (event: Event) => {
  const imgElement = event.target as HTMLImageElement;
  const originalSrc = imgElement.src;
  const fallbackUrl = 'https://placehold.co/300x200/FF0000/FFFFFF?text=Image+Load+Error'; // 使用 placehold.co

  if (originalSrc === fallbackUrl) {
    console.warn('Fallback image also failed to load or was already set:', originalSrc);
    return;
  }

  console.error('原始图片加载失败:', originalSrc);
  imgElement.src = fallbackUrl;
  imgElement.removeEventListener('error', handleImageError);
};
</script>

<style scoped>
.post-card {
  background-color: #1a1a1a;
  border: 2px solid #111; 
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 0; /* 右下角保持直角 */
  overflow: hidden; /* 确保内容在圆角内 */
  box-shadow: none;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  cursor: pointer;
  display: inline-block;
  width: 100%;
  margin-bottom: 5px;
  break-inside: avoid;
  color: #e0e0e0; /* 确保链接文字颜色 */
  text-decoration: none; /* 移除链接下划线 */
  position: relative; /* 用于定位阅读量 */
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.5);
  border-color: #00FF00; /* 鲜艳的绿色 */
}

.card-image-wrapper {
  width: 100%;
  height: auto; /* 图片高度根据其原始比例自适应 */
  overflow: hidden;
  background-color: #2a2a2a; /* 图片加载前的背景色 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-image {
  width: 100%;
  height: 100%; /* 图片高度根据其原始比例自适应 */
  object-fit: cover; 
  display: block;
}

.card-content {
  padding: 10px 15px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.card-title {
  font-size: 1em;
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 5px;
  color: #fff;
}

.card-excerpt {
  font-size: 0.85em;
  line-height: 1.4;
  color: #b0b0b0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  /* **Added standard property for compatibility** */
  line-clamp: 2; 
  -webkit-box-orient: vertical;
  margin-bottom: 0; /* 移除底部 margin，让阅读量紧贴 */
}

/* 新增：阅读量样式 */
.card-views {
  position: absolute;
  bottom: 8px; /* 距离卡片底部 */
  right: 8px; /* 距离卡片右侧 */
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.6); /* 半透明背景 */
  padding: 4px 8px;
  border-radius: 5px;
  font-size: 0.8em;
  color: rgba(255, 255, 255, 0.7); /* 半透明白色文字 */
  backdrop-filter: blur(2px); /* 增加一点毛玻璃效果 */
  -webkit-backdrop-filter: blur(2px); /* Safari 兼容 */
}

.eye-icon {
  width: 16px; /* 眼睛图标大小 */
  height: 16px;
  margin-right: 4px;
  color: rgba(255, 255, 255, 0.7); /* 图标颜色，与文字透明度一致 */
}

/* 媒体查询，适应不同屏幕尺寸 */
@media (max-width: 768px) {
  .card-views {
    bottom: 5px;
    right: 5px;
    padding: 3px 6px;
    font-size: 0.75em;
  }
  .eye-icon {
    width: 14px;
    height: 14px;
  }
}
</style>
