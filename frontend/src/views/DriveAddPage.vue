<template>
  <div class="drive-add-page">
    <div class="header-section">
      <h1>📤 添加驱动盘</h1>
      <router-link to="/toolbox/drive" class="back-btn">
        ← 返回列表
      </router-link>
    </div>
    
    <!-- 添加表单区域 -->
    <div class="form-section">
      <form @submit.prevent="addDrivePiece" class="drive-form">
        <div class="form-row">
          <!-- 套装选择 -->
          <FormSelect
            v-model="form.set_name"
            label="套装名称"
            placeholder="请选择套装"
            :options="setTypes"
            :required="true"
          />
          
          <!-- 位置选择 -->
          <FormSelect
            v-model="form.position"
            label="位置"
            :options="positionOptions"
            :required="true"
            @change="onPositionChange"
          />
          
          <!-- 主词条选择 -->
          <FormSelect
            v-model="form.main_stat_name"
            label="主词条"
            placeholder="请选择主词条"
            :options="availableMainStats"
            :required="true"
            :readonly="availableMainStats.length === 1"
            :hint="getPositionHint()"
            @change="onMainStatChange"
          />
        </div>
        
        <!-- 副词条选择区域 -->
        <SubstatsSelector
          v-if="form.main_stat_name"
          v-model="form.substats"
          :all-options="ALL_SUBSTATS"
          :exclude-options="[form.main_stat_name]"
          :min-count="3"
          :max-count="4"
        />

        <!-- 选择提示 -->
        <div v-if="!form.main_stat_name" class="selection-hint">
          <p>💡 请先选择驱动盘位置，主词条将根据位置自动设置或供您选择</p>
        </div>
        
        <!-- 操作按钮 -->
        <ActionButtons
          :submit-disabled="isSubmitting || isLoading || !isFormValid"
          :submit-loading="isSubmitting"
          submit-text="添加驱动盘"
          submit-loading-text="添加中..."
          reset-text="重置"
          @submit="addDrivePiece"
          @reset="resetForm"
        />
      </form>
    </div>

    <!-- 消息提示 -->
    <MessageToast
      :message="message.text"
      :type="message.type"
      :show="!!message.text"
      @close="clearMessage"
    />

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <LoadingAnimation />
      <p class="loading-text">正在加载数据...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDriveForm } from '../composables/useDriveForm';
import { useMessage } from '../composables/useMessage';

// 组件导入
import LoadingAnimation from '../components/LoadingAnimation.vue';
import FormSelect from '../components/FormSelect.vue';
import SubstatsSelector from '../components/SubstatsSelector.vue';
import MessageToast from '../components/MessageToast.vue';
import ActionButtons from '../components/ActionButtons.vue';

const router = useRouter();
const isLoading = ref(false);
const isSubmitting = ref(false);
const setTypes = ref<string[]>([]);
const statTypes = ref<string[]>([]);

// 使用组合式函数
const { message, showMessage, clearMessage } = useMessage();
const { 
  form, 
  POSITION_MAIN_STATS, 
  ALL_SUBSTATS, 
  availableMainStats,
  isFormValid,
  resetForm,
  onPositionChange,
  onMainStatChange,
  getPositionHint
} = useDriveForm();

// 位置选项
const positionOptions = [
  { label: '1号位', value: 1 },
  { label: '2号位', value: 2 },
  { label: '3号位', value: 3 },
  { label: '4号位', value: 4 },
  { label: '5号位', value: 5 },
  { label: '6号位', value: 6 }
];

// 加载套装类型
const loadSetTypes = async () => {
  try {
    const response = await fetch('/api/drive/set-types');
    const result = await response.json();
    
    if (response.ok) {
      setTypes.value = result;
    } else {
      showMessage('获取套装数据失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  }
};

// 加载词条类型
const loadStatTypes = async () => {
  try {
    const response = await fetch('/api/drive/stat-types');
    const result = await response.json();
    
    if (response.ok) {
      statTypes.value = result;
    } else {
      showMessage('获取词条数据失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  }
};

// 添加驱动盘
const addDrivePiece = async () => {
  if (!isFormValid.value) {
    showMessage('请完整填写表单信息并选择3-4个副词条', 'error');
    return;
  }

  isSubmitting.value = true;
  try {
    // 过滤掉空的副词条
    const filteredSubstats = form.value.substats.filter(s => s.trim() !== '');
    
    const requestData = {
      set_name: form.value.set_name,
      position: Number(form.value.position),
      main_stat_name: form.value.main_stat_name,
      substats: filteredSubstats
    };
    
    const response = await fetch('/api/drive/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    const result = await response.json();
    
    if (response.ok) {
      showMessage('驱动盘添加成功！', 'success');
      resetForm();
      // 2秒后自动跳转回列表页
      setTimeout(() => {
        router.push('/toolbox/drive');
      }, 2000);
    } else {
      showMessage(result.error || '添加失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(async () => {
  isLoading.value = true;
  try {
    // 并行加载所有数据
    await Promise.all([
      loadSetTypes(),
      loadStatTypes()
    ]);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
/* 只保留页面级别的样式 */
.drive-add-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
  position: relative;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-section h1 {
  color: #fff;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-weight: bold;
}

.back-btn {
  background: rgba(108, 117, 125, 0.8);
  backdrop-filter: blur(10px);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.back-btn:hover {
  background: rgba(84, 91, 98, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.form-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 35px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.selection-hint {
  background: rgba(23, 162, 184, 0.1);
  border: 1px solid rgba(23, 162, 184, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  text-align: center;
}

.selection-hint p {
  color: #17a2b8;
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-text {
  margin-top: 20px;
  font-size: 1.2em;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .drive-add-page {
    padding: 15px;
  }
  
  .form-section {
    padding: 25px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>