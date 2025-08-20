<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3 class="chart-title">
        <span class="chart-icon">{{ icon }}</span>
        {{ title }}
      </h3>
      <div v-if="hasControls" class="chart-controls">
        <slot name="controls"></slot>
      </div>
    </div>
    
    <div class="chart-content" :style="{ height: height }">
      <div v-if="loading" class="chart-loading">
        <LoadingAnimation />
        <p>正在加载图表数据...</p>
      </div>
      <div v-else-if="error" class="chart-error">
        <span class="error-icon">⚠️</span>
        <p>{{ error }}</p>
      </div>
      <div v-else class="chart-wrapper">
        <slot></slot>
      </div>
    </div>
    
    <div v-if="description" class="chart-description">
      {{ description }}
    </div>
  </div>
</template>

<script setup lang="ts">
import LoadingAnimation from './LoadingAnimation.vue';

interface Props {
  title: string;
  icon?: string;
  height?: string;
  loading?: boolean;
  error?: string;
  description?: string;
  hasControls?: boolean;
}

withDefaults(defineProps<Props>(), {
  icon: '📈',
  height: '400px',
  loading: false,
  hasControls: false
});
</script>

<style scoped>
.chart-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.chart-icon {
  font-size: 24px;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-content {
  position: relative;
  width: 100%;
  min-height: 200px;
}

.chart-loading,
.chart-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}

.chart-loading p,
.chart-error p {
  margin-top: 16px;
  font-size: 16px;
}

.error-icon {
  font-size: 48px;
}

.chart-wrapper {
  width: 100%;
  height: 100%;
}

.chart-description {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-container {
    padding: 20px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-content {
    min-height: 300px;
  }
}
</style>