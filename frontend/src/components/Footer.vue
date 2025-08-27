<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p>&copy; {{ currentYear }} 秋海棠的个人网站. All Rights Reserved.</p>
      <p v-if="config.footer.showIcp || config.footer.showPoliceRecord">
        <a 
          v-if="config.footer.showIcp"
          :href="config.footer.icpUrl" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="beian-link"
        >
          {{ config.footer.icpNumber }}
        </a>
        <span v-if="config.footer.showIcp && config.footer.showPoliceRecord" class="separator">|</span>
        <a 
          v-if="config.footer.showPoliceRecord"
          :href="config.footer.policeUrl" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="beian-link"
        >
          {{ config.footer.policeNumber }}
        </a>
      </p>
      <p class="powered-by">Powered by Vue 3 & Vite</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const currentYear = ref(new Date().getFullYear());

// 默认配置（海外部署）
const config = ref({
  footer: {
    showIcp: false,
    icpNumber: '',
    icpUrl: '',
    showPoliceRecord: false,
    policeNumber: '',
    policeUrl: ''
  }
});

// 加载站点配置
onMounted(async () => {
  try {
    const response = await fetch('/site-config.json');
    if (response.ok) {
      const siteConfig = await response.json();
      config.value = siteConfig;
    }
  } catch (error) {
    console.log('使用默认配置（未找到site-config.json）');
  }
});
</script>

<style scoped>
.app-footer {
  background-color: #000; /* 黑色背景，与导航栏呼应 */
  color: #b0b0b0; /* 浅灰色文字 */
  padding: 20px 0;
  text-align: center;
  font-size: 0.9em;
  border-top: 1px solid #111; /* 顶部细边框 */
  position: relative; /* 确保在内容下方 */
  z-index: 10; /* 比背景低，比内容高 */
  width: 100%;
  box-sizing: border-box;
  margin-top: 300px; /* 进一步增加上边距，为下移的照片轮播组件留出更多空间 */
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-footer p {
  margin: 5px 0;
}

.beian-link {
  color: #b0b0b0;
  text-decoration: none;
  transition: color 0.3s ease;
}

.beian-link:hover {
  color: #00FF00; /* 悬停时绿色 */
}

.separator {
  margin: 0 10px;
  color: #555;
}

.gongan-logo {
  vertical-align: middle;
  margin-right: 5px;
  height: 18px; /* 调整图标大小 */
}

.powered-by {
  margin-top: 15px;
  font-size: 0.8em;
  color: #777;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .app-footer {
    padding: 15px 0;
    font-size: 0.8em;
  }
}
</style>