<template>
  <div class="drive-page-container">
    <div class="drive-header">
      <h1>驱动盘数据统计</h1>
      <p>查看、记录和分析您的驱动盘数据</p>
      <router-link to="/drive/add" class="btn btn-primary">
        <i class="fas fa-plus"></i> <span>添加驱动盘</span>
      </router-link>
    </div>

    <div class="filter-container">
      <div class="filter-header">
        <h3>筛选驱动盘</h3>
        <button id="toggleFilters" class="btn btn-sm btn-outline-primary">
          <i class="fas fa-filter"></i> <span>展开筛选</span>
        </button>
      </div>
      <div id="filterOptions" class="filter-options" style="display: none;">
        </div>
    </div>

    <div id="drive-list-container" class="drive-list-container grid-layout">
      <div v-if="isLoading" class="loading-spinner-wrapper">
        <div class="loading-spinner"></div>
      </div>
      
      <p v-if="error" class="error-message">{{ error }}</p>

      <div
        v-for="piece in visibleDrivePieces"
        :key="piece.drive_id"
        class="drive-card fade-in"
      >
        <div class="card-header">
          <img
            :src="getSetIcon(piece.set_name)"
            :alt="piece.set_name"
            class="set-icon"
            @error="onImageError"
          />
          <div class="header-text">
            <h4 class="set-name">{{ piece.set_name }}</h4>
            <p class="card-id">ID: {{ piece.drive_id }}</p>
          </div>
          <img
            :src="getPositionIcon(piece.position)"
            :alt="'位置 ' + piece.position"
            class="position-icon"
            @error="onImageError"
          />
        </div>
        <div class="card-body">
          <div class="main-stat">
            <div class="stat-icon"><i class="fa-solid fa-star"></i></div>
            <span class="stat-name">{{ piece.main_stat_name }}</span>
          </div>
          <div class="substats-list">
            <span v-for="substat in piece.substats" :key="substat">{{ substat }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isLoading" class="load-more-container">
      <span class="items-counter">显示 {{ visibleCardsCount }} / {{ allDrivePieces.length }} 个驱动盘</span>
      <div class="button-group">
        <button v-if="hasMore" @click="loadMore" class="load-more-btn">
          <i class="fas fa-arrow-down"></i> 加载更多
        </button>
        <button v-if="visibleCardsCount > batchSize" @click="showLess" class="load-more-btn">
          <i class="fas fa-arrow-up"></i> 收起
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface DrivePiece {
  drive_id: number;
  set_name: string;
  position: number;
  main_stat_name: string;
  substats: string[];
  created_at: string;
}

const allDrivePieces = ref<DrivePiece[]>([]);
const visibleCardsCount = ref(0);
const batchSize = 12;
const isLoading = ref(true);
const error = ref('');

const visibleDrivePieces = computed(() => {
  return allDrivePieces.value.slice(0, visibleCardsCount.value);
});

const hasMore = computed(() => {
  return visibleCardsCount.value < allDrivePieces.value.length;
});

// 获取图片路径
const getSetIcon = (setName: string) => {
  return `/images/sets/${setName}.png`;
};

const getPositionIcon = (position: number) => {
  return `/images/positions/${position}.png`;
};

// 图片加载失败时的处理
const onImageError = (e: Event) => {
  const target = e.target as HTMLImageElement;
  if (target) {
    // 替换为默认图片
    if (target.className === 'set-icon') {
      target.src = '/images/sets/default.png';
    } else if (target.className === 'position-icon') {
      target.src = '/images/positions/default.png';
    }
  }
};

const fetchDrivePieces = async () => {
  isLoading.value = true;
  try {
    const response = await fetch('/api/drive/pieces');
    if (!response.ok) {
      throw new Error('网络请求失败或服务器返回错误');
    }
    allDrivePieces.value = await response.json();
    visibleCardsCount.value = Math.min(batchSize, allDrivePieces.value.length);
  } catch (err: any) {
    error.value = '无法加载驱动盘数据，请稍后重试。';
    console.error('获取驱动盘数据失败:', err);
  } finally {
    isLoading.value = false;
  }
};

const loadMore = () => {
  visibleCardsCount.value = Math.min(visibleCardsCount.value + batchSize, allDrivePieces.value.length);
};

const showLess = () => {
  visibleCardsCount.value = batchSize;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

onMounted(() => {
  fetchDrivePieces();
});
</script>

<style scoped>
/* 页面级容器 */
.drive-page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* 头部样式 */
.drive-header {
  text-align: center;
  margin-bottom: 2rem;
}

.drive-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-heading);
}

.drive-header p {
  color: var(--color-text);
  margin-bottom: 1.5rem;
}

/* 按钮样式 */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  background-color: var(--primary-color);
  color: #fff;
  border-radius: 9999px;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* 加载动画容器 */
.loading-spinner-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px; /* 足够的高度来居中显示加载器 */
}

.loading-spinner {
    display: block;
    width: 50px;
    height: 50px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* 列表容器 */
.drive-list-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

/* 卡片样式 */
.drive-card {
    background-color: var(--card-bg); /* 请在你的 CSS 中定义 --card-bg */
    border-radius: 15px;
    padding: 20px;
    box-shadow: var(--shadow); /* 请在你的 CSS 中定义 --shadow */
    color: var(--text-primary);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 15px;
    transition: all 0.4s ease;
}

.drive-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 15px;
}

.set-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-text {
    flex-grow: 1;
}

.set-name {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
}

.card-id {
    margin: 0;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.position-icon {
    width: 40px;
    height: 40px;
}

.card-body {
    border-top: 1px solid var(--border-color);
    padding-top: 15px;
}

.main-stat {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 10px;
}

.main-stat .stat-icon {
    color: var(--primary-color);
}

.substats-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.substats-list span {
    background-color: var(--badge-bg); /* 请在你的 CSS 中定义 --badge-bg */
    color: var(--badge-text);
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
}

/* 加载更多和收起按钮容器 */
.load-more-container {
    text-align: center;
    margin-top: 30px;
}

.load-more-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 25px;
    font-weight: 600;
    border-radius: 30px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.load-more-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.load-more-btn i {
    transition: transform 0.3s ease;
}

.load-more-btn:hover i {
    transform: translateY(3px);
}

.items-counter {
    display: block;
    margin-top: 10px;
    font-size: 0.9rem;
    color: var(--color-text);
}
</style>