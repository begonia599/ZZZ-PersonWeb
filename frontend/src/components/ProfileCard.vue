<template>
  <div class="profile-card">
    <!-- 装饰性背景 -->
    <div class="card-background">
      <div class="bg-pattern"></div>
      <div class="floating-elements">
        <div class="element" v-for="i in 8" :key="i" :style="getFloatingElementStyle(i)"></div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="card-content">
      <!-- 头像区域 -->
      <div class="avatar-container">
        <div class="avatar-ring">
          <img 
            :src="avatarUrl" 
            :alt="nickname" 
            class="avatar-image"
            @error="handleImageError"
          />
        </div>
        <div class="status-indicator"></div>
      </div>

      <!-- 信息区域 -->
      <div class="info-section">
        <h2 class="nickname">{{ nickname }}</h2>
        <p class="description">{{ description }}</p>
        
        <!-- 标签 -->
        <div class="tags">
          <span v-for="tag in tags" :key="tag" class="tag">{{ tag }}</span>
        </div>

        <!-- 统计信息 -->
        <div class="stats">
          <div class="stat-item">
            <div class="stat-number">{{ stats.posts }}</div>
            <div class="stat-label">文章</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.photos }}</div>
            <div class="stat-label">照片</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.tools }}</div>
            <div class="stat-label">工具</div>
          </div>
        </div>
      </div>

      <!-- 社交链接 -->
      <div class="social-links" v-if="socialLinks.length > 0">
        <a 
          v-for="link in socialLinks" 
          :key="link.name"
          :href="link.url" 
          :title="link.name"
          class="social-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span class="social-icon">{{ link.icon }}</span>
        </a>
      </div>
    </div>

    <!-- 装饰性边框 -->
    <div class="card-border"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface SocialLink {
  name: string;
  url: string;
  icon: string;
}

interface Stats {
  posts: number;
  photos: number;
  tools: number;
}

// Props
const props = defineProps<{
  avatarUrl?: string;
  nickname?: string;
  description?: string;
  tags?: string[];
  socialLinks?: SocialLink[];
  stats?: Stats;
}>();

// 默认值
const avatarUrl = computed(() => props.avatarUrl || '/images/characters/woziji.jpg');
const nickname = computed(() => props.nickname || '秋海棠');
const description = computed(() => props.description || '热爱编程与分享的开发者');
const tags = computed(() => props.tags || ['Vue.js', 'Python', '摄影爱好者']);
const socialLinks = computed(() => props.socialLinks || [
  { name: 'GitHub', url: '#', icon: '🐙' },
  { name: '邮箱', url: 'mailto:hello@example.com', icon: '📧' },
  { name: '博客', url: '#', icon: '📝' }
]);
// 实时统计数据
const realStats = ref({ posts: 0, photos: 0, tools: 2 });

const stats = computed(() => props.stats || realStats.value);

// 获取真实统计数据
const loadStats = async () => {
  try {
    const response = await fetch('/api/profile/stats');
    if (response.ok) {
      const data = await response.json();
      realStats.value = data;
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
    // 保持默认值
  }
};

// 生成浮动元素样式
const getFloatingElementStyle = (_index: number) => {
  const size = Math.random() * 6 + 3;
  const delay = Math.random() * 4;
  const duration = Math.random() * 3 + 4;
  const left = Math.random() * 100;
  const top = Math.random() * 100;
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  };
};

// 头像加载错误处理
const handleImageError = (event: Event) => {
  console.error('头像加载失败:', event);
  // 可以设置默认头像
  const img = event.target as HTMLImageElement;
  img.src = '/logo/logo.png'; // 使用默认头像
};

// 组件挂载时加载统计数据
onMounted(() => {
  loadStats();
});
</script>

<style scoped>
.profile-card {
  position: absolute;
  left: 20px;
  top: 150px;
  width: 280px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  transition: all 0.3s ease;
  z-index: 10;
}

.profile-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

/* 背景装饰 */
.card-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(255, 105, 180, 0.1) 0%,
    rgba(255, 20, 147, 0.1) 50%,
    rgba(199, 21, 133, 0.1) 100%
  );
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.element {
  position: absolute;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: floatUp infinite ease-in-out;
}

@keyframes floatUp {
  0% {
    transform: translateY(100%) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100%) rotate(360deg);
    opacity: 0;
  }
}

/* 主要内容 */
.card-content {
  position: relative;
  padding: 25px 20px;
  z-index: 2;
}

/* 头像区域 */
.avatar-container {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-ring {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff69b4, #ff1493);
  padding: 3px;
  animation: pulse 3s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 105, 180, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(255, 105, 180, 0);
  }
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: transform 0.3s ease;
}

.avatar-container:hover .avatar-image {
  transform: scale(1.05);
}

.status-indicator {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 16px;
  height: 16px;
  background: #00ff88;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.8);
  animation: blink 2s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.5; }
}

/* 信息区域 */
.info-section {
  text-align: center;
  margin-bottom: 20px;
}

.nickname {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  background: linear-gradient(135deg, #ff69b4, #ff1493);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 15px 0;
  line-height: 1.4;
}

/* 标签 */
.tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-bottom: 20px;
}

.tag {
  padding: 4px 10px;
  background: rgba(255, 105, 180, 0.2);
  border: 1px solid rgba(255, 105, 180, 0.3);
  border-radius: 12px;
  font-size: 11px;
  color: #ff69b4;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tag:hover {
  background: rgba(255, 105, 180, 0.3);
  transform: scale(1.05);
}

/* 统计信息 */
.stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.2);
}

/* 社交链接 */
.social-links {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  text-decoration: none;
  transition: all 0.3s ease;
}

.social-link:hover {
  background: rgba(255, 105, 180, 0.2);
  border-color: rgba(255, 105, 180, 0.4);
  transform: translateY(-2px);
}

.social-icon {
  font-size: 16px;
}

/* 装饰性边框 */
.card-border {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 20px;
  border: 1px solid transparent;
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.3), rgba(255, 20, 147, 0.3)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  pointer-events: none;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .profile-card {
    width: 260px;
    left: 15px;
  }
}

@media (max-width: 768px) {
  .profile-card {
    position: relative;
    left: auto;
    top: auto;
    width: 100%;
    max-width: 300px;
    margin: 0 auto 20px auto;
    order: 0; /* 在移动端显示在最前面 */
  }
  
  .card-content {
    padding: 20px 15px;
  }
  
  .nickname {
    font-size: 20px;
  }
  
  .description {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .profile-card {
    width: 95%;
    margin: 0 auto 15px auto;
  }
  
  .card-content {
    padding: 18px 12px;
  }
  
  .avatar-ring {
    width: 70px;
    height: 70px;
  }
  
  .nickname {
    font-size: 18px;
  }
  
  .description {
    font-size: 11px;
  }
  
  .tag {
    font-size: 10px;
    padding: 3px 8px;
  }
  
  .stat-number {
    font-size: 16px;
  }
  
  .stat-label {
    font-size: 10px;
  }
  
  .social-link {
    width: 32px;
    height: 32px;
  }
  
  .social-icon {
    font-size: 14px;
  }
}
</style>
