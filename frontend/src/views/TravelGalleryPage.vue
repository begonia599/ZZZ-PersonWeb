<template>
  <div class="gallery-page">
    <h1>🖼️ 照片画廊</h1>
    
    <!-- 筛选和搜索区域 -->
    <div class="filter-section">
      <div class="filter-controls">
        <div class="search-box">
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="搜索照片标题或描述..."
            class="search-input"
            @input="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">🔍</button>
        </div>
        
        <div class="filter-controls-row">
          <select v-model="selectedCategory" @change="handleFilter" class="category-filter">
            <option value="">所有分类</option>
            <option value="风景">风景</option>
            <option value="人物">人物</option>
            <option value="美食">美食</option>
            <option value="建筑">建筑</option>
            <option value="游戏截图">游戏截图</option>
            <option value="生活记录">生活记录</option>
            <option value="其他">其他</option>
          </select>
          
          <select v-model="sortBy" @change="handleSort" class="sort-select">
            <option value="created_at_desc">最新上传</option>
            <option value="created_at_asc">最早上传</option>
            <option value="title_asc">标题 A-Z</option>
            <option value="title_desc">标题 Z-A</option>
          </select>
          
          <div class="view-controls">
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="setViewMode('grid')"
              title="网格视图"
            >
              ⊞
            </button>
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'list' }"
              @click="setViewMode('list')"
              title="列表视图"
            >
              ☰
            </button>
          </div>
        </div>
      </div>
      
      <div class="stats-info">
        <span class="photos-count">
          共找到 {{ filteredPhotos.length }} 张照片
          <span v-if="selectedCategory || searchQuery">(已筛选)</span>
        </span>
        <button v-if="selectedCategory || searchQuery" @click="clearFilters" class="clear-filters-btn">
          清除筛选
        </button>
      </div>
    </div>

    <!-- 照片列表 -->
    <div class="photos-section">
      <div v-if="isLoading" class="loading">
        <LoadingAnimation />
      </div>
      <div v-else-if="filteredPhotos.length === 0" class="no-data">
        <p v-if="!selectedCategory && !searchQuery">
          还没有上传任何照片，<router-link to="/toolbox/travel/upload">点击这里上传</router-link>！
        </p>
        <p v-else>
          没有找到符合条件的照片，试试调整筛选条件。
        </p>
      </div>
      <div v-else>
        <!-- 网格视图 -->
        <div v-if="viewMode === 'grid'" class="photos-grid">
          <div 
            v-for="photo in paginatedPhotos" 
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
                <div class="photo-actions">
                  <button @click.stop="editPhoto(photo)" class="action-btn edit-btn" title="编辑">
                    ✏️
                  </button>
                  <button @click.stop="deletePhoto(photo)" class="action-btn delete-btn" title="删除">
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 列表视图 -->
        <div v-if="viewMode === 'list'" class="photos-list">
          <div 
            v-for="photo in paginatedPhotos" 
            :key="photo.id"
            class="photo-list-item"
            @click="openPhotoModal(photo)"
          >
            <div class="list-image-container">
              <img :src="photo.thumbnail_url || photo.url" :alt="photo.title" class="list-image" />
            </div>
            <div class="list-content">
              <div class="list-main-info">
                <h3 class="list-title">{{ photo.title }}</h3>
                <p class="list-description" v-if="photo.description">{{ photo.description }}</p>
                <div class="list-meta">
                  <span class="list-category">{{ photo.category }}</span>
                  <span class="list-date">{{ formatDate(photo.created_at) }}</span>
                  <span class="list-size" v-if="photo.file_size">{{ formatFileSize(photo.file_size) }}</span>
                </div>
              </div>
              <div class="list-actions">
                <button @click.stop="editPhoto(photo)" class="action-btn edit-btn" title="编辑">
                  ✏️
                </button>
                <button @click.stop="deletePhoto(photo)" class="action-btn delete-btn" title="删除">
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页控件 -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            class="page-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            ‹ 上一页
          </button>
          
          <div class="page-numbers">
            <button 
              v-for="page in visiblePages"
              :key="page"
              class="page-number"
              :class="{ active: page === currentPage }"
              @click="typeof page === 'number' ? goToPage(page) : undefined"
              :disabled="typeof page !== 'number'"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            下一页 ›
          </button>
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
          <div class="file-info">
            <p class="date">拍摄时间: {{ formatDate(selectedPhoto.created_at) }}</p>
            <p class="size" v-if="selectedPhoto.file_size">文件大小: {{ formatFileSize(selectedPhoto.file_size) }}</p>
            <p class="type" v-if="selectedPhoto.file_type">文件类型: {{ selectedPhoto.file_type }}</p>
          </div>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
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

const router = useRouter();

const isLoading = ref(false);
const photos = ref<Photo[]>([]);
const selectedPhoto = ref<Photo | null>(null);
const message = ref({ text: '', type: '' });

// 筛选和搜索状态
const searchQuery = ref('');
const selectedCategory = ref('');
const sortBy = ref('created_at_desc');
const viewMode = ref<'grid' | 'list'>('grid');

// 分页状态
const currentPage = ref(1);
const itemsPerPage = 20;

// 筛选后的照片列表
const filteredPhotos = computed(() => {
  let result = [...photos.value];
  
  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(photo => 
      photo.title.toLowerCase().includes(query) ||
      (photo.description && photo.description.toLowerCase().includes(query))
    );
  }
  
  // 分类筛选
  if (selectedCategory.value) {
    result = result.filter(photo => photo.category === selectedCategory.value);
  }
  
  // 排序
  const [field, order] = sortBy.value.split('_');
  result.sort((a, b) => {
    let aValue: any = a[field as keyof Photo];
    let bValue: any = b[field as keyof Photo];
    
    // 处理未定义值
    if (aValue === undefined || aValue === null) aValue = '';
    if (bValue === undefined || bValue === null) bValue = '';
    
    if (field === 'created_at') {
      aValue = new Date(aValue as string).getTime();
      bValue = new Date(bValue as string).getTime();
    }
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }
    
    if (order === 'desc') {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    } else {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    }
  });
  
  return result;
});

// 分页计算
const totalPages = computed(() => Math.ceil(filteredPhotos.value.length / itemsPerPage));

const paginatedPhotos = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredPhotos.value.slice(start, start + itemsPerPage);
});

const visiblePages = computed(() => {
  const pages = [];
  const total = totalPages.value;
  const current = currentPage.value;
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i);
      pages.push('...');
      pages.push(total);
    } else if (current >= total - 3) {
      pages.push(1);
      pages.push('...');
      for (let i = total - 4; i <= total; i++) pages.push(i);
    } else {
      pages.push(1);
      pages.push('...');
      for (let i = current - 1; i <= current + 1; i++) pages.push(i);
      pages.push('...');
      pages.push(total);
    }
  }
  
  return pages;
});

// 监听筛选条件变化，重置到第一页
watch([searchQuery, selectedCategory, sortBy], () => {
  currentPage.value = 1;
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

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑在 computed 中自动处理
};

// 处理分类筛选
const handleFilter = () => {
  // 筛选逻辑在 computed 中自动处理
};

// 处理排序
const handleSort = () => {
  // 排序逻辑在 computed 中自动处理
};

// 清除筛选
const clearFilters = () => {
  searchQuery.value = '';
  selectedCategory.value = '';
  sortBy.value = 'created_at_desc';
};

// 设置视图模式
const setViewMode = (mode: 'grid' | 'list') => {
  viewMode.value = mode;
  localStorage.setItem('travel-gallery-view-mode', mode);
};

// 分页操作
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    // 滚动到顶部
    document.querySelector('.photos-section')?.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start' 
    });
  }
};

// 打开照片模态框
const openPhotoModal = (photo: Photo) => {
  selectedPhoto.value = photo;
  document.body.style.overflow = 'hidden';
};

// 关闭照片模态框
const closePhotoModal = () => {
  selectedPhoto.value = null;
  document.body.style.overflow = '';
};

// 编辑照片
const editPhoto = (photo: Photo) => {
  router.push(`/toolbox/travel/edit/${photo.id}`);
};

// 删除照片
const deletePhoto = async (photo: Photo) => {
  if (!confirm(`确定要删除照片"${photo.title}"吗？此操作不可撤销。`)) {
    return;
  }
  
  try {
    const response = await fetch(`/api/travel/photos/${photo.id}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || '删除失败');
    }
    
    // 从列表中移除
    const index = photos.value.findIndex(p => p.id === photo.id);
    if (index !== -1) {
      photos.value.splice(index, 1);
    }
    
    showMessage('照片删除成功', 'success');
    
  } catch (error) {
    console.error('删除照片失败:', error);
    const errorMessage = error instanceof Error ? error.message : '删除失败';
    showMessage(errorMessage, 'error');
  }
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
    const response = await fetch('/api/travel/photos');
    
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
  
  // 恢复上次的视图模式
  const savedViewMode = localStorage.getItem('travel-gallery-view-mode');
  if (savedViewMode === 'list' || savedViewMode === 'grid') {
    viewMode.value = savedViewMode;
  }
});
</script>

<style scoped>
.gallery-page {
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

/* 筛选区域样式 */
.filter-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.filter-controls {
  margin-bottom: 15px;
}

.search-box {
  display: flex;
  margin-bottom: 15px;
  max-width: 500px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px 0 0 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-btn {
  padding: 10px 15px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-left: none;
  border-radius: 0 8px 8px 0;
  background: rgba(255, 182, 193, 0.7);
  color: white;
  cursor: pointer;
  transition: background 0.3s ease;
}

.search-btn:hover {
  background: rgba(255, 105, 180, 0.8);
}

.filter-controls-row {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.category-filter,
.sort-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  cursor: pointer;
}

.category-filter option,
.sort-select option {
  background: #333;
  color: white;
}

.view-controls {
  display: flex;
  gap: 5px;
}

.view-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-btn:hover,
.view-btn.active {
  background: rgba(255, 182, 193, 0.7);
}

.stats-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.photos-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.clear-filters-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: rgba(220, 53, 69, 0.7);
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.clear-filters-btn:hover {
  background: rgba(220, 53, 69, 0.8);
}

/* 照片区域样式 */
.photos-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
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
}

.no-data a {
  color: #ff69b4;
  text-decoration: none;
}

.no-data a:hover {
  text-decoration: underline;
}

/* 网格视图样式 */
.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
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
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
  padding: 20px;
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.photo-card:hover .photo-overlay {
  transform: translateY(0);
}

.photo-info {
  flex: 1;
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

.photo-actions {
  display: flex;
  gap: 8px;
  flex-direction: column;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.delete-btn:hover {
  background: rgba(220, 53, 69, 0.8);
}

/* 列表视图样式 */
.photos-list {
  margin-bottom: 30px;
}

.photo-list-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.photo-list-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.list-image-container {
  flex-shrink: 0;
  width: 120px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
}

.list-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.list-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.list-main-info {
  flex: 1;
}

.list-title {
  margin: 0 0 5px 0;
  color: white;
  font-size: 16px;
  font-weight: 600;
}

.list-description {
  margin: 5px 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.list-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.list-category {
  color: #ff69b4;
  font-size: 12px;
  font-weight: 500;
}

.list-date,
.list-size {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.list-actions {
  display: flex;
  gap: 8px;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.page-btn,
.page-number {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.page-btn:hover:not(:disabled),
.page-number:hover:not(.active) {
  background: rgba(255, 182, 193, 0.3);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number.active {
  background: rgba(255, 182, 193, 0.7);
}

.page-numbers {
  display: flex;
  gap: 5px;
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

.file-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.file-info p {
  margin: 5px 0;
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
  .gallery-page {
    padding: 15px;
    padding-top: 100px;
  }
  
  .photos-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
  
  .filter-controls-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .photo-list-item {
    flex-direction: column;
    gap: 10px;
  }
  
  .list-image-container {
    width: 100%;
    height: 150px;
  }
  
  .list-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .list-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .gallery-page {
    padding: 10px;
    padding-top: 120px;
  }
  
  h1 {
    font-size: 1.5em;
    margin-bottom: 20px;
  }
  
  .filter-section {
    padding: 15px;
  }
  
  .photos-section {
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
  
  .pagination {
    gap: 5px;
  }
  
  .page-btn,
  .page-number {
    padding: 6px 10px;
    font-size: 12px;
  }
}
</style>

