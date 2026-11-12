import { QueryClientProvider } from '@tanstack/react-query'
import 'bootstrap-icons/font/bootstrap-icons.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { queryClient } from './api'
import App from './App'
import { AvisosProvider } from './componentes/Avisos'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AvisosProvider>
        <BrowserRouter basename="/admin">
          <App />
        </BrowserRouter>
      </AvisosProvider>
    </QueryClientProvider>
  </StrictMode>,
)
