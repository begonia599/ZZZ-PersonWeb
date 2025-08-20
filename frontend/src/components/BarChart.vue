<template>
  <div class="bar-chart-container">
    <canvas 
      ref="chartCanvas" 
      :width="width" 
      :height="height"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
    ></canvas>
    
    <!-- 悬停提示框 -->
    <div 
      v-if="hoveredItem"
      class="chart-tooltip"
      :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
    >
      <div class="tooltip-title">{{ hoveredItem.label }}</div>
      <div class="tooltip-content">
        <div class="tooltip-item">
          <span class="tooltip-label">数量:</span>
          <span class="tooltip-value">{{ hoveredItem.value }}</span>
        </div>
        <div v-if="hoveredItem.probability" class="tooltip-item">
          <span class="tooltip-label">概率:</span>
          <span class="tooltip-value">{{ hoveredItem.probability }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';

interface BarData {
  label: string;
  value: number;
  color?: string;
  probability?: number; // 新增概率字段
}

interface Props {
  data: BarData[];
  width?: number;
  height?: number;
  horizontal?: boolean;
  showValues?: boolean;
  usePercentage?: boolean; // 新增：是否按百分比绘制
}

const props = withDefaults(defineProps<Props>(), {
  width: 600,
  height: 400,
  horizontal: false,
  showValues: true,
  usePercentage: false
});

const chartCanvas = ref<HTMLCanvasElement>();
const hoveredItem = ref<BarData | null>(null);
const tooltipPosition = ref({ x: 0, y: 0 });
const barAreas = ref<Array<{item: BarData, x: number, y: number, width: number, height: number}>>([]);

// 默认颜色
const defaultColor = '#4ECDC4';

// 处理鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  const rect = chartCanvas.value?.getBoundingClientRect();
  if (!rect) return;
  
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  
  // 检查鼠标是否在某个柱子上
  const hoveredArea = barAreas.value.find(area => 
    x >= area.x && x <= area.x + area.width &&
    y >= area.y && y <= area.y + area.height
  );
  
  if (hoveredArea) {
    hoveredItem.value = hoveredArea.item;
    tooltipPosition.value = { x: event.clientX + 10, y: event.clientY - 10 };
  } else {
    hoveredItem.value = null;
  }
};

// 处理鼠标离开
const handleMouseLeave = () => {
  hoveredItem.value = null;
};

// 绘制柱状图
const drawBarChart = () => {
  if (!chartCanvas.value || props.data.length === 0) return;
  
  const canvas = chartCanvas.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 清空画布和区域记录
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  barAreas.value = [];

  const padding = 80; // 增加左侧padding以显示完整文字
  const chartWidth = canvas.width - padding * 2;
  const chartHeight = canvas.height - padding * 2;
  
  // 根据usePercentage决定最大值
  const maxValue = props.usePercentage 
    ? Math.max(...props.data.map(item => item.probability || 0))
    : Math.max(...props.data.map(item => item.value));
  
  if (props.horizontal) {
    drawHorizontalBars(ctx, padding, chartWidth, chartHeight, maxValue);
  } else {
    drawVerticalBars(ctx, padding, chartWidth, chartHeight, maxValue);
  }
};

// 绘制垂直柱状图
const drawVerticalBars = (ctx: CanvasRenderingContext2D, padding: number, chartWidth: number, chartHeight: number, maxValue: number) => {
  const barWidth = chartWidth / props.data.length;
  const barSpacing = barWidth * 0.1;
  const actualBarWidth = barWidth - barSpacing;

  props.data.forEach((item, index) => {
    const displayValue = props.usePercentage ? (item.probability || 0) : item.value;
    const barHeight = (displayValue / maxValue) * chartHeight;
    const x = padding + index * barWidth + barSpacing / 2;
    const y = padding + chartHeight - barHeight;

    // 记录柱子区域
    barAreas.value.push({
      item,
      x: x,
      y: y,
      width: actualBarWidth,
      height: barHeight
    });

    // 绘制柱子
    ctx.fillStyle = item.color || defaultColor;
    ctx.fillRect(x, y, actualBarWidth, barHeight);

    // 绘制边框
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, actualBarWidth, barHeight);

    // 绘制数值
    if (props.showValues) {
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowBlur = 3;
      const valueText = props.usePercentage ? `${displayValue.toFixed(1)}%` : String(displayValue);
      ctx.fillText(valueText, x + actualBarWidth / 2, y - 5);
      ctx.shadowBlur = 0;
    }

    // 绘制标签
    ctx.fillStyle = '#fff';
    ctx.font = '11px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.save();
    ctx.translate(x + actualBarWidth / 2, padding + chartHeight + 10);
    ctx.rotate(item.label.length > 4 ? -Math.PI / 4 : 0);
    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
    ctx.shadowBlur = 2;
    
    // 处理长标签
    const maxLength = 8;
    const displayLabel = item.label.length > maxLength 
      ? item.label.substring(0, maxLength) + '...' 
      : item.label;
    ctx.fillText(displayLabel, 0, 0);
    ctx.restore();
    ctx.shadowBlur = 0;
  });
};

// 绘制水平柱状图
const drawHorizontalBars = (ctx: CanvasRenderingContext2D, padding: number, chartWidth: number, chartHeight: number, maxValue: number) => {
  const barHeight = chartHeight / props.data.length;
  const barSpacing = barHeight * 0.1;
  const actualBarHeight = barHeight - barSpacing;

  props.data.forEach((item, index) => {
    const displayValue = props.usePercentage ? (item.probability || 0) : item.value;
    const barWidth = (displayValue / maxValue) * chartWidth;
    const x = padding;
    const y = padding + index * barHeight + barSpacing / 2;

    // 记录柱子区域
    barAreas.value.push({
      item,
      x: x,
      y: y,
      width: barWidth,
      height: actualBarHeight
    });

    // 绘制柱子
    ctx.fillStyle = item.color || defaultColor;
    ctx.fillRect(x, y, barWidth, actualBarHeight);

    // 绘制边框
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, barWidth, actualBarHeight);

    // 绘制数值
    if (props.showValues) {
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 11px Arial';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowBlur = 3;
      const valueText = props.usePercentage ? `${displayValue.toFixed(1)}%` : String(displayValue);
      ctx.fillText(valueText, x + barWidth + 8, y + actualBarHeight / 2);
      ctx.shadowBlur = 0;
    }

    // 绘制标签 - 确保完整显示
    ctx.fillStyle = '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
    ctx.shadowBlur = 2;
    ctx.fillText(item.label, x - 15, y + actualBarHeight / 2);
    ctx.shadowBlur = 0;
  });
};

// 监听数据变化重新绘制
watch(() => props.data, () => {
  nextTick(() => {
    drawBarChart();
  });
}, { deep: true });

watch(() => props.usePercentage, () => {
  nextTick(() => {
    drawBarChart();
  });
});

onMounted(() => {
  nextTick(() => {
    drawBarChart();
  });
});
</script>

<style scoped>
.bar-chart-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

canvas {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  cursor: crosshair;
}

.chart-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  z-index: 1000;
  pointer-events: none;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.tooltip-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #4ECDC4;
  font-size: 14px;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.tooltip-label {
  color: rgba(255, 255, 255, 0.8);
}

.tooltip-value {
  font-weight: 600;
  color: #fff;
}
</style>