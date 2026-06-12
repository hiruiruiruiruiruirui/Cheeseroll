import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: process.env.CI ? '/Cheeseroll/' : '/',
  server: {
    port: 5173,
    allowedHosts: ['.trycloudflare.com', 'localhost'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('error', (err) => console.error('Proxy error:', err))
        },
      },
    },
  },
})
