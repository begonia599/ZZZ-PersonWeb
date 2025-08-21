<template>
  <div class="drive-edit-page">
    <div class="header-section">
      <h1>🛠️ 编辑驱动盘</h1>
      <div class="header-actions">
        <router-link to="/toolbox/drive" class="back-btn">
          ← 返回列表
        </router-link>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <LoadingAnimation />
      <p class="loading-text">正在加载驱动盘信息...</p>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="driveData" class="edit-content">
      <!-- 驱动盘信息展示 -->
      <div class="drive-info-section">
        <ChartContainer
          title="当前驱动盘信息"
          icon="💎"
          height="auto"
        >
          <div class="drive-info-content">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">套装:</span>
                <span class="info-value">{{ driveData.set_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">位置:</span>
                <span class="info-value">{{ driveData.position }}号位</span>
              </div>
              <div class="info-item">
                <span class="info-label">强化进度:</span>
                <span class="info-value">{{ driveData.total_upgrades || 0 }}/5</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间:</span>
                <span class="info-value">{{ formatTime(driveData.created_at) }}</span>
              </div>
            </div>
          </div>
        </ChartContainer>
      </div>

      <!-- 编辑选项 -->
      <div class="edit-options">
        <!-- 词条编辑 -->
        <ChartContainer
          title="词条编辑"
          icon="✏️"
          :has-controls="true"
          height="auto"
        >
          <template #controls>
            <button 
              class="action-btn save-btn"
              :disabled="!hasStatsChanges || isSaving"
              @click="saveStatsChanges"
            >
              {{ isSaving ? '保存中...' : '保存词条' }}
            </button>
          </template>

          <div class="stats-edit-content">
            <!-- 主词条编辑 -->
            <div class="main-stat-edit">
              <h4>主词条</h4>
              <div class="stat-edit-item">
                <label>词条类型:</label>
                <select 
                  v-model="editingMainStat" 
                  class="stat-select"
                >
                  <option 
                    v-for="stat in availableStats" 
                    :key="stat" 
                    :value="stat"
                  >
                    {{ stat }}
                  </option>
                </select>
              </div>
            </div>

            <!-- 副词条编辑 -->
            <div class="substats-edit">
              <h4>副词条 (最多4个)</h4>
              <div class="substats-edit-list">
                <div 
                  v-for="(substat, index) in editingSubstats" 
                  :key="index"
                  class="substat-edit-item"
                >
                  <select 
                    v-model="substat.name" 
                    class="stat-select"
                    @change="onSubstatChange"
                  >
                    <option value="">选择副词条</option>
                    <option 
                      v-for="stat in getAvailableSubstats(index)" 
                      :key="stat" 
                      :value="stat"
                    >
                      {{ stat }}
                    </option>
                  </select>
                  <button 
                    class="remove-btn"
                    @click="removeSubstat(index)"
                    :disabled="editingSubstats.length <= 1"
                  >
                    ✕
                  </button>
                </div>
                
                <button 
                  v-if="editingSubstats.length < 4"
                  class="add-substat-btn"
                  @click="addSubstat"
                >
                  + 添加副词条
                </button>
              </div>
            </div>
          </div>
        </ChartContainer>

        <!-- 强化管理 -->
        <ChartContainer
          title="强化管理"
          icon="⚡"
          height="auto"
        >
          <div class="upgrade-content">
            <!-- 强化进度 -->
            <div class="upgrade-progress-display">
              <div class="progress-info">
                <span class="progress-label">强化进度: {{ driveData.total_upgrades || 0 }}/5</span>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: ((driveData.total_upgrades || 0) / 5 * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- 3词条新词条选择 -->
            <div v-if="needNewSubstatSelection" class="new-substat-selection">
              <h5>选择第4个副词条</h5>
              <p class="selection-tip">当前为3词条驱动盘，第一次强化将生成第4个副词条（+0等级）</p>
              <select 
                v-model="selectedNewSubstat" 
                class="new-substat-select"
                :disabled="isUpgrading"
              >
                <option value="">请选择新副词条</option>
                <option 
                  v-for="stat in getAvailableNewSubstats()" 
                  :key="stat" 
                  :value="stat"
                >
                  {{ stat }}
                </option>
              </select>
            </div>

            <!-- 副词条强化状态 -->
            <div class="substats-upgrade-status">
              <h5>副词条强化等级</h5>
              <div class="substats-status-list">
                <div 
                  v-for="(substat, index) in driveData.substats_with_levels" 
                  :key="index"
                  class="substat-status-item"
                  :class="{ 
                    'original': substat.is_original,
                    'upgraded': substat.upgrade_count > 0 
                  }"
                >
                  <div class="substat-info">
                    <span class="substat-name">{{ substat.name }}</span>
                    <span class="substat-type">
                      {{ substat.is_original ? '原始' : '新增' }}
                    </span>
                  </div>
                  
                  <div class="substat-controls">
                    <span class="substat-level">+{{ substat.upgrade_count }}</span>
                    <div class="upgrade-buttons">
                      <button 
                        class="upgrade-btn-small decrement"
                        :disabled="substat.upgrade_count <= 0 || isUpgrading"
                        @click="decrementSubstat(substat)"
                        title="降级"
                      >
                        −
                      </button>
                      <button 
                        class="upgrade-btn-small increment"
                        :disabled="!canUpgrade || isUpgrading || needNewSubstatSelection"
                        @click="incrementSubstat(substat)"
                        :title="needNewSubstatSelection ? '请先选择第4个副词条' : '升级'"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>
                
                <!-- 3词条驱动盘的新词条生成按钮 -->
                <div v-if="needNewSubstatSelection" class="new-substat-action">
                  <button 
                    class="generate-new-substat-btn"
                    :disabled="!selectedNewSubstat || isUpgrading"
                    @click="generateNewSubstat"
                  >
                    {{ isUpgrading ? '生成中...' : '生成新副词条' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </ChartContainer>

        <!-- 危险操作 -->
        <ChartContainer
          title="危险操作"
          icon="⚠️"
          height="auto"
        >
          <div class="danger-content">
            <div class="danger-warning">
              <span class="warning-icon">⚠️</span>
              <p>以下操作不可撤销，请谨慎操作！</p>
            </div>
            
            <button 
              class="danger-btn delete-btn"
              @click="showDeleteModal = true"
              :disabled="isDeleting"
            >
              <span class="btn-icon">🗑️</span>
              {{ isDeleting ? '删除中...' : '删除此驱动盘' }}
            </button>
          </div>
        </ChartContainer>
      </div>
    </div>



    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
          <button class="close-btn" @click="showDeleteModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="delete-warning">
            <span class="warning-icon">🚨</span>
            <p>您确定要删除这个驱动盘吗？</p>
            <p class="warning-text">此操作将永久删除驱动盘及其所有强化记录，无法撤销！</p>
          </div>
          
          <div class="delete-actions">
            <button class="cancel-btn" @click="showDeleteModal = false">取消</button>
            <button class="confirm-delete-btn" @click="confirmDelete" :disabled="isDeleting">
              {{ isDeleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import LoadingAnimation from '../components/LoadingAnimation.vue';
import ChartContainer from '../components/ChartContainer.vue';

interface SubstatWithLevel {
  name: string;
  upgrade_count: number;
  is_original: boolean;
  substat_id: number;
}

interface DriveData {
  drive_id: number;
  set_name: string;
  position: number;
  main_stat_name: string;
  main_stat_level: number;
  substats_with_levels: SubstatWithLevel[];
  total_upgrades: number;
  created_at: string;
}



const router = useRouter();
const route = useRoute();

const driveId = route.params.id as string;
const isLoading = ref(true);
const isUpgrading = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);

const driveData = ref<DriveData | null>(null);
const availableStats = ref<string[]>([]);
const availableSubstats = ref<string[]>([]);

const editingMainStat = ref('');
const editingSubstats = ref<{ name: string }[]>([]);

const showDeleteModal = ref(false);
const selectedNewSubstat = ref('');
const message = ref({ text: '', type: '' });

// 检查是否可以强化
const canUpgrade = computed(() => {
  return driveData.value && (driveData.value.total_upgrades || 0) < 5;
});

// 检查是否需要新副词条选择（3词条驱动盘）
const needNewSubstatSelection = computed((): boolean => {
  return !!(driveData.value && 
         driveData.value.substats_with_levels.length === 3 && 
         (driveData.value.total_upgrades || 0) === 0);
});

// 检查词条是否有变化
const hasStatsChanges = computed(() => {
  if (!driveData.value) return false;
  
  const originalMainStat = driveData.value.main_stat_name;
  const originalSubstats = driveData.value.substats_with_levels.map(s => s.name).sort();
  const currentSubstats = editingSubstats.value.map(s => s.name).filter(n => n).sort();
  
  return editingMainStat.value !== originalMainStat || 
         JSON.stringify(originalSubstats) !== JSON.stringify(currentSubstats);
});

// 获取可用的新副词条（排除已有的副词条和主词条）
const getAvailableNewSubstats = (): string[] => {
  if (!driveData.value) return [];
  
  // 根据驱动盘准则定义的副词条
  const allSubstats = [
    '生命值', '生命值百分比', '攻击力', '攻击力百分比', 
    '防御力', '防御力百分比', '暴击率', '暴击伤害', 
    '穿透率', '异常精通'
  ];
  
  const usedStats = new Set([
    driveData.value.main_stat_name,
    ...driveData.value.substats_with_levels.map(s => s.name)
  ]);
  
  return allSubstats.filter(stat => !usedStats.has(stat));
};

// 获取可用的副词条（排除已选和主词条）
const getAvailableSubstats = (currentIndex: number): string[] => {
  const usedStats = new Set([
    editingMainStat.value,
    ...editingSubstats.value
      .map((s, idx) => idx !== currentIndex ? s.name : '')
      .filter(name => name)
  ]);
  
  return availableSubstats.value.filter(stat => !usedStats.has(stat));
};

// 添加副词条
const addSubstat = () => {
  if (editingSubstats.value.length < 4) {
    editingSubstats.value.push({ name: '' });
  }
};

// 移除副词条
const removeSubstat = (index: number) => {
  if (editingSubstats.value.length > 1) {
    editingSubstats.value.splice(index, 1);
  }
};

// 副词条变化处理
const onSubstatChange = () => {
  // 清理空的副词条项
  editingSubstats.value = editingSubstats.value.filter(s => s.name);
};

// 生成新副词条（3词条驱动盘专用）
const generateNewSubstat = async () => {
  if (!selectedNewSubstat.value) return;
  
  isUpgrading.value = true;
  
  try {
    // 直接调用强化API，让后端处理新副词条的生成
    const response = await fetch(`/api/drive/pieces/${driveId}/upgrade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        upgrade_type: 'new',
        new_substat_name: selectedNewSubstat.value
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showMessage('新副词条生成成功！', 'success');
      selectedNewSubstat.value = '';
      await loadDriveData();
    } else {
      showMessage(result.error || '生成新副词条失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isUpgrading.value = false;
  }
};

// 增加副词条等级
const incrementSubstat = async (substat: SubstatWithLevel) => {
  isUpgrading.value = true;
  
  try {
    const response = await fetch(`/api/drive/pieces/${driveId}/upgrade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        upgrade_type: 'existing',
        substat_id: substat.substat_id
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showMessage(`${substat.name} 强化成功！`, 'success');
      await loadDriveData();
    } else {
      showMessage(result.error || '强化失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isUpgrading.value = false;
  }
};

// 降低副词条等级
const decrementSubstat = async (substat: SubstatWithLevel) => {
  isUpgrading.value = true;
  
  try {
    const response = await fetch(`/api/drive/pieces/${driveId}/downgrade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        substat_id: substat.substat_id
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showMessage(`${substat.name} 降级成功！`, 'success');
      await loadDriveData();
    } else {
      showMessage(result.error || '降级失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isUpgrading.value = false;
  }
};

// 保存词条变化
const saveStatsChanges = async () => {
  isSaving.value = true;
  
  try {
    const filteredSubstats = editingSubstats.value
      .map(s => s.name)
      .filter(name => name);
    
    const response = await fetch(`/api/drive/pieces/${driveId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        main_stat_name: editingMainStat.value,
        substats: filteredSubstats
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showMessage('词条更新成功！', 'success');
      await loadDriveData(); // 重新加载数据
    } else {
      showMessage(result.error || '更新失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isSaving.value = false;
  }
};

// 确认删除
const confirmDelete = async () => {
  isDeleting.value = true;
  
  try {
    const response = await fetch(`/api/drive/pieces/${driveId}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      showMessage('驱动盘删除成功！', 'success');
      setTimeout(() => {
        router.push('/toolbox/drive');
      }, 1500);
    } else {
      const result = await response.json();
      showMessage(result.error || '删除失败', 'error');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
  } finally {
    isDeleting.value = false;
    showDeleteModal.value = false;
  }
};

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: '', type: '' };
  }, 3000);
};

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  return new Date(timeStr).toLocaleString('zh-CN');
};

// 加载驱动盘数据
const loadDriveData = async () => {
  try {
    const response = await fetch(`/api/drive/pieces/${driveId}`);
    const result = await response.json();
    
    if (response.ok) {
      driveData.value = result;
      
      // 初始化编辑数据
      editingMainStat.value = result.main_stat_name;
      editingSubstats.value = result.substats_with_levels.map((s: SubstatWithLevel) => ({
        name: s.name
      }));
      
      if (editingSubstats.value.length === 0) {
        editingSubstats.value.push({ name: '' });
      }
    } else {
      showMessage(result.error || '加载失败', 'error');
      router.push('/toolbox/drive');
    }
  } catch (error) {
    showMessage('网络错误，请稍后重试', 'error');
    router.push('/toolbox/drive');
  }
};

// 加载可用选项
const loadAvailableOptions = async () => {
  try {
    const [statsResponse] = await Promise.all([
      fetch('/api/drive/stat-types')
    ]);
    
    if (statsResponse.ok) {
      const stats = await statsResponse.json();
      availableStats.value = stats;
      availableSubstats.value = stats;
    }
  } catch (error) {
    console.error('加载选项失败:', error);
  }
};

onMounted(async () => {
  isLoading.value = true;
  await Promise.all([
    loadDriveData(),
    loadAvailableOptions()
  ]);
  isLoading.value = false;
});
</script>

<style scoped>
.drive-edit-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
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

.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.8);
}

.loading-text {
  margin-top: 20px;
  font-size: 1.1em;
}

.edit-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.drive-info-section {
  width: 100%;
}

.drive-info-content {
  padding: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.info-value {
  color: #fff;
  font-weight: 600;
}

.edit-options {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.stats-edit-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.main-stat-edit h4,
.substats-edit h4 {
  color: #fff;
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.stat-edit-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-edit-item label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  min-width: 80px;
}

.stat-select {
  flex: 1;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  backdrop-filter: blur(5px);
}

.stat-select:focus {
  outline: none;
  border-color: #4ECDC4;
  box-shadow: 0 0 10px rgba(78, 205, 196, 0.3);
}

.stat-select option {
  background: rgba(33, 37, 41, 0.95);
  color: #fff;
}

.substats-edit-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.substat-edit-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(220, 53, 69, 0.7);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover:not(:disabled) {
  background: rgba(220, 53, 69, 0.9);
  transform: scale(1.1);
}

.remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-substat-btn {
  padding: 10px 16px;
  background: rgba(40, 167, 69, 0.7);
  border: 1px solid rgba(40, 167, 69, 0.5);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.add-substat-btn:hover {
  background: rgba(40, 167, 69, 0.9);
  transform: translateY(-1px);
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.save-btn {
  background: linear-gradient(45deg, #4ECDC4, #45B7D1);
  color: white;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.4);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upgrade-btn {
  background: linear-gradient(45deg, #FF9F43, #FF6B6B);
  color: white;
}

.upgrade-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 159, 67, 0.4);
}

.upgrade-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upgrade-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.upgrade-progress-display {
  background: rgba(255, 255, 255, 0.05);
  padding: 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-label {
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(45deg, #4ECDC4, #45B7D1);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.substats-upgrade-status h5 {
  color: #fff;
  margin: 0 0 15px 0;
  font-size: 15px;
  font-weight: 600;
}

.substats-status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.substat-status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.substat-status-item.original {
  border-left: 3px solid #4ECDC4;
}

.substat-status-item.upgraded {
  background: rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.3);
}

.substat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.substat-name {
  color: #fff;
  font-weight: 600;
  font-size: 15px;
}

.substat-type {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
  width: fit-content;
}

.substat-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.substat-level {
  color: #4ECDC4;
  font-weight: 600;
  font-size: 16px;
  min-width: 30px;
  text-align: center;
}

.upgrade-buttons {
  display: flex;
  gap: 4px;
}

.upgrade-btn-small {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upgrade-btn-small.increment {
  background: linear-gradient(45deg, #4ECDC4, #45B7D1);
}

.upgrade-btn-small.decrement {
  background: linear-gradient(45deg, #FF6B6B, #DC3545);
}

.upgrade-btn-small:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.upgrade-btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.new-substat-selection {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}

.new-substat-selection h5 {
  color: #fff;
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
}

.selection-tip {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.new-substat-select {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  backdrop-filter: blur(5px);
}

.new-substat-select:focus {
  outline: none;
  border-color: #FFC107;
  box-shadow: 0 0 10px rgba(255, 193, 7, 0.3);
}

.new-substat-select option {
  background: rgba(33, 37, 41, 0.95);
  color: #fff;
}

.new-substat-action {
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  text-align: center;
}

.generate-new-substat-btn {
  padding: 10px 20px;
  background: linear-gradient(45deg, #FFC107, #FF9F43);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.generate-new-substat-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4);
}

.generate-new-substat-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.danger-content {
  padding: 20px;
  text-align: center;
}

.danger-warning {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
  padding: 20px;
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  border-radius: 10px;
}

.warning-icon {
  font-size: 32px;
}

.danger-warning p {
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 500;
}

.danger-btn {
  padding: 12px 24px;
  background: linear-gradient(45deg, #DC3545, #C82333);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
}

.danger-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
}

.danger-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 16px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background: rgba(33, 37, 41, 0.95);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  backdrop-filter: blur(15px);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.modal-body {
  padding: 20px;
}

.upgrade-tip {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.upgrade-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upgrade-option {
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upgrade-option:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #4ECDC4;
  transform: translateY(-1px);
}

.option-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.option-name {
  color: #fff;
  font-weight: 600;
  flex: 1;
}

.option-type {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

.option-current {
  color: #4ECDC4;
  font-weight: 600;
  font-size: 14px;
}

.delete-modal {
  max-width: 400px;
}

.delete-warning {
  text-align: center;
  margin-bottom: 25px;
}

.delete-warning .warning-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.delete-warning p {
  color: rgba(255, 255, 255, 0.9);
  margin: 8px 0;
}

.warning-text {
  color: rgba(255, 193, 7, 0.9) !important;
  font-size: 14px;
  font-style: italic;
}

.delete-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.cancel-btn {
  padding: 10px 20px;
  background: rgba(108, 117, 125, 0.8);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: rgba(108, 117, 125, 1);
}

.confirm-delete-btn {
  padding: 10px 20px;
  background: linear-gradient(45deg, #DC3545, #C82333);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-delete-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
}

.confirm-delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
}

.message.success {
  background: rgba(40, 167, 69, 0.9);
}

.message.error {
  background: rgba(220, 53, 69, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .drive-edit-page {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stats-edit-content {
    padding: 15px;
    gap: 25px;
  }
  
  .stat-edit-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .stat-edit-item label {
    min-width: auto;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .option-info {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .delete-actions {
    flex-direction: column;
  }
}
</style>