import { api, imagen, useAccion, useReordenar } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { alEnviar, Campo, ConDatos, limpiarArchivos, Pagina, Pista, Vacio } from '../componentes/ui'
import type { ImagenGaleria } from '../tipos'

const RUTA = '/api/admin/galeria'

export function Galeria() {
  const subir = useAccion((form: FormData) => api(RUTA, { method: 'POST', form }), [RUTA], 'Imagen agregada a la galería.')
  const editar = useAccion(({ id, form }: { id: number; form: FormData }) => api(`${RUTA}/${id}`, { method: 'PUT', form }), [RUTA], 'Imagen actualizada.')
  const eliminar = useAccion((id: number) => api(`${RUTA}/${id}`, { method: 'DELETE' }), [RUTA], 'Imagen eliminada.')
  const reordenar = useReordenar<ImagenGaleria>(RUTA, `${RUTA}/orden`)

  return (
    <Pagina titulo="Galería" icono="bi-grid-3x3-gap" descripcion="Fotos de productos o trabajos, con título opcional.">
      <form
        className="tarjeta grid items-end gap-4 sm:grid-cols-[1fr_1fr_auto]"
        onSubmit={alEnviar((f) => subir.mutate(new FormData(f), { onSuccess: () => f.reset() }))}
      >
        <Campo label="Imagen" name="imagen" type="file" accept="image/jpeg,image/png,image/webp" required />
        <Campo label="Título (opcional)" name="titulo" />
        <button className="boton" disabled={subir.isPending}><i className="bi bi-plus-lg" aria-hidden /> Agregar</button>
      </form>

      <ConDatos<ImagenGaleria[]> ruta={RUTA}>
        {(items) => items.length ? (
          <>
            <ListaOrdenable items={items} onOrdenar={reordenar}>
              {(item, asa) => (
                <form
                  className="flex flex-wrap items-center gap-3 rounded-lg border border-zinc-200 bg-white p-2"
                  onSubmit={alEnviar((f) => editar.mutate({ id: item.id, form: new FormData(f) }, { onSuccess: () => limpiarArchivos(f) }))}
                >
                  {asa}
                  <img src={imagen('gallery', item.nombre_archivo)} alt="" className="h-16 w-24 rounded object-cover" />
                  <input name="titulo" defaultValue={item.titulo ?? ''} aria-label="Título" placeholder="Sin título" className="campo min-w-40 flex-1" />
                  <label className="boton-sec cursor-pointer">
                    <i className="bi bi-arrow-repeat" aria-hidden /> Cambiar imagen
                    <input type="file" name="imagen" accept="image/jpeg,image/png,image/webp" className="sr-only"
                      onChange={(e) => e.currentTarget.form?.requestSubmit()} />
                  </label>
                  <button className="boton-sec"><i className="bi bi-check2" aria-hidden /> Guardar</button>
                  <button type="button" className="boton-peligro" onClick={() => confirm('¿Eliminar esta imagen?') && eliminar.mutate(item.id)}>
                    <i className="bi bi-trash" aria-hidden /><span className="sr-only">Eliminar</span>
                  </button>
                </form>
              )}
            </ListaOrdenable>
            <Pista>Arrastra para cambiar el orden; se guarda automáticamente.</Pista>
          </>
        ) : <Vacio>La galería está vacía.</Vacio>}
      </ConDatos>
    </Pagina>
  )
}
