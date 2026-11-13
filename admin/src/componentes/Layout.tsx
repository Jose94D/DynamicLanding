import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { api, RUTA_SESION } from '../api'
import type { Sesion } from '../tipos'

const CONTENIDOS = [
  ['hero', 'Hero / Banner'],
  ['about', 'Sobre Nosotros'],
  ['carrusel', 'Carrusel de Imágenes'],
  ['servicios', 'Servicios'],
  ['galeria', 'Galería'],
  ['testimonios', 'Testimonios'],
  ['contacto', 'Contáctanos'],
]

const enlace = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${isActive ? 'bg-zinc-900 text-white' : 'text-zinc-700 hover:bg-zinc-100'}`

export function Layout({ sesion }: { sesion: Sesion }) {
  const qc = useQueryClient()
  const [menuAbierto, setMenuAbierto] = useState(false)

  async function salir() {
    await api('/api/auth/logout', { method: 'POST' })
    qc.removeQueries({ predicate: (q) => q.queryKey[0] !== RUTA_SESION })  // no dejar datos del admin en memoria
    qc.invalidateQueries({ queryKey: [RUTA_SESION] })
  }

  const cerrar = () => setMenuAbierto(false)

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="bg-zinc-900 text-white">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
          <button className="rounded p-1 md:hidden" onClick={() => setMenuAbierto(!menuAbierto)} aria-label="Abrir menú" aria-expanded={menuAbierto}>
            <i className="bi bi-list text-2xl" aria-hidden />
          </button>
          <img src="/admin/header-logo.png" alt="DynamicLanding CMS" className="h-8" />
          <a href="/" target="_blank" rel="noopener" className="ms-auto hidden text-sm text-zinc-300 hover:text-white sm:inline">
            <i className="bi bi-box-arrow-up-right me-1" aria-hidden />Ver sitio
          </a>
          <span className="hidden text-sm text-zinc-300 sm:inline">Hola, {sesion.usuario}</span>
          <button onClick={salir} className="ms-auto rounded-lg border border-zinc-600 px-3 py-1.5 text-sm hover:bg-zinc-800 sm:ms-0">
            Cerrar sesión
          </button>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        <nav aria-label="Menú del panel" className={`${menuAbierto ? 'block' : 'hidden'} fixed inset-x-0 top-14 z-40 max-h-[calc(100vh-3.5rem)] overflow-y-auto bg-white p-4 shadow-lg md:static md:block md:w-60 md:shrink-0 md:bg-transparent md:p-0 md:shadow-none`}>
          <ul className="space-y-1" onClick={cerrar}>
            <li><NavLink to="/" end className={enlace}><i className="bi bi-grid-1x2-fill" aria-hidden />Diseño y visibilidad</NavLink></li>
            <li className="px-3 pt-3 pb-1 text-xs font-semibold tracking-wide text-zinc-400 uppercase">Contenidos</li>
            {CONTENIDOS.map(([ruta, texto]) => (
              <li key={ruta}><NavLink to={`/${ruta}`} className={enlace}>{texto}</NavLink></li>
            ))}
            <li className="pt-3" />
            <li><NavLink to="/blog" className={enlace}><i className="bi bi-journal-text" aria-hidden />Blog</NavLink></li>
            <li>
              <NavLink to="/mensajes" className={enlace}>
                <i className="bi bi-envelope-fill" aria-hidden />Mensajes
                {sesion.mensajes_no_leidos > 0 && (
                  <span className="ms-auto rounded-full bg-red-600 px-2 text-xs text-white">
                    {sesion.mensajes_no_leidos}<span className="sr-only"> sin leer</span>
                  </span>
                )}
              </NavLink>
            </li>
            <li><NavLink to="/redes" className={enlace}><i className="bi bi-instagram" aria-hidden />Redes sociales</NavLink></li>
            <li><NavLink to="/seo" className={enlace}><i className="bi bi-search" aria-hidden />SEO del sitio</NavLink></li>
            <li><NavLink to="/seo-blog" className={enlace}><i className="bi bi-journal-richtext" aria-hidden />SEO del blog</NavLink></li>
            <li><NavLink to="/privacidad" className={enlace}><i className="bi bi-shield-check" aria-hidden />Privacidad</NavLink></li>
            <li><NavLink to="/analiticas" className={enlace}><i className="bi bi-bar-chart-fill" aria-hidden />Analíticas</NavLink></li>
            <li><NavLink to="/password" className={enlace}><i className="bi bi-key-fill" aria-hidden />Cambiar contraseña</NavLink></li>
          </ul>
        </nav>

        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
