<template>
  <div class="background">
    <div class="slide-container">
      <div class="text-container">
        <div class="text-line">秋海棠 小栈</div>
        <div class="text-line">小栈 秋海棠</div>
        <div class="text-line">秋海棠 小栈</div>
      </div>
      <div class="text-container-dst">
        <div class="text-line">秋海棠 小栈</div>
        <div class="text-line">小栈 秋海棠</div>
        <div class="text-line">秋海棠 小栈</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  background: #000;
  overflow: hidden;
}
.background::before {
  content: '';
  position: absolute;
  z-index: 1;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(40deg,
    #000 0,
    #000 2px,
    transparent 2px,
    transparent 4px);
  opacity: 0.1;
}
.slide-container {
  display: flex;
  flex-direction: row;
  position: absolute;
  top: 50%;
  left: 50%;
  /* 恢复 transform 的完整属性，它在 @keyframes 中被覆盖 */
  transform: translate(-50%, -50%);
  z-index: -1;
  animation: slide 100s linear infinite;
}
.text-container,
.text-container-dst {
  display: flex;
  flex-direction: column;
  width: max-content;
  height: min-content;
  font-weight: bolder;
  color: #242424;
}
.text-line {
  font-size: 24rem;
  line-height: 24rem;
  overflow: hidden;
  white-space: nowrap;
  user-select: none;
  pointer-events: none;
}
@keyframes slide {
  0% {
    transform: translate(-50%, -50%) rotateZ(-15deg) translateX(25%);
  }
  100% {
    transform: translate(-50%, -50%) rotateZ(-15deg) translateX(-25%);
  }
}
</style>