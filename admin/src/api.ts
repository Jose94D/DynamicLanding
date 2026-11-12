import { QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAviso } from './componentes/Avisos'

export const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
})

export const RUTA_SESION = '/api/auth/sesion'

// Token CSRF de la sesión actual: lo entrega GET /api/auth/sesion y el login.
let csrfToken = ''
export const fijarCsrf = (token: string) => { csrfToken = token }

type Opciones = { method?: string; json?: unknown; form?: FormData }

/** fetch a la API con cookie de sesión, header CSRF y errores convertidos en mensajes legibles. */
export async function api<T = unknown>(ruta: string, { method = 'GET', json, form }: Opciones = {}): Promise<T> {
  const headers: Record<string, string> = {}
  if (method !== 'GET') headers['X-CSRFToken'] = csrfToken
  if (json !== undefined) headers['Content-Type'] = 'application/json'

  const r = await fetch(ruta, { method, headers, credentials: 'same-origin', body: form ?? (json !== undefined ? JSON.stringify(json) : undefined) })

  // Sesión vencida: recargar la sesión hace que la app vuelva a mostrar el login.
  if (r.status === 401 && !ruta.endsWith('/login')) queryClient.invalidateQueries({ queryKey: [RUTA_SESION] })
  if (!r.ok) throw new Error(await mensajeDeError(r))
  return (r.status === 204 ? undefined : await r.json()) as T
}

async function mensajeDeError(r: Response) {
  try {
    const { detail } = await r.json()
    if (typeof detail === 'string') return detail
    // Errores de validación de FastAPI/Pydantic: lista de {loc, msg}
    if (Array.isArray(detail)) return detail.map((e) => `${e.loc?.at(-1) ?? ''}: ${e.msg}`).join(' · ')
  } catch { /* respuesta sin JSON */ }
  return `Error ${r.status}`
}

/** GET cacheado por ruta. */
export const useDatos = <T,>(ruta: string) => useQuery({ queryKey: [ruta], queryFn: () => api<T>(ruta) })

/** Acción que modifica datos: al terminar refresca las rutas indicadas y avisa éxito o error. */
export function useAccion<V = void, R = unknown>(fn: (v: V) => Promise<R>, refrescar: string[], exito?: string) {
  const qc = useQueryClient()
  const aviso = useAviso()
  return useMutation({
    mutationFn: fn,
    onSuccess: () => {
      refrescar.forEach((ruta) => qc.invalidateQueries({ queryKey: [ruta] }))
      if (exito) aviso(exito)
    },
    onError: (e) => aviso(e.message, 'error'),
  })
}

/**
 * Reordenar tras un drag & drop: actualiza la pantalla al instante y guarda en segundo plano.
 * `campo` es para listas anidadas dentro de otra respuesta (ej. los bloques de 'about').
 */
export function useReordenar<T extends { id: string | number }>(ruta: string, rutaOrden: string, campo?: string) {
  const qc = useQueryClient()
  const aviso = useAviso()
  return (items: T[]) => {
    qc.setQueryData([ruta], (prev: unknown) => (campo ? { ...(prev as object), [campo]: items } : items))
    api(rutaOrden, { method: 'PUT', json: { orden: items.map((i) => i.id) } }).catch((e: Error) => {
      aviso(e.message, 'error')
      qc.invalidateQueries({ queryKey: [ruta] })
    })
  }
}

export const imagen = (carpeta: string, nombre: string) => `/static/uploads/${carpeta}/${nombre}`

/** Lee un <form> como objeto de strings (los checkbox se leen aparte). */
export const leerForm = (form: HTMLFormElement) => Object.fromEntries(new FormData(form)) as Record<string, string>
