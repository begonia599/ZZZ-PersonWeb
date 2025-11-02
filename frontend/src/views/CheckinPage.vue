<template>
  <div class="checkin-page">
    <h1>✅ 打卡工具</h1>
    
    <!-- 操作按钮区域 -->
    <div class="action-section">
      <router-link to="/toolbox/checkin/add" class="action-btn add-btn">
        ➕ 创建打卡任务
      </router-link>
    </div>

    <!-- 打卡任务列表 -->
    <div class="task-list-section">
      <div class="section-header">
        <h2>📋 我的打卡任务</h2>
        <div class="section-controls">
          <span class="showing-info">
            共 {{ tasks.length }} 个任务
          </span>
        </div>
      </div>
      
      <div v-if="isLoading" class="loading">
        <LoadingAnimation />
      </div>
      <div v-else-if="tasks.length === 0" class="no-data">
        <p>还没有创建任何打卡任务，<router-link to="/toolbox/checkin/add">点击这里创建</router-link>！</p>
      </div>
      <div v-else class="tasks-grid">
        <div 
          v-for="task in tasks" 
          :key="task.id"
          class="task-card"
          :class="{ 'completed': isTaskCompleted(task) }"
        >
          <div class="task-header">
            <h3 class="task-title">{{ task.title }}</h3>
            <div class="task-status">
              <span v-if="isTaskCompleted(task)" class="status-badge completed">已完成</span>
              <span v-else-if="isTaskActive(task)" class="status-badge active">进行中</span>
              <span v-else class="status-badge pending">未开始</span>
            </div>
          </div>
          
          <div class="task-info">
            <div class="info-item">
              <span class="info-label">频率：</span>
              <span class="info-value">{{ getFrequencyText(task.frequency) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">周期：</span>
              <span class="info-value">
                {{ task.is_long_term ? '长期任务' : formatDateRange(task.start_date, task.end_date) }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">进度：</span>
              <span class="info-value">
                {{ task.is_long_term ? `已打卡 ${task.checked_count} 次` : `${task.checked_count}/${task.total_count} 次` }}
              </span>
            </div>
          </div>
          
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: getProgress(task) + '%' }"></div>
          </div>
          
          <div class="task-actions">
            <button 
              v-if="!isTaskCompleted(task) && isTaskActive(task)" 
              @click="doCheckin(task.id)" 
              class="action-button checkin-btn"
              :disabled="isCheckedToday(task)"
            >
              {{ isCheckedToday(task) ? '✓ 今日已打卡' : '📝 立即打卡' }}
            </button>
            <button 
              v-if="task.is_long_term && !task.is_terminated && isTaskActive(task)"
              @click="terminateTask(task.id)" 
              class="action-button terminate-btn"
            >
              ⏸️ 终止任务
            </button>
            <router-link 
              :to="`/toolbox/checkin/detail/${task.id}`" 
              class="action-button detail-btn"
            >
              📊 查看详情
            </router-link>
            <button 
              @click="deleteTask(task.id)" 
              class="action-button delete-btn"
            >
              🗑️ 删除
            </button>
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
import { ref, onMounted } from 'vue';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import { useRouter } from 'vue-router';

interface CheckinTask {
  id: number;
  title: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  custom_days?: number;
  start_date: string;
  end_date: string;
  total_count: number;
  checked_count: number;
  last_checkin_date?: string;
  created_at: string;
  is_long_term?: boolean; // 是否为长期任务
  is_terminated?: boolean; // 是否已终止
}

const router = useRouter();
const isLoading = ref(false);
const tasks = ref<CheckinTask[]>([]);
const message = ref({ text: '', type: '' });

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
  const start = new Date(startDate).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  const end = new Date(endDate).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  return `${start} - ${end}`;
};

// 获取进度百分比
const getProgress = (task: CheckinTask) => {
  if (task.is_long_term) {
    // 长期任务显示一个基于打卡次数的进度（但不会满）
    // 每10次打卡增加10%，最多显示90%
    return Math.min(90, Math.floor(task.checked_count / 10) * 10 + 10);
  }
  if (task.total_count === 0) return 0;
  return Math.round((task.checked_count / task.total_count) * 100);
};

// 判断任务是否完成
const isTaskCompleted = (task: CheckinTask) => {
  // 如果是已终止的长期任务
  if (task.is_long_term && task.is_terminated) {
    return true;
  }
  // 长期任务且未终止，不算完成
  if (task.is_long_term && !task.is_terminated) {
    return false;
  }
  const endDate = new Date(task.end_date + 'T00:00:00');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return endDate < today || task.checked_count >= task.total_count;
};

// 判断任务是否激活
const isTaskActive = (task: CheckinTask) => {
  // 获取今天的日期（只比较日期，不比较时间）
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // 长期任务且未终止，只要开始日期到了就是激活状态
  if (task.is_long_term && !task.is_terminated) {
    const startDate = new Date(task.start_date + 'T00:00:00');
    return startDate <= today;
  }
  
  const startDate = new Date(task.start_date + 'T00:00:00');
  const endDate = new Date(task.end_date + 'T00:00:00');
  return startDate <= today && endDate >= today;
};

// 判断今天是否已打卡
const isCheckedToday = (task: CheckinTask) => {
  if (!task.last_checkin_date) return false;
  const lastCheckin = new Date(task.last_checkin_date);
  const today = new Date();
  return lastCheckin.toDateString() === today.toDateString();
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 加载打卡任务列表
const loadTasks = async () => {
  isLoading.value = true;
  try {
    const response = await fetch('/api/checkin/tasks');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (Array.isArray(result)) {
      tasks.value = result;
    } else if (result.tasks && Array.isArray(result.tasks)) {
      tasks.value = result.tasks;
    } else {
      throw new Error('API响应格式不正确');
    }
    
  } catch (error) {
    console.error('加载打卡任务列表时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`加载数据失败: ${errorMessage}`, 'error');
    // 设置示例数据用于演示
    tasks.value = [];
  } finally {
    isLoading.value = false;
  }
};

// 执行打卡
const doCheckin = async (taskId: number) => {
  router.push(`/toolbox/checkin/add?task_id=${taskId}&action=checkin`);
};

// 终止长期任务
const terminateTask = async (taskId: number) => {
  if (!confirm('确定要终止这个长期任务吗？终止后将无法继续打卡。')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/checkin/tasks/${taskId}/terminate`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    showMessage('任务已终止！', 'success');
    await loadTasks(); // 重新加载列表
    
  } catch (error) {
    console.error('终止任务时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`终止失败: ${errorMessage}`, 'error');
  }
};

// 删除任务
const deleteTask = async (taskId: number) => {
  if (!confirm('确定要删除这个打卡任务吗？')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/checkin/tasks/${taskId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    showMessage('删除成功！', 'success');
    await loadTasks(); // 重新加载列表
    
  } catch (error) {
    console.error('删除任务时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`删除失败: ${errorMessage}`, 'error');
  }
};

onMounted(() => {
  loadTasks();
});
</script>

<style scoped>
.checkin-page {
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
  border-bottom: 2px solid rgba(76, 175, 80, 0.6);
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
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(46, 125, 50, 0.8));
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.9), rgba(27, 94, 32, 0.9));
}

/* 任务列表区域样式 */
.task-list-section {
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
  color: #4caf50;
  text-decoration: none;
}

.no-data a:hover {
  text-decoration: underline;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.task-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.task-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.task-card.completed {
  opacity: 0.7;
  border-color: rgba(158, 158, 158, 0.3);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  gap: 10px;
}

.task-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  flex: 1;
}

.task-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
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

.task-info {
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.info-label {
  font-weight: 600;
  margin-right: 5px;
  min-width: 50px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.info-value {
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  transition: width 0.3s ease;
}

.task-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-button {
  flex: 1;
  min-width: 100px;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  text-align: center;
  display: inline-block;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.checkin-btn {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(46, 125, 50, 0.8));
  color: white;
}

.checkin-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.9), rgba(27, 94, 32, 0.9));
  transform: translateY(-1px);
}

.checkin-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.detail-btn {
  background: rgba(33, 150, 243, 0.8);
  color: white;
}

.detail-btn:hover {
  background: rgba(25, 118, 210, 0.9);
  transform: translateY(-1px);
}

.terminate-btn {
  background: rgba(255, 152, 0, 0.8);
  color: white;
}

.terminate-btn:hover {
  background: rgba(245, 124, 0, 0.9);
  transform: translateY(-1px);
}

.delete-btn {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.delete-btn:hover {
  background: rgba(211, 47, 47, 0.9);
  transform: translateY(-1px);
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
  .checkin-page {
    padding: 15px;
    padding-top: 100px;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
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
  .checkin-page {
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
  
  .task-list-section {
    padding: 15px;
  }
  
  .task-card {
    padding: 15px;
  }
  
  .task-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}
</style>

