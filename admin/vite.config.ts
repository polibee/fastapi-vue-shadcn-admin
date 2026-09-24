import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  appType: 'spa',
  base: '/',
  plugins: [vue(), tailwindcss()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: {
    port: 4181,
    strictPort: false,
    proxy: Object.fromEntries(['/api', '/docs', '/openapi.json'].map((path) => [path, process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8012'])),
  },
});
