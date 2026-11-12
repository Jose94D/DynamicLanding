import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// El panel se sirve en /admin/ desde FastAPI. En desarrollo, Vite reenvía la API y las
// imágenes al backend (puerto 8000) para que todo quede en el mismo origen y la cookie funcione.
export default defineConfig({
  base: '/admin/',
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
      '/articulo': 'http://localhost:8000',
    },
  },
})
