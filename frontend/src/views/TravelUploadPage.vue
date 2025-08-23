<template>
  <div class="upload-page">
    <h1>📸 上传照片</h1>
    
    <div class="upload-container">
      <!-- 文件拖拽区域 -->
      <div 
        class="drop-zone"
        :class="{ 'drag-over': isDragOver, 'uploading': isUploading }"
        @drop="handleDrop"
        @dragover.prevent="handleDragOver"
        @dragenter.prevent="handleDragEnter"
        @dragleave.prevent="handleDragLeave"
        @click="triggerFileInput"
      >
        <div v-if="!isUploading" class="drop-zone-content">
          <div class="upload-icon">📷</div>
          <p class="drop-text">
            <span v-if="!isDragOver">点击选择图片或拖拽文件到此处</span>
            <span v-else>松开鼠标上传文件</span>
          </p>
          <p class="file-types">支持 JPG、PNG、GIF、WEBP 格式，单个文件最大 10MB</p>
        </div>
        
        <div v-if="isUploading" class="uploading-content">
          <LoadingAnimation />
          <p>正在上传中...</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p class="progress-text">{{ uploadProgress }}%</p>
        </div>
      </div>
      
      <!-- 隐藏的文件输入 -->
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <!-- 选中的文件预览 -->
      <div v-if="selectedFiles.length > 0 && !isUploading" class="selected-files">
        <h3>已选择的文件 ({{ selectedFiles.length }})</h3>
        <div class="file-preview-grid">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="index"
            class="file-preview-card"
          >
            <div class="preview-image-container">
              <img :src="file.preview" :alt="file.name" class="preview-image" />
              <button 
                class="remove-file-btn"
                @click="removeFile(index)"
                title="移除文件"
              >
                ×
              </button>
            </div>
            <div class="file-info">
              <input 
                v-model="file.title"
                class="file-title-input"
                placeholder="输入照片标题..."
                maxlength="100"
              />
              <select v-model="file.category" class="file-category-select">
                <option value="">选择分类</option>
                <option value="风景">风景</option>
                <option value="人物">人物</option>
                <option value="美食">美食</option>
                <option value="建筑">建筑</option>
                <option value="游戏截图">游戏截图</option>
                <option value="生活记录">生活记录</option>
                <option value="其他">其他</option>
              </select>
              <textarea 
                v-model="file.description"
                class="file-description-input"
                placeholder="添加描述（可选）..."
                rows="2"
                maxlength="500"
              ></textarea>
              <div class="file-meta">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 上传按钮 -->
        <div class="upload-actions">
          <button 
            class="upload-btn"
            @click="uploadFiles"
            :disabled="!canUpload"
          >
            <span v-if="!isUploading">🚀 上传 {{ selectedFiles.length }} 张照片</span>
            <span v-else>上传中...</span>
          </button>
          <button class="clear-btn" @click="clearFiles" :disabled="isUploading">
            清空列表
          </button>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import LoadingAnimation from '../components/LoadingAnimation.vue';

interface FileWithMeta {
  file: File;
  name: string;
  size: number;
  preview: string;
  title: string;
  category: string;
  description: string;
}

const router = useRouter();

const isDragOver = ref(false);
const isUploading = ref(false);
const uploadProgress = ref(0);
const selectedFiles = ref<FileWithMeta[]>([]);
const fileInput = ref<HTMLInputElement>();
const message = ref({ text: '', type: '' });

// 支持的文件类型
const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
const maxFileSize = 10 * 1024 * 1024; // 10MB

// 检查是否可以上传
const canUpload = computed(() => {
  return selectedFiles.value.length > 0 && 
         selectedFiles.value.every(f => f.title.trim() && f.category) && 
         !isUploading.value;
});

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 验证文件
const validateFile = (file: File): string | null => {
  if (!supportedTypes.includes(file.type)) {
    return `不支持的文件类型: ${file.type}`;
  }
  if (file.size > maxFileSize) {
    return `文件太大: ${formatFileSize(file.size)}，最大支持 ${formatFileSize(maxFileSize)}`;
  }
  return null;
};

// 创建文件预览
const createFilePreview = (file: File): Promise<FileWithMeta> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      resolve({
        file,
        name: file.name,
        size: file.size,
        preview: e.target?.result as string,
        title: file.name.replace(/\.[^/.]+$/, ''), // 去掉扩展名作为默认标题
        category: '',
        description: ''
      });
    };
    reader.readAsDataURL(file);
  });
};

// 处理文件选择
const processFiles = async (files: FileList | File[]) => {
  const validFiles: File[] = [];
  const errors: string[] = [];

  for (const file of Array.from(files)) {
    const error = validateFile(file);
    if (error) {
      errors.push(`${file.name}: ${error}`);
    } else {
      validFiles.push(file);
    }
  }

  if (errors.length > 0) {
    showMessage(`以下文件无法上传:\n${errors.join('\n')}`, 'error');
  }

  if (validFiles.length > 0) {
    const previews = await Promise.all(validFiles.map(createFilePreview));
    selectedFiles.value.push(...previews);
    showMessage(`成功添加 ${validFiles.length} 个文件`, 'success');
  }
};

// 拖拽处理
const handleDragEnter = (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = true;
};

const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
};

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault();
  if (!e.relatedTarget || !(e.currentTarget as Element).contains(e.relatedTarget as Node)) {
    isDragOver.value = false;
  }
};

const handleDrop = async (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = false;
  
  if (isUploading.value) return;
  
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    await processFiles(files);
  }
};

// 点击选择文件
const triggerFileInput = () => {
  if (!isUploading.value) {
    fileInput.value?.click();
  }
};

// 文件输入变化
const handleFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    await processFiles(files);
    target.value = ''; // 清空输入框，允许重复选择同一文件
  }
};

// 移除文件
const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1);
};

// 清空文件列表
const clearFiles = () => {
  selectedFiles.value = [];
};

// 上传文件
const uploadFiles = async () => {
  if (!canUpload.value) return;
  
  isUploading.value = true;
  uploadProgress.value = 0;
  
  try {
    const totalFiles = selectedFiles.value.length;
    let uploadedFiles = 0;
    
    for (const fileData of selectedFiles.value) {
      const formData = new FormData();
      formData.append('file', fileData.file);
      formData.append('title', fileData.title);
      formData.append('category', fileData.category);
      formData.append('description', fileData.description);
      
      const response = await fetch('/api/travel/upload', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `上传失败: ${response.statusText}`);
      }
      
      uploadedFiles++;
      uploadProgress.value = Math.round((uploadedFiles / totalFiles) * 100);
    }
    
    showMessage(`成功上传 ${totalFiles} 张照片！`, 'success');
    clearFiles();
    
    // 延迟跳转到主页面
    setTimeout(() => {
      router.push('/toolbox/travel');
    }, 2000);
    
  } catch (error) {
    console.error('上传失败:', error);
    const errorMessage = error instanceof Error ? error.message : '上传失败';
    showMessage(errorMessage, 'error');
  } finally {
    isUploading.value = false;
    uploadProgress.value = 0;
  }
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 5000);
};
</script>

<style scoped>
.upload-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

h1 {
  text-align: center;
  color: #fff;
  margin-bottom: 30px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-weight: bold;
}

.upload-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* 拖拽区域样式 */
.drop-zone {
  border: 3px dashed rgba(255, 182, 193, 0.5);
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
}

.drop-zone:hover:not(.uploading) {
  border-color: rgba(255, 182, 193, 0.8);
  background: rgba(255, 182, 193, 0.1);
}

.drop-zone.drag-over {
  border-color: #ff69b4;
  background: rgba(255, 105, 180, 0.2);
  transform: scale(1.02);
}

.drop-zone.uploading {
  cursor: not-allowed;
  border-color: rgba(255, 182, 193, 0.3);
}

.drop-zone-content .upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.drop-zone-content .drop-text {
  font-size: 18px;
  color: #fff;
  margin-bottom: 10px;
  font-weight: 600;
}

.drop-zone-content .file-types {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.uploading-content {
  color: #fff;
}

.uploading-content p {
  margin: 10px 0;
  font-size: 16px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  margin: 15px 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff69b4, #ff1493);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

/* 文件预览样式 */
.selected-files {
  margin-top: 30px;
}

.selected-files h3 {
  color: #fff;
  margin-bottom: 20px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.file-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.file-preview-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.preview-image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-file-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: rgba(220, 53, 69, 0.8);
  color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
}

.remove-file-btn:hover {
  background: rgba(220, 53, 69, 1);
}

.file-info {
  padding: 15px;
}

.file-title-input,
.file-category-select,
.file-description-input {
  width: 100%;
  margin-bottom: 10px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  box-sizing: border-box;
}

.file-title-input::placeholder,
.file-description-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.file-category-select {
  cursor: pointer;
}

.file-category-select option {
  background: #333;
  color: white;
}

.file-description-input {
  resize: vertical;
  min-height: 50px;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 5px;
}

.file-name {
  word-break: break-all;
  flex: 1;
  margin-right: 10px;
}

.file-size {
  white-space: nowrap;
}

/* 上传操作按钮 */
.upload-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.upload-btn,
.clear-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.upload-btn {
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.8), rgba(255, 20, 147, 0.8));
  color: white;
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  background: linear-gradient(135deg, rgba(255, 20, 147, 0.9), rgba(199, 21, 133, 0.9));
}

.upload-btn:disabled {
  background: rgba(108, 117, 125, 0.6);
  cursor: not-allowed;
  transform: none;
}

.clear-btn {
  background: rgba(108, 117, 125, 0.7);
  color: white;
}

.clear-btn:hover:not(:disabled) {
  background: rgba(84, 91, 98, 0.8);
  transform: translateY(-2px);
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  z-index: 10000;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 400px;
  white-space: pre-line;
}

.message.success {
  background: rgba(40, 167, 69, 0.9);
}

.message.error {
  background: rgba(220, 53, 69, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-page {
    padding: 15px;
    padding-top: 100px;
  }
  
  .upload-container {
    padding: 20px;
  }
  
  .drop-zone {
    padding: 40px 15px;
  }
  
  .drop-zone-content .upload-icon {
    font-size: 36px;
  }
  
  .drop-zone-content .drop-text {
    font-size: 16px;
  }
  
  .file-preview-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .upload-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .upload-btn,
  .clear-btn {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .upload-page {
    padding: 10px;
    padding-top: 120px;
  }
  
  h1 {
    font-size: 1.5em;
    margin-bottom: 20px;
  }
  
  .upload-container {
    padding: 15px;
  }
  
  .drop-zone {
    padding: 30px 10px;
  }
  
  .file-info {
    padding: 10px;
  }
  
  .upload-btn,
  .clear-btn {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>

