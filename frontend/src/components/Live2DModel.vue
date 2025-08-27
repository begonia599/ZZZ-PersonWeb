<template>
  <div class="live2d-container">
    <canvas ref="l2dCanvasRef" :width="canvasWidth" :height="canvasHeight"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRoute } from 'vue-router';
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
  volume?: number;
}

const props = withDefaults(defineProps<{
  modelId?: string;
  position?: [number, number];
  scale?: number | 'auto';
  canvasWidth?: number;
  canvasHeight?: number;
}>(), {
  modelId: 'furina',
  position: () => [0, 0],
  scale: 'auto',
  canvasWidth: 300,
  canvasHeight: 300,
});

const emit = defineEmits(['model-loaded', 'model-error', 'hit']);

// 路由检查
const route = useRoute();
const isHomePage = computed(() => route.path === '/' || route.path === '/home');

const l2dCanvasRef = ref<HTMLCanvasElement | null>(null);
let l2dInstance: IL2DInstance | null = null;
let live2DModel: IL2DModel | null = null;
let expressions: Array<{ id: string }> = [];

// 生成模型路径
const fullModelPath = computed<string>(() => {
  return `/live2d_models/${props.modelId}/${props.modelId}.model3.json`;
});

// 滚动控制变量（只在主页使用）
let scrollCleanupFunctions: Array<() => void> = [];

onMounted(async () => {
  if (!l2dCanvasRef.value) {
    console.error('Canvas element not found!');
    return;
  }

  try {
    // 初始化Live2D模型
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
        if (expressions.length > 0 && typeof live2DModel?.expression === 'function') {
          const random = Math.floor(Math.random() * expressions.length);
          live2DModel.expression(expressions[random].id);
        }
      });
    }

    // 只在主页启用自定义滚动控制
    if (isHomePage.value) {
      console.log('🎮 主页检测到，启用自定义滚动控制');
      initializeCustomScroll();
    } else {
      console.log('🎮 非主页，使用原生滚动');
      // 确保原生滚动正常工作
      document.documentElement.style.overflow = '';
      document.body.style.overflow = '';
      const appElement = document.getElementById('app');
      if (appElement) {
        appElement.style.overflow = '';
      }
    }

  } catch (error) {
    console.error('Live2D 模型加载失败:', error);
    emit('model-error', error);
  }
});

// 初始化自定义滚动（仅主页）
function initializeCustomScroll() {
  let currentScrollY = 0;
  let targetScrollY = 0;
  let maxScrollY = 0;

  // 禁用原生滚动
  document.documentElement.style.overflow = 'hidden';
  document.body.style.overflow = 'hidden';
  const appElement = document.getElementById('app');
  if (appElement) {
    appElement.style.overflow = 'hidden';
  }

  // 更新最大滚动距离
  const updateMaxScroll = () => {
    const homeContainer = document.querySelector('.home-page-container') as HTMLElement;
    let contentHeight = 0;
    
    if (homeContainer) {
      contentHeight = Math.max(
        homeContainer.scrollHeight,
        homeContainer.offsetHeight,
        homeContainer.getBoundingClientRect().height
      );
    } else {
      contentHeight = Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight
      );
    }
    
    maxScrollY = Math.max(0, contentHeight - window.innerHeight);
    console.log('🎮 更新最大滚动距离:', maxScrollY);
  };

  // 平滑滚动动画
  const scrollAnimation = () => {
    const diff = targetScrollY - currentScrollY;
    
    if (Math.abs(diff) > 0.5) {
      currentScrollY += diff * 0.15; // 阻尼系数
      
      const homeContainer = document.querySelector('.home-page-container') as HTMLElement;
      if (homeContainer) {
        homeContainer.style.transform = `translateY(-${currentScrollY}px)`;
      }
    }
    
    requestAnimationFrame(scrollAnimation);
  };

  // 全局滚轮事件处理
  const handleGlobalWheel = (event: WheelEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    const scrollAmount = event.deltaY * 0.8;
    targetScrollY = Math.max(0, Math.min(targetScrollY + scrollAmount, maxScrollY));
  };

  // 窗口大小变化处理
  const handleResize = () => {
    updateMaxScroll();
  };

  // 初始化
  setTimeout(() => {
    updateMaxScroll();
    scrollAnimation();
  }, 500);

  // 添加事件监听器
  window.addEventListener('wheel', handleGlobalWheel, { passive: false });
  window.addEventListener('resize', handleResize);

  // 保存清理函数
  scrollCleanupFunctions.push(() => {
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    if (appElement) {
      appElement.style.overflow = '';
    }
    window.removeEventListener('wheel', handleGlobalWheel);
    window.removeEventListener('resize', handleResize);
  });
}

onBeforeUnmount(() => {
  if (live2DModel && typeof live2DModel.dispose === 'function') {
    live2DModel.dispose();
  }

  // 执行所有清理函数
  scrollCleanupFunctions.forEach(cleanup => cleanup());
  scrollCleanupFunctions = [];
});
</script>

<style scoped>
.live2d-container {
  position: fixed;
  right: 5px;
  bottom: 20px;
  z-index: 1000;
  pointer-events: auto;
}
</style>
