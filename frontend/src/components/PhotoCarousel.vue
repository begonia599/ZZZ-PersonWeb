<template>
  <div class="photo-carousel" v-if="photos.length > 0">
    <!-- 装饰性标题 -->
    <div class="carousel-header">
      <h3 class="carousel-title">
        <span class="title-icon">📸</span>
        <span class="title-text">美好瞬间</span>
        <span class="title-sparkle">✨</span>
      </h3>
      <div class="carousel-subtitle">随机展示海棠旅记</div>
    </div>

    <!-- 照片轮播容器 -->
    <div class="carousel-container" @mouseenter="pauseCarousel" @mouseleave="resumeCarousel">
      <!-- 照片展示区域 -->
      <div class="photo-display">
        <transition-group name="photo-fade" tag="div" class="photo-stack">
          <div
            v-for="(photo, index) in visiblePhotos"
            :key="photo.id"
            class="photo-card"
            :class="{ 
              'active': index === 0,
              'next': index === 1,
              'prev': index === 2
            }"
            @click="openPhotoModal(photo)"
          >
            <div class="photo-wrapper">
              <img 
                :src="photo.url" 
                :alt="photo.title" 
                class="photo-image"
                @load="handleImageLoad"
                @error="handleImageError"
              />
              <div class="photo-overlay">
                <div class="photo-info">
                  <h4 class="photo-title">{{ photo.title }}</h4>
                  <p class="photo-category">{{ photo.category }}</p>
                  <div class="photo-date">{{ formatDate(photo.created_at) }}</div>
                </div>
                <div class="view-hint">点击查看大图</div>
              </div>
              <!-- 动态装饰元素 -->
              <div class="floating-particles">
                <div class="particle" v-for="i in 6" :key="i" :style="getParticleStyle(i)"></div>
              </div>
            </div>
          </div>
        </transition-group>
      </div>

      <!-- 导航圆点 -->
      <div class="carousel-dots">
        <button
          v-for="(photo, index) in photos"
          :key="photo.id"
          class="dot"
          :class="{ active: index === currentIndex }"
          @click="goToSlide(index)"
          :title="photo.title"
        ></button>
      </div>

      <!-- 控制按钮 -->
      <div class="carousel-controls">
        <button class="control-btn prev-btn" @click="previousSlide" title="上一张">‹</button>
        <button class="control-btn next-btn" @click="nextSlide" title="下一张">›</button>
      </div>

      <!-- 播放/暂停按钮 -->
      <button class="play-pause-btn" @click="toggleAutoPlay" :title="isAutoPlaying ? '暂停' : '播放'">
        {{ isAutoPlaying ? '⏸️' : '▶️' }}
      </button>
    </div>

    <!-- 查看更多按钮 -->
    <div class="carousel-footer">
      <router-link to="/toolbox/travel/gallery" class="view-more-btn">
        <span class="btn-text">查看更多照片</span>
        <span class="btn-arrow">→</span>
      </router-link>
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
          <p class="date">{{ formatDate(selectedPhoto.created_at) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';

interface Photo {
  id: number;
  title: string;
  description?: string;
  category: string;
  url: string;
  thumbnail_url?: string;
  created_at: string;
}

const photos = ref<Photo[]>([]);
const currentIndex = ref(0);
const isAutoPlaying = ref(true);
const isPaused = ref(false);
const selectedPhoto = ref<Photo | null>(null);
const autoPlayInterval = ref<NodeJS.Timeout | null>(null);

// 显示的照片（当前、下一张、上一张）
const visiblePhotos = computed(() => {
  if (photos.value.length === 0) return [];
  
  const result = [];
  const total = photos.value.length;
  
  // 当前照片
  result.push(photos.value[currentIndex.value]);
  
  // 下一张照片
  if (total > 1) {
    const nextIndex = (currentIndex.value + 1) % total;
    result.push(photos.value[nextIndex]);
  }
  
  // 上一张照片
  if (total > 2) {
    const prevIndex = (currentIndex.value - 1 + total) % total;
    result.push(photos.value[prevIndex]);
  }
  
  return result;
});

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    month: 'long',
    day: 'numeric'
  });
};

// 获取粒子样式
const getParticleStyle = (index: number) => {
  const size = Math.random() * 4 + 2;
  const delay = Math.random() * 3;
  const duration = Math.random() * 3 + 2;
  const left = Math.random() * 100;
  const top = Math.random() * 100;
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  };
};

// 加载照片列表
const loadPhotos = async () => {
  try {
    const response = await fetch('/api/travel/photos?limit=10&sort=created_at&order=desc');
    if (response.ok) {
      const result = await response.json();
      if (Array.isArray(result)) {
        photos.value = result;
      } else if (result.photos && Array.isArray(result.photos)) {
        photos.value = result.photos;
      }
      
      // 随机打乱照片顺序
      if (photos.value.length > 0) {
        photos.value = shuffleArray([...photos.value]);
        startAutoPlay();
      }
    }
  } catch (error) {
    console.error('加载照片失败:', error);
  }
};

// 数组随机打乱
const shuffleArray = (array: Photo[]) => {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
};

// 下一张
const nextSlide = () => {
  if (photos.value.length > 0) {
    currentIndex.value = (currentIndex.value + 1) % photos.value.length;
  }
};

// 上一张
const previousSlide = () => {
  if (photos.value.length > 0) {
    currentIndex.value = (currentIndex.value - 1 + photos.value.length) % photos.value.length;
  }
};

// 跳转到指定幻灯片
const goToSlide = (index: number) => {
  currentIndex.value = index;
};

// 开始自动播放
const startAutoPlay = () => {
  if (autoPlayInterval.value) {
    clearInterval(autoPlayInterval.value);
  }
  if (isAutoPlaying.value && !isPaused.value) {
    autoPlayInterval.value = setInterval(() => {
      nextSlide();
    }, 4000); // 4秒切换一次
  }
};

// 停止自动播放
const stopAutoPlay = () => {
  if (autoPlayInterval.value) {
    clearInterval(autoPlayInterval.value);
    autoPlayInterval.value = null;
  }
};

// 切换自动播放
const toggleAutoPlay = () => {
  isAutoPlaying.value = !isAutoPlaying.value;
  if (isAutoPlaying.value) {
    startAutoPlay();
  } else {
    stopAutoPlay();
  }
};

// 暂停轮播
const pauseCarousel = () => {
  isPaused.value = true;
  stopAutoPlay();
};

// 恢复轮播
const resumeCarousel = () => {
  isPaused.value = false;
  if (isAutoPlaying.value) {
    startAutoPlay();
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

// 图片加载处理
const handleImageLoad = () => {
  // 图片加载成功的处理
};

const handleImageError = (event: Event) => {
  console.error('图片加载失败:', event);
};

onMounted(() => {
  loadPhotos();
});

onUnmounted(() => {
  stopAutoPlay();
  document.body.style.overflow = '';
});
</script>

<style scoped>
.photo-carousel {
  position: absolute;
  left: 20px;
  top: 550px; /* 进一步下移照片轮播组件 */
  width: 320px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.photo-carousel:hover {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

/* 标题区域 */
.carousel-header {
  text-align: center;
  margin-bottom: 20px;
}

.carousel-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.title-icon {
  animation: bounce 2s infinite;
}

.title-sparkle {
  animation: sparkle 3s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
  60% { transform: translateY(-3px); }
}

@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

.carousel-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

/* 轮播容器 */
.carousel-container {
  position: relative;
  margin-bottom: 20px;
}

.photo-display {
  position: relative;
  height: 240px;
  overflow: hidden;
  border-radius: 15px;
}

.photo-stack {
  position: relative;
  width: 100%;
  height: 100%;
}

.photo-card {
  position: absolute;
  width: 100%;
  height: 100%;
  cursor: pointer;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 15px;
  overflow: hidden;
}

.photo-card.active {
  z-index: 3;
  transform: translateX(0) scale(1);
  opacity: 1;
}

.photo-card.next {
  z-index: 2;
  transform: translateX(20px) scale(0.95);
  opacity: 0.7;
}

.photo-card.prev {
  z-index: 1;
  transform: translateX(-20px) scale(0.9);
  opacity: 0.4;
}

.photo-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 15px;
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
  padding: 20px 15px 15px 15px;
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.photo-card:hover .photo-overlay {
  transform: translateY(0);
}

.photo-info {
  margin-bottom: 8px;
}

.photo-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.photo-category {
  margin: 0 0 4px 0;
  font-size: 11px;
  color: #ff69b4;
  font-weight: 500;
}

.photo-date {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
}

.view-hint {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  font-style: italic;
}

/* 浮动粒子效果 */
.floating-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: float infinite ease-in-out;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

/* 导航圆点 */
.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 15px 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: scale(1.2);
}

.dot.active {
  background: #ff69b4;
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
}

/* 控制按钮 */
.carousel-controls {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.control-btn {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 16px;
  cursor: pointer;
  pointer-events: auto;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
}

.carousel-container:hover .control-btn {
  opacity: 1;
}

.control-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.prev-btn {
  margin-left: 10px;
}

.next-btn {
  margin-right: 10px;
}

/* 播放/暂停按钮 */
.play-pause-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
}

.carousel-container:hover .play-pause-btn {
  opacity: 1;
}

.play-pause-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

/* 查看更多按钮 */
.carousel-footer {
  text-align: center;
}

.view-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.8), rgba(255, 20, 147, 0.8));
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.view-more-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 105, 180, 0.4);
  background: linear-gradient(135deg, rgba(255, 20, 147, 0.9), rgba(199, 21, 133, 0.9));
}

.btn-arrow {
  transition: transform 0.3s ease;
}

.view-more-btn:hover .btn-arrow {
  transform: translateX(3px);
}

/* 过渡动画 */
.photo-fade-enter-active,
.photo-fade-leave-active {
  transition: all 0.6s ease;
}

.photo-fade-enter-from {
  opacity: 0;
  transform: translateX(100px) scale(0.8);
}

.photo-fade-leave-to {
  opacity: 0;
  transform: translateX(-100px) scale(0.8);
}

/* 照片模态框 */
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
  z-index: 99999; /* 提高z-index确保在所有组件之上 */
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
  background: rgba(0, 0, 0, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 30px;
  cursor: pointer;
  z-index: 100000; /* 确保关闭按钮在最顶层 */
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(220, 53, 69, 0.8);
  border-color: rgba(220, 53, 69, 0.5);
  transform: scale(1.1);
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .photo-carousel {
    width: 280px;
    left: 15px;
  }
}

@media (max-width: 768px) {
  .photo-carousel {
    position: relative;
    left: auto;
    top: auto;
    width: 100%;
    max-width: 320px;
    margin: 10px auto 20px auto; /* 减少上下边距 */
    padding: 15px;
    order: 1; /* 设置显示顺序 */
  }
  
  .photo-display {
    height: 180px; /* 减小移动端高度 */
  }
  
  .carousel-title {
    font-size: 16px;
  }
  
  .carousel-subtitle {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .photo-carousel {
    width: 95%;
    padding: 12px;
    margin: 8px auto 15px auto; /* 进一步减少边距 */
    order: 1;
  }
  
  .photo-display {
    height: 160px; /* 进一步减小小屏幕高度 */
  }
  
  .carousel-title {
    font-size: 14px;
  }
  
  .carousel-subtitle {
    font-size: 10px;
  }
  
  .view-more-btn {
    padding: 8px 16px;
    font-size: 12px;
  }
  
  .control-btn {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .play-pause-btn {
    width: 25px;
    height: 25px;
    font-size: 10px;
  }
  
  .dot {
    width: 6px;
    height: 6px;
  }
}
</style>
