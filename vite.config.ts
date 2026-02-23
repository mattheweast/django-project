import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    outDir: '../static/dist',  // outputs to Django static/
    emptyOutDir: true,
  },
  server: { port: 5173 },
  css: {
    devSourcemap: true,
  },
})