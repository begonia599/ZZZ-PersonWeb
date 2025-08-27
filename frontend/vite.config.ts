import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

// 读取站点配置
let siteConfig: any = {}
try {
  if (fs.existsSync(path.resolve(__dirname, '../site-config.json'))) {
    siteConfig = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../site-config.json'), 'utf-8'))
  }
} catch (error) {
  console.log('未找到site-config.json，使用默认配置')
}

// 自定义插件：生产环境移除console
const removeConsolePlugin = () => {
  return {
    name: 'remove-console',
    transform(code: string, id: string) {
      if (process.env.NODE_ENV === 'production') {
        return code.replace(/console\.(log|warn|error|info|debug)\(.*?\);?/g, '');
      }
      return code;
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    removeConsolePlugin() // 生产环境移除console
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  // 生产环境构建优化
  build: {
    outDir: 'dist',
    sourcemap: false, // 生产环境关闭sourcemap
    rollupOptions: {
      output: {
        // 静态资源分类
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) {
            return 'css/[name]-[hash][extname]'
          }
          if (/\.(png|jpg|jpeg|gif|svg|webp|ico)$/.test(assetInfo.name || '')) {
            return 'images/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    },
    // 压缩优化
    minify: true, // 启用默认压缩
    // 生产环境移除console通过插件实现
  },
  // 开发服务器配置
  server: {
    host: '0.0.0.0', // 允许外部访问
    port: 5173,
    // 允许的主机名（解决Blocked request问题）
    allowedHosts: siteConfig.server?.allowedHosts || [
      'localhost',
      '127.0.0.1'
    ],
    proxy: {
      '/api': {
        // 环境检测：Docker环境 vs 本地开发 vs 生产环境
        target: process.env.DOCKER_ENV === 'true' 
          ? 'http://backend:5000'  // Docker内部网络
          : process.env.NODE_ENV === 'production'
          ? 'https://your-domain.com' // 生产环境API地址 - 请替换为你的域名
          : 'http://localhost:5000', // 本地开发
        changeOrigin: true,
        secure: process.env.NODE_ENV === 'production', // 生产环境启用HTTPS
      }
    }
  },
  // 预览服务器配置（用于生产构建测试）
  preview: {
    host: '0.0.0.0',
    port: 4173,
    proxy: {
      '/api': {
        target: process.env.API_BASE_URL || 'https://your-domain.com', // 生产API地址
        changeOrigin: true,
        secure: true,
      }
    }
  }
})