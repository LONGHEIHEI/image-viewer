import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      // Keep the new service worker waiting so the app can surface
      // an explicit refresh action instead of silently swapping assets.
      registerType: 'prompt',
      includeAssets: [
        'icon.png'
      ],
      manifest: {
        name: '轻图',
        short_name: '轻图',
        description: '轻量图片浏览器（支持压缩包）',
        theme_color: '#1b1f2a',
        background_color: '#0f1117',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/icon.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icon.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: '/icon.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable'
          },
          {
            src: '/icon.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8010'
    }
  }
})
