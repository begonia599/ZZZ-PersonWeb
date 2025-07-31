<template>
  <div class="metric-card visitor-counter">
    <div class="metric-icon">
      <!-- 访问人数图标，可以使用 Lucide Icons 或 Font Awesome -->
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-users">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87 4 4 0 0 0-7-1.13"/><path d="M16 7a4 4 0 0 1 4 4v1"/></svg>
    </div>
    <div class="metric-content">
      <span class="metric-label">访问人数:</span>
      <span class="metric-value">{{ visitorCount }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const visitorCount = ref<number>(0);
const API_BASE_URL = 'http://localhost:5000/api/metrics'; // 后端 API 地址

const fetchVisitorCount = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/visitor_count`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    visitorCount.value = data.visitor_count;
    console.log('访问人数获取成功:', data.visitor_count);
  } catch (error) {
    console.error('获取访问人数失败:', error);
    visitorCount.value = 0; // 获取失败时显示0
  }
};

const incrementVisitorCount = async () => {
  // 使用 sessionStorage 来确保每个会话只增加一次访问人数
  const sessionKey = 'visitor_incremented_this_session';
  if (sessionStorage.getItem(sessionKey)) {
    console.log('本会话已增加过访问人数，跳过。');
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/increment_visitor_count`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}), // POST 请求通常需要一个 body，即使是空的
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('访问人数增加成功:', data.new_count);
    sessionStorage.setItem(sessionKey, 'true'); // 标记本会话已增加
    // 立即更新显示，避免再次请求
    visitorCount.value = data.new_count; 
  } catch (error) {
    console.error('增加访问人数失败:', error);
  }
};

onMounted(async () => {
  await incrementVisitorCount(); // 先尝试增加计数
  await fetchVisitorCount();     // 再获取最新计数
});
</script>

<style scoped>
.metric-card {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: rgba(44, 62, 80, 0.8); /* 深色背景，半透明 */
  border-radius: 8px;
  color: #ecf0f1; /* 浅色文字 */
  font-size: 0.9em;
  gap: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  min-width: 120px; /* 确保标签有一定宽度 */
}

.metric-icon svg {
  width: 18px;
  height: 18px;
  color: #3498db; /* 图标颜色 */
}

.metric-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.metric-label {
  font-weight: bold;
  opacity: 0.8;
}

.metric-value {
  font-size: 1.1em;
  font-weight: bold;
  color: #2ecc71; /* 强调数字 */
}
</style>
