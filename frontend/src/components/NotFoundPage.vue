<template>
  <div class="not-found-container">
    <div class="content-wrapper">
      <h1>404</h1>
      <h2>页面走丢了</h2>
      <p>别担心，来玩个小游戏放松一下吧！</p>
      
      <!-- 游戏区域 -->
      <div class="game-container">
        <div class="game-header">
          <h3>🐍 贪吃蛇小游戏</h3>
          <div class="game-info">
            <span>得分: {{ score }}</span>
            <span>最高分: {{ highScore }}</span>
          </div>
        </div>
        
        <canvas 
          ref="gameCanvas" 
          :width="gameConfig.width" 
          :height="gameConfig.height"
          @touchstart="handleTouchStart"
          @touchmove="handleTouchMove"
          tabindex="0"
          @keydown="handleKeyDown"
        ></canvas>
        
        <div class="game-controls">
          <div class="mobile-controls" v-if="isMobile">
            <button @click="changeDirection('up')" class="control-btn">↑</button>
            <div class="horizontal-controls">
              <button @click="changeDirection('left')" class="control-btn">←</button>
              <button @click="toggleGame" class="play-btn">{{ gameState === 'playing' ? '暂停' : '开始' }}</button>
              <button @click="changeDirection('right')" class="control-btn">→</button>
            </div>
            <button @click="changeDirection('down')" class="control-btn">↓</button>
          </div>
          <div class="desktop-controls" v-else>
            <button @click="toggleGame" class="play-btn">{{ gameState === 'playing' ? '暂停' : '开始' }}</button>
            <button @click="resetGame" class="reset-btn">重新开始</button>
            <p class="controls-hint">使用方向键控制蛇的移动</p>
          </div>
        </div>
        
        <div v-if="gameState === 'gameOver'" class="game-over">
          <h4>游戏结束！</h4>
          <p>最终得分: {{ score }}</p>
          <p v-if="score > highScore">🎉 新纪录！</p>
          <button @click="resetGame" class="restart-btn">再来一局</button>
        </div>
      </div>
      
      <!-- 导航提示 -->
      <div class="navigation-hints">
        <h4>找不到想要的内容？试试这些：</h4>
        <div class="nav-buttons">
          <router-link to="/" class="nav-btn">🏠 回到主页</router-link>
          <router-link to="/blog" class="nav-btn">📝 查看博客</router-link>
          <router-link to="/toolbox" class="nav-btn">🛠️ 打开工具箱</router-link>
          <router-link to="/toolbox/travel" class="nav-btn">🌸 浏览旅记</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

// 游戏状态
type GameState = 'idle' | 'playing' | 'paused' | 'gameOver';
type Direction = 'up' | 'down' | 'left' | 'right';

interface Position {
  x: number;
  y: number;
}

// 响应式数据
const gameCanvas = ref<HTMLCanvasElement | null>(null);
const score = ref(0);
const highScore = ref(parseInt(localStorage.getItem('snakeHighScore') || '0'));
const gameState = ref<GameState>('idle');
const isMobile = ref(false);

// 游戏配置
const gameConfig = {
  width: 400,
  height: 400,
  tileSize: 20
};

// 游戏数据
let snake: Position[] = [{ x: 10, y: 10 }];
let food: Position = { x: 15, y: 15 };
let direction: Direction = 'right';
let nextDirection: Direction = 'right';
let gameLoop: ReturnType<typeof setInterval> | null = null;
let ctx: CanvasRenderingContext2D | null = null;

// 触摸控制
let touchStartX = 0;
let touchStartY = 0;

// 检测移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

// 初始化游戏
const initGame = () => {
  if (!gameCanvas.value) return;
  
  ctx = gameCanvas.value.getContext('2d');
  if (!ctx) return;
  
  // 重置游戏状态
  snake = [{ x: 10, y: 10 }];
  food = generateFood();
  direction = 'right';
  nextDirection = 'right';
  score.value = 0;
  gameState.value = 'idle';
  
  drawGame();
};

// 生成食物位置
const generateFood = (): Position => {
  let newFood: Position;
  do {
    newFood = {
      x: Math.floor(Math.random() * (gameConfig.width / gameConfig.tileSize)),
      y: Math.floor(Math.random() * (gameConfig.height / gameConfig.tileSize))
    };
  } while (snake.some(segment => segment.x === newFood.x && segment.y === newFood.y));
  
  return newFood;
};

// 绘制游戏
const drawGame = () => {
  if (!ctx) return;
  
  // 清空画布
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, gameConfig.width, gameConfig.height);
  
  // 绘制网格
  ctx.strokeStyle = '#16213e';
  for (let i = 0; i <= gameConfig.width; i += gameConfig.tileSize) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i, gameConfig.height);
    ctx.stroke();
  }
  for (let i = 0; i <= gameConfig.height; i += gameConfig.tileSize) {
    ctx.beginPath();
    ctx.moveTo(0, i);
    ctx.lineTo(gameConfig.width, i);
    ctx.stroke();
  }
  
  // 绘制蛇
  snake.forEach((segment, index) => {
    if (ctx) {
      ctx.fillStyle = index === 0 ? '#4ecdc4' : '#45b7aa';
      ctx.fillRect(
        segment.x * gameConfig.tileSize,
        segment.y * gameConfig.tileSize,
        gameConfig.tileSize - 1,
        gameConfig.tileSize - 1
      );
    }
  });
  
  // 绘制食物
  if (ctx) {
    ctx.fillStyle = '#ff6b6b';
    ctx.fillRect(
      food.x * gameConfig.tileSize,
      food.y * gameConfig.tileSize,
      gameConfig.tileSize - 1,
      gameConfig.tileSize - 1
    );
  }
};

// 更新游戏逻辑
const updateGame = () => {
  if (gameState.value !== 'playing') return;
  
  // 更新方向
  direction = nextDirection;
  
  // 计算新的头部位置
  const head = { ...snake[0] };
  
  switch (direction) {
    case 'up':
      head.y--;
      break;
    case 'down':
      head.y++;
      break;
    case 'left':
      head.x--;
      break;
    case 'right':
      head.x++;
      break;
  }
  
  // 检查碰撞
  if (
    head.x < 0 || 
    head.x >= gameConfig.width / gameConfig.tileSize || 
    head.y < 0 || 
    head.y >= gameConfig.height / gameConfig.tileSize ||
    snake.some(segment => segment.x === head.x && segment.y === head.y)
  ) {
    gameOver();
    return;
  }
  
  snake.unshift(head);
  
  // 检查是否吃到食物
  if (head.x === food.x && head.y === food.y) {
    score.value += 10;
    food = generateFood();
  } else {
    snake.pop();
  }
  
  drawGame();
};

// 游戏结束
const gameOver = () => {
  gameState.value = 'gameOver';
  if (gameLoop) {
    clearInterval(gameLoop);
    gameLoop = null;
  }
  
  // 更新最高分
  if (score.value > highScore.value) {
    highScore.value = score.value;
    localStorage.setItem('snakeHighScore', highScore.value.toString());
  }
};

// 开始/暂停游戏
const toggleGame = () => {
  if (gameState.value === 'idle' || gameState.value === 'gameOver') {
    if (gameState.value === 'gameOver') {
      initGame();
    }
    gameState.value = 'playing';
    gameLoop = setInterval(updateGame, 150);
  } else if (gameState.value === 'playing') {
    gameState.value = 'paused';
    if (gameLoop) {
      clearInterval(gameLoop);
      gameLoop = null;
    }
  } else if (gameState.value === 'paused') {
    gameState.value = 'playing';
    gameLoop = setInterval(updateGame, 150);
  }
};

// 重置游戏
const resetGame = () => {
  if (gameLoop) {
    clearInterval(gameLoop);
    gameLoop = null;
  }
  initGame();
};

// 改变方向
const changeDirection = (newDirection: Direction) => {
  if (gameState.value !== 'playing') return;
  
  // 防止反向移动
  const oppositeDirections: Record<Direction, Direction> = {
    up: 'down',
    down: 'up',
    left: 'right',
    right: 'left'
  };
  
  if (newDirection !== oppositeDirections[direction]) {
    nextDirection = newDirection;
  }
};

// 键盘控制
const handleKeyDown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowUp':
      event.preventDefault();
      changeDirection('up');
      break;
    case 'ArrowDown':
      event.preventDefault();
      changeDirection('down');
      break;
    case 'ArrowLeft':
      event.preventDefault();
      changeDirection('left');
      break;
    case 'ArrowRight':
      event.preventDefault();
      changeDirection('right');
      break;
    case ' ':
      event.preventDefault();
      toggleGame();
      break;
  }
};

// 触摸控制
const handleTouchStart = (event: TouchEvent) => {
  const touch = event.touches[0];
  touchStartX = touch.clientX;
  touchStartY = touch.clientY;
};

const handleTouchMove = (event: TouchEvent) => {
  if (!touchStartX || !touchStartY) return;
  
  event.preventDefault();
  
  const touch = event.touches[0];
  const diffX = touchStartX - touch.clientX;
  const diffY = touchStartY - touch.clientY;
  
  if (Math.abs(diffX) > Math.abs(diffY)) {
    // 水平滑动
    if (diffX > 0) {
      changeDirection('left');
    } else {
      changeDirection('right');
    }
  } else {
    // 垂直滑动
    if (diffY > 0) {
      changeDirection('up');
    } else {
      changeDirection('down');
    }
  }
  
  touchStartX = 0;
  touchStartY = 0;
};

onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
  window.addEventListener('keydown', handleKeyDown);
  initGame();
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
  window.removeEventListener('keydown', handleKeyDown);
  if (gameLoop) {
    clearInterval(gameLoop);
  }
});
</script>

<style scoped>
.not-found-container {
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  color: #fff;
  z-index: 5;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 800px;
  width: 100%;
  text-align: center;
}

h1 {
  font-size: 6em;
  margin-bottom: 0.2em;
  color: #e74c3c;
  text-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
}

h2 {
  font-size: 2em;
  margin-bottom: 1em;
  color: #ecf0f1;
}

p {
  font-size: 1.2em;
  margin-bottom: 2em;
  color: #bdc3c7;
}

/* 游戏容器 */
.game-container {
  background: rgba(52, 73, 94, 0.9);
  border-radius: 15px;
  padding: 20px;
  margin: 30px 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.game-header h3 {
  color: #4ecdc4;
  margin: 0;
  font-size: 1.5em;
}

.game-info {
  display: flex;
  gap: 20px;
  font-weight: bold;
  color: #ecf0f1;
}

/* 游戏画布 */
canvas {
  border: 2px solid #4ecdc4;
  border-radius: 10px;
  display: block;
  margin: 0 auto 20px;
  background: #1a1a2e;
  cursor: pointer;
}

canvas:focus {
  outline: 2px solid #f39c12;
  outline-offset: 2px;
}

/* 游戏控制 */
.game-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.mobile-controls {
  display: grid;
  grid-template-rows: auto auto auto;
  gap: 10px;
  justify-items: center;
}

.horizontal-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.desktop-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.control-btn {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 10px;
  background: #3498db;
  color: white;
  font-size: 1.5em;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: #2980b9;
  transform: scale(1.05);
}

.control-btn:active {
  transform: scale(0.95);
}

.play-btn, .reset-btn, .restart-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1em;
}

.play-btn {
  background: #27ae60;
  color: white;
}

.play-btn:hover {
  background: #2ecc71;
}

.reset-btn, .restart-btn {
  background: #e74c3c;
  color: white;
}

.reset-btn:hover, .restart-btn:hover {
  background: #c0392b;
}

.controls-hint {
  color: #95a5a6;
  font-size: 0.9em;
  margin: 5px 0;
}

/* 游戏结束界面 */
.game-over {
  background: rgba(231, 76, 60, 0.1);
  border: 2px solid #e74c3c;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.game-over h4 {
  color: #e74c3c;
  margin: 0 0 10px 0;
  font-size: 1.3em;
}

.game-over p {
  margin: 5px 0;
  color: #ecf0f1;
}

/* 导航提示 */
.navigation-hints {
  margin-top: 40px;
  padding: 20px;
  background: rgba(44, 62, 80, 0.8);
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.navigation-hints h4 {
  color: #f39c12;
  margin-bottom: 20px;
  font-size: 1.3em;
}

.nav-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
}

.nav-btn {
  display: inline-block;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  text-decoration: none;
  border-radius: 25px;
  transition: all 0.3s ease;
  font-weight: bold;
  text-align: center;
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  filter: brightness(1.1);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .not-found-container {
    padding: 10px;
    min-height: calc(100vh - 80px);
  }
  
  h1 {
    font-size: 4em;
  }
  
  h2 {
    font-size: 1.5em;
  }
  
  p {
    font-size: 1em;
  }
  
  canvas {
    width: 100%;
    max-width: 350px;
    height: auto;
  }
  
  .game-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .game-info {
    justify-content: center;
  }
  
  .nav-buttons {
    grid-template-columns: 1fr;
  }
  
  .control-btn {
    width: 45px;
    height: 45px;
    font-size: 1.3em;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 3em;
  }
  
  .game-container {
    padding: 15px;
    margin: 20px 0;
  }
  
  canvas {
    max-width: 300px;
  }
  
  .control-btn {
    width: 40px;
    height: 40px;
    font-size: 1.2em;
  }
  
  .play-btn, .reset-btn, .restart-btn {
    padding: 8px 16px;
    font-size: 0.9em;
  }
}
</style>