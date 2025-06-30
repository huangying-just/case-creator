import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // 绑定到所有网络接口，允许外网访问
    port: 8866,
    allowedHosts: [
      'case.cflp.ai',    // 允许域名访问
      'localhost',       // 本地访问
      '127.0.0.1'        // 本地IP访问
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8865',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
}) 