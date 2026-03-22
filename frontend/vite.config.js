/*
 * File: vite.config.js
 * Công dụng: Cấu hình Vite build tool
 * - Cài đặt React plugin
 * - Cấu hình dev server (port 5173, proxy API calls)
 * - Cấu hình build output (dist folder)
 * - Environment variables
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
