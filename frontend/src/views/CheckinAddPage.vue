<template>
  <div class="checkin-add-page">
    <h1>{{ isCheckinMode ? '📝 打卡记录' : '➕ 创建打卡任务' }}</h1>
    
    <div class="form-container">
      <form @submit.prevent="submitForm" v-if="!isCheckinMode">
        <div class="form-group">
          <label for="title">任务名称 *</label>
          <input 
            type="text" 
            id="title" 
            v-model="formData.title" 
            placeholder="例如：每日运动打卡"
            required
          />
        </div>

        <div class="form-group">
          <label for="frequency">打卡频率 *</label>
          <select id="frequency" v-model="formData.frequency" required>
            <option value="daily">每天</option>
            <option value="weekly">每周</option>
            <option value="monthly">每月</option>
            <option value="custom">自定义</option>
          </select>
        </div>

        <div class="form-group" v-if="formData.frequency === 'custom'">
          <label for="customDays">自定义天数 *</label>
          <input 
            type="number" 
            id="customDays" 
            v-model.number="formData.customDays" 
            placeholder="例如：3"
            min="1"
            :required="formData.frequency === 'custom'"
          />
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="formData.useCustomStartDate"
            />
            <span>自定义开始日期（默认为今天）</span>
          </label>
        </div>

        <div class="form-group" v-if="formData.useCustomStartDate">
          <label for="startDate">开始日期 *</label>
          <input 
            type="date" 
            id="startDate" 
            v-model="formData.startDate" 
            :required="formData.useCustomStartDate"
          />
        </div>

        <div class="form-group">
          <label for="endMode">结束方式 *</label>
          <select id="endMode" v-model="formData.endMode" required>
            <option value="duration">持续天数</option>
            <option value="long-term">长期任务</option>
            <option value="custom">自定义结束日期</option>
          </select>
        </div>

        <div class="form-group" v-if="formData.endMode === 'duration'">
          <label for="duration">持续天数 *</label>
          <div class="duration-input-group">
            <input 
              type="number" 
              id="duration" 
              v-model.number="formData.duration" 
              placeholder="例如：30"
              min="1"
              :required="formData.endMode === 'duration'"
            />
            <span class="input-suffix">天</span>
          </div>
          <div class="quick-duration-buttons">
            <button type="button" @click="formData.duration = 7" class="quick-btn">7天</button>
            <button type="button" @click="formData.duration = 21" class="quick-btn">21天</button>
            <button type="button" @click="formData.duration = 30" class="quick-btn">30天</button>
            <button type="button" @click="formData.duration = 60" class="quick-btn">60天</button>
            <button type="button" @click="formData.duration = 100" class="quick-btn">100天</button>
          </div>
        </div>

        <div class="form-group" v-if="formData.endMode === 'long-term'">
          <div class="info-box">
            <span class="info-icon">ℹ️</span>
            <span>长期任务没有固定结束日期，您可以随时在任务列表中手动终止。</span>
          </div>
        </div>

        <div class="form-group" v-if="formData.endMode === 'custom'">
          <label for="endDate">结束日期 *</label>
          <input 
            type="date" 
            id="endDate" 
            v-model="formData.endDate" 
            :required="formData.endMode === 'custom'"
            :min="formData.useCustomStartDate ? formData.startDate : getTodayDate()"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? '创建中...' : '创建任务' }}
          </button>
          <button type="button" @click="goBack" class="cancel-btn">
            取消
          </button>
        </div>
      </form>

      <!-- 打卡表单 -->
      <form @submit.prevent="submitCheckin" v-else>
        <div class="checkin-info">
          <h2>{{ currentTask?.title }}</h2>
          <p class="task-meta">
            打卡次数：{{ currentTask?.checked_count }}/{{ currentTask?.total_count }}
          </p>
        </div>

        <div class="form-group">
          <label for="note">打卡备注（可选）</label>
          <textarea 
            id="note" 
            v-model="checkinData.note" 
            rows="4"
            placeholder="记录今天的心得或想法..."
          ></textarea>
        </div>

        <div class="form-group">
          <label for="image">打卡图片（可选）</label>
          <div class="image-upload-container">
            <input 
              type="file" 
              id="image" 
              ref="imageInput"
              accept="image/*"
              @change="handleImageSelect"
              style="display: none;"
            />
            <button type="button" @click="triggerImageUpload" class="upload-trigger-btn">
              📷 选择图片
            </button>
            <div v-if="imagePreview" class="image-preview">
              <img :src="imagePreview" alt="预览图片" />
              <button type="button" @click="removeImage" class="remove-image-btn">
                ✕ 移除
              </button>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? '提交中...' : '✓ 完成打卡' }}
          </button>
          <button type="button" @click="goBack" class="cancel-btn">
            取消
          </button>
        </div>
      </form>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

interface CheckinTask {
  id: number;
  title: string;
  frequency: string;
  start_date: string;
  end_date: string;
  total_count: number;
  checked_count: number;
}

const router = useRouter();
const route = useRoute();
const isSubmitting = ref(false);
const message = ref({ text: '', type: '' });
const imageInput = ref<HTMLInputElement | null>(null);
const imagePreview = ref<string | null>(null);
const selectedImage = ref<File | null>(null);
const currentTask = ref<CheckinTask | null>(null);

// 判断是打卡模式还是创建模式
const isCheckinMode = ref(false);
const taskId = ref<number | null>(null);

// 创建任务的表单数据
const formData = ref({
  title: '',
  frequency: 'daily',
  customDays: 1,
  startDate: '',
  endMode: 'duration', // duration(持续天数), long-term(长期), custom(自定义日期)
  duration: 30, // 持续天数，默认30天
  endDate: '',
  useCustomStartDate: false, // 是否使用自定义开始日期
});

// 打卡的表单数据
const checkinData = ref({
  note: '',
});

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 获取今天日期
const getTodayDate = () => {
  return new Date().toISOString().split('T')[0];
};

// 返回
const goBack = () => {
  router.back();
};

// 触发图片选择
const triggerImageUpload = () => {
  imageInput.value?.click();
};

// 处理图片选择
const handleImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (file) {
    if (!file.type.startsWith('image/')) {
      showMessage('请选择图片文件', 'error');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB 限制
      showMessage('图片大小不能超过10MB', 'error');
      return;
    }
    
    selectedImage.value = file;
    
    // 生成预览
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

// 移除图片
const removeImage = () => {
  selectedImage.value = null;
  imagePreview.value = null;
  if (imageInput.value) {
    imageInput.value.value = '';
  }
};

// 提交创建任务表单
const submitForm = async () => {
  if (isSubmitting.value) return;
  
  isSubmitting.value = true;
  
  try {
    // 确定开始日期
    const startDate = formData.value.useCustomStartDate && formData.value.startDate 
      ? formData.value.startDate 
      : getTodayDate();
    
    // 确定结束日期
    let endDate = null;
    
    if (formData.value.endMode === 'duration') {
      // 持续天数模式：计算结束日期
      const start = new Date(startDate);
      start.setDate(start.getDate() + formData.value.duration);
      endDate = start.toISOString().split('T')[0];
    } else if (formData.value.endMode === 'custom') {
      // 自定义日期模式
      endDate = formData.value.endDate;
      
      // 验证日期
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (end < start) {
        throw new Error('结束日期不能早于开始日期');
      }
    } else if (formData.value.endMode === 'long-term') {
      // 长期任务：设置为一个很远的日期（比如100年后）
      const start = new Date(startDate);
      start.setFullYear(start.getFullYear() + 100);
      endDate = start.toISOString().split('T')[0];
    }
    
    // 准备提交的数据
    const submitData = {
      title: formData.value.title,
      frequency: formData.value.frequency,
      custom_days: formData.value.frequency === 'custom' ? formData.value.customDays : undefined,
      start_date: startDate,
      end_date: endDate,
      is_long_term: formData.value.endMode === 'long-term', // 标记是否为长期任务
      duration: formData.value.endMode === 'duration' ? formData.value.duration : undefined,
    };
    
    const response = await fetch('/api/checkin/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(submitData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    showMessage('打卡任务创建成功！', 'success');
    
    // 延迟跳转，让用户看到成功消息
    setTimeout(() => {
      router.push('/toolbox/checkin');
    }, 1500);
    
  } catch (error) {
    console.error('创建任务时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`创建失败: ${errorMessage}`, 'error');
  } finally {
    isSubmitting.value = false;
  }
};

// 提交打卡
const submitCheckin = async () => {
  if (isSubmitting.value || !taskId.value) return;
  
  isSubmitting.value = true;
  
  try {
    const formDataToSend = new FormData();
    formDataToSend.append('task_id', taskId.value.toString());
    formDataToSend.append('note', checkinData.value.note);
    
    if (selectedImage.value) {
      formDataToSend.append('image', selectedImage.value);
    }
    
    const response = await fetch('/api/checkin/records', {
      method: 'POST',
      body: formDataToSend,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    showMessage('打卡成功！', 'success');
    
    // 延迟跳转
    setTimeout(() => {
      router.push('/toolbox/checkin');
    }, 1500);
    
  } catch (error) {
    console.error('打卡时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`打卡失败: ${errorMessage}`, 'error');
  } finally {
    isSubmitting.value = false;
  }
};

// 加载任务详情（打卡模式）
const loadTask = async (id: number) => {
  try {
    const response = await fetch(`/api/checkin/tasks/${id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    currentTask.value = result;
    
  } catch (error) {
    console.error('加载任务详情时出错:', error);
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    showMessage(`加载失败: ${errorMessage}`, 'error');
  }
};

onMounted(() => {
  // 检查是否是打卡模式
  const action = route.query.action as string;
  const id = route.query.task_id as string;
  
  if (action === 'checkin' && id) {
    isCheckinMode.value = true;
    taskId.value = parseInt(id, 10);
    loadTask(taskId.value);
  } else {
    // 设置默认日期（当用户选择自定义日期时使用）
    const today = getTodayDate();
    const nextMonth = new Date();
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    
    formData.value.startDate = today;
    formData.value.endDate = nextMonth.toISOString().split('T')[0];
  }
});
</script>

<style scoped>
.checkin-add-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

h1 {
  text-align: center;
  color: #fff;
  margin-bottom: 30px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-weight: bold;
}

h2 {
  color: #fff;
  margin-bottom: 10px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.form-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.checkin-info {
  margin-bottom: 25px;
  padding: 20px;
  background: rgba(76, 175, 80, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.checkin-info h2 {
  margin: 0 0 10px 0;
}

.task-meta {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #fff;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: rgba(76, 175, 80, 0.8);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #fff;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
  transform: scale(1.2);
}

.checkbox-label span {
  user-select: none;
}

.duration-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.duration-input-group input {
  flex: 1;
}

.input-suffix {
  color: #fff;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
}

.quick-duration-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 8px 16px;
  background: rgba(76, 175, 80, 0.6);
  color: white;
  border: 1px solid rgba(76, 175, 80, 0.8);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-btn:hover {
  background: rgba(76, 175, 80, 0.8);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.quick-btn:active {
  transform: translateY(0);
}

.info-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(33, 150, 243, 0.15);
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.info-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.upload-trigger-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.8), rgba(25, 118, 210, 0.8));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  align-self: flex-start;
}

.upload-trigger-btn:hover {
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.9), rgba(21, 101, 192, 0.9));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.image-preview {
  position: relative;
  max-width: 300px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.remove-image-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 6px 12px;
  background: rgba(244, 67, 54, 0.9);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-image-btn:hover {
  background: rgba(211, 47, 47, 1);
  transform: scale(1.05);
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.submit-btn,
.cancel-btn {
  flex: 1;
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(46, 125, 50, 0.8));
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.9), rgba(27, 94, 32, 0.9));
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.cancel-btn {
  background: rgba(158, 158, 158, 0.8);
  color: white;
}

.cancel-btn:hover {
  background: rgba(117, 117, 117, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(158, 158, 158, 0.4);
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  z-index: 10000;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.message.success {
  background: rgba(76, 175, 80, 0.9);
}

.message.error {
  background: rgba(244, 67, 54, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .checkin-add-page {
    padding: 15px;
    padding-top: 100px;
  }
  
  .form-container {
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .submit-btn,
  .cancel-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .checkin-add-page {
    padding: 10px;
    padding-top: 120px;
  }
  
  h1 {
    font-size: 1.5em;
    margin-bottom: 20px;
  }
  
  .form-container {
    padding: 15px;
  }
  
  .image-preview {
    max-width: 100%;
  }
}
</style>

