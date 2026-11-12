import { useState } from 'react'
import { api, leerForm, useAccion, useReordenar } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { SelectorIcono } from '../componentes/SelectorIcono'
import { alEnviar, AreaTexto, Campo, ConDatos, Pagina, Pista, Vacio } from '../componentes/ui'
import type { Servicio } from '../tipos'

const RUTA = '/api/admin/servicios'

function CamposServicio({ s }: { s?: Servicio }) {
  return (
    <>
      <SelectorIcono name="icono" inicial={s?.icono} />
      <Campo label="Título" name="titulo" defaultValue={s?.titulo} required />
      <AreaTexto label="Descripción" name="descripcion" defaultValue={s?.descripcion} rows={3} required />
    </>
  )
}

export function Servicios() {
  const [editando, setEditando] = useState<number | null>(null)
  const crear = useAccion((datos: Record<string, string>) => api(RUTA, { method: 'POST', json: datos }), [RUTA], 'Servicio agregado.')
  const editar = useAccion(
    ({ id, datos }: { id: number; datos: Record<string, string> }) => api(`${RUTA}/${id}`, { method: 'PUT', json: datos }),
    [RUTA],
    'Servicio actualizado.',
  )
  const eliminar = useAccion((id: number) => api(`${RUTA}/${id}`, { method: 'DELETE' }), [RUTA], 'Servicio eliminado.')
  const reordenar = useReordenar<Servicio>(RUTA, `${RUTA}/orden`)

  return (
    <Pagina titulo="Servicios" icono="bi-stars" descripcion="Lo que ofreces, con un ícono por servicio.">
      <form className="tarjeta space-y-4" onSubmit={alEnviar((f) => crear.mutate(leerForm(f), { onSuccess: () => f.reset() }))}>
        <h2 className="font-medium text-zinc-900">Nuevo servicio</h2>
        <CamposServicio />
        <button className="boton" disabled={crear.isPending}><i className="bi bi-plus-lg" aria-hidden /> Agregar servicio</button>
      </form>

      <ConDatos<Servicio[]> ruta={RUTA}>
        {(servicios) => servicios.length ? (
          <>
            <ListaOrdenable items={servicios} onOrdenar={reordenar}>
              {(s, asa) => editando === s.id ? (
                <form
                  className="tarjeta space-y-4"
                  onSubmit={alEnviar((f) => editar.mutate({ id: s.id, datos: leerForm(f) }, { onSuccess: () => setEditando(null) }))}
                >
                  <CamposServicio s={s} />
                  <div className="flex gap-2">
                    <button className="boton" disabled={editar.isPending}>Guardar</button>
                    <button type="button" className="boton-sec" onClick={() => setEditando(null)}>Cancelar</button>
                  </div>
                </form>
              ) : (
                <div className="flex items-center gap-3 rounded-lg border border-zinc-200 bg-white px-3 py-2">
                  {asa}
                  <i className={`bi ${s.icono} text-xl text-zinc-700`} aria-hidden />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-zinc-900">{s.titulo}</p>
                    <p className="truncate text-xs text-zinc-500">{s.descripcion}</p>
                  </div>
                  <button className="boton-sec" onClick={() => setEditando(s.id)}><i className="bi bi-pencil" aria-hidden /> Editar</button>
                  <button className="boton-peligro" onClick={() => confirm(`¿Eliminar "${s.titulo}"?`) && eliminar.mutate(s.id)}>
                    <i className="bi bi-trash" aria-hidden /><span className="sr-only">Eliminar</span>
                  </button>
                </div>
              )}
            </ListaOrdenable>
            <Pista>Arrastra para cambiar el orden; se guarda automáticamente.</Pista>
          </>
        ) : <Vacio>Aún no hay servicios.</Vacio>}
      </ConDatos>
    </Pagina>
  )
}
