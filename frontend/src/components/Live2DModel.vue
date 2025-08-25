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
  } catch (error) {
    console.error('Live2D 模型加载失败:', error);
    emit('model-error', error);
  }
});

onBeforeUnmount(() => {
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
  position: absolute;
  right: -20px;
  bottom: 0px;
  z-index: 1000;
  width: fit-content;
  height: fit-content;
}

canvas {
  display: block;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  /* border: 2px solid red; 新增红色边框，方便定位 */
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