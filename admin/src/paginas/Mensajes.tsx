import { api, RUTA_SESION, useAccion } from '../api'
import { ConDatos, Pagina, Vacio } from '../componentes/ui'
import type { Mensaje } from '../tipos'

const RUTA = '/api/admin/mensajes'
const fechaHora = (iso: string) => new Date(iso).toLocaleString('es-CL', { dateStyle: 'medium', timeStyle: 'short' })

export function Mensajes() {
  // RUTA_SESION también: el contador de no leídos del menú viene de ahí.
  const leido = useAccion((id: number) => api(`${RUTA}/${id}/leido`, { method: 'POST' }), [RUTA, RUTA_SESION])
  const eliminar = useAccion((id: number) => api(`${RUTA}/${id}`, { method: 'DELETE' }), [RUTA, RUTA_SESION], 'Mensaje eliminado.')

  return (
    <Pagina titulo="Mensajes" icono="bi-envelope-fill" descripcion="Lo que llega desde el formulario de contacto de la landing.">
      <ConDatos<{ mensajes: Mensaje[]; no_leidos: number }> ruta={RUTA}>
        {({ mensajes, no_leidos }) => mensajes.length ? (
          <>
            <p className="text-sm text-zinc-600">{mensajes.length} mensajes · {no_leidos} sin leer</p>
            <ul className="space-y-3">
              {mensajes.map((m) => (
                <li key={m.id} className={`tarjeta ${m.leido ? '' : 'border-l-4 border-l-zinc-900'}`}>
                  <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                    <p className="font-medium text-zinc-900">{m.nombre}</p>
                    <a href={`mailto:${m.email}`} className="text-sm text-zinc-600 hover:underline">{m.email}</a>
                    <span className="ms-auto text-xs text-zinc-500">{fechaHora(m.fecha_envio)}</span>
                  </div>
                  <p className="mt-2 text-sm whitespace-pre-line text-zinc-700">{m.mensaje}</p>
                  <div className="mt-3 flex gap-2">
                    {!m.leido && (
                      <button className="boton-sec" onClick={() => leido.mutate(m.id)}><i className="bi bi-check2" aria-hidden /> Marcar como leído</button>
                    )}
                    <button className="boton-peligro" onClick={() => confirm(`¿Eliminar el mensaje de ${m.nombre}?`) && eliminar.mutate(m.id)}>
                      <i className="bi bi-trash" aria-hidden /> Eliminar
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </>
        ) : <Vacio>No has recibido mensajes todavía.</Vacio>}
      </ConDatos>
    </Pagina>
  )
}
