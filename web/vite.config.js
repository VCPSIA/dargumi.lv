import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const htmlBypass = (req) => {
  if (req.method === 'GET' && req.headers.accept?.includes('text/html')) return '/index.html';
};

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth':       'http://localhost:8001',
      '/catalog':    { target: 'http://localhost:8001', bypass: htmlBypass },
      '/collection': { target: 'http://localhost:8001', bypass: htmlBypass },
      '/recognize':  { target: 'http://localhost:8001', bypass: htmlBypass },
      '/admin':      { target: 'http://localhost:8001', bypass: htmlBypass },
      '/uploads':    'http://localhost:8001',
    }
  }
})
