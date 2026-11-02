import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/questions': 'http://localhost:5001',
      '/submit': 'http://localhost:5001',
      '/submission': 'http://localhost:5001'
    }
  }
})
