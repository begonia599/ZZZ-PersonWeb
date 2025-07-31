<template>
  <div class="metrics-sidebar">
    <!-- 访问人数组件 -->
    <div class="metric-item-wrapper">
      <VisitorCounter />
    </div>
    <!-- 网站运行时间组件 -->
    <div class="metric-item-wrapper">
      <WebsiteUptime />
    </div>
  </div>
</template>

<script setup lang="ts">
import VisitorCounter from './metrics/VisitorCounter.vue';
import WebsiteUptime from './metrics/WebsiteUptime.vue';

// 移除了 'hovered' ref，因为现在通过 CSS :hover 控制展开/收起
</script>

<style scoped>
.metrics-sidebar {
  position: fixed;
  /* 初始位置：大部分在屏幕外，只露出 20px 的“标签” */
  /* 假设展开后的宽度为 220px，露出 20px，则隐藏 200px */
  left: -240px; 
  top: 50%; /* 垂直居中 */
  transform: translateY(-50%);
  z-index: 999; /* 确保在大多数内容之上，但在 Live2D 模型之下 */
  display: flex;
  flex-direction: column;
  gap: 10px; /* 标签之间的间距 */
  padding: 10px;
  background-color: rgba(44, 62, 80, 0.9); /* 深色背景，略透明 */
  border-radius: 0 8px 8px 0; /* 左侧直角，右侧圆角 */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4); /* 增加阴影，使其看起来像一个浮动面板 */
  transition: left 0.3s ease-out; /* 添加 left 属性的过渡效果 */
  width: 220px; /* 侧边栏的固定宽度，与展开的卡片宽度一致 */
}

/* 悬停时整个侧边栏完全滑入 */
.metrics-sidebar:hover {
  left: 0;
}

.metric-item-wrapper {
  position: relative;
  border-radius: 8px; /* 继承子组件的圆角 */
  /* overflow: hidden; /* 移除这里的 overflow: hidden，让父级 sidebar 裁剪 */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); /* 阴影效果 */
}

/* 内部的 metric-card 始终是其完整宽度 */
.metric-item-wrapper :deep(.metric-card) {
  width: 100%; /* 始终占据父容器的 100% 宽度 (即 220px) */
  height: auto; /* 高度自适应内容 */
  display: flex; /* 确保 flex 布局 */
  align-items: center; /* 垂直居中 */
  padding: 8px 12px; /* 默认 padding */
  background-color: rgba(44, 62, 80, 0.8); /* 深色背景，半透明 */
  border-radius: 8px;
  color: #ecf0f1;
  font-size: 0.9em;
  gap: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease-out; /* 保持内部过渡 */
  cursor: pointer;
}

.metric-item-wrapper :deep(.metric-card .metric-icon) {
  width: 24px; /* 图标大小 */
  height: 24px;
  flex-shrink: 0; /* 防止图标被压缩 */
  /* 关键：将图标推到最右边，使其在侧边栏收起时可见 */
  margin-left: auto; 
  margin-right: 0; /* 移除默认右边距 */
  transition: margin 0.3s ease-out; /* 平滑过渡 */
}

.metric-item-wrapper :deep(.metric-card .metric-content) {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  white-space: nowrap; /* 防止文本换行 */
  overflow: hidden;
  text-overflow: ellipsis; /* 溢出显示省略号 */
  /* 默认隐藏内容，通过 opacity 和 visibility 控制 */
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease-out, visibility 0.3s ease-out;
  flex-grow: 1; /* 让内容占据剩余空间 */
}

/* 当侧边栏悬停时，显示内容，并调整图标位置 */
.metrics-sidebar:hover .metric-item-wrapper :deep(.metric-card .metric-content) {
  opacity: 1;
  visibility: visible;
}

.metrics-sidebar:hover .metric-item-wrapper :deep(.metric-card .metric-icon) {
  margin-left: 0; /* 图标回到左边 */
  margin-right: 8px; /* 恢复右边距 */
}

/* 移动端适配 */
@media (max-width: 768px) {
  .metrics-sidebar {
    top: auto;
    bottom: 20px; /* 移动到底部 */
    left: 50%; /* 水平居中 */
    transform: translateX(-50%); /* 居中对齐 */
    flex-direction: row; /* 移动端横向排列 */
    width: calc(100% - 20px); /* 占据大部分宽度 */
    justify-content: center;
    border-radius: 8px; /* 移动端四角圆角 */
    padding: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    /* 移动端不进行左右滑动效果 */
    transition: none; /* 移动端不进行 left 过渡 */
  }

  /* 移动端不进行 translateX 动画 */
  .metric-item-wrapper {
    transform: none !important; 
  }

  .metric-item-wrapper :deep(.metric-card) {
    width: 120px; /* 移动端标签宽度 */
    height: 80px; /* 移动端标签高度 */
    flex-direction: column; /* 移动端图标和文字垂直排列 */
    font-size: 0.8em;
    padding: 8px 12px; /* 移动端默认显示所有内容，所以需要 padding */
  }

  .metric-item-wrapper :deep(.metric-card .metric-content) {
    display: flex; /* 移动端默认显示文本内容 */
    align-items: center;
    white-space: normal; /* 允许文本换行 */
    text-overflow: clip;
    opacity: 1; /* 移动端始终可见 */
    visibility: visible;
    margin-left: 0; /* Reset margin for vertical stacking */
  }

  .metric-item-wrapper :deep(.metric-card .metric-icon) {
    width: 24px;
    height: 24px;
    margin-bottom: 5px;
    margin-left: auto; /* Reset to auto for centering */
    margin-right: auto; /* Reset to auto for centering */
  }

  .metric-item-wrapper :deep(.metric-card .metric-label) {
    font-size: 0.9em;
  }

  .metric-item-wrapper :deep(.metric-card .metric-value) {
    font-size: 1em;
  }

  .metric-item-wrapper:hover :deep(.metric-card) {
    width: 120px;
    height: auto;
    padding: 8px 12px;
  }
}
</style>
