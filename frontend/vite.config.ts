import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // 允许的主机名（解决Blocked request问题）
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'bgnhub.me'
    ],
    proxy: {
      '/api': {
        // 检查是否在Docker环境中（通过检查backend主机是否可解析）
        target: process.env.DOCKER_ENV === 'true' ? 'http://backend:5000' : 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})