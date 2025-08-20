<template>
  <div class="drive-card" :class="{ 'fade-in': fadeIn }">
    <!-- 角色背景图片 -->
    <div class="card-background">
      <img 
        :src="characterImage" 
        :alt="`${drive.set_name} 推荐角色`"
        class="character-image"
        @error="onImageError"
      />
      <div class="background-overlay"></div>
    </div>
    
    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 顶部信息栏 -->
      <div class="top-bar">
        <span class="position-badge">{{ drive.position }}号位</span>
        <h3 class="set-name">{{ drive.set_name }}</h3>
      </div>
      
      <!-- 词条区域 -->
      <div class="stats-section">
        <!-- 主词条 -->
        <div class="main-stat">
          <div class="main-stat-value">{{ drive.main_stat_name }}</div>
          <div class="main-stat-level">+{{ drive.main_stat_level || 15 }}</div>
        </div>
        
        <!-- 分隔线 -->
        <div class="divider"></div>
        
        <!-- 副词条 -->
        <div class="substats">
          <div 
            v-for="(substat, index) in drive.substats_with_levels" 
            :key="index" 
            class="substat-item"
            :class="{ 'upgraded': substat.upgrade_count > 0 }"
          >
            <span class="substat-dot">•</span>
            <span class="substat-text">{{ substat.name }}</span>
            <span v-if="substat.upgrade_count > 0" class="substat-level">+{{ substat.upgrade_count }}</span>
          </div>
        </div>
      </div>
      
      <!-- 强化进度指示器 -->
      <div class="upgrade-progress">
        <div class="progress-label">强化进度</div>
        <div class="progress-dots">
          <span 
            v-for="n in 5" 
            :key="n"
            class="progress-dot"
            :class="{ 'active': n <= (drive.total_upgrades || 0) }"
          ></span>
        </div>
      </div>
      
      <!-- 底部信息 -->
      <div class="card-footer">
        <div class="character-name">{{ getRecommendedCharacter() }}</div>
        <div class="created-time">{{ formatTime(drive.created_at) }}</div>
      </div>
    </div>
    
    <!-- 编辑按钮 -->
    <button class="edit-btn" @click="handleEdit" title="编辑驱动盘">
      <span class="edit-icon">✏️</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

interface SubstatWithLevel {
  name: string;
  upgrade_count: number;
  is_original: boolean;
}

interface DrivePiece {
  drive_id: number;
  set_name: string;
  position: number;
  main_stat_name: string;
  main_stat_level?: number;
  substats: string[];
  substats_with_levels?: SubstatWithLevel[];
  total_upgrades?: number;
  created_at: string;
}

interface Props {
  drive: DrivePiece;
  fadeIn?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  fadeIn: false
});

const router = useRouter();
const imageError = ref(false);

// 处理编辑按钮点击
const handleEdit = (event: MouseEvent) => {
  event.stopPropagation(); // 防止卡片点击事件触发
  router.push(`/toolbox/drive/edit/${props.drive.drive_id}`);
};

// 根据套装名称获取推荐角色和对应图片
const getCharacterInfo = () => {
  const characterMap: Record<string, { name: string; image: string }> = {
    '折枝剑歌': { 
      name: '星见雅', 
      image: '/images/characters/zzjg.jpg' 
    },
    '冲击流派': { 
      name: '朱鸢', 
      image: '/images/characters/zhu_yuan.jpg' 
    },
    '街头巨星': { 
      name: '妮可', 
      image: '/images/characters/nicole.jpg' 
    },
    '荒野金属': { 
      name: '比利', 
      image: '/images/characters/billy.jpg' 
    },
    '摇摆爵士': { 
      name: '安比', 
      image: '/images/characters/anby.jpg' 
    },
    '燃烧烈火': { 
      name: '本', 
      image: '/images/characters/ben.jpg' 
    },
    // 默认角色
    '默认': { 
      name: '代理人', 
      image: '/images/characters/default.jpg' 
    }
  };
  
  return characterMap[props.drive.set_name] || characterMap['默认'];
};

const characterInfo = computed(() => getCharacterInfo());

const characterImage = computed(() => {
  if (imageError.value) {
    return '/images/characters/default.jpg';
  }
  return characterInfo.value.image;
});

const getRecommendedCharacter = () => {
  return `推荐：${characterInfo.value.name}`;
};

const onImageError = () => {
  imageError.value = true;
};

const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  return date.toLocaleDateString('zh-CN');
};
</script>

<style scoped>
.drive-card {
  position: relative;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  /* 30:37 的宽高比，基于宽度320px */
  width: 100%;
  aspect-ratio: 30/37;
  cursor: pointer;
}

.drive-card.fade-in {
  animation: fadeInUp 0.5s ease-out;
}

.drive-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.3);
}

.drive-card:hover .character-image {
  transform: scale(1.05);
}

.drive-card:hover .background-overlay {
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.3) 50%,
    rgba(0, 0, 0, 0.7) 100%
  );
}

.drive-card:hover .edit-btn {
  opacity: 1;
  transform: scale(1);
}

/* 背景图片区域 */
.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.character-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.3s ease;
  filter: brightness(0.8);
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.2) 0%,
    rgba(0, 0, 0, 0.4) 50%,
    rgba(0, 0, 0, 0.75) 100%
  );
  transition: background 0.3s ease;
}

/* 卡片内容 */
.card-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  color: white;
}

/* 顶部信息栏 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.position-badge {
  background: rgba(0, 123, 255, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.set-name {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  text-align: right;
  line-height: 1.2;
  max-width: 60%;
}

/* 词条区域 */
.stats-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

/* 主词条 */
.main-stat {
  margin-bottom: 16px;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.main-stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}

.main-stat-level {
  font-size: 14px;
  color: #4ECDC4;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

/* 分隔线 */
.divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.3);
  margin: 16px 0;
}

/* 副词条 */
.substats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.substat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.substat-item.upgraded {
  background: rgba(78, 205, 196, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  border-left: 3px solid #4ECDC4;
}

.substat-dot {
  color: rgba(0, 123, 255, 0.8);
  font-size: 16px;
  font-weight: bold;
  line-height: 1;
  flex-shrink: 0;
}

.substat-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  flex: 1;
}

.substat-level {
  font-size: 12px;
  color: #4ECDC4;
  font-weight: 600;
  background: rgba(78, 205, 196, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

/* 强化进度指示器 */
.upgrade-progress {
  margin: 16px 0 8px 0;
  padding: 8px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 6px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.progress-dots {
  display: flex;
  gap: 4px;
}

.progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.progress-dot.active {
  background: #4ECDC4;
  box-shadow: 0 0 8px rgba(78, 205, 196, 0.5);
}

/* 底部信息 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.character-name {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 123, 255, 0.3);
  padding: 4px 8px;
  border-radius: 6px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.created-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

/* 编辑按钮 */
.edit-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  opacity: 0;
  transform: scale(0.8);
  backdrop-filter: blur(5px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.edit-btn:hover {
  background: rgba(78, 205, 196, 0.9);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(78, 205, 196, 0.4);
}

.edit-icon {
  font-size: 16px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-content {
    padding: 16px;
  }
  
  .set-name {
    font-size: 14px;
  }
  
  .main-stat-value {
    font-size: 18px;
  }
  
  .substat-text {
    font-size: 13px;
  }
  
  .edit-btn {
    width: 32px;
    height: 32px;
    bottom: 10px;
    right: 10px;
  }
  
  .edit-icon {
    font-size: 14px;
  }
}
</style>