<template>
  <div class="metric-card website-uptime">
    <div class="metric-icon">
      <!-- 运行时间图标，可以使用 Lucide Icons 或 Font Awesome -->
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clock">
        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    </div>
    <div class="metric-content">
      <span class="metric-label">运行时间:</span>
      <span class="metric-value">{{ formattedUptime }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';

import { apiFetch, API_ENDPOINTS } from '@/config/api';
const formattedUptime = ref<string>('加载中...');
let intervalId: NodeJS.Timeout | null = null;

/**
 * 格式化总秒数为“X天 X时 X分 X秒”的字符串。
 * @param totalSeconds 总秒数。
 * @returns 格式化后的字符串。
 */
const formatUptimeSeconds = (totalSeconds: number): string => {
  // 检查输入是否为有效数字且非负
  if (typeof totalSeconds !== 'number' || isNaN(totalSeconds) || totalSeconds < 0) {
    return '数据异常'; // 处理无效或负数的情况
  }

  const days = Math.floor(totalSeconds / (3600 * 24));
  const hours = Math.floor((totalSeconds % (3600 * 24)) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);

  let parts: string[] = [];
  // 只有当有天数时才显示天数部分
  if (days > 0) {
    parts.push(`${days}天`);
  }
  // 如果有天数或小时数大于0，就显示小时数
  if (hours > 0 || days > 0) {
    parts.push(`${hours}时`);
  }
  // 如果有天数、小时数或分钟数大于0，就显示分钟数
  if (minutes > 0 || hours > 0 || days > 0) {
    parts.push(`${minutes}分`);
  }
  // 秒数总是显示，确保即使是0秒也能看到
  parts.push(`${seconds}秒`);

  return parts.join(' ');
};

/**
 * 从后端获取网站运行时间并更新显示。
 */
const fetchAndDisplayUptime = async () => {
  try {
    const data = await apiFetch(API_ENDPOINTS.METRICS.UPTIME);
    
    // !!! 关键修改: 从后端响应中正确获取 'uptimeSeconds'
    const uptimeSeconds = data.uptimeSeconds; 

    // 再次检查获取到的值是否为有效数字
    if (typeof uptimeSeconds === 'number' && !isNaN(uptimeSeconds)) {
      formattedUptime.value = formatUptimeSeconds(uptimeSeconds);
    } else {
      formattedUptime.value = '数据格式错误';
      console.error('后端返回的 uptimeSeconds 不是有效数字或缺失:', uptimeSeconds);
    }
  } catch (error) {
    console.error('获取网站运行时间失败:', error);
    formattedUptime.value = '获取失败';
  }
};

onMounted(() => {
  fetchAndDisplayUptime(); // 组件挂载时立即获取并显示一次
  // 每秒重新从后端获取运行时间，以保持实时更新
  intervalId = setInterval(fetchAndDisplayUptime, 1000); 
});

onBeforeUnmount(() => {
  // 组件卸载前清除定时器，防止内存泄漏
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null;
  }
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
  color: #f39c12; /* 图标颜色 */
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
  color: #e67e22; /* 强调数字 */
}
</style>