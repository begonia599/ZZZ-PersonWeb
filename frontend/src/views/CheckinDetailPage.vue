<template>
  <div class="checkin-detail-page">
    <div v-if="isLoading" class="loading">
      <LoadingAnimation />
    </div>
    
    <div v-else-if="task" class="detail-container">
      <!-- 任务信息头部 -->
      <div class="task-header">
        <h1>{{ task.title }}</h1>
        <div class="task-status">
          <span v-if="isTaskCompleted" class="status-badge completed">已完成</span>
          <span v-else-if="isTaskActive" class="status-badge active">进行中</span>
          <span v-else class="status-badge pending">未开始</span>
        </div>
      </div>

      <!-- 任务统计信息 -->
      <div class="task-stats">
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-content">
            <div class="stat-label">打卡频率</div>
            <div class="stat-value">{{ getFrequencyText(task.frequency, task.custom_days) }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-label">完成进度</div>
            <div class="stat-value">{{ task.is_long_term ? `已打卡 ${task.checked_count} 次` : `${task.checked_count}/${task.total_count}` }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <div class="stat-label">时间周期</div>
            <div class="stat-value">{{ task.is_long_term ? '长期任务' : formatDateRange(task.start_date, task.end_date) }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🔥</div>
          <div class="stat-content">
            <div class="stat-label">{{ task.is_long_term ? '最近打卡' : '完成率' }}</div>
            <div class="stat-value">{{ task.is_long_term ? (task.last_checkin_date ? new Date(task.last_checkin_date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : '未打卡') : getCompletionRate + '%' }}</div>
          </div>
        </div>
      </div>

      <!-- 进度条/打卡次数 -->
      <div class="progress-section">
        <div v-if="task.is_long_term" class="progress-header">
          <span class="progress-label">累计打卡</span>
          <span class="progress-percentage">{{ task.checked_count }} 次</span>
        </div>
        <div v-else>
          <div class="progress-header">
            <span class="progress-label">总体进度</span>
            <span class="progress-percentage">{{ getCompletionRate }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: getCompletionRate + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 打卡记录列表 -->
      <div class="records-section">
        <div class="section-header">
          <h2>📝 打卡记录</h2>
          <div class="section-controls">
            <span class="showing-info">
              共 {{ records.length }} 条记录
            </span>
          </div>
        </div>
        
        <div v-if="records.length === 0" class="no-records">
          <p>还没有打卡记录</p>
        </div>
        <div v-else class="records-list">
          <div 
            v-for="record in records" 
            :key="record.id"
            class="record-card"
          >
            <div class="record-header">
              <div class="record-date">
                <span class="date-icon">📅</span>
                <span class="date-text">{{ formatDateTime(record.created_at) }}</span>
              </div>
              <button @click="deleteRecord(record.id)" class="delete-record-btn">
                🗑️
              </button>
            </div>
            
            <div v-if="record.note" class="record-note">
              <div class="note-label">备注：</div>
              <div class="note-content">{{ record.note }}</div>
            </div>
            
            <div v-if="record.image_url" class="record-image">
              <img 
                :src="record.image_url" 
                :alt="'打卡图片 ' + record.id" 
                @click="openImageModal(record.image_url)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button 
          v-if="!isTaskCompleted && isTaskActive" 
          @click="goToCheckin" 
          class="action-btn primary-btn"
          :disabled="isCheckedToday"
        >
          {{ isCheckedToday ? '✓ 今日已打卡' : '📝 立即打卡' }}
        </button>
        <button 
          v-if="task.is_long_term && !task.is_terminated && isTaskActive"
          @click="terminateTask" 
          class="action-btn terminate-btn"
        >
          ⏸️ 终止任务
        </button>
        <button @click="goBack" class="action-btn secondary-btn">
          返回列表
        </button>
      </div>
    </div>

    <!-- 图片查看模态框 -->
    <div v-if="modalImage" class="image-modal" @click="closeImageModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closeImageModal">&times;</button>
        <img :src="modalImage" alt="打卡图片" />
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
import { useRouter, useRoute } from 'vue-router';
import LoadingAnimation from '../components/LoadingAnimation.vue';

interface CheckinTask {
  id: number;
  title: string;
  frequency: string;
  custom_days?: number;
  start_date: string;
  end_date: string;
  total_count: number;
  checked_count: number;
  last_checkin_date?: string;
  created_at: string;
  is_long_term?: boolean;
  is_terminated?: boolean;
}

interface CheckinRecord {
  id: number;
  task_id: number;
  checkin_date: string;
  note?: string;
  image_url?: string;
  created_at: string;
}

const router = useRouter();
const route = useRoute();
const isLoading = ref(true);
const task = ref<CheckinTask | null>(null);
const records = ref<CheckinRecord[]>([]);
const message = ref({ text: '', type: '' });
const modalImage = ref<string | null>(null);

const taskId = computed(() => {
  return parseInt(route.params.id as string, 10);
});

// 计算属性
const isTaskCompleted = computed(() => {
  if (!task.value) return false;
  // 长期任务且已终止
  if (task.value.is_long_term && task.value.is_terminated) {
    return true;
  }
  // 长期任务且未终止
  if (task.value.is_long_term && !task.value.is_terminated) {
    return false;
  }
  const endDate = new Date(task.value.end_date + 'T00:00:00');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return endDate < today || task.value.checked_count >= task.value.total_count;
});

const isTaskActive = computed(() => {
  if (!task.value) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // 长期任务且未终止
  if (task.value.is_long_term && !task.value.is_terminated) {
    const startDate = new Date(task.value.start_date + 'T00:00:00');
    return startDate <= today;
  }
  const startDate = new Date(task.value.start_date + 'T00:00:00');
  const endDate = new Date(task.value.end_date + 'T00:00:00');
  return startDate <= today && endDate >= today;
});

const isCheckedToday = computed(() => {
  if (!task.value || !task.value.last_checkin_date) return false;
  const lastCheckin = new Date(task.value.last_checkin_date + 'T00:00:00');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return lastCheckin.toDateString() === today.toDateString();
});

const getCompletionRate = computed(() => {
  if (!task.value) return 0;
  // 长期任务的进度显示
  if (task.value.is_long_term) {
    return Math.min(90, Math.floor(task.value.checked_count / 10) * 10 + 10);
  }
  if (task.value.total_count === 0) return 0;
  return Math.round((task.value.checked_count / task.value.total_count) * 100);
});

// 获取频率文本
const getFrequencyText = (frequency: string, customDays?: number) => {
  const frequencyMap: { [key: string]: string } = {
    daily: '每天',
    weekly: '每周',
    monthly: '每月',
    custom: customDays ? `每${customDays}天` : '自定义'
  };
  return frequencyMap[frequency] || '未知';
};

// 格式化日期范围
const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' });
  const end = new Date(endDate).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' });
  return `${start} - ${end}`;
};

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 返回
const goBack = () => {
  router.push('/toolbox/checkin');
};

// 跳转到打卡页面
const goToCheckin = () => {
  router.push(`/toolbox/checkin/add?task_id=${taskId.value}&action=checkin`);
};

// 终止长期任务
const terminateTask = async () => {
  if (!confirm('确定要终止这个长期任务吗？终止后将无法继续打卡。')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/checkin/tasks/${taskId.value}/terminate`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    showMessage('任务已终止！', 'success');
    await loadTask(); // 重新加载任务信息
    
  } catch (error) {
    console.error('终止任务时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`终止失败: ${errorMessage}`, 'error');
  }
};

// 打开图片模态框
const openImageModal = (imageUrl: string) => {
  modalImage.value = imageUrl;
  document.body.style.overflow = 'hidden';
};

// 关闭图片模态框
const closeImageModal = () => {
  modalImage.value = null;
  document.body.style.overflow = '';
};

// 删除打卡记录
const deleteRecord = async (recordId: number) => {
  if (!confirm('确定要删除这条打卡记录吗？')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/checkin/records/${recordId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    showMessage('删除成功！', 'success');
    await loadRecords(); // 重新加载记录
    await loadTask(); // 重新加载任务信息（更新计数）
    
  } catch (error) {
    console.error('删除记录时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`删除失败: ${errorMessage}`, 'error');
  }
};

// 加载任务详情
const loadTask = async () => {
  try {
    const response = await fetch(`/api/checkin/tasks/${taskId.value}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    task.value = result;
    
  } catch (error) {
    console.error('加载任务详情时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`加载任务失败: ${errorMessage}`, 'error');
  }
};

// 加载打卡记录
const loadRecords = async () => {
  try {
    const response = await fetch(`/api/checkin/tasks/${taskId.value}/records`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (Array.isArray(result)) {
      records.value = result;
    } else if (result.records && Array.isArray(result.records)) {
      records.value = result.records;
    } else {
      throw new Error('API响应格式不正确');
    }
    
  } catch (error) {
    console.error('加载打卡记录时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`加载记录失败: ${errorMessage}`, 'error');
    records.value = [];
  }
};

onMounted(async () => {
  isLoading.value = true;
  await Promise.all([loadTask(), loadRecords()]);
  isLoading.value = false;
});
</script>

<style scoped>
.checkin-detail-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

.loading {
  text-align: center;
  padding: 100px 40px;
  color: rgba(255, 255, 255, 0.8);
}

.detail-container {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 任务头部 */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
  flex-wrap: wrap;
}

h1 {
  color: #fff;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-weight: bold;
  flex: 1;
}

h2 {
  color: #fff;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.task-status .status-badge {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.completed {
  background: rgba(158, 158, 158, 0.8);
  color: white;
}

.status-badge.active {
  background: rgba(76, 175, 80, 0.8);
  color: white;
}

.status-badge.pending {
  background: rgba(255, 193, 7, 0.8);
  color: white;
}

/* 统计卡片 */
.task-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin-bottom: 5px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.stat-value {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

/* 进度条区域 */
.progress-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  margin-bottom: 30px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.progress-percentage {
  color: #4caf50;
  font-size: 18px;
  font-weight: 700;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  transition: width 0.5s ease;
  border-radius: 6px;
}

/* 记录区域 */
.records-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(76, 175, 80, 0.6);
}

.section-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.showing-info {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.no-records {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
  padding: 40px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.record-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(5px);
  border-radius: 10px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.record-card:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.record-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.date-icon {
  font-size: 18px;
}

.delete-record-btn {
  padding: 6px 12px;
  background: rgba(244, 67, 54, 0.8);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-record-btn:hover {
  background: rgba(211, 47, 47, 0.9);
  transform: scale(1.05);
}

.record-note {
  margin-bottom: 12px;
}

.note-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin-bottom: 5px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.note-content {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  padding: 10px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  border-left: 3px solid rgba(76, 175, 80, 0.6);
}

.record-image {
  margin-top: 12px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.record-image img {
  width: 100%;
  max-width: 400px;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.record-image:hover img {
  transform: scale(1.05);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 15px 40px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.primary-btn {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(46, 125, 50, 0.8));
  color: white;
}

.primary-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.9), rgba(27, 94, 32, 0.9));
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.terminate-btn {
  background: rgba(255, 152, 0, 0.8);
  color: white;
}

.terminate-btn:hover {
  background: rgba(245, 124, 0, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}

.secondary-btn {
  background: rgba(158, 158, 158, 0.8);
  color: white;
}

.secondary-btn:hover {
  background: rgba(117, 117, 117, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(158, 158, 158, 0.4);
}

/* 图片模态框 */
.image-modal {
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
  justify-content: center;
  align-items: center;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(244, 67, 54, 0.9);
  border: none;
  color: white;
  font-size: 30px;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(211, 47, 47, 1);
  transform: scale(1.1);
}

.modal-content img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
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
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.message.success {
  background: rgba(76, 175, 80, 0.9);
}

.message.error {
  background: rgba(244, 67, 54, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .checkin-detail-page {
    padding: 15px;
    padding-top: 100px;
  }
  
  .task-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .task-stats {
    grid-template-columns: 1fr;
  }
  
  .records-section {
    padding: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .checkin-detail-page {
    padding: 10px;
    padding-top: 120px;
  }
  
  h1 {
    font-size: 1.5em;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .progress-section {
    padding: 15px;
  }
  
  .records-section {
    padding: 15px;
  }
  
  .record-card {
    padding: 15px;
  }
  
  .record-image img {
    max-width: 100%;
  }
}
</style>

