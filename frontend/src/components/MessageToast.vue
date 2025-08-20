<template>
  <Teleport to="body">
    <Transition name="slide-in">
      <div v-if="visible" :class="['message-toast', type]">
        <div class="message-content">
          <span class="message-icon">{{ getIcon() }}</span>
          <span class="message-text">{{ message }}</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

interface Props {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  show: boolean;
}

interface Emits {
  (e: 'close'): void;
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000
});

const emit = defineEmits<Emits>();

const visible = ref(false);

const getIcon = () => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };
  return icons[props.type] || 'ℹ';
};

watch(() => props.show, (newShow) => {
  if (newShow) {
    visible.value = true;
    if (props.duration > 0) {
      setTimeout(() => {
        visible.value = false;
        setTimeout(() => emit('close'), 300); // 等待动画完成
      }, props.duration);
    }
  } else {
    visible.value = false;
    setTimeout(() => emit('close'), 300);
  }
});
</script>

<style scoped>
.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  z-index: 1000;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  min-width: 300px;
  max-width: 500px;
}

.message-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.message-icon {
  font-size: 18px;
  font-weight: bold;
}

.message-text {
  flex: 1;
}

.message-toast.success {
  background: rgba(40, 167, 69, 0.9);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.message-toast.error {
  background: rgba(220, 53, 69, 0.9);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.message-toast.warning {
  background: rgba(255, 193, 7, 0.9);
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
}

.message-toast.info {
  background: rgba(23, 162, 184, 0.9);
  box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
}

.slide-in-enter-active,
.slide-in-leave-active {
  transition: all 0.3s ease-out;
}

.slide-in-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-in-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>