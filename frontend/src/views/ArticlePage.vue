<template>
  <div class="article-page-container">
    <h1 class="article-title">{{ article.title }}</h1>
    <p class="article-meta">
      发布日期: {{ formattedCreatedAt }} | 作者: 秋海棠 
      <span v-if="article.updatedAt && article.createdAt !== article.updatedAt">(更新于: {{ formattedUpdatedAt }})</span>
    </p>
    <div class="article-content-wrapper">
      <!-- 加载动画显示区域 -->
      <div v-if="isLoadingArticle" class="loading-overlay-article">
        <LoadingAnimation />
        <!-- 移除“文章加载中...”的文字 -->
      </div>
      
      <!-- 文章内容，在加载时隐藏或半透明 -->
      <div :class="{'article-content': true, 'loading-fade': isLoadingArticle}">
        <p v-if="fetchError" class="error-message">加载文章失败: {{ fetchError }}</p>
        <div v-else>
          <img v-if="article.imageUrl" :src="article.imageUrl" alt="文章封面" class="article-cover-image">
          <p class="article-excerpt">{{ article.excerpt }}</p>
          <div class="full-content">{{ article.content }}</div>
        </div>
      </div>
    </div>
    <router-link to="/blog" class="back-to-blog-btn">返回博客</router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import { apiFetch, API_ENDPOINTS } from '@/config/api';

const route = useRoute();

interface Article {
  id: number | null;
  title: string;
  excerpt: string;
  content: string;
  imageUrl: string;
  createdAt: string;
  updatedAt: string;
}

const article = ref<Article>({
  id: null,
  title: '加载中...',
  excerpt: '',
  content: '',
  imageUrl: '',
  createdAt: '',
  updatedAt: '',
});

const isLoadingArticle = ref(true);
const fetchError = ref<string | null>(null);

const formattedCreatedAt = computed(() => {
  if (!article.value.createdAt) return '';
  const date = new Date(article.value.createdAt);
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
});

const formattedUpdatedAt = computed(() => {
  if (!article.value.updatedAt) return '';
  const date = new Date(article.value.updatedAt);
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
});

const fetchArticle = async (id: string | string[]) => {
  if (!id) {
    fetchError.value = '文章ID缺失。';
    isLoadingArticle.value = false;
    return;
  }

  isLoadingArticle.value = true;
  fetchError.value = null;

  try {
    // **关键修改：使用统一的 API 配置**
    const data: Article = await apiFetch(API_ENDPOINTS.POST_BY_ID(Number(id)));
    article.value = data;
  } catch (error: any) {
    console.error('获取文章详情失败:', error);
    fetchError.value = error.message || '未知错误';
    article.value.title = '文章加载失败';
    article.value.content = '无法加载文章内容，请稍后再试。';
    article.value.imageUrl = '';
  } finally {
    isLoadingArticle.value = false;
  }
};

onMounted(() => {
  fetchArticle(route.params.id);
});

watch(() => route.params.id, (newId) => {
  fetchArticle(newId);
});
</script>

<style scoped>
.article-page-container {
  padding-top: 80px;
  padding-bottom: 40px;
  width: 80%;
  max-width: 900px;
  margin: 0 auto;
  box-sizing: border-box;
  position: relative;
  z-index: 5;
  color: #e0e0e0;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  min-height: 500px;
}

.article-title {
  font-size: 2.8em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 15px;
  color: #fff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.article-meta {
  text-align: center;
  font-size: 0.9em;
  color: #b0b0b0;
  margin-bottom: 30px;
}

.article-content-wrapper {
  position: relative;
  min-height: 300px;
}

.loading-overlay-article {
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
  z-index: 15;
  border-radius: 8px;
  transition: opacity 0.3s ease;
}

/* 移除了 .loading-text-article 样式 */

.article-content {
  font-size: 1.1em;
  line-height: 1.8;
  margin-bottom: 40px;
  transition: opacity 0.3s ease;
}

.article-content.loading-fade {
  opacity: 0.3;
  pointer-events: none;
}

.article-cover-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 25px;
}

.article-excerpt {
  font-size: 1.1em;
  line-height: 1.6;
  color: #c0c0c0;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #333;
}

.article-content p {
  margin-bottom: 1em;
}

.full-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error-message {
  text-align: center;
  font-size: 1.2em;
  color: #ff6b6b;
  margin-top: 20px;
}

.back-to-blog-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #00FF00;
  color: #000;
  text-decoration: none;
  border-radius: 9999px;
  transition: all 0.3s ease;
  font-weight: bold;
  margin-top: 20px;
}

.back-to-blog-btn:hover {
  background-color: #00CC00;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 255, 0, 0.3);
}

@media (max-width: 768px) {
  .article-page-container {
    width: 90%;
    padding: 20px;
  }
  .article-title {
    font-size: 2em;
  }
  .article-content, .article-excerpt {
    font-size: 1em;
  }
}
</style>
