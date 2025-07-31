<template>
  <div class="loading-container">
    <div class="zzz-loading_anim"></div>
  </div>
</template>

<script setup lang="ts">
// 这个组件不需要脚本逻辑
</script>

<style scoped>
.loading-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  /* 移除背景颜色，使其透明 */
  background-color: transparent;
}
.zzz-loading_anim {
  min-width: 110px;
  min-height: 150px;
  /* 保持背景图片和动画设置 */
  background: url('https://zamyang.cn/api/image/jSPGd73xHu4Tg7h9Z8NXzw.webp') no-repeat;
  background-position: 0 6px;
  animation: zzz-loading_loop .5s steps(30) infinite;
  /* 保持颜色反转滤镜，使得黑色人物变成白色 */
  filter: invert(1);
}
@keyframes zzz-loading_loop {
  0% {
    background-position: 0 6px;
  }
  100% {
    background-position: 0 -4494px;
  }
}
</style>