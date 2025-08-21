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
      
      <div :class="{'post-grid': true, 'loading-fade': isLoadingPosts}">
        <PostCard
          v-for="(post, index) in posts"
          :key="post.id || index"
          :id="post.id"
          :title="post.title"
          :excerpt="post.excerpt"
          :image-url="post.imageUrl"
          :views="post.views"
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
import { ref, onMounted } from 'vue';
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

const modules = import.meta.glob('../assets/images/*.{jpg,png,webp}', { eager: true });
const presetImageUrls: string[] = Object.values(modules).map((module: any) => module.default || module);

console.log('Collected preset image URLs:', presetImageUrls);

const posts = ref<Post[]>([]);
const isLoadingPosts = ref(true);
const fetchError = ref<string | null>(null);

const fetchPosts = async () => {
  isLoadingPosts.value = true;
  fetchError.value = null;
  try {
    // **关键修改：使用统一的 API 配置**
    const data: Post[] = await apiFetch(API_ENDPOINTS.POSTS); 
    posts.value = data;
  } catch (error: any) {
    console.error('获取文章失败:', error);
    fetchError.value = error.message || '未知错误';
  } finally {
    isLoadingPosts.value = false;
  }
};

onMounted(() => {
  fetchPosts();
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
  columns: 5 200px;
  column-gap: 15px;
  break-inside: avoid-column;
  transition: opacity 0.3s ease;
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

/* 响应式布局优化 */
@media (max-width: 1400px) {
  .post-grid {
    columns: 4 200px;
  }
}

@media (max-width: 1200px) {
  .post-grid {
    columns: 3 200px;
  }
}

@media (max-width: 900px) {
  .post-grid {
    columns: 2 200px;
  }
}

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
    columns: 1 300px; /* 移动端单列布局 */
    column-gap: 0;
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
    columns: 1 280px;
  }
}
</style>