<template>
  <div class="form-actions">
    <button 
      v-if="showSubmit"
      type="submit" 
      :disabled="submitDisabled"
      class="submit-btn"
      @click="$emit('submit')"
    >
      <span class="button-icon" v-if="submitIcon">{{ submitIcon }}</span>
      <span>{{ submitLoading ? submitLoadingText : submitText }}</span>
    </button>
    
    <button 
      v-if="showReset"
      type="button" 
      :disabled="resetDisabled"
      class="reset-btn"
      @click="$emit('reset')"
    >
      <span class="button-icon" v-if="resetIcon">{{ resetIcon }}</span>
      <span>{{ resetText }}</span>
    </button>
    
    <button 
      v-if="showCancel"
      type="button" 
      :disabled="cancelDisabled"
      class="cancel-btn"
      @click="$emit('cancel')"
    >
      <span class="button-icon" v-if="cancelIcon">{{ cancelIcon }}</span>
      <span>{{ cancelText }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  showSubmit?: boolean;
  showReset?: boolean;
  showCancel?: boolean;
  submitText?: string;
  resetText?: string;
  cancelText?: string;
  submitLoadingText?: string;
  submitLoading?: boolean;
  submitDisabled?: boolean;
  resetDisabled?: boolean;
  cancelDisabled?: boolean;
  submitIcon?: string;
  resetIcon?: string;
  cancelIcon?: string;
}

interface Emits {
  (e: 'submit'): void;
  (e: 'reset'): void;
  (e: 'cancel'): void;
}

withDefaults(defineProps<Props>(), {
  showSubmit: true,
  showReset: true,
  showCancel: false,
  submitText: '提交',
  resetText: '重置',
  cancelText: '取消',
  submitLoadingText: '提交中...',
  submitLoading: false,
  submitDisabled: false,
  resetDisabled: false,
  cancelDisabled: false
});

defineEmits<Emits>();
</script>

<style scoped>
.form-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
  flex-wrap: wrap;
}

.submit-btn,
.reset-btn,
.cancel-btn {
  padding: 16px 40px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-icon {
  font-size: 18px;
}

.submit-btn {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.8), rgba(0, 86, 179, 0.8));
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, rgba(0, 86, 179, 0.9), rgba(0, 64, 133, 0.9));
}

.submit-btn:disabled {
  background: rgba(108, 117, 125, 0.8);
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.reset-btn {
  background: rgba(108, 117, 125, 0.8);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.reset-btn:hover:not(:disabled) {
  background: rgba(84, 91, 98, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.cancel-btn {
  background: rgba(220, 53, 69, 0.8);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.cancel-btn:hover:not(:disabled) {
  background: rgba(200, 35, 51, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .submit-btn,
  .reset-btn,
  .cancel-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>