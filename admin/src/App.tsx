import { useQuery } from '@tanstack/react-query'
import { Navigate, Route, Routes } from 'react-router-dom'
import { api, fijarCsrf, RUTA_SESION } from './api'
import { Layout } from './componentes/Layout'
import { Cargando, ErrorCarga } from './componentes/ui'
import { About } from './paginas/About'
import { Analiticas } from './paginas/Analiticas'
import { Blog, EditarArticulo } from './paginas/Blog'
import { Carrusel } from './paginas/Carrusel'
import { Contacto } from './paginas/Contacto'
import { Galeria } from './paginas/Galeria'
import { Hero } from './paginas/Hero'
import { Login } from './paginas/Login'
import { Mensajes } from './paginas/Mensajes'
import { Modulos } from './paginas/Modulos'
import { Password } from './paginas/Password'
import { Redes } from './paginas/Redes'
import { Seo } from './paginas/Seo'
import { Servicios } from './paginas/Servicios'
import { Testimonios } from './paginas/Testimonios'
import type { Sesion } from './tipos'

export default function App() {
  const sesion = useQuery({
    queryKey: [RUTA_SESION],
    queryFn: async () => {
      const s = await api<Sesion>(RUTA_SESION)
      fijarCsrf(s.csrf_token)
      return s
    },
  })

  if (sesion.isPending) return <div className="p-6"><Cargando /></div>
  if (sesion.isError) return <div className="p-6"><ErrorCarga error={sesion.error} /></div>
  if (!sesion.data.usuario) return <Login />

  return (
    <Routes>
      <Route element={<Layout sesion={sesion.data} />}>
        <Route index element={<Modulos />} />
        <Route path="hero" element={<Hero />} />
        <Route path="about" element={<About />} />
        <Route path="carrusel" element={<Carrusel />} />
        <Route path="servicios" element={<Servicios />} />
        <Route path="galeria" element={<Galeria />} />
        <Route path="testimonios" element={<Testimonios />} />
        <Route path="contacto" element={<Contacto />} />
        <Route path="blog" element={<Blog />} />
        <Route path="blog/:id" element={<EditarArticulo />} />
        <Route path="mensajes" element={<Mensajes />} />
        <Route path="redes" element={<Redes />} />
        <Route path="seo" element={<Seo key="seo" ruta="/api/admin/seo" titulo="SEO del sitio" />} />
        <Route path="seo-blog" element={<Seo key="seo-blog" ruta="/api/admin/seo/blog" titulo="SEO del blog" />} />
        <Route path="analiticas" element={<Analiticas />} />
        <Route path="password" element={<Password />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
