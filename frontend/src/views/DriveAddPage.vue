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
          <div class="form-group">
            <label>套装名称</label>
            <select v-model="form.set_name" required>
              <option value="">请选择套装</option>
              <option v-for="setName in setTypes" :key="setName" :value="setName">
                {{ setName }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>位置</label>
            <select v-model.number="form.position" required>
              <option value="">请选择位置</option>
              <option value="1">1号位</option>
              <option value="2">2号位</option>
              <option value="3">3号位</option>
              <option value="4">4号位</option>
              <option value="5">5号位</option>
              <option value="6">6号位</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>主词条</label>
            <select v-model="form.main_stat_name" required>
              <option value="">请选择主词条</option>
              <option v-for="statName in statTypes" :key="statName" :value="statName">
                {{ statName }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label>副词条 (最多4个)</label>
          <div class="substats-container">
            <div v-for="(substat, index) in form.substats" :key="index" class="substat-item">
              <select v-model="form.substats[index]">
                <option value="">请选择副词条</option>
                <option v-for="statName in statTypes" :key="statName" :value="statName">
                  {{ statName }}
                </option>
              </select>
              <button type="button" @click="removeSubstat(index)" class="remove-btn">×</button>
            </div>
            <button v-if="form.substats.length < 4" type="button" @click="addSubstat" class="add-substat-btn">
              + 添加副词条
            </button>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="submit" :disabled="isSubmitting || isLoading" class="submit-btn">
            {{ isSubmitting ? '添加中...' : '添加驱动盘' }}
          </button>
          <button type="button" @click="resetForm" class="reset-btn">重置</button>
        </div>
      </form>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <LoadingAnimation />
      <p class="loading-text">正在加载数据...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import LoadingAnimation from '../components/LoadingAnimation.vue';

interface DriveForm {
  set_name: string;
  position: number | string;
  main_stat_name: string;
  substats: string[];
}

const router = useRouter();
const isLoading = ref(false);
const isSubmitting = ref(false);
const setTypes = ref<string[]>([]);
const statTypes = ref<string[]>([]);
const message = ref({ text: '', type: '' });

const form = ref<DriveForm>({
  set_name: '',
  position: '',
  main_stat_name: '',
  substats: ['']
});

// 添加副词条
const addSubstat = () => {
  if (form.value.substats.length < 4) {
    form.value.substats.push('');
  }
};

// 移除副词条
const removeSubstat = (index: number) => {
  form.value.substats.splice(index, 1);
  if (form.value.substats.length === 0) {
    form.value.substats.push('');
  }
};

// 重置表单
const resetForm = () => {
  form.value = {
    set_name: '',
    position: '',
    main_stat_name: '',
    substats: ['']
  };
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

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
.drive-add-page {
  padding: 20px;
  max-width: 800px;
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
  color: #333;
  margin: 0;
}

.back-btn {
  background: #6c757d;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background: #545b62;
}

/* 表单区域样式 */
.form-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.drive-form {
  max-width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #555;
}

.form-group select {
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
  background: white;
}

.form-group select:focus {
  outline: none;
  border-color: #007bff;
}

.substats-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.substat-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.substat-item select {
  flex: 1;
}

.remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.remove-btn:hover {
  background: #c82333;
}

.add-substat-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  align-self: flex-start;
  transition: background-color 0.3s;
}

.add-substat-btn:hover {
  background: #218838;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.submit-btn,
.reset-btn {
  padding: 15px 40px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.reset-btn {
  background: #6c757d;
  color: white;
}

.reset-btn:hover {
  background: #545b62;
  transform: translateY(-1px);
}

/* 加载状态样式 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-text {
  margin-top: 15px;
  font-size: 1.1em;
  color: #555;
}

/* 消息提示样式 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.message.success {
  background: #28a745;
}

.message.error {
  background: #dc3545;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .drive-add-page {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .submit-btn,
  .reset-btn {
    width: 100%;
  }
}
</style>