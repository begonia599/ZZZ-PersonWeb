<template>
  <div class="drive-page">
    <h1>🎮 绝区零驱动盘统计工具</h1>
    
    <!-- 操作按钮区域 -->
    <div class="action-section">
      <router-link to="/toolbox/drive/add" class="add-drive-btn">
        📤 添加驱动盘
      </router-link>
    </div>

    <!-- 统计展示区域 -->
    <div class="stats-section">
      <h2>📊 驱动盘统计</h2>
      <div class="stats-summary">
        <div class="stat-card">
          <h3>总数量</h3>
          <p class="stat-number">{{ driveList.length }}</p>
        </div>
        <div class="stat-card">
          <h3>套装分布</h3>
          <div class="set-distribution">
            <div v-for="(count, setName) in setDistribution" :key="setName" class="set-item">
              <span class="set-name">{{ setName }}</span>
              <span class="set-count">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 驱动盘列表 -->
    <div class="drive-list-section">
      <div class="list-header">
        <h2>📋 驱动盘列表</h2>
        <div class="list-controls">
          <span class="showing-info">
            显示 {{ Math.min(displayCount, driveList.length) }} / {{ driveList.length }} 个
          </span>
          <button 
            v-if="displayCount < driveList.length" 
            @click="loadMore" 
            class="load-more-btn"
            :disabled="isLoadingMore"
          >
            {{ isLoadingMore ? '加载中...' : `展开更多 (${Math.min(3, driveList.length - displayCount)})` }}
          </button>
          <button 
            v-if="displayCount > 3" 
            @click="collapseList" 
            class="collapse-btn"
          >
            收起列表
          </button>
        </div>
      </div>
      
      <div v-if="isLoading" class="loading">
        <LoadingAnimation />
      </div>
      <div v-else-if="driveList.length === 0" class="no-data">
        <p>还没有添加任何驱动盘，<router-link to="/toolbox/drive/add">点击这里添加</router-link>！</p>
      </div>
      <div v-else class="drive-grid">
        <div 
          v-for="(drive, index) in displayedDrives" 
          :key="drive.drive_id" 
          :class="['drive-card', { 'fade-in': index >= displayCount - 3 }]"
        >
          <div class="drive-header">
            <h3>{{ drive.set_name }}</h3>
            <span class="position-badge">{{ drive.position }}号位</span>
          </div>
          <div class="drive-main-stat">
            <strong>主词条：</strong>{{ drive.main_stat_name }}
          </div>
          <div class="drive-substats">
            <strong>副词条：</strong>
            <div class="substats-list">
              <span v-for="substat in drive.substats" :key="substat" class="substat-tag">
                {{ substat }}
              </span>
            </div>
          </div>
          <div class="drive-time">
            {{ formatTime(drive.created_at) }}
          </div>
        </div>
      </div>
      
      <!-- 加载更多指示器 -->
      <div v-if="isLoadingMore && displayCount < driveList.length" class="loading-more">
        <div class="loading-more-animation">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <p>正在加载更多...</p>
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

interface DrivePiece {
  drive_id: number;
  set_name: string;
  position: number;
  main_stat_name: string;
  substats: string[];
  created_at: string;
}

const isLoading = ref(false);
const isLoadingMore = ref(false);
const driveList = ref<DrivePiece[]>([]);
const displayCount = ref(3); // 初始显示3个
const message = ref({ text: '', type: '' });

// 计算套装分布
const setDistribution = computed(() => {
  const distribution: Record<string, number> = {};
  driveList.value.forEach(drive => {
    distribution[drive.set_name] = (distribution[drive.set_name] || 0) + 1;
  });
  return distribution;
});

// 计算当前显示的驱动盘
const displayedDrives = computed(() => {
  return driveList.value.slice(0, displayCount.value);
});

// 加载更多
const loadMore = async () => {
  isLoadingMore.value = true;
  
  // 模拟加载延迟，提升用户体验
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const nextCount = Math.min(displayCount.value + 3, driveList.value.length);
  displayCount.value = nextCount;
  
  isLoadingMore.value = false;
};

// 收起列表
const collapseList = () => {
  displayCount.value = 3;
  // 滚动到列表顶部
  document.querySelector('.drive-list-section')?.scrollIntoView({ 
    behavior: 'smooth', 
    block: 'start' 
  });
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  return date.toLocaleString('zh-CN');
};

// 加载驱动盘列表
const loadDriveList = async () => {
  isLoading.value = true;
  try {
    const response = await fetch('/api/drive/pieces');
    const result = await response.json();
    
    if (response.ok) {
      driveList.value = result;
      // 重置显示数量
      displayCount.value = Math.min(3, result.length);
    } else {
      showMessage('获取数据失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadDriveList();
});
</script>

<style scoped>
.drive-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

h2 {
  color: #444;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 5px;
}

/* 操作按钮区域样式 */
.action-section {
  text-align: center;
  margin-bottom: 30px;
}

.add-drive-btn {
  display: inline-block;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 15px 30px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
  transition: all 0.3s ease;
}

.add-drive-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

/* 统计区域样式 */
.stats-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stats-summary {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
}

.stat-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #007bff;
  margin: 0;
}

.set-distribution {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.set-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 10px;
  background: white;
  border-radius: 4px;
}

.set-count {
  font-weight: bold;
  color: #007bff;
}

/* 驱动盘列表样式 */
.drive-list-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.list-header h2 {
  margin: 0;
}

.list-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.showing-info {
  color: #666;
  font-size: 14px;
  white-space: nowrap;
}

.load-more-btn,
.collapse-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.load-more-btn {
  background: #28a745;
  color: white;
}

.load-more-btn:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
}

.load-more-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.collapse-btn {
  background: #6c757d;
  color: white;
}

.collapse-btn:hover {
  background: #545b62;
  transform: translateY(-1px);
}

.loading {
  text-align: center;
  padding: 40px;
}

.no-data {
  text-align: center;
  color: #777;
  font-style: italic;
  padding: 40px;
}

.no-data a {
  color: #007bff;
  text-decoration: none;
}

.no-data a:hover {
  text-decoration: underline;
}

.drive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.drive-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  border-left: 4px solid #007bff;
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.3s;
}

.drive-card.fade-in {
  animation: fadeInUp 0.5s ease-out;
}

.drive-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.drive-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.drive-header h3 {
  margin: 0;
  color: #333;
}

.position-badge {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.drive-main-stat {
  margin-bottom: 10px;
  color: #555;
}

.drive-substats {
  margin-bottom: 15px;
}

.substats-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
}

.substat-tag {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: #495057;
}

.drive-time {
  font-size: 12px;
  color: #888;
  text-align: right;
}

/* 加载更多动画 */
.loading-more {
  text-align: center;
  padding: 20px;
  color: #666;
}

.loading-more-animation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.loading-more-animation .dot {
  width: 8px;
  height: 8px;
  background: #007bff;
  border-radius: 50%;
  animation: loadingDot 1.4s infinite ease-in-out both;
}

.loading-more-animation .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-more-animation .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loadingDot {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 消息提示样式 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.message.success {
  background: #28a745;
}

.message.error {
  background: #dc3545;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .drive-page {
    padding: 15px;
  }
  
  .stats-summary {
    grid-template-columns: 1fr;
  }
  
  .drive-grid {
    grid-template-columns: 1fr;
  }
  
  .list-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .list-controls {
    justify-content: center;
  }
  
  .load-more-btn,
  .collapse-btn {
    flex: 1;
    min-width: 120px;
  }
}
</style>