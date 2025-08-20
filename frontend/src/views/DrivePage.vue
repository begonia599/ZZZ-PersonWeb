<template>
  <div class="drive-page">
    <h1>🎮 绝区零驱动盘统计工具</h1>
    
    <!-- 操作按钮区域 -->
    <div class="action-section">
      <router-link to="/toolbox/drive/add" class="action-btn add-btn">
        📤 添加驱动盘
      </router-link>
      <router-link to="/toolbox/drive/stats" class="action-btn stats-btn">
        📊 查看统计信息
      </router-link>
    </div>

    <!-- 驱动盘列表 -->
    <div class="drive-list-section">
      <div class="list-header">
        <h2>📋 驱动盘列表</h2>
        <div class="list-controls">
          <span class="showing-info">
            显示 {{ Math.min(displayCount, driveList.length) }} / {{ totalDrives }} 个
            ({{ displayRows }} / {{ Math.ceil(totalDrives / itemsPerRow) }} 行，每行 {{ itemsPerRow }} 个)
          </span>
          <button 
            v-if="displayCount < totalDrives && !isLoadingMore" 
            @click="loadMore" 
            class="load-more-btn"
            :disabled="isLoadingMore"
          >
            {{ isLoadingMore ? '加载中...' : `展开 ${nextExpandRows} 行 (${nextExpandRows * itemsPerRow} 个)` }}
          </button>
          <button 
            v-if="displayRows > 3" 
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
        <DriveCard 
          v-for="(drive, index) in displayedDrives" 
          :key="drive.drive_id"
          :drive="drive"
          :fade-in="index >= displayCount - (nextExpandRows * itemsPerRow)"
        />
      </div>
      
      <!-- 加载更多指示器 -->
      <div v-if="isLoadingMore && hasNextPage" class="loading-more">
        <div class="loading-more-animation">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <p>正在加载更多数据...</p>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import DriveCard from '../components/DriveCard.vue';

interface SubstatWithLevel {
  name: string;
  upgrade_count: number;
  is_original: boolean;
  substat_id: number;
}

interface DrivePiece {
  drive_id: number;
  set_name: string;
  position: number;
  main_stat_name: string;
  main_stat_level?: number;
  substats: string[];
  substats_with_levels?: SubstatWithLevel[];
  total_upgrades?: number;
  created_at: string;
  updated_at?: string;
}

interface PaginationInfo {
  current_page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

const isLoading = ref(false);
const isLoadingMore = ref(false);
const driveList = ref<DrivePiece[]>([]);
const pagination = ref<PaginationInfo | null>(null);
const displayRows = ref(3); // 初始显示3行
const itemsPerRow = ref(3); // 每行项目数，会根据屏幕宽度动态计算
const message = ref({ text: '', type: '' });

// 计算总驱动盘数量
const totalDrives = computed(() => {
  return pagination.value?.total_items || driveList.value.length;
});

// 是否还有下一页
const hasNextPage = computed(() => {
  return pagination.value?.has_next || false;
});

// 计算每行能显示多少个项目
const calculateItemsPerRow = () => {
  const container = document.querySelector('.drive-grid');
  if (!container) return 3;
  
  const containerWidth = container.clientWidth;
  const minItemWidth = 280; // 卡片最小宽度
  const gap = 24; // gap间距
  
  // 计算能容纳的列数
  const cols = Math.floor((containerWidth + gap) / (minItemWidth + gap));
  const result = Math.max(1, cols); // 至少1列
  
  console.log(`容器宽度: ${containerWidth}px, 计算列数: ${result}`);
  return result;
};

// 计算当前应该显示的项目数量
const displayCount = computed(() => {
  return displayRows.value * itemsPerRow.value;
});

// 计算当前显示的驱动盘
const displayedDrives = computed(() => {
  return driveList.value.slice(0, displayCount.value);
});

// 计算还有多少行可以展开
const remainingRows = computed(() => {
  const totalItems = totalDrives.value;
  const currentItems = displayCount.value;
  const remainingItems = totalItems - currentItems;
  return Math.ceil(remainingItems / itemsPerRow.value);
});

// 计算下次展开会显示多少行
const nextExpandRows = computed(() => {
  return Math.min(3, remainingRows.value);
});

// 加载更多（按行）
const loadMore = async () => {
  if (isLoadingMore.value) return;
  
  isLoadingMore.value = true;
  
  console.log(`展开前: 显示行数=${displayRows.value}, 每行=${itemsPerRow.value}, 总显示=${displayCount.value}`);
  
  try {
    // 如果本地数据不足，需要从服务器加载更多
    const neededItems = (displayRows.value + nextExpandRows.value) * itemsPerRow.value;
    
    if (driveList.value.length < neededItems && hasNextPage.value) {
      // 计算需要加载的页数
      const currentPage = pagination.value?.current_page || 1;
      const perPage = pagination.value?.per_page || 20;
      const nextPage = currentPage + 1;
      
      const response = await fetch(`/api/drive/pieces?page=${nextPage}&per_page=${perPage}`);
      const result = await response.json();
      
      if (response.ok) {
        // 合并新数据
        driveList.value.push(...result.drives);
        pagination.value = result.pagination;
        console.log(`从服务器加载了 ${result.drives.length} 个驱动盘`);
      } else {
        showMessage('加载更多数据失败', 'error');
        return;
      }
    }
    
    // 模拟加载延迟，提升用户体验
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // 增加显示行数
    displayRows.value += nextExpandRows.value;
    
    console.log(`展开后: 显示行数=${displayRows.value}, 每行=${itemsPerRow.value}, 总显示=${displayCount.value}`);
    
  } catch (error) {
    console.error('加载更多数据时出错:', error);
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isLoadingMore.value = false;
  }
};

// 收起列表
const collapseList = () => {
  displayRows.value = 3;
  // 滚动到列表顶部
  document.querySelector('.drive-list-section')?.scrollIntoView({ 
    behavior: 'smooth', 
    block: 'start' 
  });
};

// 更新每行项目数
const updateItemsPerRow = async () => {
  await nextTick(); // 等待DOM更新
  const newItemsPerRow = calculateItemsPerRow();
  if (newItemsPerRow !== itemsPerRow.value) {
    console.log(`每行项目数从 ${itemsPerRow.value} 更新为 ${newItemsPerRow}`);
    itemsPerRow.value = newItemsPerRow;
  }
};

// 窗口大小改变时重新计算
const handleResize = () => {
  updateItemsPerRow();
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 加载驱动盘列表
const loadDriveList = async () => {
  isLoading.value = true;
  try {
    const response = await fetch('/api/drive/pieces?page=1&per_page=20');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    console.log('API响应:', result);
    
    // 检查响应格式
    if (result.drives && Array.isArray(result.drives)) {
      driveList.value = result.drives;
      pagination.value = result.pagination;
      console.log(`加载了 ${result.drives.length} 个驱动盘，总共 ${result.pagination?.total_items || 0} 个`);
    } else if (Array.isArray(result)) {
      // 如果直接返回数组格式（向后兼容）
      driveList.value = result;
      pagination.value = null;
      console.log(`加载了 ${result.length} 个驱动盘（数组格式）`);
    } else {
      throw new Error('API响应格式不正确');
    }
    
    // 重置显示行数
    displayRows.value = 3;
    
    // 等待DOM渲染完成后再计算每行项目数
    await nextTick();
    setTimeout(() => {
      updateItemsPerRow();
    }, 100);
    
  } catch (error) {
    console.error('加载驱动盘列表时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`加载数据失败: ${errorMessage}`, 'error');
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  await loadDriveList();
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* 保持原有样式，只添加新的样式 */
.drive-page {
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
  border-bottom: 2px solid rgba(0, 123, 255, 0.6);
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

.add-btn {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.8), rgba(0, 86, 179, 0.8));
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, rgba(0, 86, 179, 0.9), rgba(0, 64, 133, 0.9));
}

.stats-btn {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.8), rgba(33, 136, 56, 0.8));
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.stats-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
  background: linear-gradient(135deg, rgba(33, 136, 56, 0.9), rgba(25, 103, 42, 0.9));
}

/* 驱动盘列表样式 */
.drive-list-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
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
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  white-space: nowrap;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
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
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.load-more-btn {
  background: rgba(40, 167, 69, 0.7);
}

.load-more-btn:hover:not(:disabled) {
  background: rgba(33, 136, 56, 0.8);
  transform: translateY(-1px);
}

.load-more-btn:disabled {
  background: rgba(108, 117, 125, 0.7);
  cursor: not-allowed;
}

.collapse-btn {
  background: rgba(108, 117, 125, 0.7);
}

.collapse-btn:hover {
  background: rgba(84, 91, 98, 0.8);
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
  color: #007bff;
  text-decoration: none;
}

.no-data a:hover {
  text-decoration: underline;
}

.drive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.loading-more {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.loading-more-animation {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
}

.loading-more-animation .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ECDC4;
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.loading-more-animation .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-more-animation .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
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
  .drive-page {
    padding: 15px;
  }
  
  .drive-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .list-controls {
    justify-content: center;
  }
  
  .showing-info {
    text-align: center;
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
</style>