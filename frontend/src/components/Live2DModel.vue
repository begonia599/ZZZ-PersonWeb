<template>
  <div class="live2d-container">
    <canvas ref="l2dCanvasRef" :width="canvasWidth" :height="canvasHeight"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { init } from 'l2d';

interface IL2DInstance {
  create: (options: ICreateOptions) => Promise<IL2DModel>;
}

interface IL2DModel {
  setPosition: (position: [number, number]) => void;
  setScale: (scale: number | 'auto') => void;
  setVolume: (volume: number) => void;
  on: (event: 'hit', callback: (area: string[] | Record<string, any> | undefined) => void) => void;
  showHitAreaFrames: () => void;
  hideHitAreaFrames: () => void;
  dispose?: () => void;
  getExpressions?: () => Array<{ id: string; name?: string; file?: string }>;
  expression?: (id: string) => void;
}

interface ICreateOptions {
  path: string;
  position?: [number, number];
  scale?: number | 'auto';
}

interface Props {
  modelId: string;
  position?: [number, number];
  scale?: number | 'auto';
  canvasWidth?: number;
  canvasHeight?: number;
}

const props = withDefaults(defineProps<Props>(), {
  position: () => [60, 0],
  scale: 'auto',
  canvasWidth: 300,
  canvasHeight: 300,
});

const emit = defineEmits(['model-loaded', 'model-error', 'hit']);

const l2dCanvasRef = ref<HTMLCanvasElement | null>(null);
let l2dInstance: IL2DInstance | null = null;
let live2DModel: IL2DModel | null = null;
let expressions: Array<{ id: string }> = []; // 存储表情列表

// 生成模型路径
const fullModelPath = computed<string>(() => {
  return `/live2d_models/${props.modelId}/${props.modelId}.model3.json`;
});

onMounted(async () => {
  if (!l2dCanvasRef.value) {
    console.error('Canvas element not found!');
    return;
  }

  try {
    l2dInstance = init(l2dCanvasRef.value) as unknown as IL2DInstance;

    const createOptions: ICreateOptions = {
      path: fullModelPath.value,
      position: props.position,
      scale: props.scale,
    };

    live2DModel = await l2dInstance.create(createOptions) as IL2DModel;
    console.log('Live2D 模型加载成功！', fullModelPath.value);
    emit('model-loaded', live2DModel);

    // 获取表情列表
    if (live2DModel && typeof live2DModel.getExpressions === 'function') {
      expressions = live2DModel.getExpressions() || [];
      console.log('表情列表:', expressions);
    }

    // 点击模型时随机切换表情
    if (live2DModel) {
      live2DModel.on('hit', () => {
        if (
          expressions.length > 0 &&
          typeof live2DModel?.expression === 'function'
        ) {
          const random = Math.floor(Math.random() * expressions.length);
          live2DModel.expression(expressions[random].id);
        }
      });
    }

    // 全局滚动控制 - 替换原生滚动
    console.log('🎮 初始化全局滚动控制');
    
    let currentScrollY = 0;
    let targetScrollY = 0;
    let isScrolling = false;
    let maxScrollY = 0;
    
    // 更新最大滚动距离
    const updateMaxScroll = () => {
      // 查找主页容器元素来获取实际内容高度
      const homeContainer = document.querySelector('.home-page-container') as HTMLElement;
      let contentHeight = 0;
      
      if (homeContainer) {
        // 获取容器的实际高度
        contentHeight = Math.max(
          homeContainer.scrollHeight,
          homeContainer.offsetHeight,
          homeContainer.getBoundingClientRect().height
        );
        console.log('🎮 找到主页容器，高度:', contentHeight);
      } else {
        // 备用方案：使用文档高度
        contentHeight = Math.max(
          document.body.scrollHeight,
          document.body.offsetHeight,
          document.documentElement.clientHeight,
          document.documentElement.scrollHeight,
          document.documentElement.offsetHeight
        );
        console.log('🎮 使用文档高度:', contentHeight);
      }
      
      maxScrollY = Math.max(0, contentHeight - window.innerHeight);
      console.log('🎮 更新最大滚动距离:', maxScrollY, '内容高度:', contentHeight, '视口高度:', window.innerHeight);
    };
      
    // 直接滚动动画函数（使用transform移动内容）
    const directScrollAnimation = () => {
      const diff = targetScrollY - currentScrollY;
      
      if (Math.abs(diff) > 0.5) {
        currentScrollY += diff * 0.3; // 快速响应
        
        // 使用transform移动主页容器
        const homeContainer = document.querySelector('.home-page-container') as HTMLElement;
        if (homeContainer) {
          homeContainer.style.transform = `translateY(${-currentScrollY}px)`;
        }
        
        requestAnimationFrame(directScrollAnimation);
      } else {
        // 滚动完成
        currentScrollY = targetScrollY;
        const homeContainer = document.querySelector('.home-page-container') as HTMLElement;
        if (homeContainer) {
          homeContainer.style.transform = `translateY(${-currentScrollY}px)`;
        }
        isScrolling = false;
        
        console.log('🎮 滚动完成', { 位置: currentScrollY });
      }
    };
      
    // 全局滚轮事件处理
    const handleGlobalWheel = (event: WheelEvent) => {
      event.preventDefault();
      
      const scrollAmount = event.deltaY * 1.0; // 正常敏感度
      targetScrollY = Math.max(0, Math.min(maxScrollY, targetScrollY + scrollAmount));
      
      console.log('🎮 全局滚动', {
        滚动距离: scrollAmount,
        目标位置: targetScrollY,
        最大滚动: maxScrollY
      });
      
      if (!isScrolling) {
        isScrolling = true;
        requestAnimationFrame(directScrollAnimation);
      }
    };
    
    // 初始化 - 延迟更长时间确保DOM完全渲染
    setTimeout(() => {
      updateMaxScroll();
      currentScrollY = 0; // 从0开始
      targetScrollY = 0;
      
      // 确保主页容器初始位置正确
      const homeContainer = document.querySelector('.home-page-container') as HTMLElement;
      if (homeContainer) {
        homeContainer.style.transform = `translateY(0px)`;
        console.log('🎮 主页容器初始化完成');
      }
    }, 500); // 增加延迟时间
    
    // 添加全局滚轮监听
    window.addEventListener('wheel', handleGlobalWheel, { passive: false });
    window.addEventListener('resize', updateMaxScroll);
    
    // 存储清理函数
    (l2dCanvasRef.value as any).__cleanup = () => {
      window.removeEventListener('wheel', handleGlobalWheel);
      window.removeEventListener('resize', updateMaxScroll);
    };
  } catch (error) {
    console.error('Live2D 模型加载失败:', error);
    emit('model-error', error);
  }
});

onBeforeUnmount(() => {
  // 清理全局滚动事件监听器
  if (l2dCanvasRef.value && (l2dCanvasRef.value as any).__cleanup) {
    (l2dCanvasRef.value as any).__cleanup();
    console.log('全局滚动事件监听器已清理');
  }
  
  if (l2dInstance) {
    if (live2DModel && typeof live2DModel.dispose === 'function') {
      live2DModel.dispose();
      console.log('Live2D 模型已销毁');
    }
    const ctx = l2dCanvasRef.value?.getContext('2d');
    if (ctx && l2dCanvasRef.value) {
      ctx.clearRect(0, 0, l2dCanvasRef.value.width, l2dCanvasRef.value.height);
      console.log('Canvas 已清空');
    }
    l2dInstance = null;
    live2DModel = null;
  }
});
</script>

<style scoped>
.live2d-container {
  position: fixed; /* 改为fixed，固定在屏幕上 */
  right: 5px; /* 距离右边5px，更靠近右边 */
  bottom: 20px; /* 距离底部20px */
  z-index: 1000;
  width: fit-content;
  height: fit-content;
  /* 允许所有鼠标事件，但让滚轮事件穿透 */
  pointer-events: auto;
}

canvas {
  display: block;
  /* 完全去除边框和阴影，让模型完全透明化 */
  /* 让Canvas可以接收点击事件，但不阻止滚轮事件 */
  pointer-events: auto;
}

/* 移动端完全隐藏Live2D模型 */
@media (max-width: 768px) {
  .live2d-container {
    display: none !important;
  }
}

/* 小屏幕设备完全隐藏 */
@media (max-width: 480px) {
  .live2d-container {
    display: none !important;
  }
}
</style>