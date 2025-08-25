<template>
  <div class="article-editor-container">
    <h1 class="editor-title">编辑文章</h1>
    
    <div v-if="loading" class="loading-container">
      <LoadingAnimation />
      <p>正在加载文章...</p>
    </div>
    
    <form v-else @submit.prevent="submitArticle" class="article-form">
      <div class="form-group">
        <label for="title">文章标题</label>
        <input type="text" id="title" v-model="article.title" required placeholder="请输入文章标题">
      </div>

      <!-- 封面图片选择区域 -->
      <div class="form-group image-selection-group">
        <label>封面图片</label>
        <div class="image-preview-area">
          <img v-if="selectedImageUrl" :src="selectedImageUrl" alt="封面预览" class="selected-image-preview">
          <div v-else class="no-image-placeholder">
            <span>未选择图片</span>
          </div>
        </div>

        <div class="image-options">
          <!-- 图片库选择 -->
          <div class="image-library">
            <h3>选择图片库图片:</h3>
            <div class="image-thumbnails">
              <div
                v-for="(url, index) in presetImageUrls"
                :key="index"
                class="thumbnail-wrapper"
                :class="{ 'selected': selectedImageUrl === url }"
                @click="selectPresetImage(url)"
              >
                <img :src="url" alt="预设图片" class="thumbnail">
              </div>
            </div>
            <button type="button" @click="clearImageSelection" class="clear-selection-btn">清除选择</button>
          </div>

          <!-- 或上传图片 -->
          <div class="image-upload">
            <h3>或上传图片:</h3>
            <input type="file" id="imageUpload" ref="fileInputRef" @change="handleFileUpload" accept="image/*" class="hidden-file-input">
            <button type="button" @click="triggerFileInput" class="custom-file-upload-btn">
              选择文件
            </button>
            <p v-if="uploadedFileName" class="uploaded-file-info">已选择文件: {{ uploadedFileName }}</p>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="excerpt">文章简介</label>
        <textarea id="excerpt" v-model="article.excerpt" rows="3" required placeholder="请输入文章简介"></textarea>
      </div>
      
      <div class="form-group">
        <label for="content">文章内容</label>
        
        <!-- 格式选择器 -->
        <div class="content-format-selector">
          <button 
            type="button"
            :class="['format-btn', { active: contentFormat === 'plain' }]"
            @click="contentFormat = 'plain'"
          >
            纯文本
          </button>
          <button 
            type="button"
            :class="['format-btn', { active: contentFormat === 'markdown' }]"
            @click="contentFormat = 'markdown'"
          >
            Markdown
          </button>
        </div>

        <!-- 纯文本编辑器 -->
        <textarea 
          v-if="contentFormat === 'plain'"
          id="content" 
          v-model="article.content" 
          rows="15" 
          required 
          placeholder="在这里书写你的文章内容..."
          class="plain-text-editor"
        ></textarea>

        <!-- Markdown 编辑器 -->
        <MarkdownEditor 
          v-if="contentFormat === 'markdown'"
          v-model="article.content"
          placeholder="在这里使用 Markdown 语法书写你的文章内容..."
          class="markdown-editor-wrapper"
        />
      </div>
      
      <div class="form-actions">
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? '更新中...' : '更新文章' }}
        </button>
        <router-link to="/blog" class="cancel-btn">取消</router-link>
      </div>
      
      <p v-if="submitError" class="error-message-submit">
        更新失败: {{ submitError }}
      </p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import MarkdownEditor from '../components/MarkdownEditor.vue';
import { apiFetch, API_ENDPOINTS } from '@/config/api';

const router = useRouter();
const route = useRoute();

// 文章数据模型
const article = ref({
  title: '',
  imageUrl: '',
  excerpt: '',
  content: '',
});

// 内容格式选择
const contentFormat = ref<'plain' | 'markdown'>('markdown');

// 图片相关
const selectedImageUrl = ref<string | null>(null);
const uploadedFileName = ref<string | null>(null);
const uploadedFile = ref<File | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);

// 批量导入本地预设图片
const modules = import.meta.glob('../assets/images/*.{jpg,png,webp}', { eager: true });
const presetImageUrls: string[] = Object.values(modules).map((module: any) => module.default || module);

// 状态管理
const loading = ref(true);
const isSubmitting = ref(false);
const submitError = ref<string | null>(null);

// 获取文章ID
const articleId = computed(() => {
  return Number(route.params.id);
});

// 加载文章数据
const loadArticle = async () => {
  loading.value = true;
  try {
    const data = await apiFetch(API_ENDPOINTS.POST_BY_ID(articleId.value));
    article.value = {
      title: data.title,
      imageUrl: data.imageUrl || data.image_url || '',
      excerpt: data.excerpt,
      content: data.content,
    };
    
    // 设置选中的图片
    if (article.value.imageUrl) {
      selectedImageUrl.value = article.value.imageUrl;
    }
    
  } catch (error: any) {
    console.error('加载文章失败:', error);
    alert('加载文章失败: ' + (error.message || '未知错误'));
    router.push('/blog');
  } finally {
    loading.value = false;
  }
};

// 选择预设图片
const selectPresetImage = (url: string) => {
  selectedImageUrl.value = url;
  article.value.imageUrl = url;
  uploadedFileName.value = null;
  uploadedFile.value = null;
  if (fileInputRef.value) fileInputRef.value.value = '';
};

// 处理文件上传
const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    uploadedFile.value = file;
    uploadedFileName.value = file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
      selectedImageUrl.value = e.target?.result as string;
      article.value.imageUrl = selectedImageUrl.value;
    };
    reader.readAsDataURL(file);
  } else {
    uploadedFile.value = null;
    uploadedFileName.value = null;
    selectedImageUrl.value = null;
    article.value.imageUrl = '';
  }
};

// 清除图片选择
const clearImageSelection = () => {
  selectedImageUrl.value = null;
  article.value.imageUrl = '';
  uploadedFileName.value = null;
  uploadedFile.value = null;
  if (fileInputRef.value) fileInputRef.value.value = '';
};

// 触发文件输入
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

// 提交文章更新
const submitArticle = async () => {
  isSubmitting.value = true;
  submitError.value = null;

  let finalImageUrl = article.value.imageUrl;

  // 如果没有选择图片，随机分配一张预设图片
  if (!finalImageUrl && presetImageUrls.length > 0) {
    const randomIndex = Math.floor(Math.random() * presetImageUrls.length);
    finalImageUrl = presetImageUrls[randomIndex];
  }

  article.value.imageUrl = finalImageUrl;

  try {
    const result = await apiFetch(API_ENDPOINTS.UPDATE_POST(articleId.value), {
      method: 'PUT',
      body: JSON.stringify(article.value),
    });

    console.log('文章更新成功:', result);
    router.push('/blog');
  } catch (error: any) {
    console.error('更新文章失败:', error);
    submitError.value = error.message || '未知错误';
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  loadArticle();
});
</script>

<style scoped>
/* 复用ArticleEditorPage的样式 */
.article-editor-container {
  padding-top: 80px;
  padding-bottom: 40px;
  width: 90%;
  max-width: 800px;
  margin: 0 auto;
  box-sizing: border-box;
  position: relative;
  z-index: 5;
  color: #e0e0e0;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.editor-title {
  font-size: 2.5em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
  color: #fff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #fff;
}

.loading-container p {
  margin-top: 20px;
  font-size: 1.1em;
}

.article-form .form-group {
  margin-bottom: 20px;
}

.article-form label {
  display: block;
  margin-bottom: 8px;
  font-size: 1.1em;
  color: #fff;
}

.article-form input[type="text"],
.article-form input[type="url"],
.article-form textarea {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #333;
  border-radius: 5px;
  background-color: #222;
  color: #e0e0e0;
  font-size: 1em;
  box-sizing: border-box;
}

.article-form input[type="text"]:focus,
.article-form input[type="url"]:focus,
.article-form textarea:focus {
  outline: none;
  border-color: #00FF00;
  box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
}

.article-form textarea {
  resize: vertical;
}

/* 图片选择样式 */
.image-selection-group {
  margin-bottom: 30px;
}

.image-preview-area {
  width: 100%;
  height: 200px;
  background-color: #222;
  border: 1px dashed #555;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  margin-bottom: 20px;
  border-radius: 5px;
}

.selected-image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image-placeholder {
  color: #888;
  font-size: 1.2em;
}

.image-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.image-library,
.image-upload {
  flex: 1;
  min-width: 280px;
  background-color: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 15px;
}

.image-library h3,
.image-upload h3 {
  font-size: 1.1em;
  color: #fff;
  margin-top: 0;
  margin-bottom: 15px;
}

.image-thumbnails {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
  max-height: 150px;
  overflow-y: auto;
  padding-right: 5px;
}

.thumbnail-wrapper {
  width: 80px;
  height: 60px;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
}

.thumbnail-wrapper:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.thumbnail-wrapper.selected {
  border-color: #00FF00;
  box-shadow: 0 0 8px rgba(0, 255, 0, 0.6);
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.clear-selection-btn {
  background-color: #555;
  color: #fff;
  border: none;
  padding: 8px 15px;
  border-radius: 9999px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
  font-size: 0.9em;
  margin-top: 10px;
}

.clear-selection-btn:hover {
  background-color: #777;
  transform: translateY(-1px);
}

.hidden-file-input {
  display: none;
}

.custom-file-upload-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #00FF00;
  color: #000;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1em;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 255, 0, 0.3);
  margin-top: 10px;
}

.custom-file-upload-btn:hover {
  background-color: #00CC00;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 255, 0, 0.5);
}

.uploaded-file-info {
  font-size: 0.9em;
  color: #b0b0b0;
  margin-top: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.submit-btn,
.cancel-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 9999px;
  font-weight: bold;
  font-size: 1.1em;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  text-align: center;
}

.submit-btn {
  background-color: #00FF00;
  color: #000;
  box-shadow: 0 4px 10px rgba(0, 255, 0, 0.3);
}

.submit-btn:hover {
  background-color: #00CC00;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 255, 0, 0.5);
}

.submit-btn:disabled {
  background-color: #666;
  color: #999;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background-color: #555;
  color: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.cancel-btn:hover {
  background-color: #777;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.5);
}

.error-message-submit {
  color: #ff6b6b;
  text-align: right;
  font-size: 0.9em;
  margin-top: 10px;
}

/* 内容格式选择器样式 */
.content-format-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.format-btn {
  padding: 8px 16px;
  border: 1px solid #333;
  border-radius: 4px;
  background-color: #2a2a2a;
  color: #e0e0e0;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9em;
}

.format-btn:hover {
  background-color: #333;
  border-color: #00FF00;
}

.format-btn.active {
  background-color: #00FF00;
  color: #000;
  border-color: #00FF00;
}

/* 纯文本编辑器样式 */
.plain-text-editor {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #333;
  border-radius: 5px;
  background-color: #222;
  color: #e0e0e0;
  font-size: 1em;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
}

.plain-text-editor:focus {
  outline: none;
  border-color: #00FF00;
  box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
}

/* Markdown 编辑器包装器样式 */
.markdown-editor-wrapper {
  width: 100%;
  min-height: 400px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .article-editor-container {
    width: 95%;
    padding: 20px;
  }
  
  .editor-title {
    font-size: 2em;
  }
  
  .article-form input,
  .article-form textarea {
    font-size: 0.95em;
  }
  
  .submit-btn,
  .cancel-btn,
  .custom-file-upload-btn {
    padding: 10px 20px;
    font-size: 1em;
  }
  
  .image-options {
    flex-direction: column;
  }
  
  .image-library,
  .image-upload {
    min-width: auto;
    width: 100%;
  }
}
</style>
