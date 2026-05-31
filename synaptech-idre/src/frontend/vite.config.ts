import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND_TARGET = process.env.BACKEND_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: BACKEND_TARGET,
        changeOrigin: true,
      },
      '/stream': {
        target: BACKEND_TARGET,
        changeOrigin: true,
        ws: false,
      },
      '/health': {
        target: BACKEND_TARGET,
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
