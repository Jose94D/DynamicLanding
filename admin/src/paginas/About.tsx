import { api, imagen, useAccion, useReordenar } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { alEnviar, AreaTexto, BotonGuardar, Campo, ConDatos, Interruptor, limpiarArchivos, Pagina, Pista } from '../componentes/ui'
import type { About as AboutT, Modulo } from '../tipos'

const RUTA = '/api/admin/about'

export function About() {
  const guardar = useAccion((form: FormData) => api(RUTA, { method: 'PUT', form }), [RUTA], 'Sección Sobre Nosotros actualizada.')
  const visibilidad = useAccion(
    ({ id, activo }: { id: string; activo: boolean }) => api(`${RUTA}/bloques/${id}`, { method: 'PATCH', json: { activo } }),
    [RUTA],
  )
  const reordenar = useReordenar<Modulo>(RUTA, `${RUTA}/bloques/orden`, 'bloques')

  return (
    <Pagina titulo="Sobre Nosotros" icono="bi-person-vcard" descripcion="Historia, misión e imagen de tu negocio.">
      <ConDatos<AboutT> ruta={RUTA}>
        {(a) => (
          <>
            <form className="tarjeta space-y-4" onSubmit={alEnviar((f) => guardar.mutate(new FormData(f), { onSuccess: () => limpiarArchivos(f) }))}>
              <Campo label="Título" name="titulo" defaultValue={a.titulo} required />
              <AreaTexto label="Descripción / historia" name="descripcion" defaultValue={a.descripcion ?? ''} rows={5} />
              <AreaTexto label="Misión o propuesta de valor" name="mision" defaultValue={a.mision ?? ''} rows={3} />
              <div className="flex flex-wrap items-end gap-4">
                {a.nombre_archivo && (
                  <img src={imagen('about', a.nombre_archivo)} alt="Imagen actual" className="h-24 w-36 rounded-lg object-cover" />
                )}
                <div className="flex-1">
                  <Campo label={a.nombre_archivo ? 'Reemplazar imagen (opcional)' : 'Imagen'} name="imagen" type="file" accept="image/jpeg,image/png,image/webp" />
                </div>
              </div>
              <BotonGuardar pendiente={guardar.isPending} />
            </form>

            <div className="tarjeta space-y-3">
              <h2 className="font-medium text-zinc-900">Bloques de la sección</h2>
              <ListaOrdenable items={a.bloques} onOrdenar={reordenar}>
                {(b, asa) => (
                  <div className="flex items-center gap-3 rounded-lg border border-zinc-200 px-3 py-2">
                    {asa}
                    <span className="flex-1 text-sm">{b.nombre_legible}</span>
                    <Interruptor label={b.activo ? 'Visible' : 'Oculto'} checked={b.activo} onChange={(activo) => visibilidad.mutate({ id: b.id, activo })} />
                  </div>
                )}
              </ListaOrdenable>
              <Pista>El orden y la visibilidad de los bloques se guardan al instante.</Pista>
            </div>
          </>
        )}
      </ConDatos>
    </Pagina>
  )
}
