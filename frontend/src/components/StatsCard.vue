<template>
  <div class="stats-card">
    <div class="card-header">
      <h3 class="card-title">
        <span class="card-icon">{{ icon }}</span>
        {{ title }}
      </h3>
    </div>
    <div class="card-content">
      <div v-if="type === 'number'" class="number-display">
        <span class="number">{{ value }}</span>
        <span v-if="unit" class="unit">{{ unit }}</span>
      </div>
      <div v-else-if="type === 'percentage'" class="percentage-display">
        <span class="percentage">{{ value }}%</span>
        <div class="percentage-bar">
          <div class="percentage-fill" :style="{ width: value + '%' }"></div>
        </div>
      </div>
      <div v-else-if="type === 'list'" class="list-display">
        <div v-for="item in listData" :key="item.label" class="list-item">
          <span class="list-label">{{ item.label }}</span>
          <span class="list-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
    <div v-if="description" class="card-description">
      {{ description }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface ListItem {
  label: string;
  value: string | number;
}

interface Props {
  title: string;
  icon?: string;
  type: 'number' | 'percentage' | 'list';
  value?: string | number;
  unit?: string;
  listData?: ListItem[];
  description?: string;
}

withDefaults(defineProps<Props>(), {
  icon: '📊',
  type: 'number'
});
</script>

<style scoped>
.stats-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.3);
}

.card-header {
  margin-bottom: 20px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.card-icon {
  font-size: 24px;
}

.number-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.number {
  font-size: 36px;
  font-weight: bold;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.unit {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.percentage-display {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.percentage {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.percentage-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.percentage-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #007bff);
  transition: width 0.8s ease;
}

.list-display {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.list-item:last-child {
  border-bottom: none;
}

.list-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.list-value {
  color: #fff;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.card-description {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-card {
    padding: 20px;
  }
  
  .number {
    font-size: 28px;
  }
  
  .percentage {
    font-size: 24px;
  }
}
</style>