<template>
  <div class="pie-chart-container">
    <canvas 
      ref="chartCanvas" 
      :width="size" 
      :height="size"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
    ></canvas>
    <div class="pie-legend">
      <div 
        v-for="(item, index) in data" 
        :key="item.label" 
        class="legend-item"
        :class="{ 'highlighted': hoveredItem && hoveredItem.label === item.label }"
      >
        <span 
          class="legend-color" 
          :style="{ backgroundColor: colors[index % colors.length] }"
        ></span>
        <span class="legend-label">{{ item.label }}</span>
        <span class="legend-value">{{ item.value }} ({{ getPercentage(item.value) }}%)</span>
      </div>
    </div>
    
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
        <div class="tooltip-item">
          <span class="tooltip-label">占比:</span>
          <span class="tooltip-value">{{ getPercentage(hoveredItem.value) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';

interface PieData {
  label: string;
  value: number;
}

interface Props {
  data: PieData[];
  size?: number;
  colors?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  size: 300,
  colors: () => [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    '#10AC84', '#EE5A24', '#0984E3', '#6C5CE7', '#FD79A8'
  ]
});

const chartCanvas = ref<HTMLCanvasElement>();
const total = ref(0);
const hoveredItem = ref<PieData | null>(null);
const tooltipPosition = ref({ x: 0, y: 0 });
const pieSlices = ref<Array<{item: PieData, startAngle: number, endAngle: number, centerX: number, centerY: number, radius: number}>>([]);

// 计算百分比
const getPercentage = (value: number): string => {
  if (total.value === 0) return '0.0';
  return ((value / total.value) * 100).toFixed(1);
};

// 处理鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  const rect = chartCanvas.value?.getBoundingClientRect();
  if (!rect) return;
  
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  
  // 检查鼠标是否在某个扇形上
  const hoveredSlice = pieSlices.value.find(slice => {
    const dx = x - slice.centerX;
    const dy = y - slice.centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance > slice.radius) return false;
    
    let angle = Math.atan2(dy, dx);
    if (angle < 0) angle += 2 * Math.PI;
    
    // 调整角度以匹配我们的绘制起点（顶部）
    angle = (angle + Math.PI / 2) % (2 * Math.PI);
    
    return angle >= slice.startAngle && angle <= slice.endAngle;
  });
  
  if (hoveredSlice) {
    hoveredItem.value = hoveredSlice.item;
    tooltipPosition.value = { x: event.clientX + 10, y: event.clientY - 10 };
  } else {
    hoveredItem.value = null;
  }
};

// 处理鼠标离开
const handleMouseLeave = () => {
  hoveredItem.value = null;
};

// 绘制饼图
const drawPieChart = () => {
  if (!chartCanvas.value) return;
  
  const canvas = chartCanvas.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 清空画布和扇形记录
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  pieSlices.value = [];
  
  // 计算总值
  total.value = props.data.reduce((sum, item) => sum + item.value, 0);
  
  if (total.value === 0) return;

  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = Math.min(centerX, centerY) - 20;
  
  let currentAngle = 0; // 从顶部开始，但这里用0作为起始

  props.data.forEach((item, index) => {
    const sliceAngle = (item.value / total.value) * 2 * Math.PI;
    const startAngle = currentAngle;
    const endAngle = currentAngle + sliceAngle;
    
    // 记录扇形信息
    pieSlices.value.push({
      item,
      startAngle,
      endAngle,
      centerX,
      centerY,
      radius
    });
    
    // 绘制扇形
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, startAngle - Math.PI / 2, endAngle - Math.PI / 2);
    ctx.closePath();
    
    // 判断是否是悬停的扇形
    const isHovered = hoveredItem.value && hoveredItem.value.label === item.label;
    
    // 填充颜色（悬停时稍微变亮）
    const baseColor = props.colors[index % props.colors.length];
    ctx.fillStyle = isHovered ? lightenColor(baseColor, 20) : baseColor;
    ctx.fill();
    
    // 绘制边框
    ctx.strokeStyle = isHovered ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = isHovered ? 3 : 2;
    ctx.stroke();
    
    // 绘制标签（如果扇形足够大）
    if (sliceAngle > 0.1) {
      const labelAngle = (startAngle + endAngle) / 2 - Math.PI / 2;
      const labelRadius = radius * 0.7;
      const labelX = centerX + Math.cos(labelAngle) * labelRadius;
      const labelY = centerY + Math.sin(labelAngle) * labelRadius;
      
      ctx.fillStyle = '#fff';
      ctx.font = isHovered ? 'bold 14px Arial' : 'bold 12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowBlur = 3;
      ctx.fillText(`${getPercentage(item.value)}%`, labelX, labelY);
      ctx.shadowBlur = 0;
    }
    
    currentAngle = endAngle;
  });
};

// 颜色变亮函数
const lightenColor = (color: string, percent: number): string => {
  const num = parseInt(color.replace("#", ""), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) + amt;
  const G = (num >> 8 & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
};

// 监听数据变化重新绘制
watch(() => props.data, () => {
  nextTick(() => {
    drawPieChart();
  });
}, { deep: true });

// 监听悬停状态变化重新绘制
watch(() => hoveredItem.value, () => {
  nextTick(() => {
    drawPieChart();
  });
});

onMounted(() => {
  nextTick(() => {
    drawPieChart();
  });
});
</script>

<style scoped>
.pie-chart-container {
  position: relative;
  display: flex;
  gap: 30px;
  align-items: flex-start;
  flex-wrap: wrap;
}

canvas {
  cursor: pointer;
  transition: all 0.3s ease;
}

.pie-legend {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.legend-item:hover,
.legend-item.highlighted {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  color: #fff;
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.legend-value {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 14px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .pie-chart-container {
    flex-direction: column;
    align-items: center;
  }
  
  .pie-legend {
    width: 100%;
  }
}
</style>