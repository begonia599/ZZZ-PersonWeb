<template>
  <div class="quote-dialog">
    <!-- 对话框容器 -->
    <div class="dialog-container" :class="{ 'show': isVisible }">
      <!-- 对话框头部 -->
      <div class="dialog-header">
        <div class="avatar-container">
          <div class="avatar">💭</div>
          <div class="avatar-glow"></div>
        </div>
        <div class="dialog-title">
          <h3>{{ currentQuote.author || '智慧之声' }}</h3>
          <p class="subtitle">{{ currentQuote.category || '人生感悟' }}</p>
        </div>
        <div class="dialog-controls">
          <button 
            class="control-btn" 
            @click="toggleAutoPlay" 
            :title="isAutoPlaying ? '暂停' : '播放'"
          >
            {{ isAutoPlaying ? '⏸️' : '▶️' }}
          </button>
          <button 
            class="control-btn" 
            @click="nextQuote" 
            title="下一句"
          >
            ⏭️
          </button>
        </div>
      </div>

      <!-- 对话框内容 -->
      <div class="dialog-content">
        <div class="quote-bubble">
          <div class="quote-text">
            <span class="typed-text">{{ displayedText }}</span>
          </div>
          <div class="bubble-tail"></div>
        </div>
        
        <!-- 进度指示器 -->
        <div class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${typingProgress}%` }"
            ></div>
          </div>
          <div class="progress-text">
            {{ currentQuoteIndex + 1 }} / {{ quotes.length }}
          </div>
        </div>
      </div>

      <!-- 装饰性粒子效果 -->
      <div class="particles">
        <div 
          v-for="i in 8" 
          :key="i" 
          class="particle"
          :style="getParticleStyle()"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';

interface Quote {
  text: string;
  author?: string;
  category?: string;
}

const quotes = ref<Quote[]>([
  {
    text: "生活不是等待暴风雨过去，而是学会在雨中起舞。",
    author: "维维安·格林",
    category: "人生哲理"
  },
  {
    text: "每一次的失败，都是成功的彩排。",
    author: "奥普拉·温弗瑞",
    category: "励志语录"
  },
  {
    text: "代码是诗，程序员是诗人。",
    author: "编程格言",
    category: "技术感悟"
  },
  {
    text: "最好的时光，是在路上；最美的自己，是在远方。",
    author: "三毛",
    category: "旅行感悟"
  },
  {
    text: "保持好奇心，世界会变得更有趣。",
    author: "爱因斯坦",
    category: "智慧箴言"
  },
  {
    text: "用心记录每一个美好瞬间，让时光慢下来。",
    author: "摄影感悟",
    category: "艺术人生"
  },
  {
    text: "梦想不会逃跑，会逃跑的永远都是自己。",
    author: "村上春树",
    category: "梦想追求"
  },
  {
    text: "编程的乐趣在于创造，而不仅仅是解决问题。",
    author: "技术思考",
    category: "编程哲学"
  }
]);

const currentQuoteIndex = ref(0);
const displayedText = ref('');
const isVisible = ref(false);
const isTyping = ref(false);
const isAutoPlaying = ref(true);
const typingSpeed = 80; // 毫秒
const pauseBetweenQuotes = 3000; // 3秒
const displayDuration = 5000; // 5秒显示完整文本

let typingInterval: NodeJS.Timeout | null = null;
let autoPlayTimeout: NodeJS.Timeout | null = null;

// 当前名言
const currentQuote = computed(() => {
  return quotes.value[currentQuoteIndex.value] || quotes.value[0];
});

// 打字进度
const typingProgress = computed(() => {
  if (!currentQuote.value.text) return 0;
  return (displayedText.value.length / currentQuote.value.text.length) * 100;
});

// 获取粒子样式
const getParticleStyle = () => {
  const size = Math.random() * 3 + 1;
  const delay = Math.random() * 4;
  const duration = Math.random() * 3 + 2;
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

// 开始打字效果
const startTyping = () => {
  if (isTyping.value) return;
  
  displayedText.value = '';
  isTyping.value = true;
  
  const fullText = currentQuote.value.text;
  let charIndex = 0;
  
  typingInterval = setInterval(() => {
    if (charIndex < fullText.length) {
      displayedText.value += fullText[charIndex];
      charIndex++;
    } else {
      // 打字完成
      isTyping.value = false;
      clearInterval(typingInterval!);
      
      // 显示完整文本一段时间后，开始下一句
      if (isAutoPlaying.value) {
        autoPlayTimeout = setTimeout(() => {
          nextQuote();
        }, displayDuration);
      }
    }
  }, typingSpeed);
};

// 下一句名言
const nextQuote = () => {
  clearInterval(typingInterval!);
  clearTimeout(autoPlayTimeout!);
  
  currentQuoteIndex.value = (currentQuoteIndex.value + 1) % quotes.value.length;
  
  setTimeout(() => {
    startTyping();
  }, 500); // 短暂延迟
};

// 切换自动播放
const toggleAutoPlay = () => {
  isAutoPlaying.value = !isAutoPlaying.value;
  
  if (isAutoPlaying.value && !isTyping.value) {
    // 如果当前没在打字，开始下一句
    autoPlayTimeout = setTimeout(() => {
      nextQuote();
    }, pauseBetweenQuotes);
  } else if (!isAutoPlaying.value) {
    // 暂停自动播放
    clearTimeout(autoPlayTimeout!);
  }
};



onMounted(() => {
  // 延迟显示动画
  setTimeout(() => {
    isVisible.value = true;
  }, 1000);
  
  // 再延迟开始打字
  setTimeout(() => {
    startTyping();
  }, 1500);
});

onUnmounted(() => {
  clearInterval(typingInterval!);
  clearTimeout(autoPlayTimeout!);
});
</script>

<style scoped>
.quote-dialog {
  position: absolute;
  top: 65%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 8;
  max-width: 600px;
  width: 90%;
}

.dialog-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  position: relative;
  opacity: 0;
  transform: translateY(30px) scale(0.9);
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.dialog-container.show {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* 对话框头部 */
.dialog-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.8), rgba(255, 20, 147, 0.8));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 2;
}

.avatar-glow {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.4), rgba(255, 20, 147, 0.4));
  border-radius: 50%;
  z-index: 1;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.1); opacity: 0.3; }
}

.dialog-title {
  flex: 1;
  color: white;
}

.dialog-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.subtitle {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

.dialog-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

/* 对话框内容 */
.dialog-content {
  position: relative;
}

.quote-bubble {
  background: rgba(0, 0, 0, 0.6);
  border-radius: 15px;
  padding: 20px 25px;
  position: relative;
  margin-bottom: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.quote-bubble::before {
  content: '"';
  position: absolute;
  top: -10px;
  left: 20px;
  font-size: 40px;
  color: rgba(255, 105, 180, 0.6);
  font-family: serif;
}

.quote-bubble::after {
  content: '"';
  position: absolute;
  bottom: -15px;
  right: 20px;
  font-size: 40px;
  color: rgba(255, 105, 180, 0.6);
  font-family: serif;
}

.bubble-tail {
  position: absolute;
  bottom: -8px;
  left: 30px;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 8px solid rgba(0, 0, 0, 0.6);
}

.quote-text {
  font-size: 16px;
  line-height: 1.6;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  min-height: 50px;
  display: flex;
  align-items: center;
}

.typed-text {
  flex: 1;
}

/* 进度指示器 */
.progress-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  flex: 1;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff69b4, #ff1493);
  border-radius: 2px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6));
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-20px); }
  100% { transform: translateX(20px); }
}

.progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  min-width: 40px;
  text-align: center;
}

/* 粒子效果 */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  border-radius: 20px;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 105, 180, 0.6);
  border-radius: 50%;
  animation: float infinite ease-in-out;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quote-dialog {
    position: relative; /* 改为相对定位，避免重合 */
    top: auto;
    left: auto;
    transform: none;
    max-width: 95%;
    margin: 20px auto; /* 添加上下边距 */
    order: 2; /* 设置显示顺序在照片轮播之后 */
  }
  
  .dialog-container {
    padding: 18px;
    margin: 0 10px; /* 增加左右边距 */
  }
  
  .dialog-header {
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
  }
  
  .avatar {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .dialog-title h3 {
    font-size: 16px;
  }
  
  .subtitle {
    font-size: 11px;
  }
  
  .quote-text {
    font-size: 14px;
    min-height: 35px;
    line-height: 1.5;
  }
  
  .quote-bubble {
    padding: 15px 18px;
    margin-bottom: 12px;
  }
  
  .control-btn {
    width: 30px;
    height: 30px;
    font-size: 12px;
  }
  
  .progress-text {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .quote-dialog {
    position: relative;
    top: auto;
    left: auto;
    transform: none;
    max-width: 98%;
    margin: 15px auto; /* 减少边距，更紧凑 */
    order: 2;
  }
  
  .dialog-container {
    padding: 12px;
    margin: 0 5px;
  }
  
  .dialog-header {
    margin-bottom: 12px;
  }
  
  .avatar {
    width: 35px;
    height: 35px;
    font-size: 14px;
  }
  
  .dialog-title h3 {
    font-size: 14px;
  }
  
  .subtitle {
    font-size: 10px;
  }
  
  .quote-bubble {
    padding: 12px 15px;
    margin-bottom: 10px;
  }
  
  .quote-text {
    font-size: 13px;
    min-height: 30px;
  }
  
  .control-btn {
    width: 28px;
    height: 28px;
    font-size: 11px;
  }
  
  .progress-text {
    font-size: 10px;
    min-width: 35px;
  }
  
  .particles {
    display: none; 
  }
}
</style>
