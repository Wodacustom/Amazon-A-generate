import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiProxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8002'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '0.0.0.0',
      proxy: {
        '/api': apiProxyTarget,
      },
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) return undefined
            if (id.includes('element-plus')) return 'vendor-element-plus'
            if (id.includes('lucide-vue-next')) return 'vendor-icons'
            if (id.includes('axios')) return 'vendor-axios'
            if (id.includes('vue') || id.includes('pinia')) return 'vendor-vue'
            return 'vendor'
          },
        },
      },
    },
  }
})
