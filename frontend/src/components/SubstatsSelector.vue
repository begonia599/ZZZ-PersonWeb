<template>
  <div class="substats-section">
    <div class="substats-header">
      <label>副词条选择 * (请选择3-4个)</label>
      <span class="selected-count" :class="{ 'valid': isValid, 'invalid': !isValid && selectedCount > 0 }">
        已选择: {{ selectedCount }}/4
      </span>
    </div>
    
    <div class="substats-grid">
      <div 
        v-for="stat in availableOptions" 
        :key="stat" 
        class="substat-checkbox"
      >
        <label>
          <input 
            type="checkbox" 
            :value="stat"
            :checked="modelValue.includes(stat)"
            @change="handleChange(stat, $event)"
            :disabled="!canSelectMore && !modelValue.includes(stat)"
          />
          <span class="checkbox-label">{{ stat }}</span>
        </label>
      </div>
    </div>
    
    <div v-if="!isValid && selectedCount > 0" class="validation-hint">
      {{ selectedCount < 3 ? `还需要选择 ${3 - selectedCount} 个副词条` : '最多只能选择4个副词条，请取消一些选择' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  modelValue: string[];
  allOptions: string[];
  excludeOptions?: string[];
  minCount?: number;
  maxCount?: number;
}

interface Emits {
  (e: 'update:modelValue', value: string[]): void;
}

const props = withDefaults(defineProps<Props>(), {
  excludeOptions: () => [],
  minCount: 3,
  maxCount: 4
});

const emit = defineEmits<Emits>();

// 可选择的选项（排除被排除的选项）
const availableOptions = computed(() => {
  return props.allOptions.filter(option => !props.excludeOptions.includes(option));
});

// 已选择数量
const selectedCount = computed(() => {
  return props.modelValue.filter(item => item).length;
});

// 是否有效
const isValid = computed(() => {
  const count = selectedCount.value;
  return count >= props.minCount && count <= props.maxCount;
});

// 是否可以选择更多
const canSelectMore = computed(() => {
  return selectedCount.value < props.maxCount;
});

// 处理选择变化
const handleChange = (stat: string, event: Event) => {
  const isChecked = (event.target as HTMLInputElement).checked;
  let newValue = [...props.modelValue];
  
  if (isChecked) {
    if (!newValue.includes(stat)) {
      newValue.push(stat);
    }
  } else {
    newValue = newValue.filter(item => item !== stat);
  }
  
  emit('update:modelValue', newValue);
};
</script>

<style scoped>
.substats-section {
  margin-top: 30px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.substats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.substats-header label {
  font-weight: 600;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  font-size: 15px;
  margin: 0;
}

.selected-count {
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  background: rgba(108, 117, 125, 0.8);
}

.selected-count.valid {
  background: rgba(40, 167, 69, 0.8);
}

.selected-count.invalid {
  background: rgba(220, 53, 69, 0.8);
}

.substats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.substat-checkbox {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.substat-checkbox:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.substat-checkbox label {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  margin: 0;
  width: 100%;
}

.substat-checkbox input[type="checkbox"] {
  margin-right: 10px;
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #007bff;
}

.checkbox-label {
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  font-size: 14px;
  font-weight: 500;
}

.substat-checkbox input[type="checkbox"]:disabled + .checkbox-label {
  opacity: 0.5;
  cursor: not-allowed;
}

.validation-hint {
  color: #ffc107;
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 193, 7, 0.3);
  font-weight: 500;
}
</style>