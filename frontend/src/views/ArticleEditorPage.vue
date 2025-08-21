<template>
  <div class="article-editor-container">
    <h1 class="editor-title">书写新文章</h1>
    <form @submit.prevent="submitArticle" class="article-form">
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
            <!-- 隐藏原生文件输入框，并添加 ref -->
            <input type="file" id="imageUpload" ref="fileInputRef" @change="handleFileUpload" accept="image/*" class="hidden-file-input">
            <!-- 自定义文件选择按钮 -->
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
        <textarea id="content" v-model="article.content" rows="15" required placeholder="在这里书写你的文章内容..."></textarea>
      </div>
      <div class="form-actions">
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? '发布中...' : '发布文章' }}
        </button>
        <router-link to="/blog" class="cancel-btn">取消</router-link>
      </div>
      <p v-if="submitError" class="error-message-submit">
        发布失败: {{ submitError }}
      </p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Define the article data model
const article = ref({
  title: '',
  imageUrl: '', // Final image URL
  excerpt: '',
  content: '',
});

// Store the URL of the currently selected image (can be preset or uploaded preview URL)
const selectedImageUrl = ref<string | null>(null);
// Store the name of the uploaded file
const uploadedFileName = ref<string | null>(null);
// Store the uploaded file object (for future actual upload)
const uploadedFile = ref<File | null>(null);

// Reference to the hidden file input
const fileInputRef = ref<HTMLInputElement | null>(null);

// Batch import local preset images
const modules = import.meta.glob('../assets/images/*.{jpg,png,webp}', { eager: true });
const presetImageUrls: string[] = Object.values(modules).map((module: any) => module.default || module);

// Debug code: Print the content of presetImageUrls
console.log('Editor Collected preset image URLs:', presetImageUrls);

const isSubmitting = ref(false); // 提交状态
const submitError = ref<string | null>(null); // 提交错误信息

// Select a preset image
const selectPresetImage = (url: string) => {
  selectedImageUrl.value = url;
  article.value.imageUrl = url; // Assign the selected URL to the article data
  uploadedFileName.value = null; // Clear uploaded file info
  uploadedFile.value = null;
  // Clear the file input field to prevent visual confusion
  if (fileInputRef.value) fileInputRef.value.value = '';
};

// Handle file upload
const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    uploadedFile.value = file;
    uploadedFileName.value = file.name;

    // Create a temporary URL for preview
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedImageUrl.value = e.target?.result as string;
      article.value.imageUrl = selectedImageUrl.value; // Preview URL as temporary imageUrl
    };
    reader.readAsDataURL(file);

    // Clear preset image selection
    // selectedPresetImage.value = null;
  } else {
    uploadedFile.value = null;
    uploadedFileName.value = null;
    selectedImageUrl.value = null;
    article.value.imageUrl = '';
  }
};

// Clear image selection
const clearImageSelection = () => {
  selectedImageUrl.value = null;
  article.value.imageUrl = '';
  uploadedFileName.value = null;
  uploadedFile.value = null;
  if (fileInputRef.value) fileInputRef.value.value = '';
};

// Trigger the hidden file input click
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

const submitArticle = async () => {
  isSubmitting.value = true;
  submitError.value = null;

  let finalImageUrl = article.value.imageUrl;

  // If the user hasn't selected an image, randomly assign a preset image
  if (!finalImageUrl) {
    if (presetImageUrls.length > 0) {
      const randomPresetIndex = Math.floor(Math.random() * presetImageUrls.length);
      finalImageUrl = presetImageUrls[randomPresetIndex];
    } else {
      // If no preset images, fallback to a generic placeholder
      finalImageUrl = 'https://placehold.co/300x200/cccccc/000000?text=No+Image'; 
    }
  }

  // Update the article's final image URL
  article.value.imageUrl = finalImageUrl;

  try {
    // **重要提示：目前图片上传只是前端预览，实际生产环境需要将 uploadedFile.value 发送到后端的文件上传API**
    // 后端文件上传API会返回一个可访问的URL，然后将该URL赋值给 article.imageUrl
    // **关键修改：将 localhost 替换为 backend 服务名**
    const response = await fetch('/api/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(article.value),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('文章发布成功:', result);
    router.push('/blog'); // 模拟保存成功后跳转回博客列表页
  } catch (error: any) {
    console.error('发布文章失败:', error);
    submitError.value = error.message || '未知错误';
  } finally {
    isSubmitting.value = false;
  }
};

// On page load, if there are presetImageUrls, you can optionally select the first one or a random one by default
onMounted(() => {
  if (presetImageUrls.length > 0 && !selectedImageUrl.value) {
    // You can set the first one as default here, or leave it for the user to select
    // selectPresetImage(presetImageUrls[0]); 
  }
});
</script>

<style scoped>
.article-editor-container {
  padding-top: 80px; /* Space for the navbar */
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
  width: calc(100% - 20px); /* Subtract padding */
  padding: 10px;
  border: 1px solid #333;
  border-radius: 5px;
  background-color: #222;
  color: #e0e0e0;
  font-size: 1em;
  box-sizing: border-box; /* Ensure padding doesn't increase width */
}

.article-form input[type="text"]:focus,
.article-form input[type="url"]:focus,
.article-form textarea:focus {
  outline: none;
  border-color: #00FF00; /* Green border on focus */
  box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
}

.article-form textarea {
  resize: vertical; /* Allow vertical resizing */
}

/* Cover image selection styles */
.image-selection-group {
  margin-bottom: 30px;
}

.image-preview-area {
  width: 100%;
  height: 200px; /* Fixed height for preview area */
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
  flex-wrap: wrap; /* Allow wrapping */
  gap: 20px;
}

.image-library,
.image-upload {
  flex: 1; /* Distribute space evenly */
  min-width: 280px; /* Minimum width */
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
  max-height: 150px; /* Limit height, make scrollable */
  overflow-y: auto;
  padding-right: 5px; /* Prevent scrollbar from obscuring content */
}

.thumbnail-wrapper {
  width: 80px; /* Fixed thumbnail width */
  height: 60px; /* Fixed thumbnail height */
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
  border-color: #00FF00; /* Green border when selected */
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

/* Hide the native file input */
.hidden-file-input {
  display: none;
}

/* Custom file upload button styles */
.custom-file-upload-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #00FF00; /* Green button */
  color: #000;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1em;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 255, 0, 0.3);
  margin-top: 10px; /* Space from the "Or upload image" heading */
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

/* New styles for submit error message */
.error-message-submit {
  color: #ff6b6b;
  text-align: right;
  font-size: 0.9em;
  margin-top: 10px;
}

/* Responsive adjustments */
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
  .custom-file-upload-btn { /* Apply responsive styles to custom button too */
    padding: 10px 20px;
    font-size: 1em;
  }
  .image-options {
    flex-direction: column; /* Vertical stacking on small screens */
  }
  .image-library,
  .image-upload {
    min-width: auto; /* Remove min-width constraint */
    width: 100%;
  }
}
</style>
