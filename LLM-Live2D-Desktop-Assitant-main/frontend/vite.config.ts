import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      // Proxy API routes to backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Proxy WebSocket routes to backend
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../dist-frontend',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          live2d: [] // Will be populated when Live2D libraries are added
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@static': path.resolve(__dirname, '../static')
    }
  },
  publicDir: 'public', // Use standard public directory
  define: {
    // Define environment variables for the frontend
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development')
  }
})