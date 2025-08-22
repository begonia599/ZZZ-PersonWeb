<template>
  <div class="blog-page-container">
    <h2 class="page-title">博客</h2>
    <div class="write-article-section">
      <router-link to="/blog/new" class="write-article-btn">
        书写新文章
      </router-link>
    </div>
    <div class="post-grid-wrapper">
      <div v-if="isLoadingPosts" class="loading-overlay">
        <LoadingAnimation />
        </div>
      
      <div ref="postGridRef" :class="{'post-grid': true, 'loading-fade': isLoadingPosts}">
        <PostCard
          v-for="(post, index) in sortedPosts"
          :key="post.id || index"
          :id="post.id"
          :title="post.title"
          :excerpt="post.excerpt"
          :image-url="post.imageUrl"
          :views="post.views"
          :index="index"
          @refresh="fetchPosts"
          @delete="handlePostDelete"
        />
        <p v-if="posts.length === 0 && !isLoadingPosts" class="no-posts-message">
          暂无文章，快去书写第一篇吧！
        </p>
        <p v-if="fetchError" class="error-message">
          加载文章失败: {{ fetchError }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import PostCard from '../components/PostCard.vue';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import { apiFetch, API_ENDPOINTS } from '@/config/api';

interface Post {
  id: number;
  title: string;
  excerpt: string;
  content: string;
  imageUrl: string;
  createdAt: string;
  updatedAt: string;
  views: number;
}

const posts = ref<Post[]>([]);
const isLoadingPosts = ref(true);
const fetchError = ref<string | null>(null);
const postGridRef = ref<HTMLElement | null>(null);

// 按时间排序的文章列表 - 从新到旧
const sortedPosts = computed(() => {
  return [...posts.value].sort((a, b) => {
    // 如果有创建时间，按创建时间排序
    if (a.createdAt && b.createdAt) {
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    }
    // 否则按ID排序（较新的ID通常较大）
    return b.id - a.id;
  });
});

// 瀑布流布局函数
const initWaterfallLayout = async () => {
  await nextTick();
  if (!postGridRef.value) return;

  const container = postGridRef.value;
  const items = container.querySelectorAll('.post-card') as NodeListOf<HTMLElement>;
  
  if (items.length === 0) return;

  // 获取容器宽度和计算列数
  const containerWidth = container.offsetWidth - 20; // 减去padding
  const itemWidth = 280; // 每个卡片的宽度
  const gap = 20; // 卡片间隙
  const cols = Math.max(1, Math.floor((containerWidth + gap) / (itemWidth + gap)));
  
  if (cols <= 1) {
    // 单列布局时，重置为正常布局
    items.forEach(item => {
      item.style.position = 'static';
      item.style.left = '';
      item.style.top = '';
      item.style.width = 'auto';
      item.style.maxWidth = '400px';
      item.style.margin = '0 auto 15px auto';
      item.style.visibility = 'visible';
    });
    container.style.height = 'auto';
    container.style.transition = 'height 0.3s ease';
    return;
  }

  // 初始化每列的高度数组
  const columnHeights = new Array(cols).fill(0);
  
  // 设置容器为relative定位
  container.style.position = 'relative';
  
  // 计算居中偏移
  const totalWidth = cols * itemWidth + (cols - 1) * gap;
  const offsetX = Math.max(0, (containerWidth - totalWidth) / 2);
  
  // 先重置所有元素样式，等待图片加载
  items.forEach(item => {
    item.style.position = 'absolute';
    item.style.width = `${itemWidth}px`;
    item.style.visibility = 'hidden'; // 暂时隐藏，等待布局完成
  });

  // 等待图片加载完成后进行布局
  const layoutItems = () => {
    items.forEach((item) => {
      // 找到最短的列
      const shortestColumnIndex = columnHeights.indexOf(Math.min(...columnHeights));
      
      // 计算位置
      const left = offsetX + shortestColumnIndex * (itemWidth + gap);
      const top = columnHeights[shortestColumnIndex];
      
      // 应用定位
      item.style.left = `${left}px`;
      item.style.top = `${top}px`;
      item.style.visibility = 'visible'; // 显示元素
      
      // 更新列高度
      const itemHeight = item.offsetHeight;
      columnHeights[shortestColumnIndex] += itemHeight + gap;
    });
    
    // 设置容器高度，确保不小于最小高度
    const maxHeight = Math.max(...columnHeights);
    const finalHeight = Math.max(maxHeight, 600); // 至少600px高度
    container.style.height = `${finalHeight}px`;
    container.style.transition = 'height 0.3s ease'; // 平滑过渡
  };

  // 等待所有图片加载完成
  const images = container.querySelectorAll('img');
  let loadedImages = 0;
  const totalImages = images.length;

  if (totalImages === 0) {
    // 没有图片，直接布局
    setTimeout(layoutItems, 100);
  } else {
    const onImageLoad = () => {
      loadedImages++;
      if (loadedImages >= totalImages) {
        layoutItems();
      }
    };

    images.forEach(img => {
      if (img.complete) {
        onImageLoad();
      } else {
        img.addEventListener('load', onImageLoad);
        img.addEventListener('error', onImageLoad); // 错误时也继续
      }
    });

    // 最大等待时间2秒
    setTimeout(() => {
      if (loadedImages < totalImages) {
        layoutItems();
      }
    }, 2000);
  }
};

const fetchPosts = async () => {
  isLoadingPosts.value = true;
  fetchError.value = null;
  try {
    const data: Post[] = await apiFetch(API_ENDPOINTS.POSTS); 
    posts.value = data;
  } catch (error: any) {
    console.error('获取文章失败:', error);
    fetchError.value = error.message || '未知错误';
  } finally {
    isLoadingPosts.value = false;
    // 数据加载完成且loading结束后初始化瀑布流布局
    await nextTick();
    setTimeout(initWaterfallLayout, 500);
  }
};

// 处理文章删除
const handlePostDelete = (deletedPostId: number | string) => {
  posts.value = posts.value.filter(post => post.id !== deletedPostId);
  // 删除后重新布局
  setTimeout(initWaterfallLayout, 100);
};

// 监听窗口大小变化，重新布局
let resizeTimeout: number | null = null;
const handleResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  resizeTimeout = window.setTimeout(initWaterfallLayout, 300);
};

onMounted(() => {
  fetchPosts();
  window.addEventListener('resize', handleResize);
});

// 监听posts变化，重新布局
watch(() => posts.value.length, () => {
  if (posts.value.length > 0 && !isLoadingPosts.value) {
    setTimeout(initWaterfallLayout, 500);
  }
});

// 监听loading状态变化
watch(isLoadingPosts, (newVal) => {
  if (!newVal && posts.value.length > 0) {
    setTimeout(initWaterfallLayout, 300);
  }
});

// 组件卸载时清理事件监听
import { onUnmounted } from 'vue';
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
});
</script>

<style scoped>
.blog-page-container {
  padding-top: 80px;
  padding-bottom: 20px;
  width: 90%;
  max-width: 1400px;
  margin: 0 auto;
  box-sizing: border-box;
  position: relative;
  z-index: 5;
  color: #fff;
}

.page-title {
  font-size: 2.5em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
  color: #eee;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}

.write-article-section {
  text-align: center;
  margin-bottom: 30px;
}

.write-article-btn {
  display: inline-block;
  padding: 12px 25px;
  background-color: #00FF00;
  color: #000;
  text-decoration: none;
  border-radius: 9999px;
  transition: all 0.3s ease;
  font-weight: bold;
  font-size: 1.1em;
  box-shadow: 0 4px 10px rgba(0, 255, 0, 0.3);
}

.write-article-btn:hover {
  background-color: #00CC00;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 255, 0, 0.5);
}

.post-grid-wrapper {
  position: relative;
  min-height: 300px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: transparent; /* **修改：背景设置为透明** */
  z-index: 10;
  border-radius: 8px;
  transition: opacity 0.3s ease;
}

/* 移除了 .loading-text 样式，因为模板中不再有该元素 */

.post-grid {
  position: relative;
  width: 100%;
  transition: opacity 0.3s ease;
  padding: 0 10px;
  min-height: 800px; /* 预留足够的空间防止Footer闪烁 */
}

.post-grid.loading-fade {
  opacity: 0.3;
  pointer-events: none;
}

.no-posts-message, .error-message {
  text-align: center;
  font-size: 1.2em;
  color: #b0b0b0;
  margin-top: 50px;
  width: 100%;
}
.error-message {
  color: #ff6b6b;
}

/* 响应式布局现在由JavaScript处理 */

@media (max-width: 768px) {
  .blog-page-container {
    width: 95%;
    padding-top: 100px; /* 适应移动端导航栏高度 */
  }
  
  .page-title {
    font-size: 2em;
    margin-bottom: 20px;
  }
  
  .write-article-btn {
    padding: 10px 20px;
    font-size: 1em;
  }
  
  .post-grid {
    /* 移动端布局由JavaScript处理 */
  }
}

@media (max-width: 480px) {
  .blog-page-container {
    width: 98%;
    padding-top: 120px;
    padding-left: 10px;
    padding-right: 10px;
  }
  
  .page-title {
    font-size: 1.8em;
  }
  
  .write-article-btn {
    padding: 8px 16px;
    font-size: 0.95em;
  }
  
  .post-grid {
    /* 超小屏布局由JavaScript处理 */
  }
}
</style>