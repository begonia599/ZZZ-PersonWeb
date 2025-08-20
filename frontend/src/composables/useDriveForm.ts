import { ref, computed } from 'vue';

interface DriveForm {
  set_name: string;
  position: number | string;
  main_stat_name: string;
  substats: string[];
}

export function useDriveForm() {
  const form = ref<DriveForm>({
    set_name: '',
    position: 1,
    main_stat_name: '生命值',
    substats: []
  });

  // 位置主词条映射规则
  const POSITION_MAIN_STATS: Record<number, string[]> = {
    1: ['生命值'],
    2: ['攻击力'],
    3: ['防御力'],
    4: ['异常精通', '生命值百分比', '攻击力百分比', '防御力百分比', '暴击伤害', '暴击'],
    5: ['以太伤害加成', '冰属性伤害加成', '火属性伤害加成', '物理伤害加成', '电属性伤害加成', '攻击力百分比', '生命值百分比', '防御力百分比', '穿透率'],
    6: ['冲击力', '异常掌控', '能量回复', '攻击力百分比', '生命值百分比', '防御力百分比']
  };

  // 所有副词条选项
  const ALL_SUBSTATS = [
    '生命值', '生命值百分比', '攻击力', '攻击力百分比', '防御力', '防御力百分比',
    '暴击', '暴击伤害', '穿透值', '异常精通'
  ];

  // 计算可用的主词条
  const availableMainStats = computed(() => {
    const position = Number(form.value.position);
    return POSITION_MAIN_STATS[position] || [];
  });

  // 表单是否有效
  const isFormValid = computed(() => {
    const substatCount = form.value.substats.filter(s => s).length;
    return form.value.set_name && 
           form.value.position && 
           form.value.main_stat_name && 
           substatCount >= 3 && 
           substatCount <= 4;
  });

  // 位置变化处理
  const onPositionChange = () => {
    const position = Number(form.value.position);
    const mainStats = POSITION_MAIN_STATS[position];
    
    if (mainStats && mainStats.length === 1) {
      form.value.main_stat_name = mainStats[0];
    } else {
      form.value.main_stat_name = '';
    }
    
    form.value.substats = [];
  };

  // 主词条变化处理
  const onMainStatChange = () => {
    form.value.substats = [];
  };

  // 获取位置提示信息
  const getPositionHint = () => {
    const position = Number(form.value.position);
    if (position >= 1 && position <= 3) {
      return `${position}号位主词条固定为: ${availableMainStats.value[0]}`;
    } else if (position >= 4 && position <= 6) {
      return `${position}号位可选择多种主词条`;
    }
    return '';
  };

  // 重置表单
  const resetForm = () => {
    form.value = {
      set_name: '',
      position: 1,
      main_stat_name: '生命值',
      substats: []
    };
  };

  return {
    form,
    POSITION_MAIN_STATS,
    ALL_SUBSTATS,
    availableMainStats,
    isFormValid,
    onPositionChange,
    onMainStatChange,
    getPositionHint,
    resetForm
  };
}