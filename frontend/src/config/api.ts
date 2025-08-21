// API 配置文件
// 统一管理所有 API 调用，适应不同环境

/**
 * 获取 API 基础 URL
 * 根据当前环境自动判断使用哪个后端地址
 */
function getApiBaseUrl(): string {
  // 在开发环境中，使用相对路径通过 Vite 代理
  if (import.meta.env.DEV) {
    return '/api';
  }
  
  // 在生产环境中，检查是否有环境变量指定后端地址
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  if (backendUrl) {
    return `${backendUrl}/api`;
  }
  
  // 默认情况下，假设后端和前端在同一域名下
  const { protocol, hostname, port } = window.location;
  
  // 如果前端端口是 5173（开发环境），后端端口是 5000
  if (port === '5173') {
    return `${protocol}//${hostname}:5000/api`;
  }
  
  // 生产环境下，假设后端在同一域名的 /api 路径下
  return '/api';
}

export const API_BASE_URL = getApiBaseUrl();

/**
 * 统一的 fetch 封装
 * 自动添加错误处理和日志
 */
export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    console.log(`API 调用: ${options.method || 'GET'} ${url}`);
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(`API 响应成功: ${url}`, data);
    return data;
  } catch (error) {
    console.error(`API 调用失败: ${url}`, error);
    throw error;
  }
}

// 导出具体的 API 端点
export const API_ENDPOINTS = {
  // 博客相关
  POSTS: '/posts',
  POST_BY_ID: (id: number) => `/posts/${id}`,
  
  // 指标相关
  METRICS: {
    VISITOR_COUNT: '/metrics/visitor_count',
    INCREMENT_VISITOR: '/metrics/increment_visitor_count',
    UPTIME: '/metrics/uptime',
  },
  
  // 驱动盘相关
  DRIVE: {
    PIECES: '/drive/pieces',
    PIECE_BY_ID: (id: number) => `/drive/pieces/${id}`,
    UPGRADE: (id: number) => `/drive/pieces/${id}/upgrade`,
    ADD: '/drive/add',
    SET_TYPES: '/drive/set-types',
    STAT_TYPES: '/drive/stat-types',
    STATS: '/drive/stats',
    PAIRING: '/drive/stats/pairing',
  },
} as const;
