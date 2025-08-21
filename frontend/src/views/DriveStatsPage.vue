<template>
  <div class="drive-stats-page">
    <div class="header-section">
      <h1>📊 驱动盘统计分析</h1>
      <router-link to="/toolbox/drive" class="back-btn">
        ← 返回列表
      </router-link>
    </div>

    <!-- 数据总览 -->
    <div class="overview-section">
      <div class="stats-grid">
        <StatsCard
          title="驱动盘总数"
          icon="💎"
          type="number"
          :value="statsData.total_pieces"
          unit="个"
          description="您已收集的驱动盘总数量"
        />
        
        <StatsCard
          title="套装种类"
          icon="🎯"
          type="number"
          :value="statsData.total_sets"
          unit="种"
          description="已收集的不同套装类型"
        />
        
        <StatsCard
          title="平均副词条"
          icon="⚡"
          type="number"
          :value="statsData.avg_substats"
          unit="个"
          description="每个驱动盘的平均副词条数量"
        />
        
        <StatsCard
          title="位置分布"
          icon="📍"
          type="list"
          :list-data="positionDistribution"
          description="各个位置的驱动盘分布情况"
        />
      </div>
    </div>

    <!-- 主词条分析 - 重新设计 -->
    <div class="main-stats-section">
      <h2 class="section-title">
        <span class="section-icon">🎖️</span>
        主词条分布分析
      </h2>
      <p class="section-description">显示各位置主词条的选择分布情况和概率排行</p>
      
      <div v-for="pos in [4, 5, 6]" :key="pos" class="position-analysis">
        <ChartContainer
          :title="`${pos}号位主词条分布`"
          icon="📍"
          :loading="loading"
          height="auto"
        >
          <div class="position-content">
            <!-- 左侧饼图 -->
            <div class="chart-section">
              <PieChart 
                :data="getMainStatsByPosition(pos)" 
                :size="280" 
              />
            </div>
            
            <!-- 右侧详细列表 -->
            <div class="stats-section">
              <h4 class="stats-title">主词条概率排行</h4>
              <div class="stats-list">
                <div 
                  v-for="(item, index) in getMainStatsRanking(pos)" 
                  :key="item.stat_name"
                  class="stat-item"
                  :class="`rank-${index + 1}`"
                >
                  <div class="stat-rank">{{ index + 1 }}</div>
                  <div class="stat-info">
                    <div class="stat-name">{{ item.stat_name }}</div>
                    <div class="stat-details">
                      <span class="stat-count">{{ item.count }} 个</span>
                      <span class="stat-probability">{{ item.probability }}%</span>
                    </div>
                  </div>
                  <div class="stat-bar">
                    <div 
                      class="stat-fill" 
                      :style="{ width: item.probability + '%', backgroundColor: getStatColor(item.stat_name) }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </ChartContainer>
      </div>
    </div>

    <!-- 副词条分析 - 重新设计 -->
    <div class="substats-analysis-section">
      <h2 class="section-title">
        <span class="section-icon">🔥</span>
        副词条出现分析
      </h2>
      <p class="section-description">各副词条在所有驱动盘中的出现概率和统计信息</p>
      
      <ChartContainer
        title="副词条概率分析"
        icon="📊"
        :loading="loading"
        height="auto"
      >
        <div class="substats-content">
          <!-- 左侧条形图 -->
          <div class="chart-section">
            <BarChart
              :data="substatChartData"
              :width="500"
              :height="400"
              :horizontal="true"
              :use-percentage="true"
              :show-values="true"
            />
          </div>
          
          <!-- 右侧详细列表 -->
          <div class="stats-section">
            <h4 class="stats-title">副词条详细统计</h4>
            <div class="substats-list">
              <div 
                v-for="(item, index) in substatDetailList" 
                :key="item.stat_name"
                class="substat-item"
                :class="`rank-${index + 1}`"
              >
                <div class="substat-rank">{{ index + 1 }}</div>
                <div class="substat-info">
                  <div class="substat-name">{{ item.stat_name }}</div>
                  <div class="substat-details">
                    <span class="substat-count">{{ item.count }} 次</span>
                    <span class="substat-probability">{{ item.probability }}%</span>
                    <span class="substat-frequency">每{{ item.frequency }}个出现一次</span>
                  </div>
                </div>
                <div class="substat-bar">
                  <div 
                    class="substat-fill" 
                    :style="{ 
                      width: item.probability + '%', 
                      backgroundColor: getStatColor(item.stat_name) 
                    }"
                  ></div>
                </div>
              </div>
            </div>
            
            <!-- 统计摘要 -->
            <div class="stats-summary">
              <div class="summary-item">
                <span class="summary-label">最常出现:</span>
                <span class="summary-value">{{ mostCommonSubstat?.stat_name || '-' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最稀有:</span>
                <span class="summary-value">{{ rarestSubstat?.stat_name || '-' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">平均概率:</span>
                <span class="summary-value">{{ averageProbability }}%</span>
              </div>
            </div>
          </div>
        </div>
      </ChartContainer>
    </div>

    <!-- 套装统计 - 重新设计为饼图布局 -->
    <div class="sets-analysis-section">
      <h2 class="section-title">
        <span class="section-icon">📦</span>
        套装收集分析
      </h2>
      <p class="section-description">各套装的收集数量分布和占比情况</p>
      
      <ChartContainer
        title="套装收集分布"
        icon="📊"
        :loading="loading"
        height="auto"
      >
        <div class="sets-content">
          <!-- 左侧饼图 -->
          <div class="chart-section">
            <PieChart 
              :data="setChartData" 
              :size="350"
              :colors="setColors"
            />
          </div>
          
          <!-- 右侧详细列表 -->
          <div class="stats-section">
            <h4 class="stats-title">套装收集排行</h4>
            <div class="sets-list">
              <div 
                v-for="(item, index) in setDetailList" 
                :key="item.set_name"
                class="set-item"
                :class="`rank-${index + 1}`"
              >
                <div class="set-rank">{{ index + 1 }}</div>
                <div class="set-info">
                  <div class="set-name">{{ item.set_name }}</div>
                  <div class="set-details">
                    <span class="set-count">{{ item.count }} 个</span>
                    <span class="set-percentage">{{ item.percentage }}%</span>
                  </div>
                </div>
                <div class="set-bar">
                  <div 
                    class="set-fill" 
                    :style="{ 
                      width: item.percentage + '%', 
                      backgroundColor: getSetColor(item.set_name, index) 
                    }"
                  ></div>
                </div>
              </div>
            </div>
            
            <!-- 套装统计摘要 -->
            <div class="stats-summary">
              <div class="summary-item">
                <span class="summary-label">最多套装:</span>
                <span class="summary-value">{{ mostCollectedSet?.set_name || '-' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最少套装:</span>
                <span class="summary-value">{{ leastCollectedSet?.set_name || '-' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">套装种类:</span>
                <span class="summary-value">{{ setDetailList.length }} 种</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">平均每套:</span>
                <span class="summary-value">{{ averagePerSet }} 个</span>
              </div>
            </div>
          </div>
        </div>
      </ChartContainer>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <LoadingAnimation />
      <p class="loading-text">正在计算统计数据...</p>
    </div>

    <!-- 新增：词条配对概率计算区域 -->
    <div class="pairing-analysis-section">
      <h2 class="section-title">
        <span class="section-icon">🎯</span>
        词条配对概率计算
      </h2>
      <p class="section-description">选择词条组合，计算理论概率和实际概率对比</p>
      
      <ChartContainer
        title="词条配对概率分析"
        icon="⚡"
        :loading="loading"
        height="auto"
      >
        <div class="pairing-content">
          <!-- 左侧：词条选择器 -->
          <div class="selector-section">
            <h4 class="selector-title">选择词条组合</h4>
            
            <!-- 词条选择器 -->
            <div class="stat-selector">
              <div class="selector-group">
                <label>选择副词条 (最多选择4个):</label>
                <div class="stat-tags">
                  <div 
                    v-for="stat in availableSubstats" 
                    :key="stat.name"
                    class="stat-tag"
                    :class="{ 
                      'selected': selectedStats.includes(stat.name),
                      'disabled': !selectedStats.includes(stat.name) && selectedStats.length >= 4
                    }"
                    @click="toggleStat(stat.name)"
                  >
                    <span class="stat-tag-name">{{ stat.name }}</span>
                    <span class="stat-tag-prob">{{ stat.probability }}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 计算按钮 -->
            <div class="calculation-controls">
              <button 
                class="calculate-btn"
                :disabled="selectedStats.length === 0 || calculatingPairing"
                @click="calculatePairingProbability"
              >
                <span class="btn-icon">🔬</span>
                {{ calculatingPairing ? '计算中...' : '计算概率' }}
              </button>
              <button 
                class="clear-btn"
                @click="clearSelection"
                :disabled="selectedStats.length === 0"
              >
                <span class="btn-icon">🗑️</span>
                清空选择
              </button>
            </div>
          </div>
          
          <!-- 右侧：结果显示 -->
          <div class="results-section">
            <h4 class="results-title">概率计算结果</h4>
            
            <div v-if="selectedStats.length === 0" class="no-selection">
              <span class="empty-icon">🎲</span>
              <p>请选择至少一个副词条进行概率计算</p>
            </div>
            
            <div v-else-if="pairingResults" class="results-display">
              <!-- 选中的词条 -->
              <div class="selected-combination">
                <h5>选中组合:</h5>
                <div class="combination-tags">
                  <span 
                    v-for="stat in selectedStats" 
                    :key="stat"
                    class="combination-tag"
                    :style="{ backgroundColor: getStatColor(stat) }"
                  >
                    {{ stat }}
                  </span>
                </div>
              </div>
              
              <!-- 概率对比 -->
              <div class="probability-comparison">
                <div class="prob-card theoretical">
                  <div class="prob-header">
                    <span class="prob-icon">📐</span>
                    <span class="prob-title">理论概率</span>
                  </div>
                  <div class="prob-value">{{ pairingResults.theoretical }}%</div>
                  <div class="prob-description">基于各词条独立概率计算</div>
                </div>
                
                <div class="prob-card actual">
                  <div class="prob-header">
                    <span class="prob-icon">📊</span>
                    <span class="prob-title">实际概率</span>
                  </div>
                  <div class="prob-value">{{ pairingResults.actual }}%</div>
                  <div class="prob-description">从现有{{ pairingResults.matchCount }}个匹配/{{ pairingResults.totalPieces }}个总计算</div>
                </div>
              </div>
              
              <!-- 差异分析 -->
              <div class="difference-analysis">
                <div class="diff-item">
                  <span class="diff-label">概率差异:</span>
                  <span class="diff-value" :class="getDifferenceClass(pairingResults.difference)">
                    {{ pairingResults.difference > 0 ? '+' : '' }}{{ pairingResults.difference }}%
                  </span>
                </div>
                <div class="diff-item">
                  <span class="diff-label">期望获得:</span>
                  <span class="diff-value">每{{ pairingResults.expectation }}个驱动盘</span>
                </div>
                <div class="diff-item">
                  <span class="diff-label">置信度:</span>
                  <span class="diff-value">{{ getConfidenceLevel(pairingResults.matchCount) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ChartContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import StatsCard from '../components/StatsCard.vue';
import ChartContainer from '../components/ChartContainer.vue';
import PieChart from '../components/PieChart.vue';
import BarChart from '../components/BarChart.vue';
import LoadingAnimation from '../components/LoadingAnimation.vue';

const router = useRouter();
const loading = ref(true);

// 统计数据
interface StatsData {
  total_pieces: number;
  total_sets: number;
  avg_substats: number;
  position_distribution: Record<string | number, number>;
  main_stats: Record<string, Record<string, number>>;
  substat_frequency: Record<string, { count: number }>;
  set_distribution: Record<string, number>;
  substat_count_distribution: Record<number, number>;
}

const statsData = ref<StatsData>({
  total_pieces: 0,
  total_sets: 0,
  avg_substats: 0,
  position_distribution: {},
  main_stats: {},
  substat_frequency: {},
  set_distribution: {},
  substat_count_distribution: {}
});

// 位置分布数据
const positionDistribution = computed(() => {
  return Object.entries(statsData.value.position_distribution).map(([pos, count]) => ({
    label: `${pos}号位`,
    value: typeof count === 'number' ? count : Number(count)
  }));
});

// 根据位置获取主词条数据（饼图用）
const getMainStatsByPosition = (position: number) => {
  const positionData = statsData.value.main_stats[`${position}号位`] || {};
  return Object.entries(positionData).map(([stat, count]) => ({
    label: stat,
    value: count as number
  }));
};

// 根据位置获取主词条排行（详细列表用）
const getMainStatsRanking = (position: number) => {
  const positionData = statsData.value.main_stats[`${position}号位`] || {};
  const totalForPosition = Object.values(positionData).reduce((sum, count) => sum + (count as number), 0);
  
  return Object.entries(positionData)
    .map(([stat_name, count]) => ({
      stat_name,
      count: count as number,
      probability: totalForPosition > 0 ? parseFloat(((count as number) / totalForPosition * 100).toFixed(1)) : 0
    }))
    .sort((a, b) => b.probability - a.probability);
};

// 获取词条颜色
const getStatColor = (statName: string): string => {
  const colorMap: Record<string, string> = {
    '生命值': '#FF6B6B',
    '生命值百分比': '#FF8E8E',
    '攻击力': '#4ECDC4',
    '攻击力百分比': '#6FD4D1',
    '防御力': '#45B7D1',
    '防御力百分比': '#6BC5E0',
    '暴击': '#96CEB4',
    '暴击伤害': '#A8D8C5',
    '异常精通': '#FECA57',
    '异常掌控': '#FED976',
    '冲击力': '#FF9FF3',
    '能量回复': '#FFB3F6',
    '以太伤害加成': '#54A0FF',
    '冰属性伤害加成': '#7DB4FF',
    '火属性伤害加成': '#5F27CD',
    '物理伤害加成': '#7B4BDB',
    '电属性伤害加成': '#00D2D3',
    '穿透率': '#26E0E1',
    '穿透值': '#10AC84'
  };
  return colorMap[statName] || generateColor(statName);
};

// 副词条图表数据（按概率）
const substatChartData = computed(() => {
  return Object.entries(statsData.value.substat_frequency)
    .map(([stat, data]: [string, any]) => ({
      label: stat,
      value: data.count,
      probability: parseFloat(((data.count / statsData.value.total_pieces * 100) || 0).toFixed(1)),
      color: getStatColor(stat)
    }))
    .sort((a, b) => b.probability - a.probability);
});

// 副词条详细列表
const substatDetailList = computed(() => {
  return Object.entries(statsData.value.substat_frequency)
    .map(([stat_name, data]: [string, any]) => {
      const probability = parseFloat(((data.count / statsData.value.total_pieces * 100) || 0).toFixed(1));
      const frequency = probability > 0 ? Math.round(100 / probability) : 0;
      
      return {
        stat_name,
        count: data.count,
        probability,
        frequency // 每N个驱动盘出现一次
      };
    })
    .sort((a, b) => b.probability - a.probability);
});

// 最常见的副词条
const mostCommonSubstat = computed(() => {
  const list = substatDetailList.value;
  return list.length > 0 ? list[0] : null;
});

// 最稀有的副词条
const rarestSubstat = computed(() => {
  const list = substatDetailList.value;
  return list.length > 0 ? list[list.length - 1] : null;
});

// 平均概率
const averageProbability = computed(() => {
  const list = substatDetailList.value;
  if (list.length === 0) return '0';
  const total = list.reduce((sum, item) => sum + item.probability, 0);
  return (total / list.length).toFixed(1);
});

// 套装图表数据
const setChartData = computed(() => {
  return Object.entries(statsData.value.set_distribution).map(([setName, count]) => ({
    label: setName,
    value: count as number
  }));
});

// 套装详细列表
const setDetailList = computed(() => {
  const totalPieces = statsData.value.total_pieces;
  return Object.entries(statsData.value.set_distribution)
    .map(([set_name, count]) => ({
      set_name,
      count: count as number,
      percentage: totalPieces > 0 ? parseFloat(((count as number) / totalPieces * 100).toFixed(1)) : 0
    }))
    .sort((a, b) => b.count - a.count);
});

// 最多收集的套装
const mostCollectedSet = computed(() => {
  const list = setDetailList.value;
  return list.length > 0 ? list[0] : null;
});

// 最少收集的套装
const leastCollectedSet = computed(() => {
  const list = setDetailList.value;
  return list.length > 0 ? list[list.length - 1] : null;
});

// 平均每套数量
const averagePerSet = computed(() => {
  const list = setDetailList.value;
  if (list.length === 0) return '0';
  const total = list.reduce((sum, item) => sum + item.count, 0);
  return (total / list.length).toFixed(1);
});

// 套装颜色
const setColors = computed(() => {
  return setDetailList.value.map((_, index) => {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
      '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
      '#10AC84', '#EE5A24', '#0984E3', '#6C5CE7', '#FD79A8'
    ];
    return colors[index % colors.length];
  });
});

// 获取套装颜色
const getSetColor = (setName: string, index: number): string => {
  return setColors.value[index] || generateColor(setName);
};

// 生成颜色
const generateColor = (str: string): string => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    '#10AC84', '#EE5A24', '#0984E3', '#6C5CE7', '#FD79A8'
  ];
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

// 获取统计数据
const loadStatsData = async () => {
  try {
    const response = await fetch('/api/drive/stats');
    const result = await response.json();
    
    if (response.ok) {
      statsData.value = result;
    } else {
      console.error('获取统计数据失败:', result);
    }
  } catch (error) {
    console.error('网络错误:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadStatsData();
});

// 新增状态
const selectedStats = ref<string[]>([]);
const calculatingPairing = ref(false);
const pairingResults = ref<any>(null);

// 可选择的副词条列表
const availableSubstats = computed(() => {
  return substatDetailList.value.map(item => ({
    name: item.stat_name,
    probability: item.probability,
    count: item.count
  }));
});

// 切换词条选择
const toggleStat = (statName: string) => {
  if (selectedStats.value.includes(statName)) {
    selectedStats.value = selectedStats.value.filter(s => s !== statName);
  } else if (selectedStats.value.length < 4) {
    selectedStats.value.push(statName);
  }
  
  // 清空之前的计算结果
  if (pairingResults.value) {
    pairingResults.value = null;
  }
};

// 清空选择
const clearSelection = () => {
  selectedStats.value = [];
  pairingResults.value = null;
};

// 计算配对概率
const calculatePairingProbability = async () => {
  if (selectedStats.value.length === 0) return;
  
  calculatingPairing.value = true;
  
  try {
    const response = await fetch('/api/drive/stats/pairing', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        selected_stats: selectedStats.value
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      pairingResults.value = result;
    } else {
      console.error('计算配对概率失败:', result);
    }
  } catch (error) {
    console.error('网络错误:', error);
  } finally {
    calculatingPairing.value = false;
  }
};

// 获取差异样式类
const getDifferenceClass = (difference: number) => {
  if (difference > 5) return 'positive-high';
  if (difference > 0) return 'positive-low';
  if (difference < -5) return 'negative-high';
  if (difference < 0) return 'negative-low';
  return 'neutral';
};

// 获取置信度等级
const getConfidenceLevel = (matchCount: number) => {
  if (matchCount >= 50) return '高';
  if (matchCount >= 20) return '中';
  if (matchCount >= 10) return '低';
  return '极低';
};

</script>

<style scoped>
.drive-stats-page {
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

.overview-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

/* 主词条分析区域样式 */
.main-stats-section {
  margin-bottom: 40px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.section-icon {
  font-size: 28px;
}

.section-description {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 30px 0;
  font-size: 16px;
  line-height: 1.5;
}

.position-analysis {
  margin-bottom: 30px;
}

.position-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  min-height: 300px;
}

.chart-section {
  flex-shrink: 0;
}

.stats-section {
  flex: 1;
  min-width: 0;
}

.stats-title {
  color: #fff;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.stat-item.rank-1 {
  background: rgba(255, 215, 0, 0.1);
  border-left: 4px solid #FFD700;
}

.stat-item.rank-2 {
  background: rgba(192, 192, 192, 0.1);
  border-left: 4px solid #C0C0C0;
}

.stat-item.rank-3 {
  background: rgba(205, 127, 50, 0.1);
  border-left: 4px solid #CD7F32;
}

.stat-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #fff;
  font-size: 14px;
  flex-shrink: 0;
}

.rank-1 .stat-rank {
  background: linear-gradient(45deg, #FFD700, #FFA500);
  color: #333;
}

.rank-2 .stat-rank {
  background: linear-gradient(45deg, #C0C0C0, #A9A9A9);
  color: #333;
}

.rank-3 .stat-rank {
  background: linear-gradient(45deg, #CD7F32, #B8860B);
  color: #fff;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-name {
  font-weight: 600;
  color: #fff;
  font-size: 15px;
  margin-bottom: 4px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.stat-details {
  display: flex;
  gap: 12px;
  font-size: 13px;
}

.stat-count {
  color: rgba(255, 255, 255, 0.8);
}

.stat-probability {
  color: #4ECDC4;
  font-weight: 600;
}

.stat-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  flex-shrink: 0;
}

.stat-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-text {
  margin-top: 20px;
  font-size: 1.2em;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

/* 副词条分析区域样式 */
.substats-analysis-section {
  margin-bottom: 40px;
}

.substats-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  min-height: 400px;
}

.chart-section {
  flex-shrink: 0;
}

.stats-section {
  flex: 1;
  min-width: 0;
}

.substats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 30px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.substats-list::-webkit-scrollbar {
  width: 6px;
}

.substats-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.substats-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.substats-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.substat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.substat-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.substat-item.rank-1 {
  background: rgba(255, 215, 0, 0.1);
  border-left: 3px solid #FFD700;
}

.substat-item.rank-2 {
  background: rgba(192, 192, 192, 0.1);
  border-left: 3px solid #C0C0C0;
}

.substat-item.rank-3 {
  background: rgba(205, 127, 50, 0.1);
  border-left: 3px solid #CD7F32;
}

.substat-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #fff;
  font-size: 12px;
  flex-shrink: 0;
}

.rank-1 .substat-rank {
  background: linear-gradient(45deg, #FFD700, #FFA500);
  color: #333;
}

.rank-2 .substat-rank {
  background: linear-gradient(45deg, #C0C0C0, #A9A9A9);
  color: #333;
}

.rank-3 .substat-rank {
  background: linear-gradient(45deg, #CD7F32, #B8860B);
  color: #fff;
}

.substat-info {
  flex: 1;
  min-width: 0;
}

.substat-name {
  font-weight: 600;
  color: #fff;
  font-size: 14px;
  margin-bottom: 3px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.substat-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 12px;
}

.substat-frequency {
  color: #FF9FF3;
  font-weight: 500;
  font-style: italic;
}

.stats-summary {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.summary-value {
  color: #fff;
  font-weight: 600;
  font-size: 13px;
}

/* 套装统计区域样式 */
.sets-analysis-section {
  margin-bottom: 40px;
}

.sets-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  min-height: 400px;
}

.sets-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 30px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.sets-list::-webkit-scrollbar {
  width: 6px;
}

.sets-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.sets-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.sets-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.set-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.set-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.set-item.rank-1 {
  background: rgba(255, 215, 0, 0.1);
  border-left: 4px solid #FFD700;
}

.set-item.rank-2 {
  background: rgba(192, 192, 192, 0.1);
  border-left: 4px solid #C0C0C0;
}

.set-item.rank-3 {
  background: rgba(205, 127, 50, 0.1);
  border-left: 4px solid #CD7F32;
}

.set-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #fff;
  font-size: 14px;
  flex-shrink: 0;
}

.rank-1 .set-rank {
  background: linear-gradient(45deg, #FFD700, #FFA500);
  color: #333;
}

.rank-2 .set-rank {
  background: linear-gradient(45deg, #C0C0C0, #A9A9A9);
  color: #333;
}

.rank-3 .set-rank {
  background: linear-gradient(45deg, #CD7F32, #B8860B);
  color: #fff;
}

.set-info {
  flex: 1;
  min-width: 0;
}

.set-name {
  font-weight: 600;
  color: #fff;
  font-size: 15px;
  margin-bottom: 4px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.set-details {
  display: flex;
  gap: 12px;
  font-size: 13px;
}

.set-count {
  color: rgba(255, 255, 255, 0.8);
}

.set-percentage {
  color: #4ECDC4;
  font-weight: 600;
}

.set-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  flex-shrink: 0;
}

.set-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

/* 配对分析区域样式 */
.pairing-analysis-section {
  margin-bottom: 40px;
}

.pairing-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  min-height: 500px;
}

.selector-section,
.results-section {
  flex: 1;
  min-width: 0;
}

.selector-title,
.results-title {
  color: #fff;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.stat-selector {
  margin-bottom: 30px;
}

.selector-group label {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-bottom: 15px;
  font-size: 14px;
}

.stat-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 8px;
}

.stat-tag {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.stat-tag:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.stat-tag.selected {
  background: rgba(78, 205, 196, 0.2);
  border-color: #4ECDC4;
  box-shadow: 0 0 15px rgba(78, 205, 196, 0.3);
}

.stat-tag.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stat-tag-name {
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  text-align: center;
  margin-bottom: 4px;
}

.stat-tag-prob {
  color: rgba(255, 255, 255, 0.7);
  font-size: 11px;
}

.calculation-controls {
  display: flex;
  gap: 15px;
}

.calculate-btn,
.clear-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.calculate-btn {
  background: linear-gradient(45deg, #4ECDC4, #45B7D1);
  color: white;
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
}

.calculate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(78, 205, 196, 0.4);
}

.calculate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.clear-btn {
  background: rgba(108, 117, 125, 0.8);
  color: white;
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.clear-btn:hover:not(:disabled) {
  background: rgba(84, 91, 98, 0.9);
  transform: translateY(-2px);
}

.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 16px;
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.results-display {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.selected-combination h5 {
  color: #fff;
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
}

.combination-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.combination-tag {
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 13px;
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.probability-comparison {
  display: flex;
  gap: 20px;
}

.prob-card {
  flex: 1;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.prob-card.theoretical {
  background: rgba(96, 206, 180, 0.1);
  border: 2px solid rgba(96, 206, 180, 0.3);
}

.prob-card.actual {
  background: rgba(84, 160, 255, 0.1);
  border: 2px solid rgba(84, 160, 255, 0.3);
}

.prob-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.prob-icon {
  font-size: 20px;
}

.prob-title {
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}

.prob-value {
  color: #fff;
  font-size: 28px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  margin-bottom: 8px;
}

.prob-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  line-height: 1.4;
}

.difference-analysis {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.diff-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.diff-item:last-child {
  border-bottom: none;
}

.diff-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.diff-value {
  font-weight: 600;
  font-size: 14px;
}

.diff-value.positive-high {
  color: #10AC84;
}

.diff-value.positive-low {
  color: #54A0FF;
}

.diff-value.neutral {
  color: #FECA57;
}

.diff-value.negative-low {
  color: #FF9F43;
}

.diff-value.negative-high {
  color: #EE5A24;
}

/* 响应式设计 */
@media (max-width: 968px) {
  .position-content {
    flex-direction: column;
    align-items: center;
    gap: 30px;
  }
  
  .chart-section {
    align-self: center;
  }
  
  .stats-section {
    width: 100%;
  }
  
  .substats-content {
    flex-direction: column;
    align-items: center;
    gap: 30px;
  }
  
  .sets-content {
    flex-direction: column;
    align-items: center;
    gap: 30px;
  }
  
  .substats-list {
    max-height: 250px;
  }
  
  .sets-list {
    max-height: 250px;
  }
}

@media (max-width: 768px) {
  .drive-stats-page {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .position-content {
    gap: 20px;
  }
  
  .substats-content {
    gap: 20px;
  }
  
  .sets-content {
    gap: 20px;
  }
  
  .stat-item {
    padding: 10px 12px;
  }
  
  .substat-item {
    padding: 8px 12px;
  }
  
  .set-item {
    padding: 10px 12px;
  }
  
  .stat-details {
    flex-direction: column;
    gap: 4px;
  }
  
  .substat-details {
    flex-direction: column;
    gap: 2px;
  }
}
</style>