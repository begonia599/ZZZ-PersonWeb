<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p>&copy; {{ currentYear }} 秋海棠的个人网站. All Rights Reserved.</p>
      <p>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" class="beian-link">
          苏ICP备2025190782号-1
        </a>
        <!-- 如果有公安备案，也可以加上 -->
        <!-- <span class="separator">|</span> -->
        <!-- <a href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=XXXXXXXXXXXXXX" target="_blank" rel="noopener noreferrer" class="beian-link">
          <img src="/path/to/gongan_logo.png" alt="公安备案图标" class="gongan-logo"> 粤公网安备 XXXXXXXXXXXXXX号
        </a> -->
      </p>
      <p class="powered-by">Powered by Vue 3 & Vite</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const currentYear = ref(new Date().getFullYear());
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
  margin-top: auto; /* 确保页脚推到底部 */
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