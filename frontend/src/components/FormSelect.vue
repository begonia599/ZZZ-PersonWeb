<template>
  <div class="form-group">
    <label v-if="label" :class="{ required: required }">
      {{ label }}
      <span v-if="required" class="required-star"> *</span>
    </label>
    
    <!-- 只读状态：只显示只读输入框 -->
    <input 
      v-if="readonly"
      type="text" 
      :value="getDisplayValue()" 
      readonly 
      class="readonly-input"
    />
    
    <!-- 正常状态：显示选择框 -->
    <select 
      v-else
      :value="modelValue"
      @change="handleChange"
      :required="required"
      :disabled="disabled"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="typeof option === 'object' ? option.value : option"
        :value="typeof option === 'object' ? option.value : option"
      >
        {{ typeof option === 'object' ? option.label : option }}
      </option>
    </select>
    
    <div v-if="hint" class="form-hint">
      {{ hint }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Option {
  label: string;
  value: string | number;
}

interface Props {
  modelValue: string | number;
  label?: string;
  placeholder?: string;
  options: (string | Option)[];
  required?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  hint?: string;
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void;
  (e: 'change', value: string | number): void;
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  readonly: false
});

const emit = defineEmits<Emits>();

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement | null;
  const value = target ? target.value : '';
  emit('update:modelValue', value);
  emit('change', value);
};

// 获取显示值（用于只读状态）
const getDisplayValue = () => {
  if (!props.modelValue) return '';
  
  // 如果 options 中有对象格式，查找对应的 label
  const option = props.options.find(opt => {
    if (typeof opt === 'object') {
      return opt.value === props.modelValue;
    }
    return opt === props.modelValue;
  });
  
  if (typeof option === 'object') {
    return option.label;
  }
  
  return String(props.modelValue);
};
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 10px;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  font-size: 15px;
}

.required-star {
  color: #ff6b6b;
}

.form-group select {
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(5px);
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.form-group select:focus {
  outline: none;
  border-color: rgba(0, 123, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 123, 255, 0.3);
}

.form-group select option {
  background: rgba(33, 37, 41, 0.95);
  color: white;
  padding: 8px;
}

.readonly-input {
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 14px;
  background: rgba(108, 117, 125, 0.3);
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  cursor: not-allowed;
  font-weight: 500;
}

.form-hint {
  font-size: 12px;
  color: #ffc107;
  margin-top: 5px;
  font-weight: 500;
}

.form-group select:disabled {
  background: rgba(108, 117, 125, 0.3);
  cursor: not-allowed;
  opacity: 0.7;
}
</style>