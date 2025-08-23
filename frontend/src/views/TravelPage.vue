<template>
  <div class="travel-page">
    <h1>🌸 海棠旅记</h1>
    
    <!-- 操作按钮区域 -->
    <div class="action-section">
      <router-link to="/toolbox/travel/upload" class="action-btn upload-btn">
        📸 上传照片
      </router-link>
      <router-link to="/toolbox/travel/gallery" class="action-btn gallery-btn">
        🖼️ 照片画廊
      </router-link>
    </div>

    <!-- 最新照片预览 -->
    <div class="recent-photos-section">
      <div class="section-header">
        <h2>📋 最新照片</h2>
        <div class="section-controls">
          <span class="showing-info">
            显示最近 {{ displayedPhotos.length }} 张照片
          </span>
          <router-link to="/toolbox/travel/gallery" class="view-all-btn">
            查看全部
          </router-link>
        </div>
      </div>
      
      <div v-if="isLoading" class="loading">
        <LoadingAnimation />
      </div>
      <div v-else-if="photos.length === 0" class="no-data">
        <p>还没有上传任何照片，<router-link to="/toolbox/travel/upload">点击这里上传</router-link>！</p>
      </div>
      <div v-else class="photos-grid">
        <div 
          v-for="photo in displayedPhotos" 
          :key="photo.id"
          class="photo-card"
          @click="openPhotoModal(photo)"
        >
          <div class="photo-image-container">
            <img :src="photo.thumbnail_url || photo.url" :alt="photo.title" class="photo-image" />
            <div class="photo-overlay">
              <div class="photo-info">
                <h3 class="photo-title">{{ photo.title }}</h3>
                <p class="photo-category">{{ photo.category }}</p>
                <p class="photo-date">{{ formatDate(photo.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 照片查看模态框 -->
    <div v-if="selectedPhoto" class="photo-modal" @click="closePhotoModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closePhotoModal">&times;</button>
        <img :src="selectedPhoto.url" :alt="selectedPhoto.title" class="modal-image" />
        <div class="modal-info">
          <h3>{{ selectedPhoto.title }}</h3>
          <p class="category">分类: {{ selectedPhoto.category }}</p>
          <p class="description" v-if="selectedPhoto.description">{{ selectedPhoto.description }}</p>
          <p class="date">拍摄时间: {{ formatDate(selectedPhoto.created_at) }}</p>
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
import { ref, onMounted, computed } from 'vue';
import LoadingAnimation from '../components/LoadingAnimation.vue';

interface Photo {
  id: number;
  title: string;
  description?: string;
  category: string;
  url: string;
  thumbnail_url?: string;
  created_at: string;
  file_size?: number;
  file_type?: string;
}

const isLoading = ref(false);
const photos = ref<Photo[]>([]);
const selectedPhoto = ref<Photo | null>(null);
const message = ref({ text: '', type: '' });

// 显示最近的8张照片
const displayedPhotos = computed(() => {
  return photos.value.slice(0, 8);
});

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 打开照片模态框
const openPhotoModal = (photo: Photo) => {
  selectedPhoto.value = photo;
  document.body.style.overflow = 'hidden'; // 防止背景滚动
};

// 关闭照片模态框
const closePhotoModal = () => {
  selectedPhoto.value = null;
  document.body.style.overflow = ''; // 恢复滚动
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 加载照片列表
const loadPhotos = async () => {
  isLoading.value = true;
  try {
    const response = await fetch('/api/travel/photos?limit=8&sort=created_at&order=desc');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (Array.isArray(result)) {
      photos.value = result;
    } else if (result.photos && Array.isArray(result.photos)) {
      photos.value = result.photos;
    } else {
      throw new Error('API响应格式不正确');
    }
    
  } catch (error) {
    console.error('加载照片列表时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`加载数据失败: ${errorMessage}`, 'error');
    // 设置一些示例数据用于演示
    photos.value = [];
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadPhotos();
});
</script>

<style scoped>
.travel-page {
  padding: 20px;
  max-width: 1400px;
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

h2 {
  color: #fff;
  margin-bottom: 20px;
  border-bottom: 2px solid rgba(255, 182, 193, 0.6);
  padding-bottom: 5px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

/* 操作按钮区域样式 */
.action-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.action-btn {
  display: inline-block;
  padding: 15px 30px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.upload-btn {
  background: linear-gradient(135deg, rgba(255, 182, 193, 0.8), rgba(255, 105, 180, 0.8));
  box-shadow: 0 4px 15px rgba(255, 182, 193, 0.3);
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 182, 193, 0.4);
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.9), rgba(255, 20, 147, 0.9));
}

.gallery-btn {
  background: linear-gradient(135deg, rgba(138, 43, 226, 0.8), rgba(75, 0, 130, 0.8));
  box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
}

.gallery-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(138, 43, 226, 0.4);
  background: linear-gradient(135deg, rgba(75, 0, 130, 0.9), rgba(72, 61, 139, 0.9));
}

/* 最新照片区域样式 */
.recent-photos-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h2 {
  margin: 0;
}

.section-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.showing-info {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  white-space: nowrap;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.view-all-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
  white-space: nowrap;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  background: rgba(138, 43, 226, 0.7);
}

.view-all-btn:hover {
  background: rgba(75, 0, 130, 0.8);
  transform: translateY(-1px);
}

.loading {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.8);
}

.no-data {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
  padding: 40px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.no-data a {
  color: #ff69b4;
  text-decoration: none;
}

.no-data a:hover {
  text-decoration: underline;
}

.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.photo-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.photo-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.photo-image-container {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.photo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.photo-card:hover .photo-image {
  transform: scale(1.05);
}

.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 20px;
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.photo-card:hover .photo-overlay {
  transform: translateY(0);
}

.photo-title {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.photo-category {
  margin: 0 0 5px 0;
  font-size: 12px;
  color: #ff69b4;
  font-weight: 500;
}

.photo-date {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

/* 照片模态框样式 */
.photo-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  padding: 20px;
  box-sizing: border-box;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  color: white;
  font-size: 30px;
  cursor: pointer;
  z-index: 10001;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.modal-info {
  padding: 20px;
  color: white;
  background: rgba(0, 0, 0, 0.5);
}

.modal-info h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #ff69b4;
}

.modal-info .category {
  margin: 5px 0;
  color: #ffb6c1;
  font-weight: 500;
}

.modal-info .description {
  margin: 10px 0;
  line-height: 1.5;
}

.modal-info .date {
  margin: 5px 0 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
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
}

.message.success {
  background: rgba(40, 167, 69, 0.9);
}

.message.error {
  background: rgba(220, 53, 69, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .travel-page {
    padding: 15px;
    padding-top: 100px;
  }
  
  .photos-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .section-controls {
    justify-content: center;
  }
  
  .action-section {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    max-width: 300px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .travel-page {
    padding: 10px;
    padding-top: 120px;
  }
  
  h1 {
    font-size: 1.5em;
    margin-bottom: 20px;
  }
  
  .action-btn {
    padding: 12px 20px;
    font-size: 14px;
  }
  
  .recent-photos-section {
    padding: 15px;
  }
  
  .photos-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .modal-content {
    max-width: 95vw;
    max-height: 95vh;
  }
  
  .modal-info {
    padding: 15px;
  }
}
</style>
