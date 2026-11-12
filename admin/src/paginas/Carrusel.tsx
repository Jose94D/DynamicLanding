import { api, imagen, useAccion, useReordenar } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { ConDatos, Pagina, Pista, Vacio } from '../componentes/ui'
import type { Imagen } from '../tipos'

const RUTA = '/api/admin/carrusel'

export function Carrusel() {
  const subir = useAccion((archivo: File) => {
    const form = new FormData()
    form.append('imagen', archivo)
    return api(RUTA, { method: 'POST', form })
  }, [RUTA], 'Imagen subida.')
  const eliminar = useAccion((id: number) => api(`${RUTA}/${id}`, { method: 'DELETE' }), [RUTA], 'Imagen eliminada.')
  const reordenar = useReordenar<Imagen>(RUTA, `${RUTA}/orden`)

  return (
    <Pagina titulo="Carrusel de imágenes" icono="bi-images" descripcion="Imágenes que rotan en el carrusel de la landing.">
      <div className="tarjeta">
        <label className="boton cursor-pointer has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-zinc-500">
          <i className="bi bi-upload" aria-hidden /> {subir.isPending ? 'Subiendo…' : 'Subir imágenes'}
          <input
            type="file"
            multiple
            accept="image/jpeg,image/png,image/webp"
            className="sr-only"
            disabled={subir.isPending}
            onChange={async (e) => {
              const input = e.currentTarget
              for (const archivo of Array.from(input.files ?? [])) await subir.mutateAsync(archivo).catch(() => {})
              input.value = ''
            }}
          />
        </label>
        <p className="mt-2 text-xs text-zinc-500">JPG, PNG o WebP, hasta 10 MB. Se optimizan automáticamente.</p>
      </div>

      <ConDatos<Imagen[]> ruta={RUTA}>
        {(imagenes) => imagenes.length ? (
          <>
            <ListaOrdenable items={imagenes} onOrdenar={reordenar} grilla>
              {(img, asa) => (
                <figure className="overflow-hidden rounded-lg border border-zinc-200 bg-white">
                  <img src={imagen('carousel', img.nombre_archivo)} alt="" className="aspect-video w-full object-cover" />
                  <figcaption className="flex items-center justify-between p-2">
                    {asa}
                    <button className="boton-peligro" onClick={() => confirm('¿Eliminar esta imagen?') && eliminar.mutate(img.id)}>
                      <i className="bi bi-trash" aria-hidden /> <span className="sr-only">Eliminar</span>
                    </button>
                  </figcaption>
                </figure>
              )}
            </ListaOrdenable>
            <Pista>Arrastra para cambiar el orden; se guarda automáticamente.</Pista>
          </>
        ) : <Vacio>Aún no hay imágenes en el carrusel.</Vacio>}
      </ConDatos>
    </Pagina>
  )
}
