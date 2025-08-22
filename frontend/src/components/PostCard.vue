<template>
  <div class="post-card" :style="cardStyle">
    <!-- 管理员按钮 -->
    <div class="admin-controls" v-if="showAdminControls">
      <button @click.stop="handleEdit" class="admin-btn edit-btn" title="编辑文章">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
        </svg>
      </button>
      <button @click.stop="handleDelete" class="admin-btn delete-btn" title="删除文章">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
      </button>
    </div>

    <!-- 文章内容区域 -->
    <router-link :to="`/blog/${id}`" class="card-link">
      <div class="card-image-wrapper">
        <img :src="finalImageUrl" alt="文章封面" class="card-image" @error="handleImageError" @load="handleImageLoad">
      </div>
      <div class="card-content">
        <h3 class="card-title">{{ title }}</h3>
        <p class="card-excerpt">{{ excerpt }}</p>
        <!-- 阅读量显示 -->
        <div class="card-views">
          <svg class="eye-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zm0 13c-3.03 0-5.5-2.47-5.5-5.5s2.47-5.5 5.5-5.5 5.5 2.47 5.5 5.5-2.47 5.5-5.5 5.5zm0-9c-1.93 0-3.5 1.57-3.5 3.5s1.57 3.5 3.5 3.5 3.5-1.57 3.5-3.5-1.57-3.5-3.5-3.5z"/>
          </svg>
          <span>{{ views }}</span>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { apiFetch, API_ENDPOINTS } from '@/config/api';

const router = useRouter();
const emit = defineEmits(['refresh', 'delete']);

// Props定义
const props = defineProps({
  id: {
    type: [String, Number],
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
    default: '',
  },
  views: {
    type: Number,
    default: 0,
  },
  index: {
    type: Number,
    default: 0,
  },
});

// 响应式数据
const imageLoaded = ref(false);
const showAdminControls = ref(true); // 简化：始终显示管理控制

// 预设图片列表（与ArticleEditorPage保持一致）
const modules = import.meta.glob('../assets/images/*.{jpg,png,webp}', { eager: true });
const presetImageUrls: string[] = Object.values(modules).map((module: any) => module.default || module);

// 智能图片选择策略 - 基于文章ID和标题，确保一致性
const generateConsistentImageUrl = (articleId: number | string, title: string): string => {
  if (presetImageUrls.length === 0) {
    return 'https://placehold.co/300x200/cccccc/000000?text=No+Image';
  }

  // 使用文章ID和标题的hash来确保同一篇文章总是使用相同的图片
  const hashInput = `${articleId}-${title}`;
  let hash = 0;
  for (let i = 0; i < hashInput.length; i++) {
    const char = hashInput.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  const index = Math.abs(hash) % presetImageUrls.length;
  return presetImageUrls[index];
};

// 计算最终图片URL
const finalImageUrl = computed(() => {
  if (props.imageUrl && props.imageUrl.trim()) {
    return props.imageUrl;
  }
  return generateConsistentImageUrl(props.id, props.title);
});

// 移除手动高度限制，让图片自然展示
const cardStyle = computed(() => {
  // 不再限制图片高度，让图片按照原始比例自然展示
  return {};
});

// 图片加载处理
const handleImageLoad = () => {
  imageLoaded.value = true;
};

const handleImageError = (event: Event) => {
  const imgElement = event.target as HTMLImageElement;
  const fallbackUrl = 'https://placehold.co/300x200/FF0000/FFFFFF?text=Image+Load+Error';
  
  if (imgElement.src !== fallbackUrl) {
    console.error('图片加载失败:', imgElement.src);
    imgElement.src = fallbackUrl;
  }
};

// 管理功能
const handleEdit = () => {
  router.push(`/blog/edit/${props.id}`);
};

const handleDelete = async () => {
  if (!confirm(`确定要删除文章"${props.title}"吗？此操作不可撤销。`)) {
    return;
  }

  try {
    await apiFetch(API_ENDPOINTS.DELETE_POST(Number(props.id)), {
      method: 'DELETE',
    });
    
    // 通知父组件刷新列表
    emit('delete', props.id);
    emit('refresh');
  } catch (error: any) {
    console.error('删除文章失败:', error);
    alert('删除文章失败: ' + (error.message || '未知错误'));
  }
};
</script>

<style scoped>
.post-card {
  background-color: #1a1a1a;
  border: 2px solid #111; 
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  display: block;
  width: 280px;
  margin-bottom: 15px;
  position: absolute; /* 这个会被JavaScript动态设置 */
  z-index: 1;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
  border-color: #00FF00;
  z-index: 10; /* 悬停时提升层级 */
}

/* 管理员控制按钮 */
.admin-controls {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.post-card:hover .admin-controls {
  opacity: 1;
}

.admin-btn {
  background-color: rgba(0, 0, 0, 0.8);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.admin-btn svg {
  width: 16px;
  height: 16px;
  color: #fff;
}

.edit-btn:hover {
  background-color: rgba(0, 255, 0, 0.2);
  border: 1px solid #00FF00;
}

.delete-btn:hover {
  background-color: rgba(255, 0, 0, 0.2);
  border: 1px solid #ff4444;
}

/* 链接样式 */
.card-link {
  display: block;
  color: inherit;
  text-decoration: none;
  width: 100%;
  height: 100%;
}

/* 图片容器 */
.card-image-wrapper {
  width: 100%;
  height: auto;
  overflow: hidden;
  background-color: #2a2a2a;
  position: relative;
}

.card-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.post-card:hover .card-image {
  transform: scale(1.05);
}

/* 内容区域 */
.card-content {
  padding: 15px;
  display: flex;
  flex-direction: column;
  min-height: 80px;
  position: relative;
}

.card-title {
  font-size: 1.1em;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #fff;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-excerpt {
  font-size: 0.9em;
  line-height: 1.5;
  color: #b0b0b0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin-bottom: 30px;
  flex-grow: 1;
}

/* 阅读量显示 */
.card-views {
  position: absolute;
  bottom: 10px;
  right: 15px;
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 15px;
  font-size: 0.8em;
  color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.eye-icon {
  width: 14px;
  height: 14px;
  margin-right: 4px;
  opacity: 0.8;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .post-card {
    margin-bottom: 12px;
    border-radius: 10px;
  }
  
  .card-content {
    padding: 12px;
    min-height: 70px;
  }
  
  .card-title {
    font-size: 1em;
    -webkit-line-clamp: 2;
  }
  
  .card-excerpt {
    font-size: 0.85em;
    -webkit-line-clamp: 2;
    margin-bottom: 25px;
  }
  
  .card-views {
    bottom: 8px;
    right: 12px;
    padding: 3px 6px;
    font-size: 0.75em;
  }
  
  .eye-icon {
    width: 12px;
    height: 12px;
  }
  
  .admin-controls {
    top: 6px;
    right: 6px;
    gap: 4px;
  }
  
  .admin-btn {
    width: 28px;
    height: 28px;
  }
  
  .admin-btn svg {
    width: 14px;
    height: 14px;
  }
}

@media (max-width: 480px) {
  .card-image-wrapper {
    height: auto;
  }
  
  .card-content {
    padding: 10px;
  }
  
  .card-title {
    font-size: 0.95em;
  }
  
  .card-excerpt {
    font-size: 0.8em;
  }
}
</style>
